# -*- coding: utf-8 -*-
"""
Week 9(번외·데이터베이스) 강의자료(PPT) 생성 스크립트
실행:  python make_ppt.py   →   Week09_데이터베이스_SQLite.pptx
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ppt_theme import Deck

KICKER = "파이썬으로 만드는 실시간 채팅 프로그램 · 번외"

d = Deck()

# ── 1. 표지 ────────────────────────────────────────────────
d.title(
    kicker=KICKER,
    title="채팅 데이터를 진짜 DB에 담자",
    subtitle="SQLite · CRUD · JOIN — 이론은 배웠으니, 이번엔 손으로",
    notes=(
        "번외 강좌. 목표: DB 이론만 배운 학생이 SQL 을 '직접 실행' 해 보게 한다.\n"
        "핵심 프레이밍: 새 주제가 아니라 RoomRepository 에 SQLite 구현체를 하나 더 붙이는 것.\n"
        "깊이: DDL(CREATE)+DML(CRUD/JOIN)만. DCL 은 한 줄로 스킵."
    ),
)

# ── 2. 도입 질문 ──────────────────────────────────────────
d.big_question(
    question="서버를 껐다 켜면 대화가 사라진다.\n어디에, 어떻게 남겨 둘까?",
    hint="지금은 메모리·JSON 파일에 저장했죠. 이번엔 '진짜 데이터베이스' 에.",
    notes=(
        "7~8주차에 InMemory / File 저장소를 만들었다. 이제 진짜 DB(SQLite) 차례.\n"
        "이건 RoomRepository 구현체를 하나 더 만드는 것 — 5주차 Strategy/DI 의 연장."
    ),
)

# ── 3. 왜 SQLite / SQL 3분류 ──────────────────────────────
d.table(
    "SQL 은 세 종류 — 한 번만 짚고 갑니다",
    ["분류", "하는 일", "예", "우리는?"],
    [
        ["DDL", "표(구조)를 만든다", "CREATE, DROP", "CREATE 만"],
        ["DML", "데이터를 다룬다", "SELECT/INSERT/UPDATE/DELETE", "전부 (핵심)"],
        ["DCL", "권한을 관리한다", "GRANT, REVOKE", "안 씀 (SQLite 해당 없음)"],
    ],
    col_widths=[1.6, 3.6, 4.2, 2.4],
    caption="SQLite = 파일 하나가 곧 DB. 설치·서버·권한(DCL) 없음 → CREATE + CRUD + JOIN 에 집중.",
    notes=(
        "DDL/DML/DCL 은 '한 번 인지' 하고 넘어간다. 우리는 DCL 을 안 쓴다(파일 DB라 권한 개념 없음).\n"
        "SQLite 는 파이썬 표준 sqlite3 — pip 도 설치도 필요 없다는 점을 강조."
    ),
)

# ── 3b. 실습 준비: VS Code 로 DB 보기 ─────────────────────
d.bullets(
    "실습 준비 — VS Code 로 DB 보기 (설치 → 실행)",
    [
        "VS Code 확장 2개 설치  (Ctrl+Shift+X 에서 검색)",
        ("\"SQLite Viewer\"  —  .db 파일을 '클릭만' 하면 표로 보기", 1),
        ("\"SQLite\" (제작자 alexcvzz)  —  .sql 을 직접 실행", 1),
        "① DB 파일 만들기:  터미널에  python run_sql.py 01_crud.sql",
        ("→ 폴더에 chat.db 가 생긴다 (터미널에도 결과가 표로 나옴)", 1),
        "② 데이터 눈으로 보기:  탐색기에서 chat.db 클릭 → SQLite Viewer 가 연다",
        "③ 쿼리 직접 실행:  02_join.sql 열고 → Ctrl+Shift+P → \"SQLite: Run Query\" → chat.db 선택",
        "확장이 없어도 python run_sql.py 만으로 결과는 다 볼 수 있다 (설치 0)",
    ],
    notes=(
        "실습 전 환경 세팅. 학생 대부분 VS Code 를 쓰니 확장 2개만 깔면 된다.\n"
        "SQLite 는 서버가 없어 '접속 정보(호스트/비번)' 없이 .db 파일만 열면 끝 — MySQL 과 다른 점.\n"
        "가장 간단한 길은 python run_sql.py — DB 도구가 없어도 즉시 결과가 표로 나온다.\n"
        "GUI 로 편하게 볼 땐 SQLite Viewer(보기) + alexcvzz SQLite(쿼리 실행) 조합을 권한다.\n"
        "주의: run_sql.py 는 실행마다 chat.db 를 새로 만든다 → 확장으로 열어 뒀으면 새로고침하면 반영."
    ),
)

# ── 4. 스키마: 우리 객체가 곧 표 ──────────────────────────
d.code(
    "우리 채팅이 곧 표가 된다 (DDL)",
    "-- 우리 객체 → 테이블\n"
    "--   Session(유저) → users,  Room → rooms,  Message → messages\n"
    "\n"
    "CREATE TABLE users (\n"
    "    user_id  INTEGER PRIMARY KEY AUTOINCREMENT,   -- PK\n"
    "    nickname TEXT NOT NULL UNIQUE\n"
    ");\n"
    "CREATE TABLE messages (\n"
    "    message_id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
    "    room_id INTEGER REFERENCES rooms(room_id),     -- FK → rooms\n"
    "    user_id INTEGER REFERENCES users(user_id),     -- FK → users\n"
    "    content TEXT NOT NULL\n"
    ");",
    caption="PK = 그 행을 유일하게 가리키는 열,  FK = 다른 표의 PK 를 가리키는 열.",
    notes=(
        "학생이 이미 아는 PK/FK 를 '우리 프로젝트' 로 실체화. 추상적 정규화 이론은 다시 안 한다.\n"
        "room_members(다대다)는 설계 과제로 남긴다 — 스스로 왜 복합 PK 인지 생각하게."
    ),
)

# ── 5. CRUD ───────────────────────────────────────────────
d.code(
    "데이터 다루기 4형제 — CRUD (DML)",
    "-- C: 추가\n"
    "INSERT INTO messages (room_id, user_id, content) VALUES (1, 1, '안녕');\n"
    "\n"
    "-- R: 조회\n"
    "SELECT content FROM messages WHERE room_id = 1;\n"
    "\n"
    "-- U: 수정   (WHERE 를 빼면 전체가 바뀐다! 항상 WHERE)\n"
    "UPDATE messages SET content = '수정됨' WHERE message_id = 1;\n"
    "\n"
    "-- D: 삭제   (역시 WHERE 필수)\n"
    "DELETE FROM messages WHERE kind = 'EMOJI';",
    caption="UPDATE/DELETE 에 WHERE 빼먹기 = 실무 사고 1위. 항상 WHERE 를 먼저 쓰는 습관.",
    notes=(
        "01_crud.sql 을 python run_sql.py 01_crud.sql 로 그 자리에서 실행해 보여 준다.\n"
        "WHERE 누락 사고를 반드시 강조."
    ),
)

# ── 6. JOIN 개념 ──────────────────────────────────────────
d.bullets(
    "JOIN — 흩어진 표를 잇는다 (핵심)",
    [
        "messages 에는 user_id(숫자)만, 닉네임은 users 에 있다",
        "둘을 '연결 고리(FK = PK)' 로 이어 함께 보여 주는 게 JOIN",
        ("messages.user_id  ==  users.user_id  →  닉네임과 함께 보기", 1),
        "3-테이블 조인: messages + users + rooms → 누가·어느 방·무슨 말",
        "다대다 조인: room_members + users → 방 멤버 목록",
        "집계: GROUP BY 로 방별 메시지 수 같은 통계",
    ],
    notes=(
        "JOIN 은 어렵게 설명하지 말 것 — 'FK 와 PK 를 맞춰 두 표를 붙인다' 면 충분.\n"
        "ON 뒤의 조건이 '연결 고리' 라는 것만 또렷이."
    ),
)

# ── 7. JOIN 실행 결과 (실제 캡처) ─────────────────────────
d.terminals(
    "직접 돌려보자 — JOIN 결과 (실제 실행)",
    [
        ("SQL",
         "SELECT u.nickname AS 보낸사람,\n"
         "       m.content\n"
         "FROM   messages m\n"
         "JOIN   users u\n"
         "  ON m.user_id = u.user_id\n"
         "WHERE  m.room_id = 1;"),
        ("결과 (python run_sql.py)",
         "보낸사람 │ content\n"
         "─────────────────\n"
         "철수    │ 얘들아 안녕\n"
         "영희    │ 안녕 철수\n"
         "영희    │ smile\n"
         "\n"
         "→ 숫자(user_id)가\n"
         "  닉네임으로 이어졌다"),
    ],
    notes=(
        "02_join.sql 을 실제로 실행한 결과. JOIN 전엔 user_id 숫자만, JOIN 후엔 닉네임.\n"
        "DB 도구 없이 python run_sql.py 로 돌아간다는 점(설치 0)을 강조."
    ),
)

# ── 8. 프로젝트에 붙이기 (힌트) ───────────────────────────
d.bullets(
    "프로젝트에 붙이기 — SqliteRoomRepository",
    [
        "week07~08 의 계약 그대로: create / find / save / all",
        "구현만 SQLite 로 — InMemory → File → SQLite (부품 하나 더)",
        ("build_server() 에서 rooms = SqliteRoomRepository(\"chat.db\") 로 교체", 1),
        "서버·Room·명령 코드는 한 줄도 안 바뀐다 (계약으로 격리했으니까)",
        "정답은 안 준다 — sqlite_repository_hint.py 의 TODO 를 스스로 채운다",
        ("⚠️ 값은 반드시 ? 파라미터로 (문자열 합치기 = SQL 주입 위험)", 1),
    ],
    notes=(
        "여기서 '다 주지 않는다'. 힌트 파일의 뼈대와 접근법만 보여 주고 학생이 완성.\n"
        "핵심 재확인: RoomRepository 계약 덕에 저장 방식(DB)을 갈아끼워도 나머지는 그대로."
    ),
)

# ── 9. 깨달음 (DB 변경 대비) ──────────────────────────────
d.takeaway(
    headline="계약으로 격리하면,\nDB 를 통째로 갈아끼울 수 있다.",
    points=[
        "SQL 은 CREATE + CRUD + JOIN 만으로 충분히 시작한다",
        "우리 객체(Room·유저·메시지)가 곧 표 — PK/FK 로 잇는다",
        "DB 는 RoomRepository 의 또 다른 구현체 (Strategy/DI 재확인)",
        "나중에 MySQL 로? MysqlRoomRepository 하나 더 + build 한 줄 = 끝",
    ],
    notes=(
        "이 강좌의 진짜 목표는 SQL 문법이 아니라 'DB 도 부품' 이라는 설계 감각.\n"
        "DB 특유 문법은 Repository 안에만 가두고, SQL 은 표준으로 — 그래야 갈아끼울 수 있다."
    ),
)

# ── 10. 직접 해보기 ──────────────────────────────────────
d.bullets(
    "직접 해보기",
    [
        "python run_sql.py 01_crud.sql / 02_join.sql 을 돌려 결과를 확인",
        "room_members(다대다) 를 스스로 설계 — 왜 복합 PK 인지 한 줄로 설명",
        "\"각 방의 마지막 메시지\" 를 뽑는 SELECT 를 직접 작성",
        "sqlite_repository_hint.py 의 create/find/all 을 완성해 방 저장/복원",
        "(생각) MySQL 로 바꾼다면 어디를 고치고, 서버.py 는 왜 안 고쳐도 되나?",
    ],
    notes=(
        "마지막 생각거리가 이 강좌의 결론(계약으로 격리 = DB 교체 자유)을 스스로 말하게 한다."
    ),
)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "Week09_데이터베이스_SQLite.pptx")
d.save(out)
print("저장 완료:", out)
print("슬라이드 수:", len(d.prs.slides._sldIdLst))
