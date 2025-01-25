from inject_environment_variables import EnvironmentVariableInjector


def inject_environment_variables(variables: dict):
    def decorator_func(func):
        def wrapper_func(*args, **kwargs):
            with EnvironmentVariableInjector(variables):
                res = func(*args, **kwargs)
            return res
        return wrapper_func
    return decorator_func
