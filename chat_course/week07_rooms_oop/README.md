# Week 7 — 방을 객체로 + 저장소를 DI로

6주차의 흩어진 전역 상태를 **`Room` 객체**로 캡슐화하고, 방의 생성·저장을
**`RoomRepository`(인터페이스+DI)** 로 분리합니다. 저장소를 파일 버전으로 바꾸면
**서버를 껐다 켜도 방이 남습니다.**

## 파일
| 파일 | 설명 |
|------|------|
| `room.py` | `Room` 객체 — 이름·멤버·기록 + `join/leave/post` |
| `repository.py` | `RoomRepository`(계약) + `InMemory`/`File` 구현 |
| `server.py` | 저장소를 주입받아 사용, 상태 변경은 Room 에 위임 |
| `client.py` | 방 명령 클라이언트 (6주차와 동일) |
| `messages.py` | 이전 주차 재사용 |
| `codec.py` | **AesGcmCodec(AES-256-GCM)** — 6주차부터 평문 제거, 계속 암호화 |
| `make_ppt.py` / `Week07_Room객체_저장소DI.pptx` | 강의 슬라이드 |

## 준비물
AES 암호화를 계속 쓰므로 `cryptography` 가 필요합니다 (6주차와 동일):
```bash
pip install cryptography
```
> 서버·클라이언트가 `codec.py` 의 같은 `SECRET_PASSPHRASE` 를 써야 통합니다.

## 실행 방법
```bash
python server.py            # 터미널 1
python client.py            # 터미널 2, 3 …
```
명령: `/create 방`, `/join 방`, `/leave`, `/rooms`, `/who`

**재시작해도 방 유지하기**: `server.py` 의 한 줄을 바꿉니다.
```python
REPO = InMemoryRoomRepository()             # 끄면 사라짐
REPO = FileRoomRepository("rooms.json")     # 재시작해도 남음
```

## 핵심 개념
- **캡슐화**: 방의 데이터(이름·멤버·기록)와 동작(join/leave/post)을 `Room` 한 덩어리로
- **저장소 DI**: 메모리/파일/DB 는 교체 가능한 부품 (`RoomRepository` 계약)
- **합성(composition)**: 서버 has Room, Room has 멤버
- 6주차의 "세 군데 맞추기"가 **Room 위임**으로 사라짐

## 실제 동작 (재시작 비교)
```
메모리 저장소:  생성 ['잡담']        → 재시작 → []                  (사라짐)
파일 저장소:    생성 ['잡담','게임']  → 재시작 → ['잡담','게임']      (살아있음)
                복원된 기록: ['민수: 안녕']
```

## 실습 / 과제
1. `Room` 에 최대 인원 제한 추가 (`capacity` / `is_full`, 힌트는 `room.py` 주석)
2. `FileRoomRepository` 로 바꿔 재시작 후 방 유지 확인
3. `SqliteRoomRepository` 골격 구현 (원하는 학생)

> 다음 주: 다시 커진 서버를 명령 해석·세션 관리 등 **작은 객체들로** 나눕니다.

## PPT 다시 만들기 (강사용)
```bash
pip install python-pptx
python make_ppt.py
```
