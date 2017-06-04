# -*- coding: utf-8 -*-

""" Provide classes to parse HGT file or iterate over the values in these files """

import os
import re
import struct
import math
import fractions


class HgtParser(object):
    """ A tool to parse a HGT file

    It is intended to be used in a context manager::

        with HgtParser('myhgtfile.hgt') as parser:
            parser.get_elevation((lat, lng))

    :param str filepath: the path to the HGT file to parse
    :param int width: provide the number of columns if not standard HGT squared file
    :param int width: provide the number of lines if not standard HGT squared file
    """

    VOID_VALUE = -32768

    def __init__(self, filepath, width=None, height=None):
        if not os.path.exists(filepath):
            raise Exception('file {} not found'.format(filepath))

        self.file = None
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        sample = int(math.sqrt(os.path.getsize(filepath) / 2))

        self.sample_lat = height or sample
        self.sample_lng = width or sample

        # the width (length on the longitude axis) of a square providing one elevation value
        self.square_width = fractions.Fraction(1, self.sample_lng - 1)

        # the height (length on the latitude axis) of a square providing one elevation value
        self.square_height = fractions.Fraction(1, self.sample_lat - 1)

        # the total width of the HGT file
        self.area_width = 1 + self.square_width

        # the total height of the HGT file
        self.area_height = 1 + self.square_height

        self.bottom_left_center = self._get_bottom_left_center(self.filename)
        self.corners = self._get_corners_from_filename(self.bottom_left_center)
        self.top_left_square = self._get_top_left_square()

    def __enter__(self):
        self.file = open(self.filepath, 'rb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
            self.file = None

    def get_value_iterator(self, as_float=True):
        return HgtValueIterator(self, as_float=as_float)

    def get_sample_iterator(self, width, height, as_float=True):
        return HgtSampleIterator(self, width, height, as_float=as_float)

    @property
    def nb_values(self):
        """
        :return: the total number of values in the file
        :rtype: int
        """
        return self.sample_lat * self.sample_lng

    def _get_top_left_square(self):
        """ Get the corners of the top left square in the HGT file

         .. note:: useful when iterating over all the values

        :return: tuple of 4 position tuples (bottom left, top left, top right, bottom right) with (lat, lng) for each
        position as float
        :rtype: ((float, float), (float, float), (float, float), (float, float))
        """
        return (
            (self.corners[1][0] - self.square_height, self.corners[1][1]),
            self.corners[1],
            (self.corners[1][0], self.corners[1][1] + self.square_width),
            (self.corners[1][0] - self.square_height, self.corners[1][1] + self.square_width)
        )

    def get_square_corners(self, line, col):
        """ Get the 4 corner positions of a square knowing the line number and the column

        :param int line: the line of the square
        :param int col: the column of the square
        :return: tuple of 4 position tuples (bottom left, top left, top right, bottom right) with (lat, lng) for each
        position as float
        :rtype: ((float, float), (float, float), (float, float), (float, float))
        """
        return (
            # bottom left corner
            (self.top_left_square[0][0] - line * self.square_height,
             self.top_left_square[0][1] + col * self.square_width),
            # top left corner
            (self.top_left_square[1][0] - line * self.square_height,
             self.top_left_square[1][1] + col * self.square_width),
            # top right corner
            (self.top_left_square[2][0] - line * self.square_height,
             self.top_left_square[2][1] + col * self.square_width),
            # bottom right corner
            (self.top_left_square[3][0] - line * self.square_height,
             self.top_left_square[3][1] + col * self.square_width)
        )

    def shift_first_square(self, line, col):
        """ Shift the top left square by the provided number of lines and columns

        :param int line: line number (from 0 to sample_lat - 1)
        :param int col: column number (from 0 to sample_lng - 1)
        :return: tuple of 4 position tuples (bottom left, top left, top right, bottom right) with (lat, lng) for each
        position as float
        :rtype: ((float, float), (float, float), (float, float), (float, float))
        """
        if not 0 <= line < self.sample_lat or not 0 <= col < self.sample_lng:
            raise Exception('Out of bound line or col')

        shifted = ()
        for corner in self.top_left_square:
            shifted += ((corner[0] - line * self.square_height, corner[1] + col * self.square_width),)
        return shifted

    @staticmethod
    def _get_bottom_left_center(filename):
        """ Extract the latitude and longitude of the center of the bottom left elevation
        square based on the filename

        :param str filename: name of the HGT file
        :return: tuple (latitude of the center of the bottom left square, longitude of the bottom left square)
        :rtype: tuple of float
        :raises Exception: if filename does not match an expected HGT file pattern
        """
        filename_regex = re.compile('^([NS])([0-9]+)([WE])([0-9]+).*')
        result = filename_regex.match(filename)
        if not result:
            raise Exception('file {} does not match expected HGT file pattern'.format(filename))

        lat_order, lat_left_bottom_center, lng_order, lng_left_bottom_center = result.groups()

        lat_left_bottom_center = fractions.Fraction(int(lat_left_bottom_center), 1)
        lng_left_bottom_center = fractions.Fraction(int(lng_left_bottom_center), 1)
        if lat_order == 'S':
            lat_left_bottom_center *= -1
        if lng_order == 'W':
            lng_left_bottom_center *= -1

        return lat_left_bottom_center, lng_left_bottom_center

    def _get_corners_from_filename(self, bottom_left_corner):
        """ Based on the bottom left center latitude and longitude get the latitude and longitude of all the corner
         covered by the parsed HGT file

        :param tuple bottom_left_corner: position of the bottom left corner (lat, lng)
        :return: tuple of 4 position tuples (bottom left, top left, top right, bottom right) with (lat, lng) for each
        position as float
        :rtype: ((float, float), (float, float), (float, float), (float, float))
        """
        bottom_left = (bottom_left_corner[0] - self.square_height / 2, bottom_left_corner[1] - self.square_width / 2)
        top_left = (bottom_left[0] + self.area_height, bottom_left[1])
        top_right = (top_left[0], top_left[1] + self.area_width)
        bottom_right = (bottom_left[0], bottom_left[1] + self.area_width)

        return bottom_left, top_left, top_right, bottom_right

    def is_inside(self, point):
        """ Check if the point is inside the parsed HGT file

        :param tuple point: (lat, lng) of the point
        :return: True if the point is inside else False
        :rtype: bool
        """
        return \
            self.corners[0][0] < point[0] \
            and self.corners[0][1] < point[1] \
            and point[0] < self.corners[2][0] \
            and point[1] < self.corners[2][1]

    def get_idx(self, col, line):
        """ Calculate the index of the value based on the column and line numbers of the value

        :param int col: the column number (zero based)
        :param int line: the line number (zero based)
        :return: the index of the value
        :rtype: int
        :raises Exception: if the col and line are outside the file
        """
        if not 0 <= line < self.sample_lat or not 0 <= col < self.sample_lng:
            raise Exception('Out of bound line or col')

        return line * self.sample_lng + col

    def get_value(self, idx):
        """ Get the elevation value at the provided index

        :param int idx: index of the value
        :return: the elevation value or None if no value at this index (instead of -32768)
        :rtype: int
        """
        self.file.seek(0)
        self.file.seek(idx * 2)
        buf = self.file.read(2)
        val, = struct.unpack('>h', buf)

        return val

    def get_idx_in_file(self, pos):
        """ From a position (lat, lng) as float. Get the index of the elevation value inside the HGT file

        :param tuple pos: (lat, lng) of the position
        :return: tuple (index on the latitude from the top, index on the longitude from the left, index in the file)
        :rtype: (int, int, int)
        :raises Exception: if the point could not be found in the parsed HGT file
        """
        if not self.is_inside(pos):
            raise Exception('point {} is not inside HGT file {}'.format(pos, self.filename))

        lat_idx = (self.sample_lat - 1) - int(round((pos[0] - self.bottom_left_center[0]) / self.square_height))
        lng_idx = int(round((pos[1] - self.bottom_left_center[1]) / self.square_width))
        idx = lat_idx * self.sample_lng + lng_idx
        return lat_idx, lng_idx, idx

    def get_elevation(self, pos):
        """ Get the elevation for a position

        :param tuple pos: (lat, lng) of the position
        :return: tuple (index on the latitude from the top, index on the longitude from the left, elevation in meters)
        :rtype: (int, int, int)
        :raises Exception: if the point could not be found in the parsed HGT file
        """
        lat_idx, lng_idx, idx = self.get_idx_in_file(pos)

        # If no elevation returns None
        value = self.get_value(idx)
        value = value if value != self.VOID_VALUE else None

        return lat_idx, lng_idx, value


class HgtBaseIterator(object):
    """ Base iterator to share methods

    :param bool as_float: if True returns square cornes as float else as :class:`fractions.Fraction`
    """
    def __init__(self, as_float=True):
        self.as_float = as_float

    def to_float(self, value):
        """ Convert a :class:`fractions.Fraction` to a float if `as_float` is True

        :param value: the fraction to convert
        :type value: :class:`fractions.Fraction`
        :return: the converted value
        :rtype: :class:`fractions.Fraction` or float
        """
        return float(value) if self.as_float else value

    def format_corners(self, corners):
        """ """
        square = ()
        for corner in corners:
            square += ((self.to_float(corner[0]), self.to_float(corner[1])),)
        return square


class HgtValueIterator(HgtBaseIterator):
    """ Iterator over all the elevation values in the file

    :param parser: a HgtParser instance
    :type parser: :class:`gmalthgtparser.parser.HgtParser`
    :param bool as_float: if True converts fraction to float
    :return: tuple with (zero based line number, zero based column number, zero based index,
    square corners of the elevation value, elevation value)
    :rtype: (int, int, int, ((float, float), (float, float), (float, float), (float, float)), int)
    """
    def __init__(self, parser, as_float=True):
        super(HgtValueIterator, self).__init__(as_float=as_float)
        self.parser = parser
        self.idx = 0

    @property
    def nb_values(self):
        """
        :return: the total number of values returned contained the iterable
        :rtype: int
        """
        return self.parser.nb_values

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        current_idx = self.idx
        if current_idx < self.parser.sample_lat * self.parser.sample_lng:
            line, col = divmod(current_idx, self.parser.sample_lng)
            square = self.parser.shift_first_square(line, col)
            self.idx += 1
            return line, col, current_idx, self.format_corners(square), self.parser.get_value(current_idx)
        raise StopIteration()


class HgtSampleIterator(HgtBaseIterator):
    """ Iterator over samples. For example 50x50 values per 50x50

    :param parser: a HgtParser instance
    :type parser: :class:`gmalthgtparser.parser.HgtParser`
    :param int width: width of the sample area
    :param int height: height of the sample area
    :param bool as_float: if True converts fraction to float
    :return: tuple with (zero based line number of top left corner, zero based column number of top left corner,
    zero based index of top left corner, square corners position, list of all elevation values in square line per line)
    :rtype: (int, int, int, ((float, float), (float, float), (float, float), (float, float)), int[][)
    """
    def __init__(self, parser, width, height, as_float=True):
        super(HgtSampleIterator, self).__init__(as_float=as_float)
        self.parser = parser
        self.width = width
        self.height = height
        self.range_line = range(0, self.parser.sample_lat, self.height)
        self.idx_line = 0
        self.range_col = range(0, self.parser.sample_lng, self.width)
        self.idx_col = 0

    @property
    def nb_values(self):
        """
        :return: the total number of values returned contained the iterable
        :rtype: int
        """
        return len(self.range_line) * len(self.range_col)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.idx_col > len(self.range_col) - 1:
            self.idx_col = 0
            self.idx_line += 1

        if self.idx_line > len(self.range_line) - 1:
            raise StopIteration()

        top_left_col_idx = self.range_col[self.idx_col]
        top_left_line_idx = self.range_line[self.idx_line]

        values = self._get_square_values(top_left_col_idx, top_left_line_idx)
        # Get all corners of the samples square area
        top_left_square_corners = self.parser.get_square_corners(top_left_line_idx, top_left_col_idx)
        top_left_corner = top_left_square_corners[1]
        square_corners = (
            # bottom left
            (top_left_corner[0] - len(values) * self.parser.square_height, top_left_corner[1]),
            # top left
            top_left_corner,
            # top right
            (top_left_corner[0], top_left_corner[1] + len(values[0]) * self.parser.square_width),
            # bottom right
            (top_left_corner[0] - len(values) * self.parser.square_height,
             top_left_corner[1] + len(values[0]) * self.parser.square_width)
        )

        # Return same model as HgtValueIterator with square width and height
        self.idx_col += 1
        return (
            top_left_line_idx,
            top_left_col_idx,
            self.parser.get_idx(top_left_col_idx, top_left_line_idx),
            self.format_corners(square_corners),
            values
        )

    def _get_square_values(self, top_left_col_idx, top_left_line_idx):
        """ Get all the elevation values in the requested square knowing
        its top left corner line and column numbers

        :param int top_left_col_idx: column number of the top left corner of the requested square
        :param int top_left_line_idx: line number of the top left corner of the requested square
        :return: list of list of elevation values (grouped per line)
        :rtype: list[list[int]]
        """
        square_values = []
        for idx in range(top_left_line_idx, min(self.parser.sample_lat, top_left_line_idx + self.height)):
            square_values.append(self._read_line(top_left_col_idx, idx))
        return square_values

    def _read_line(self, col_idx, line_idx):
        """ Get a line of elevation values in the requested square knowing the starting
        column number and the line number

        :param int col_idx: the starting column number
        :param int line_idx: the line number
        :return: list of elevation values
        :rtype: list[int]
        """
        line_values = []
        for idx in range(col_idx, min(self.parser.sample_lng, col_idx + self.width)):
            value_idx = self.parser.get_idx(idx, line_idx)
            line_values.append(self.parser.get_value(value_idx))
        return line_values
