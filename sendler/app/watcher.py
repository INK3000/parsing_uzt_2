from time import perf_counter


def watcher(func):
    def wrapper(*args, **kwargs):
        start = perf_counter()
        result = func(*args, **kwargs)
        print(
            f"Время выполнения {func.__name__}: {perf_counter() - start:.6f} сек.")
        return result

    return wrapper
