tasks = []


def task(func):
    func.__task__ = True
    tasks.append(func)
    return func
