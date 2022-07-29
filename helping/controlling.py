def run_once(f):
    """
    A wrapper to run a function **f** only once.

    :param f: a function.
    :return: f's function return.
    """
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)
    wrapper.has_run = False
    return wrapper
