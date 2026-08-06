"""
[시연용] wifi_mitm_demo/server.py  :  진짜 채팅 서비스 (★ '다른 컴퓨터'에서 실행)
============================================================
이 데모는 '악성 무료 와이파이(rogue AP)' 상황을 보여 줍니다. 기계 2대를 씁니다.

  학생(피해자) ──▶ 핫스팟 노트북 [sniffer.py :5000] ──▶ 다른 컴퓨터 [이 server.py :5000]
                    (몰래 엿보는 중간자)                  (진짜 서버, 저 멀리)

server.py 는 '진짜 채팅 서비스'라서 sniffer 와는 다른 컴퓨터에서 돌립니다.
학생은 서버가 저기 있는 줄만 알지, 그 앞(핫스팟)에 sniffer 가 몰래 끼어 있는 건 모릅니다.
→ "서버는 멀리 있는데도 중간에서 다 털린다"가 더 잘 드러납니다.

이 서버는 밖(sniffer)에서 접속해야 하므로 HOST="0.0.0.0" 으로 받습니다.
그 컴퓨터의 방화벽에서 5000 인바운드를 허용해야 합니다(README 참고).
"""

import socket
import threading

from interfaces import MessageStore, Transport
from codec import PlainCodec, SecretCodec
from messages import SystemMessage

HOST = "0.0.0.0"       # 다른 기계(sniffer)가 접속해야 하므로 모든 인터페이스에서 수신
PORT = 5000            # 다른 컴퓨터라 sniffer(5000)와 겹치지 않음 → 5000 통일

# ★ 평문/암호화 전환 ★  클라이언트도 같은 값으로 맞추세요.
USE_SECRET = False


class ChatServer:
    def __init__(self, codec, store):
        self.codec = codec
        self.store = store
        self.clients = {}
        self._lock = threading.Lock()

    def join(self, transport, nickname):
        with self._lock:
            self.clients[transport] = nickname
            count = len(self.clients)
        self._broadcast(SystemMessage(f"*** {nickname}님이 들어왔습니다 (현재 {count}명) ***"))
        return count

    def leave(self, transport):
        with self._lock:
            nickname = self.clients.pop(transport, None)
            count = len(self.clients)
        if nickname:
            self._broadcast(SystemMessage(f"*** {nickname}님이 나갔습니다 (현재 {count}명) ***"))

    def on_line(self, transport, line):
        msg = self.codec.decode(line)
        with self._lock:
            msg.sender = self.clients.get(transport, "?")
        try:
            self.store.save(msg)
        except Exception as e:
            print(f"[경고] 저장 실패: {e}")
        self._broadcast(msg)
        return msg

    def _broadcast(self, message):
        data = self.codec.encode(message)
        with self._lock:
            targets = list(self.clients.keys())
        for t in targets:
            t.send(data)


class InMemoryStore(MessageStore):
    def __init__(self):
        self._items = []

    def save(self, message):
        self._items.append(message)

    def all(self):
        return list(self._items)


class SocketTransport(Transport):
    def __init__(self, conn):
        self.conn = conn

    def send(self, data):
        try:
            self.conn.sendall(data)
        except OSError:
            pass


def build_server():
    codec = SecretCodec() if USE_SECRET else PlainCodec()
    return ChatServer(codec, InMemoryStore())


def main():
    server = build_server()
    print(f"[서비스] Codec={server.codec.name}  /  {HOST}:{PORT} 대기 (다른 컴퓨터의 진짜 서버)")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()

    def handle(conn, addr):
        reader = conn.makefile("r", encoding="utf-8")
        transport = SocketTransport(conn)
        nickname = (reader.readline() or "").strip()
        if not nickname:
            conn.close()
            return
        server.join(transport, nickname)
        try:
            while True:
                line = reader.readline()
                if not line:
                    break
                server.on_line(transport, line.rstrip("\n"))
        except OSError:
            pass
        finally:
            server.leave(transport)
            conn.close()

    try:
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[서비스] 종료합니다.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
