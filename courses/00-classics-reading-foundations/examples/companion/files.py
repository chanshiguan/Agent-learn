# 目的：本节先统一 JSON 结果的位置；后续模块共用同一个读写约定。
# 预期：保存后只有导入和定义；导入它不会自动运行整个业务。
import hashlib
import json
import os
from pathlib import Path

# 目的：允许用环境变量选择实验数据目录，默认仍是项目内 data/live。
# 预期：保存结果后可用编辑器检查；这三个函数不触发模型请求。
def data_dir():
    directory = Path(os.environ.get("READING_DATA_DIR", "data/live"))
    directory.mkdir(parents=True, exist_ok=True)
    return directory

# 目的：读取已存在的 JSON；文件不存在时返回调用者明确给出的默认值。
# 预期：保存结果后可用编辑器检查；这三个函数不触发模型请求。
def load(name, default=None):
    file = data_dir() / name
    return json.loads(file.read_text(encoding="utf-8")) if file.exists() else default

# 目的：先完整写临时文件再替换，避免留下半个 JSON。
# 预期：保存结果后可用编辑器检查；这三个函数不触发模型请求。
def save(name, value):
    file = data_dir() / name
    file.parent.mkdir(parents=True, exist_ok=True)
    temporary = file.with_suffix(file.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
    # 先完整写入再替换，读者不会读到只写了一半的 JSON；索引任务应单实例执行。
    temporary.replace(file)
    return file

# 目的：字典按键排序后再编码，避免仅因字段排列不同得到不同指纹。
# 预期：后续用它计算文档和片段身份，不用它代替权限判断。
def digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
