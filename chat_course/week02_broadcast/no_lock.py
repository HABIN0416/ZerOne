import threading, time

counter = 0

def increment():
    global counter
    for _ in range(1_000):
        v = counter
        counter = v + 1

threads = [threading.Thread(target=increment) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()

print(f"기대값: 5000, 실제값: {counter}")
## 실행해보면 어 이게 왜 동작하는거 같지????