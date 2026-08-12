"""
Week 6 - 서버 (server.py)  :  방(Room) — 일부러 엉성한 버전
------------------------------------------------------------
이번 주 목표: '전체 채팅'에서 '방별 채팅'으로.
            같은 방 사람에게만 메시지가 가게 한다.

※ 지난주의 깔끔한 ChatServer(부품 주입)를 '잠깐 내려놓습니다'.
  방을 우선 '막' 붙여 보고 — 곧(다음 주) 다시 객체로 정리할 겁니다.
  (버리는 코드를 두려워하지 않는다: 엉성한 버전 → 좋은 버전)

그래서 일부러 엉성하게 만듭니다.
방·사람·소켓 정보를 전부 '전역 딕셔너리'에 흩어 둡니다.

  rooms      = {방이름: [소켓, ...]}     # 방마다 누가 있나
  nicknames  = {소켓: 닉네임}            # 이 소켓은 누구
  where      = {소켓: 방이름}            # 이 소켓은 지금 어느 방

⚠️ 돌아가긴 합니다. 하지만 상태가 여기저기 흩어져 있어서,
   join/leave/퇴장 때마다 '세 군데를 다 맞춰' 고쳐야 합니다.
   하나라도 빠뜨리면 유령 회원 같은 버그가 생깁니다.
   이 엉킴이 다음 주 'Room 객체'의 동기입니다.
------------------------------------------------------------
명령: /create 방, /join 방, /leave, /rooms, /who
"""

import socket
import threading

from codec import AesGcmCodec
from messages import TextMessage, SystemMessage

HOST = "127.0.0.1"
PORT = 5000
CODEC = AesGcmCodec()   # AES-256-GCM 로 암호화 (평문 제거). 클라이언트도 같은 codec/암호여야 통함

# ── 전역 상태 (여기저기서 수정된다 = 엉성함의 근원) ──
rooms = {}          # 방이름 -> [소켓, ...]
nicknames = {}      # 소켓 -> 닉네임
where = {}          # 소켓 -> 현재 방이름 (없으면 None)
lock = threading.Lock()


def send_to(conn, message):
    try:
        conn.sendall(CODEC.encode(message))
    except OSError:
        pass


def room_broadcast(room_name, message):
    """그 방의 멤버에게만 보낸다."""
    with lock:
        members = list(rooms.get(room_name, []))
    for c in members:
        send_to(c, message)

##---------새로운 메소드 ------- 현재는 빈방일 시에 0명 처리만 되기에 빈 방일 때 방 폭파시키는 메소드 추가
def leave_room(conn, room_name):
    """conn을 room_name에서 빼고, 방이 비었으면 삭제한다"""
    if not room_name or room_name not in rooms:
        return
    if conn in rooms[room_name]:
        rooms[room_name].remove(conn)
    if not rooms[room_name]:
        del rooms[room_name]
        print(f"[서버] 빈 방 삭제: {room_name}")


def handle_command(conn, text):
    """명령을 직접 파싱 (엉성: 명령 처리 로직이 여기 다 모여 전역을 마구 건드림)."""
    parts = text.split(" ", 1)
    cmd = parts[0]
    arg = parts[1].strip() if len(parts) > 1 else ""
    nickname = nicknames[conn]

    # 방 이름이 필요한 명령인데 이름을 안 적었으면 막는다 (빈 이름 방 생성 방지)
    if cmd in ("/create", "/join") and not arg:
        send_to(conn, SystemMessage(f"방 이름을 함께 적어주세요:  {cmd} 방이름"))
        return

    if cmd == "/create":  #방만들기
        with lock:
            if arg in rooms:
                send_to(conn, SystemMessage(f"이미 있는 방입니다: {arg}"))
                return
            rooms[arg] = []
        send_to(conn, SystemMessage(f"방을 만들었습니다: {arg}  (/join {arg} 로 입장)"))

    elif cmd == "/join": #입장하기
        with lock:
            if arg not in rooms:
                send_to(conn, SystemMessage(f"없는 방입니다: {arg}  (/create {arg} 먼저)"))
                return
            old = where.get(conn)
            # 1) 이전 방에서 빼고 ------------>이 부분을 주석처리를 하면 1번방에서 나갔을 때 카운트가 중복으로 계속 남게됨
            # if old and conn in rooms.get(old, []):
            #     rooms[old].remove(conn)
            leave_room(conn, old)       ##과제 -- 빈 방이 되면 자동으로 삭제되게 해보기    
            # 2) 새 방에 넣고
            rooms[arg].append(conn)
            # 3) 현재 방 갱신  ← 이 '세 군데'를 매번 맞춰야 한다
            where[conn] = arg
        if old:
            room_broadcast(old, SystemMessage(f"*** {nickname}님이 방을 나갔습니다 ***"))
        room_broadcast(arg, SystemMessage(f"*** {nickname}님이 입장했습니다 ***"))

    elif cmd == "/leave":
        with lock:
            old = where.get(conn)
            if old and conn in rooms.get(old, []):
                rooms[old].remove(conn)
            where[conn] = None
        if old:
            room_broadcast(old, SystemMessage(f"*** {nickname}님이 방을 나갔습니다 ***"))
            send_to(conn, SystemMessage(f"방에서 나왔습니다: {old}"))

    elif cmd == "/rooms":
        # 주의: 메시지 한 개 = 한 줄 이라, 텍스트 안에 줄바꿈을 넣으면 안 된다.
        with lock:
            entries = [f"{name}({len(members)}명)" for name, members in rooms.items()]
        send_to(conn, SystemMessage("방 목록: " + (", ".join(entries) if entries else "(없음)")))

    elif cmd == "/who": ######where,.get(conn), rooms.get(room, []) ------->이거를 한줄로 만드는게 필요!!그게 room클래스
        with lock:
            room = where.get(conn)
            names = [nicknames[c] for c in rooms.get(room, [])] if room else []
        if room:
            send_to(conn, SystemMessage(f"[{room}] ({len(names)}명): " + ", ".join(names))) ##과제1 :/who를 개선해 닉네임과 방제를 보기좋게 함께 표시
        else:
            send_to(conn, SystemMessage("아직 방에 없습니다. /join 방이름"))

    else:
        send_to(conn, SystemMessage(f"알 수 없는 명령: {cmd}"))


def handle(conn, addr):
    reader = conn.makefile("r", encoding="utf-8")
    nickname = (reader.readline() or "").strip()
    if not nickname:
        conn.close()
        return

    with lock:
        nicknames[conn] = nickname
        where[conn] = None
    print(f"[서버] {nickname} 접속")
    send_to(conn, SystemMessage("명령: /create 방, /join 방, /leave, /rooms, /who"))

    try:
        while True:
            line = reader.readline()
            if not line:
                break
            msg = CODEC.decode(line.rstrip("\n"))

            # 엉성: 텍스트이면서 '/'로 시작하면 명령으로 가로챈다
            if isinstance(msg, TextMessage) and msg.text.startswith("/"):
                handle_command(conn, msg.text)
                continue

            # 일반 메시지는 '지금 있는 방'에만 뿌린다
            room = where.get(conn)
            if not room:
                send_to(conn, SystemMessage("먼저 /join 으로 방에 들어가세요."))
                continue
            msg.sender = nicknames[conn]
            room_broadcast(room, msg)
    except OSError:
        pass

    # 퇴장 처리: 전역 세 군데를 모두 정리해야 한다 (하나만 빠져도 버그)
    with lock:
        room = where.pop(conn, None)
        if room and conn in rooms.get(room, []):
            rooms[room].remove(conn)
        name = nicknames.pop(conn, "?")
    if room:
        room_broadcast(room, SystemMessage(f"*** {name}님이 나갔습니다 ***"))
    conn.close()
    print(f"[서버] {name} 퇴장")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[서버] {HOST}:{PORT} 대기 중... (Ctrl+C 종료)")
    try:
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[서버] 종료합니다.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
