class BaseTask:
    def __init__(self):
        self.__has_error = False

    def do(self):
        raise NotImplementedError

    @property
    def has_error(self):
        return self.__has_error

    @has_error.setter
    def has_error(self, value):
        raise AttributeError("has_error is read-only")

    def _set_error(self):
        self.__has_error = True