import re


class Resource:
    def __init__(self, func, name=None):
        self.func = func
        self.name = name or self.func.__name__

    def __call__(self, *args, **kwargs):
        return self.func


class Hook(Resource):
    def __init__(self, callback, name=None):
        super().__init__(callback, name)
        self.func = callback
        self.regex = ''

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    @staticmethod
    def get_cls(f):
        def decorated(f_arg):
            if not isinstance(f_arg, Hook):
                f_arg = Hook(f_arg)

            return f(f_arg)

        return decorated

    def bake(self):
        pattern = r'(?P<hook>{name})'
        if self.regex:
            pattern += r'\s+{rest}'

        self.regex = re.compile(pattern.format(name=self.name, rest=self.regex))


def hook(name=None):
    @Hook.get_cls
    def decorated(f):
        f.name = name
        f.bake()

        return f

    return decorated


def parameter(name, greedy=True):
    @Hook.get_cls
    def decorated(f):
        f.regex += '(?P<{name}>{regex})'.format(name=name, regex='.+' if greedy else r'\S+')

        return f

    return decorated


def resource(name=None):
    def decorated(f):
        return Resource(f, name)

    return decorated
