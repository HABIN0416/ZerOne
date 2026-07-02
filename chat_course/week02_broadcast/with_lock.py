import threading, time

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100_000):
        with lock:          # 이 블록은 한 번에 한 스레드만
            v = counter
            #time.sleep(0.00001)
            time.sleep(0)
            counter = v + 1

threads = [threading.Thread(target=increment) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()

print(f"기대값: 500000, 실제값: {counter}")  # 정확히 500000

