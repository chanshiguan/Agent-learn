"""固定字段的持久记忆：用户隔离、授权写入、版本更新、过期和删除。"""

# owner 与 name 共同定位一条记忆；身份在示例中由调用者传入，生产系统必须另做认证。
import sqlite3
import time


class MemoryStore:
    def __init__(self, path):
        # 连接指定磁盘文件；关闭后重新打开同一路径，才能验证记忆跨进程保留。
        self.db = sqlite3.connect(path)
        # owner 与 name 组成主键，保证每位用户的同类偏好只有一份；不能只按 name 查询，否则会混用他人记忆。
        # source 供回查授权来源，expires 控制有效期，version 用于拒绝过期更新，updated_at 记录实际写入时间。
        self.db.execute("CREATE TABLE IF NOT EXISTS memories (owner TEXT, name TEXT, value TEXT, source TEXT, expires REAL, version INTEGER, updated_at REAL, PRIMARY KEY(owner,name))")
        # 读取现有列名，兼容之前创建的数据库；PRAGMA 返回每列的信息，其中下标 1 是列名。
        columns = {row[1] for row in self.db.execute('PRAGMA table_info(memories)')}
        if 'updated_at' not in columns:
            # 旧库只增加缺少的更新时间列；已有数据不重建，未知的历史时间保留 NULL。
            self.db.execute('ALTER TABLE memories ADD COLUMN updated_at REAL')
            self.db.commit()  # 旧记录写入时间未知，保留 NULL；不伪造迁移时间。

    # 在同一写事务中读版本、比版本、更新；旧任务不能悄悄覆盖新偏好。
    def put(self, owner, name, value, *, consent, expected_version, source, ttl=86400):
        if consent is not True or not owner or name != "answer_style":
            raise ValueError("需要明确同意，只允许保存回答风格")
        if value not in {"先短后长", "分步解释", "先给表格"} or not source or ttl <= 0:
            raise ValueError("无效记忆内容或期限")
        with self.db:
            # 先取得写事务，再读版本和写新值，避免两次更新同时通过旧版本检查。
            self.db.execute("BEGIN IMMEDIATE")
            # 用参数占位符传入 owner/name，不将用户文本拼进 SQL；查询范围始终包含用户身份。
            row = self.db.execute("SELECT version FROM memories WHERE owner=? AND name=?", (owner, name)).fetchone()
            version = row[0] if row else 0
            # 调用方必须带上读到的版本；冲突时先重读，不静默覆盖别人的更新。
            if version != expected_version:
                raise ValueError("版本冲突：先读取当前记忆")
            now = time.time()
            # 在同一事务里保存新值、来源、到期时间和递增版本；中途抛错时 with 会回滚，不能留下半次更新。
            self.db.execute("INSERT OR REPLACE INTO memories (owner,name,value,source,expires,version,updated_at) VALUES (?,?,?,?,?,?,?)", (owner, name, value, source, now+ttl, version+1, now))
        return version + 1

    # 读取也检查期限；过期返回 None，不代表已从磁盘物理擦除。
    def get(self, owner, name):
        # 同时读取事实、来源和版本；调用方更新时需要携带这个版本，不能只读取偏好文字。
        row = self.db.execute("SELECT value,source,expires,version,updated_at FROM memories WHERE owner=? AND name=?", (owner, name)).fetchone()
        if row is None or row[2] <= time.time():
            return None
        return {"value": row[0], "source": row[1], "version": row[3],
                "user_id": owner, "updated_at": row[4], "expires_at": row[2]}

    # 只删除指定用户的指定记忆；外部缓存或备份不在这个函数的处理范围内。
    def delete(self, owner, name):
        with self.db:
            # 两个条件一起限定删除范围；删掉指定用户的指定偏好，不影响同名的其他用户记录。
            self.db.execute("DELETE FROM memories WHERE owner=? AND name=?", (owner, name))

    def close(self):
        # 释放数据库连接；调用方可随后用新连接读取，检验保存来自磁盘而非旧对象的内存。
        self.db.close()


if __name__ == "__main__":
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "memory.sqlite"
        store = MemoryStore(path)
        store.put("alice", "answer_style", "先短后长", consent=True, expected_version=0, source="用户本次明确选择")
        store.close()
        store = MemoryStore(path)
        print("重新打开：", store.get("alice", "answer_style"))
        print("其他用户：", store.get("bob", "answer_style"))
        store.delete("alice", "answer_style")
        print("删除后：", store.get("alice", "answer_style"))
        store.close()
