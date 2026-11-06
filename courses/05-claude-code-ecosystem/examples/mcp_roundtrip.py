"""真实 stdio MCP Client→Server 往返，只读取演示资料。"""

# 这个客户端会启动独立服务进程，完成初始化、工具发现、调用与错误返回。
import asyncio
import sys
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# 用当前 Python 启动服务，避免客户端和服务端意外使用不同虚拟环境。
async def main():
    server=StdioServerParameters(command=sys.executable,args=[str(Path(__file__).with_name('readonly_server.py'))])
    async with stdio_client(server) as (read,write):
        async with ClientSession(read,write) as session:
            # 先完成协议初始化，再发现和调用工具；不是直接调用服务端 Python 函数。
            await session.initialize()
            listing=await session.list_tools()
            assert 'read_note' in [tool.name for tool in listing.tools]
            valid=await session.call_tool('read_note',{'name':'notes.txt'})
            # 故意尝试越界路径，确认限制实际由 server 执行。
            denied=await session.call_tool('read_note',{'name':'../observe_hook.py'})
            assert not valid.isError and denied.isError
            print('工具发现成功；合法读取成功；越界请求拒绝。')
            print(valid.model_dump_json())


if __name__=='__main__':
    asyncio.run(main())
