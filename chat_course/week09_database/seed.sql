-- ============================================================
-- seed.sql  :  실습용 샘플 데이터 (INSERT)
-- ============================================================
-- 이 데이터가 들어간 상태에서 SELECT/JOIN 을 연습합니다.
--   users:  철수(1), 영희(2), 민수(3)
--   rooms:  잡담(1), 게임(2)
--   멤버:   잡담 = 철수·영희,   게임 = 철수·민수
-- ============================================================

INSERT INTO users (nickname) VALUES ('철수'), ('영희'), ('민수');

INSERT INTO rooms (name) VALUES ('잡담'), ('게임');

-- (room_id, user_id) — 누가 어느 방에
INSERT INTO room_members (room_id, user_id) VALUES
    (1, 1),   -- 잡담: 철수
    (1, 2),   -- 잡담: 영희
    (2, 1),   -- 게임: 철수
    (2, 3);   -- 게임: 민수

-- (room_id, user_id, kind, content)
INSERT INTO messages (room_id, user_id, kind, content) VALUES
    (1, 1, 'TEXT',  '얘들아 안녕'),
    (1, 2, 'TEXT',  '안녕 철수'),
    (1, 2, 'EMOJI', 'smile'),
    (2, 1, 'TEXT',  '게임 ㄱㄱ'),
    (2, 3, 'TEXT',  '좋아 바로 가자');
