-- ============================================================
-- 02_join.sql  :  여러 표를 잇는다 — JOIN (이번 강좌의 핵심)
-- ============================================================
-- messages 에는 user_id(숫자)만 있고 '닉네임'은 users 에 있습니다.
-- 둘을 이어(JOIN) 보여 주는 게 JOIN 입니다.
--   messages.user_id  ==  users.user_id   를 기준으로 두 표를 붙인다.
--
-- 실행:  python run_sql.py 02_join.sql
-- ============================================================

-- ── ① 방 대화를 '닉네임과 함께' 보기 (messages + users) ──
SELECT u.nickname AS 보낸사람, m.kind, m.content
FROM   messages m
JOIN   users    u ON m.user_id = u.user_id     -- 이 줄이 두 표를 잇는 '연결 고리'
WHERE  m.room_id = 1                            -- 잡담방만
ORDER BY m.message_id;

-- ── ② 방 이름까지 (messages + users + rooms, 3-테이블 조인) ──
SELECT r.name AS 방, u.nickname AS 보낸사람, m.content
FROM   messages m
JOIN   users    u ON m.user_id = u.user_id
JOIN   rooms    r ON m.room_id = r.room_id
ORDER BY r.room_id, m.message_id;

-- ── ③ 방 멤버 목록 (room_members + users, 다대다 조인) ──
SELECT r.name AS 방, u.nickname AS 멤버
FROM   room_members rm
JOIN   users u ON rm.user_id = u.user_id
JOIN   rooms r ON rm.room_id = r.room_id
ORDER BY r.room_id, u.nickname;

-- ── ④ 방별 메시지 수 (JOIN + 집계 GROUP BY) ──
SELECT r.name AS 방, COUNT(*) AS 메시지수
FROM   messages m
JOIN   rooms    r ON m.room_id = r.room_id
GROUP  BY r.room_id
ORDER  BY 메시지수 DESC;

-- ── ⑤ (심화) 메시지를 한 번도 안 쓴 사람? (LEFT JOIN) ──
--   JOIN 은 '양쪽에 다 있는 것'만, LEFT JOIN 은 '왼쪽은 다' 남긴다.
--   → 메시지가 없으면 m.content 가 NULL 로 나온다.
SELECT u.nickname, COUNT(m.message_id) AS 보낸메시지수
FROM   users u
LEFT JOIN messages m ON u.user_id = m.user_id
GROUP  BY u.user_id
ORDER  BY 보낸메시지수;

-- ============================================================
-- 핵심 한 줄: JOIN = "이 표의 FK 와 저 표의 PK 를 맞춰 두 표를 붙인다."
--   ON 뒤의 조건이 '연결 고리' — FK = PK.
-- ============================================================

select * from user;