class MockOpenedFile(object):
    def __init__(self, value='value'):
        self.seek_values = []
        self.buf_values = []
        self.value = value

    def seek(self, offset):
        self.seek_values.append(offset)

    def read(self, buf):
        self.buf_values.append(buf)
        return self.value

    def clean(self):
        self.seek_values = []
        self.buf_values = []
