from io import StringIO

import mock

# http://codereview.stackexchange.com/questions/9228/monkeypatching-builtin-open-and-file-mock-up-for-unit-testing-satisfactory-appr
class MockFile(StringIO):
    """Wraps StringIO, because of python 2.6: clumsy name-property reset"""

    name = None #overwrite TextIOWrapper-property - part 1/2
    _vfs = {} #virtual File-System enables to "re-read" already written MockFiles

    def __init__(self, name, mode='r', buffer_=''):
        self.name = name #overwrite TextIOWrapper-property - part 2/2
        buffer_ = self._vfs.get(name, buffer_)
        super(MockFile, self).__init__(buffer_)

    def close(self):
        self._vfs[self.name] = self.getvalue()
        super(MockFile, self).close()

    @property
    def contents(self):
        return self._vfs[self.name]

def mockio(files):
    """
    A decorator that allows you mock `open` method.
    Usage:

        files = {
            "/etc/nginx/sites-enabled/foo": "server {}"
        }

        @mockio(files)
        def test_foo():
            assert open("/etc/nginx/sites-enabled/foo").read(), "server {}"

    """
    class LocalMockFile(MockFile):
        _vfs = files.copy()

    def get_file(filename, *args):
        try:
            return LocalMockFile(filename)
        except KeyError:
            raise IOError

    def wrap(func):
        def inner(*args, **kwargs):
            with mock.patch("builtins.open") as _open:
                _open.side_effect = get_file
                return func(*args, **kwargs)
        return inner

    return wrap
