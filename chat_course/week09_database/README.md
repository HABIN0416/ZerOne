# Week 9 (번외) — 데이터베이스로 채팅 데이터 다루기 (SQLite · CRUD · JOIN)

우리가 만든 채팅의 데이터를 **진짜 데이터베이스**에 넣고 꺼내 봅니다.
DB 이론은 배웠으니, 여기서는 **손으로 직접** SQL 을 실행하는 데 집중합니다.

> 핵심 프레이밍: 이건 '새 주제' 가 아니라 **week07~08 의 `RoomRepository` 에 구현체 하나
> 더 추가하는 것**입니다. `InMemory → File → **SQLite**`. 5주차 Strategy/DI 를 DB 에 그대로.

## 왜 SQLite?
- **설치 0** — 파이썬 표준 라이브러리 `sqlite3` (pip·서버 불필요). 파일 하나가 곧 DB.
- **DCL 고민 없음** — 파일이라 사용자·권한 개념이 없음 → 아래 3분류 중 DCL 은 안 씀.
- SQL 자체는 실무(MySQL/PostgreSQL)와 거의 같음 — 나중에 서버·권한만 더 배우면 됨.

## SQL 3분류 — 한 번만 짚고 갑니다
| 분류 | 뜻 | 예 | 우리는? |
|------|----|----|---------|
| **DDL** | 표(구조)를 만든다 | `CREATE TABLE`, `DROP` | ✅ `CREATE` 만 (`schema.sql`) |
| **DML** | 데이터를 다룬다 | `SELECT/INSERT/UPDATE/DELETE` | ✅ **전부** (핵심) |
| **DCL** | 권한을 관리한다 | `GRANT`, `REVOKE` | ❌ 큰 DB·여러 사용자용. 우리 SQLite 엔 해당 없음 |

→ **한 번 인지하고, 실제로는 `CREATE` + `CRUD` + `JOIN` 만.**

## 파일
| 파일 | 내용 |
|------|------|
| `schema.sql` | 표 설계 (users / rooms / messages / room_members) — PK·FK·다대다 |
| `seed.sql` | 샘플 데이터 (철수·영희·민수 / 잡담·게임 방 / 메시지) |
| `01_crud.sql` | 한 테이블로 INSERT·SELECT·UPDATE·DELETE |
| `02_join.sql` | 여러 표 잇기 — JOIN (이번 강좌의 핵심) |
| `run_sql.py` | SQL 을 실행해 결과를 표로 보여 주는 도구 (설치 불필요) |
| `sqlite_repository_hint.py` | 프로젝트에 붙이는 `SqliteRoomRepository` **뼈대+힌트** (정답 아님) |

## 실행 방법 (DB 도구 안 깔아도 됨)
```bash
python run_sql.py 01_crud.sql     # CRUD 예제 실행
python run_sql.py 02_join.sql     # JOIN 예제 실행
```
`run_sql.py` 가 매번 `schema.sql`+`seed.sql` 로 DB 를 **처음 상태로 새로** 만든 뒤 실행하므로,
몇 번을 돌려도 결과가 같습니다(실습에 안전). 만들어진 `chat.db` 는 지워도 됩니다.

## 스키마 한눈에
```
users(user_id PK, nickname)
rooms(room_id PK, name, created_at)
messages(message_id PK, room_id→rooms, user_id→users, kind, content, created_at)
room_members(room_id→rooms, user_id→users, PK(room_id,user_id))   ← 다대다(M:N)
```
- `messages.room_id`, `messages.user_id` 가 **외래키(FK)** — 다른 표의 PK 를 가리킴.
- `room_members` 는 **한 쌍(방,사람)을 복합 PK** 로 묶어 중복 가입 방지.

## 배우는 순서 (한 번에 다 안 줌)
1. `01_crud.sql` — 한 테이블에서 CRUD 4형제. (특히 UPDATE/DELETE 는 **항상 WHERE**)
2. `02_join.sql` — `messages`+`users` 로 "닉네임과 함께" → 3-테이블 → 다대다 → 집계.
3. **설계는 힌트로** — 프로젝트에 붙이는 건 `sqlite_repository_hint.py` 의 TODO 를 채우며.

## ★ DB 변경 대비 (이 강좌의 진짜 목표)
"나중에 SQLite 로 부족하면 MySQL 로 바꾸고 싶다" — 그때를 대비한 설계는?

> **`RoomRepository` 계약으로 격리해 뒀기 때문에, DB 를 바꿔도 서버는 안 바뀝니다.**
> `MysqlRoomRepository` 를 *같은 계약*으로 하나 더 만들고 `build_server()` 한 줄만 교체.

그래서 지킬 규칙 두 가지:
1. **DB 특유 문법(연결·SQL 방언)은 Repository 파일 안에만 가둔다.** 서버·Room 이 SQL 을
   직접 알면, DB 바꿀 때 여기저기 다 고쳐야 한다.
2. **SQL 은 되도록 표준으로.** SQLite 전용 기능은 최소화.

→ "계약으로 격리하면 부품(DB)을 통째로 갈아끼울 수 있다" 는 이 강의 전체 메시지의 마지막 증명입니다.

## 안전 습관 (짧게)
- **UPDATE/DELETE 엔 반드시 WHERE** — 빼먹으면 전체가 바뀌거나 지워진다.
- 파이썬에서 값은 **`?` 파라미터**로 (`... VALUES (?)`, `(name,)`) — 문자열 합치기는 SQL 주입 위험.
