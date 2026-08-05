import threading, time

counter = 0

def increment():
    global counter
    for _ in range(1_000):
        v = counter
        # 왜 슬립이 생겼을까?? 
        #   강제로 만든건데 예를 들어 파일을 처리한다거나. 데이터베이스에 저장한다거나...
        # time.sleep(0.00001)
        time.sleep(0)
        counter = v + 1

threads = [threading.Thread(target=increment) for _ in range(5)]
for t in threads: t.start()
for t in threads: t.join()

print(f"기대값: 5000, 실제값: {counter}")