import time

# t1 = time.perf_counter()
# time.sleep(10/1000)
# t2 = time.perf_counter()
# print(f"Raw: {t2 - t1}")
# final = (t2 - t1)*1000
# print(f"{final} ms")
# print(f"Difference: {final - 10} ms")

for _ in range(30):
    t1 = time.perf_counter()
    time.sleep(0.030)
    t2 = time.perf_counter()
    print(f"{(t2 - t1) * 1000} ms")
