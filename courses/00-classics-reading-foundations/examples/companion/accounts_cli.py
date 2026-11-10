# 目的：getpass 交互输入不会把口令写在命令行参数中；结果只显示账号和角色。
# 预期：可以创建测试读者，数据库只保存盐与派生值。
import argparse
import getpass
import json
from .auth import create_user
from .state import initialize


def main(kind="create-user"):
    parser=argparse.ArgumentParser(description="管理员创建试用账号")
    parser.add_argument("username")
    parser.add_argument("--tenant",default="demo")
    parser.add_argument("--role",choices=["reader","parent","content_admin"],default="reader")
    args=parser.parse_args();initialize()
    password=getpass.getpass("设置至少12字符的口令（不回显）：")
    if password!=getpass.getpass("再次输入："):raise ValueError("两次口令不同。")
    create_user(args.tenant,args.username,password,args.role)
    print(json.dumps({"created":args.username,"role":args.role},ensure_ascii=False))
