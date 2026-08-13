-- ============================================================
-- schema.sql  :  우리 채팅을 담을 '표(테이블)' 설계 (DDL)
-- ============================================================
-- DDL = 표(구조)를 만드는 명령. 여기서는 CREATE TABLE 만 씁니다.
-- 우리 프로젝트의 객체가 그대로 테이블이 됩니다:
--   Session(유저) → users,   Room → rooms,   Message → messages,
--   "누가 어느 방에" → room_members (다대다)
--
-- PK(기본키) = 그 행을 유일하게 가리키는 열
-- FK(외래키) = 다른 표의 PK 를 가리키는 열 (REFERENCES 로 표시)
-- ============================================================

-- 사람 (닉네임은 겹치지 않게 UNIQUE)
CREATE TABLE users (
    user_id  INTEGER PRIMARY KEY AUTOINCREMENT,   -- PK: 자동 증가하는 번호
    nickname TEXT    NOT NULL UNIQUE
);

-- 방
CREATE TABLE rooms (
    room_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT    NOT NULL UNIQUE,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- 메시지 (어느 방에서 who 가 무슨 말을)
CREATE TABLE messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id    INTEGER NOT NULL REFERENCES rooms(room_id),   -- FK → rooms
    user_id    INTEGER NOT NULL REFERENCES users(user_id),   -- FK → users
    kind       TEXT    NOT NULL DEFAULT 'TEXT',              -- TEXT / EMOJI / FILE
    content    TEXT    NOT NULL,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- 방 멤버십 (다대다: 한 사람이 여러 방, 한 방에 여러 사람)
--   한 쌍(방, 사람)은 한 번만 존재해야 하므로 두 열을 묶어 PK 로.
CREATE TABLE room_members (
    room_id INTEGER NOT NULL REFERENCES rooms(room_id),
    user_id INTEGER NOT NULL REFERENCES users(user_id),
    PRIMARY KEY (room_id, user_id)      -- 복합 기본키 = 중복 가입 방지
);

-- ⚠️ SQLite 는 기본적으로 FK 를 '검사만 안 하고 기록만' 합니다.
--    실제로 강제하려면 연결할 때  PRAGMA foreign_keys = ON;  (run_sql.py 가 켜 줍니다)
