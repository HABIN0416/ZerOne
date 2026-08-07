##쓰기만
f = open("C:/work/ZerOne/chat_course/week02_broadcast/BIN/새파일.txt", "w", encoding="utf-8") #encoding="utf-8" 한글 안깨지게
for i in range(1,11):
    data = "%d번째 줄입니다.\n" %i
    f.write(data)
f.close()

##readline()한줄씩 읽기
# f = open("C:/work/ZerOne/chat_course/week02_broadcast/BIN/새파일.txt", "r", encoding="utf-8")
# line = f.readline()
# print(line)
# f.close

#모든 줄 읽기
f = open("C:/work/ZerOne/chat_course/week02_broadcast/BIN/새파일.txt", "r", encoding="utf-8")
while True:
    line = f.readline()
    if not line: break
    print(line)
f.close()

#모든 줄을 한번에 읽기
# f = open("C:/work/ZerOne/chat_course/week02_broadcast/BIN/새파일.txt", "r", encoding="utf-8")
# while True:
#     line = f.readlines()
#     if not line: break
#     print(line) ###############붙여서 프린트되네 읽기 어려움
# f.close()

#read함수 사용하기
f = open("C:/work/ZerOne/chat_course/week02_broadcast/BIN/새파일.txt", "r", encoding="utf-8")
data = f.read()
print(data)
f.close()

#""a""는 새로운 내용 추가하기
f = open("C:/work/ZerOne/chat_course/week02_broadcast/BIN/새파일.txt", "a", encoding="utf-8")
for i in range(11,20):
    data = "%d 번째 줄입니다. \n" %i
    f.write(data)
f.close()