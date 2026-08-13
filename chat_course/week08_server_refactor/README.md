# Week 8 — 서버 종합 리팩터링: 객체들의 협력

다시 커진 서버를 **작은 객체로 나눕니다**. `ChatServer` 는 직접 일하지 않고
부품들을 조립해 흐름만 지휘합니다. 새 명령(`/rename`, 귓속말 `/w`)이
**한 곳 수정**으로 추가되는 걸 확인합니다.

## 파일
| 파일 | 책임 |
|------|------|
| `session.py` | `Session`(접속 한 사람) · `ConnectionManager`(접속 관리) |
| `command.py` | `CommandHandler` — 명령을 '표(dict)'로 해석 |
| `room.py` | `Room` — 방의 멤버·기록·전송 (7주차 재사용) |
| `repository.py` | `RoomRepository` — 방 저장/조회 (7주차 재사용) |
| `server.py` | `ChatServer` — 부품을 조립하고 흐름만 지휘 |
| `client.py` | 명령이 늘어난 클라이언트 |
| `codec.py` | `AesGcmCodec`(AES-256-GCM) — 6주차부터 평문 제거, 계속 암호화 |
| `make_ppt.py` / `Week08_서버리팩터링.pptx` | 강의 슬라이드 |

## 준비물
AES 암호화를 계속 쓰므로 `cryptography` 가 필요합니다 (6~7주차와 동일):
```bash
pip install cryptography
```
> 서버·클라이언트가 `codec.py` 의 같은 `SECRET_PASSPHRASE` 를 써야 통합니다.

## 실행 방법
```bash
python server.py            # 터미널 1
python client.py            # 터미널 2, 3 …
```
명령: `/create 방`, `/join 방`, `/leave`, `/rooms`, `/who`, `/rename 이름`, `/w 닉 메시지`

## 핵심 개념
- **단일 책임**: 한 객체는 한 가지 일만 (연결 / 명령 / 방 / 저장)
- **협력**: `ChatServer` 는 '지휘자', 일은 부품(객체)들이 한다
- **명령 표**: 긴 `if/elif` 대신 `{명령: 메서드}` 표 → 새 명령은 한 줄 + 메서드 하나
- **조립(DI)**: `ChatServer(codec, rooms, connections)` 한 곳에서 주입

## 새 명령을 추가한 곳 (한 곳!)
```python
# command.py 의 표에 두 줄을 더했을 뿐, server.py 는 그대로
"/rename": self.cmd_rename,
"/w":      self.cmd_whisper,
```

## 실습 / 과제
1. 새 명령 추가 — 예: `/me`(행동 표현), `/count`(접속자 수)
   → `command.py` 표에 한 줄 + 메서드 하나
2. 귓속말 `/w` 를 현재 방 안에서만 가능하게 제한
3. (생각) 명령이 100개가 되어도 이 구조가 견딜까? 왜?

> 여기까지가 **서버의 완성**입니다. 10주차부터는 서버를 그대로 둔 채
> 화면(tkinter)·웹(WebSocket) 클라이언트를 붙입니다.

## PPT 다시 만들기 (강사용)
```bash
pip install python-pptx
python make_ppt.py
```
