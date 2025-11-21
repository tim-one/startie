import time


def main(obj):
    import array
    for _ in range(10_000):
        assert data.index(10, 100) == len(data) - 1


if __name__ == '__main__':
    data = memoryview(bytearray(64 * 1024))
    data[-1] = 10
    start = time.perf_counter()
    main(data)
    stop = time.perf_counter()
    print(f'time = {stop-start:.3f}')