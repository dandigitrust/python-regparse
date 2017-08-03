from jinja2 import Environment, PackageLoader


class JinjaEnv(object):
    _env = None

    @classmethod
    def get_env(cls):
        if not cls._env:
            # do environment initialization here
            cls._env = Environment(keep_trailing_newline=True, loader=PackageLoader('regparse', 'templates'))
        return cls._env
