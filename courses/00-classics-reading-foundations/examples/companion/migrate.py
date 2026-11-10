"""第 28 章：只在恢复副本上练习向前兼容迁移，旧程序仍可读取原字段。"""
from .state import connect, initialize


def migrate():
    initialize()
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version == 1:
            # 新字段允许为空，使已有笔记不必编造时间或补填不存在的信息。
            db.execute("ALTER TABLE notes ADD COLUMN archived_at REAL")
            db.execute("PRAGMA user_version=2")
        elif version != 2:
            raise ValueError("未知数据库版本，先准备单独的迁移方案。")
        return {"schema_version": 2, "note_count": db.execute("SELECT count(*) FROM notes").fetchone()[0]}


if __name__ == "__main__":
    print(migrate())
