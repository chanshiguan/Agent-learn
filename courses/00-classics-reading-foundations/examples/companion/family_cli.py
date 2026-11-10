# 目的：关联需要单独动作，不在用户注册或模型回答时自动推断。
# 预期：命令成功后仅开放已约定进度字段。
import argparse
from .state import initialize
from .auth import link_family


def main():
    parser=argparse.ArgumentParser(description="管理员核实后关联家长与读者")
    parser.add_argument("parent");parser.add_argument("child")
    parser.add_argument("--tenant",default="demo")
    args=parser.parse_args();initialize();link_family(args.tenant,args.parent,args.child)
    print("关联已保存；只授权读取显式进度。")
