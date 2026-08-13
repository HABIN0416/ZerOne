"""
run_sql.py  :  SQL 파일을 실행해 결과를 보여 주는 작은 도구 (설치 불필요)
============================================================
DB 도구(DBeaver 등)를 안 깔아도, 파이썬 표준 라이브러리 sqlite3 만으로
SQL 을 실행하고 결과를 표로 봅니다.

실행:
    python run_sql.py 01_crud.sql
    python run_sql.py 02_join.sql

동작:
    매번 chat.db 를 새로 만들고(schema.sql + seed.sql 적용) → 준 SQL 파일을 실행.
    (그래서 몇 번을 돌려도 항상 같은 시작 상태 — 실습에 안전)
"""
import sqlite3
import sys
import os

DB = "chat.db"


def split_statements(sql_text):
    """세미콜론(;) 으로 문장을 나눈다. 줄 주석(--) 은 미리 제거."""
    lines = [ln for ln in sql_text.splitlines() if not ln.strip().startswith("--")]
    cleaned = "\n".join(lines)
    return [s.strip() for s in cleaned.split(";") if s.strip()]


def build_db(con):
    """schema + seed 로 DB 를 처음 상태로 만든다."""
    con.executescript(open("schema.sql", encoding="utf-8").read())
    con.executescript(open("seed.sql", encoding="utf-8").read())
    con.commit()


def print_table(cols, rows):
    """조회 결과를 보기 좋은 표로 출력."""
    widths = [len(str(c)) for c in cols]
    for r in rows:
        for i, v in enumerate(r):
            widths[i] = max(widths[i], len(str(v)))
    line = "─" * (sum(widths) + 3 * len(cols) + 1)
    print(line)
    print("│ " + " │ ".join(str(c).ljust(widths[i]) for i, c in enumerate(cols)) + " │")
    print(line)
    for r in rows:
        print("│ " + " │ ".join(str(v).ljust(widths[i]) for i, v in enumerate(r)) + " │")
    print(line)
    print(f"({len(rows)} 행)\n")


def main():
    if len(sys.argv) < 2:
        print("사용법:  python run_sql.py <SQL파일>   (예: python run_sql.py 02_join.sql)")
        return
    target = sys.argv[1]

    if os.path.exists(DB):
        os.remove(DB)                       # 항상 깨끗한 상태로 시작
    con = sqlite3.connect(DB)
    con.execute("PRAGMA foreign_keys = ON")  # FK 실제로 검사하게
    build_db(con)

    print(f"=== {target} 실행 ===\n")
    for stmt in split_statements(open(target, encoding="utf-8").read()):
        cur = con.execute(stmt)
        if cur.description:                  # SELECT → 결과가 있다
            cols = [d[0] for d in cur.description]
            print("▶ " + " ".join(stmt.split())[:70] + " ...")
            print_table(cols, cur.fetchall())
        else:                                # INSERT/UPDATE/DELETE
            print(f"▶ {stmt.split()[0]} 실행됨 ({cur.rowcount} 행 영향)\n")
    con.commit()
    con.close()


if __name__ == "__main__":
    main()
