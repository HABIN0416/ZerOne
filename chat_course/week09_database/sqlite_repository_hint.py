"""
[힌트] SqliteRoomRepository  :  방을 '진짜 DB(SQLite)' 에 저장하는 저장소
============================================================
※ 정답 코드를 다 주지 않습니다. '방식(접근법)' 과 '뼈대' 만 — 나머지는 여러분이 채웁니다.

우리는 이미 week07~08 에서 RoomRepository '계약' 을 만들었습니다:
    create(name) / find(name) / save(room) / all()
이번엔 그 계약의 'SQLite 버전' 을 하나 더 만들 뿐입니다.
    InMemoryRoomRepository → FileRoomRepository → SqliteRoomRepository (이번)

서버·Room·명령 코드는 한 줄도 안 바뀝니다. build_server() 에서
    rooms = SqliteRoomRepository("chat.db")
로 갈아끼우면 끝. (5주차에 배운 Strategy/DI 를 DB 에도 그대로 적용)

────────────────────────────────────────────────────────────
★★ DB 변경 대비 (이 강좌의 진짜 목표) ★★
  나중에 SQLite 가 부족해서 MySQL/PostgreSQL 로 바꾸고 싶다면?
  → MysqlRoomRepository 를 '똑같은 계약(create/find/save/all)' 으로 하나 더 만들고
    build_server() 한 줄만 바꾼다. 나머지는 그대로.
  → 그래서 '규칙' 두 가지:
     ① DB 특유 문법(SQL 방언·연결 방식)은 이 파일 '안에만' 가둔다.
        (서버·Room 이 SQL 을 직접 알면 안 된다 — 그럼 DB 바꿀 때 여기저기 고쳐야 함)
     ② SQL 은 되도록 '표준' 으로 쓴다. (SQLite 전용 기능은 최소화)
  이게 "계약으로 격리하면 부품(DB)을 통째로 갈아끼울 수 있다" 의 실전.
────────────────────────────────────────────────────────────

⚠️ 보안: 값은 반드시 '?' 파라미터로 넘긴다 (문자열 합치기 금지 = SQL 주입 방지)
     con.execute("INSERT INTO rooms(name) VALUES (?)", (name,))     # ✅ 안전
     con.execute(f"INSERT INTO rooms(name) VALUES ('{name}')")      # ❌ 위험!
"""

import sqlite3

# 이 파일을 실제로 쓰려면 week08 폴더 옆에 두거나, repository.py·room.py 를 곁에 두세요.
# from repository import RoomRepository
# from room import Room


class SqliteRoomRepository:            # (실제로는 RoomRepository 를 상속: class ...(RoomRepository))
    """RoomRepository 계약의 SQLite 구현. TODO 를 채워 완성하세요."""

    def __init__(self, db_path="chat.db"):
        # 힌트: 서버는 스레드로 도니 check_same_thread=False 가 필요할 수 있다.
        self.con = sqlite3.connect(db_path, check_same_thread=False)
        self.con.execute("PRAGMA foreign_keys = ON")
        self._ensure_tables()

    def _ensure_tables(self):
        # 힌트: schema.sql 의 CREATE 문을 CREATE TABLE IF NOT EXISTS 로 바꿔 실행.
        #       (self.con.executescript(...) 또는 execute 를 여러 번)
        # TODO: rooms / messages / users / room_members 테이블을 없으면 만든다.
        ...

    def create(self, name):
        # 힌트: rooms 에 INSERT 하고 commit, 그다음 Room(name) 객체를 만들어 return.
        #   self.con.execute("INSERT INTO rooms(name) VALUES (?)", (name,))
        # TODO
        ...

    def find(self, name):
        # 힌트: SELECT room_id FROM rooms WHERE name=?  → 없으면 None.
        #       있으면 Room(name) 을 만들고, messages 에서 그 방 기록을 읽어 room.history 복원.
        # TODO
        ...

    def save(self, room):
        # 힌트: room 의 '새' 메시지를 messages 에 INSERT.
        #   (이미 저장된 것과 새것을 어떻게 구분할지는 여러분의 설계 — 예: 저장된 개수를 기억)
        # TODO
        ...

    def all(self):
        # 힌트: SELECT name FROM rooms → 각 이름으로 find() 를 부르거나 Room 리스트를 만든다.
        # TODO
        ...


# ────────────────────────────────────────────
# [직접 해보기]
# 1. _ensure_tables 와 create/find/all 을 먼저 완성해 방 생성·조회만 되게 하라.
# 2. save 로 메시지 저장까지 붙이고, 서버를 껐다 켜도 대화가 남는지 확인하라.
# 3. build_server() 에서 FileRoomRepository → SqliteRoomRepository 로 바꿔 채팅해 보라.
#    (서버 코드 다른 곳은 손대면 안 된다 — 손댔다면 격리가 안 된 것!)
# 4. (생각) 만약 MySQL 로 바꾼다면, 위 4개 메서드 중 실제로 고쳐야 할 곳은 어디이고
#    서버.py 는 왜 안 고쳐도 되는가? 를 한 줄로 적어 보라.
# ────────────────────────────────────────────
