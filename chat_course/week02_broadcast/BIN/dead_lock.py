import threading, time

lock_a = threading.Lock()
lock_b = threading.Lock()

def worker1():
    with lock_a:
        print("[T1] A 획득")
        time.sleep(0.1)          # T2가 B를 잡을 시간을 확보 (재현성용)
        print("[T1] B 대기...")
        with lock_b:
            print("[T1] B 획득")

def worker2():
    with lock_b:                 # T1과 반대 순서!
        print("[T2] B 획득")
        time.sleep(0.1)
        print("[T2] A 대기...")
        with lock_a:
            print("[T2] A 획득")

t1 = threading.Thread(target=worker1)
t2 = threading.Thread(target=worker2)
t1.start(); t2.start()
t1.join(); t2.join()
print("끝")   
# 영원히 출력되지 않음
# 여기서 질문 왜 lock 2개일까요?
# 하나만 쓰면 해결 아닌가요?
# 하나만 쓰면 데드락 없는 거 아닌가?