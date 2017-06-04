import collections
import struct
import os
from fractions import Fraction

import pytest

from . import tools as test_tools
import gmalthgtparser.parser as hgt


@pytest.fixture
def srtm1_hgt_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'srtm1', 'N00E010.hgt')


@pytest.fixture
def srtm3_hgt_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'srtm3', 'N00E010.hgt')


@pytest.fixture
def srtm1_hgt(srtm1_hgt_path):
    return hgt.HgtParser(srtm1_hgt_path)


@pytest.fixture
def srtm3_hgt(srtm3_hgt_path):
    return hgt.HgtParser(srtm3_hgt_path)


class TestHgtParser(object):

    def test_instanciate_file_not_found(self):
        with pytest.raises(Exception) as e:
            hgt.HgtParser('N00E010.hgt')
        assert str(e.value) == "file N00E010.hgt not found"

    def test_get_iterators(self, srtm3_hgt):
        assert isinstance(srtm3_hgt.get_value_iterator(), collections.Iterable)
        assert isinstance(srtm3_hgt.get_sample_iterator(50, 50), collections.Iterable)

    def test_nb_values(self, srtm1_hgt, srtm3_hgt):
        assert srtm1_hgt.nb_values == 12967201
        assert srtm3_hgt.nb_values == 1442401

    def test_get_top_left_square(self, srtm3_hgt):
        corners = (
            (Fraction(2399, 2400), Fraction(23999, 2400)),  # (0.9995833333333334, 9.999583333333334)
            (Fraction(2401, 2400), Fraction(23999, 2400)),  # (1.0004166666666667, 9.999583333333334)
            (Fraction(2401, 2400), Fraction(24001, 2400)),  # (1.0004166666666667, 10.000416666666666)
            (Fraction(2399, 2400), Fraction(24001, 2400))  # (0.9995833333333334, 10.000416666666666)
        )
        assert srtm3_hgt._get_top_left_square() == corners

    def test_shift_first_square(self, srtm3_hgt):
        corners = (
            (Fraction(95, 96), Fraction(23999, 2400)),  # (0.9895833333333334, 9.999583333333334)
            (Fraction(2377, 2400), Fraction(23999, 2400)),  # (0.9904166666666666, 9.999583333333334)
            (Fraction(2377, 2400), Fraction(24001, 2400)),  # (0.9904166666666666, 10.000416666666666)
            (Fraction(95, 96), Fraction(24001, 2400))  # (0.9895833333333334, 10.000416666666666)
        )
        assert srtm3_hgt.shift_first_square(12, 0) == corners

        corners = (
            (Fraction(2399, 2400), Fraction(24023, 2400)),  # (0.9995833333333334, 10.009583333333333)
            (Fraction(2401, 2400), Fraction(24023, 2400)),  # (1.0004166666666667, 10.009583333333333)
            (Fraction(2401, 2400), Fraction(961, 96)),  # (1.0004166666666667, 10.010416666666666)
            (Fraction(2399, 2400), Fraction(961, 96))  # (0.9995833333333334, 10.010416666666666)
        )
        assert srtm3_hgt.shift_first_square(0, 12) == corners

        corners = (
            (Fraction(413, 480), Fraction(8717, 800)),  # (0.8604166666666667, 10.89625)
            (Fraction(689, 800), Fraction(8717, 800)),  # (0.86125, 10.89625)
            (Fraction(689, 800), Fraction(26153, 2400)),  # (0.86125, 10.897083333333333)
            (Fraction(413, 480), Fraction(26153, 2400))  # (0.8604166666666667, 10.897083333333333)
        )
        assert srtm3_hgt.shift_first_square(167, 1076) == corners

        with pytest.raises(Exception) as e:
            srtm3_hgt.shift_first_square(-5, 0)
        assert str(e.value) == "Out of bound line or col"
        with pytest.raises(Exception) as e:
            srtm3_hgt.shift_first_square(56, 1201)
        assert str(e.value) == "Out of bound line or col"

    def test_square_width_height(self, srtm3_hgt, srtm1_hgt):
        assert srtm3_hgt.square_width == Fraction(1, 1200)  # 0.0008333333333333334
        assert srtm3_hgt.square_height == Fraction(1, 1200)  # 0.0008333333333333334

        assert srtm1_hgt.square_width == Fraction(1, 3600)  # 0.0002777777777777778
        assert srtm1_hgt.square_height == Fraction(1, 3600)  # 0.0002777777777777778

    def test_area_width_height(self, srtm3_hgt, srtm1_hgt):
        assert srtm3_hgt.area_width == Fraction(1201, 1200)  # 1.0008333333333332
        assert srtm3_hgt.area_height == Fraction(1201, 1200)  # 1.0008333333333332

        assert srtm1_hgt.area_width == Fraction(3601, 3600)  # 1.0002777777777778
        assert srtm1_hgt.area_height == Fraction(3601, 3600)  # 1.0002777777777778

    def test_get_bottom_left_center(self, srtm3_hgt):
        assert srtm3_hgt._get_bottom_left_center('N00E010.hgt') == (0, 10)
        assert srtm3_hgt._get_bottom_left_center('S20W03.hgt') == (-20, -3)
        assert srtm3_hgt._get_bottom_left_center('N01W001.hgt') == (1, -1)
        with pytest.raises(Exception):
            srtm3_hgt._get_bottom_left_center('SF01AB001.hgt')

    def test_get_corners_from_filename(self, srtm3_hgt, srtm1_hgt):
        corners = (
            (Fraction(-1, 2400), Fraction(23999, 2400)),  # (-0.0004166666666666667, 9.999583333333334)
            (Fraction(2401, 2400), Fraction(23999, 2400)),  # (1.0004166666666667, 9.999583333333334)
            (Fraction(2401, 2400), Fraction(26401, 2400)),  # (1.0004166666666667, 11.000416666666666)
            (Fraction(-1, 2400), Fraction(26401, 2400))  # (-0.0004166666666666667, 11.000416666666666)
        )
        assert srtm3_hgt._get_corners_from_filename((0, 10)) == corners

        corners = (
            (Fraction(-1, 7200), Fraction(71999, 7200)),  # (-0.0001388888888888889, 9.99986111111111)
            (Fraction(7201, 7200), Fraction(71999, 7200)),  # (1.000138888888889, 9.99986111111111)
            (Fraction(7201, 7200), Fraction(79201, 7200)),  # (1.000138888888889, 11.00013888888889)
            (Fraction(-1, 7200), Fraction(79201, 7200))  # (-0.0001388888888888889, 11.00013888888889)
        )
        assert srtm1_hgt._get_corners_from_filename((0, 10)) == corners

    def test_is_inside(self, srtm3_hgt):
        assert srtm3_hgt.is_inside((0.5, 10.5))
        assert srtm3_hgt.is_inside((0.1, 10.9))

        assert not srtm3_hgt.is_inside((1.5, 10.9))
        assert not srtm3_hgt.is_inside((0.5, 9.8))

    def test_get_idx(self, srtm3_hgt, srtm1_hgt):
        assert srtm3_hgt.get_idx(5, 1200) == 1441205
        assert srtm3_hgt.get_idx(1200, 5) == 7205

        with pytest.raises(Exception) as e:
            assert srtm3_hgt.get_idx(-5, 1200)
        assert str(e.value) == "Out of bound line or col"
        with pytest.raises(Exception) as e:
            assert srtm3_hgt.get_idx(5, 1201)
        assert str(e.value) == "Out of bound line or col"

        assert srtm1_hgt.get_idx(5, 1200) == 4321205
        assert srtm1_hgt.get_idx(1200, 5) == 19205

    def test_get_value(self, monkeypatch, srtm3_hgt):
        opened_file = test_tools.MockOpenedFile(struct.pack('>h', 156))
        monkeypatch.setattr(srtm3_hgt, 'file', opened_file)
        alt_value = srtm3_hgt.get_value(7205)

        assert opened_file.seek_values == [0, 14410]
        assert opened_file.buf_values == [2]
        assert alt_value == 156

        opened_file.clean()
        opened_file.value = struct.pack('>h', -32768)
        alt_value = srtm3_hgt.get_value(7205)
        assert alt_value == -32768

    def test_get_idx_in_file(self, srtm3_hgt):
        with pytest.raises(Exception) as e:
            srtm3_hgt.get_idx_in_file((3.0, 12))
        assert str(e.value) == "point (3.0, 12) is not inside HGT file N00E010.hgt"

        assert srtm3_hgt.get_idx_in_file((0.56, 10.86)) == (528, 1032, 635160)

    def test_get_elevation(self, srtm3_hgt):
        with srtm3_hgt as parser:
            assert parser.get_elevation((0.56, 10.86)) == (528, 1032, 411)
            assert parser.get_elevation((0.1, 10.1)) == (1080, 120, 53)
            assert parser.get_elevation((1.0001, 11.0001)) == (0, 1200, 505)

    def test_get_elevation_void_value(self, monkeypatch, srtm3_hgt):
        def mockreturn(idx):
            return hgt.HgtParser.VOID_VALUE
        monkeypatch.setattr(srtm3_hgt, 'get_value', mockreturn)
        with srtm3_hgt as parser:
            assert parser.get_elevation((1.0001, 11.0001)) == (0, 1200, None)


class TestHgtValueIterator(object):
    def test_nb_values(self, srtm3_hgt):
        with srtm3_hgt as parser:
            assert parser.get_value_iterator().nb_values == 1442401

    def test_iter(self, srtm3_hgt):
        with srtm3_hgt as parser:
            values = list(parser.get_value_iterator())

            assert len(values) == 1442401
            assert (0, 0, 0,
                    ((0.9995833333333334, 9.999583333333334),
                     (1.0004166666666667, 9.999583333333334),
                     (1.0004166666666667, 10.000416666666666),
                     (0.9995833333333334, 10.000416666666666)),
                    57) == values[0]
            assert (2, 1053, 3455,
                    ((0.9979166666666667, 10.877083333333333),
                     (0.99875, 10.877083333333333),
                     (0.99875, 10.877916666666666),
                     (0.9979166666666667, 10.877916666666666)),
                    516) == values[3455]

    def test_iter_not_as_float(self, srtm3_hgt):
        with srtm3_hgt as parser:
            value = next(iter(parser.get_value_iterator(as_float=False)))
            assert (0, 0, 0,
                    ((Fraction(2399, 2400), Fraction(23999, 2400)),
                     (Fraction(2401, 2400), Fraction(23999, 2400)),
                     (Fraction(2401, 2400), Fraction(24001, 2400)),
                     (Fraction(2399, 2400), Fraction(24001, 2400))),
                    57) == value


class TestHgtSampleIterator(object):
    def test_nb_values(self, srtm3_hgt):
        with srtm3_hgt as parser:
            assert parser.get_sample_iterator(50, 50).nb_values == 625

    def test_iter(self, srtm3_hgt):
        with srtm3_hgt as parser:
            square_values = list(parser.get_sample_iterator(50, 50))

            assert len(square_values) == 625

            assert square_values[0][0] == 0
            assert square_values[0][1] == 0
            assert square_values[0][2] == 0
            assert square_values[0][3] == ((0.95875, 9.999583333333334),
                                           (1.0004166666666667, 9.999583333333334),
                                           (1.0004166666666667, 10.04125),
                                           (0.95875, 10.04125))
            assert len([value for line in square_values[0][4] for value in line]) == 2500

            assert square_values[24][0] == 0
            assert square_values[24][1] == 1200
            assert square_values[24][2] == 1200
            assert square_values[24][3] == ((0.95875, 10.999583333333334),
                                            (1.0004166666666667, 10.999583333333334),
                                            (1.0004166666666667, 11.000416666666666),
                                            (0.95875, 11.000416666666666))
            assert len([value for line in square_values[24][4] for value in line]) == 50

            assert square_values[25][0] == 50
            assert square_values[25][1] == 0
            assert square_values[25][2] == 60050
            assert square_values[25][3] == ((0.9170833333333334, 9.999583333333334),
                                            (0.95875, 9.999583333333334),
                                            (0.95875, 10.04125),
                                            (0.9170833333333334, 10.04125))
            assert len([value for line in square_values[25][4] for value in line]) == 2500

            assert square_values[612][0] == 1200
            assert square_values[612][1] == 600
            assert square_values[612][2] == 1441800
            assert square_values[612][3] == ((-0.0004166666666666667, 10.499583333333334),
                                             (0.0004166666666666667, 10.499583333333334),
                                             (0.0004166666666666667, 10.54125),
                                             (-0.0004166666666666667, 10.54125))
            assert len([value for line in square_values[612][4] for value in line]) == 50

            assert square_values[624][0] == 1200
            assert square_values[624][1] == 1200
            assert square_values[624][2] == 1442400
            assert square_values[624][3] == ((-0.0004166666666666667, 10.999583333333334),
                                             (0.0004166666666666667, 10.999583333333334),
                                             (0.0004166666666666667, 11.000416666666666),
                                             (-0.0004166666666666667, 11.000416666666666))
            assert len([value for line in square_values[624][4] for value in line]) == 1

    def test_iter_not_as_float(self, srtm3_hgt):
        with srtm3_hgt as parser:
            value = next(iter(parser.get_sample_iterator(50, 50, as_float=False)))
            assert value[0] == 0
            assert value[1] == 0
            assert value[2] == 0
            assert value[3] == ((Fraction(767, 800), Fraction(23999, 2400)),
                                (Fraction(2401, 2400), Fraction(23999, 2400)),
                                (Fraction(2401, 2400), Fraction(8033, 800)),
                                (Fraction(767, 800), Fraction(8033, 800)))
            assert len([elev_value for line in value[4] for elev_value in line]) == 2500
