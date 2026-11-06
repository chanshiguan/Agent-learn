// 仅验证教学脚本的编排契约；不是 Claude workflow runtime。
// 导入同步读取函数，用于读取固定教学脚本和虚构文件。
import { readFileSync } from 'node:fs'
// 导入 URL 转本地路径函数，处理当前模块的 file URL。
import { fileURLToPath } from 'node:url'
// 导入目录提取和路径拼接函数，避免依赖启动位置。
import { dirname, join } from 'node:path'

// 取得本脚本所在目录，作为寻找输入文件的基准。
const base = dirname(fileURLToPath(import.meta.url))
// 读取固定工作流源码；这里不读取外部或模型生成的程序。
const source = readFileSync(join(base, 'audit-readmes.js'), 'utf8')
// 去掉模块导出语法，使该固定脚本可放入下方异步函数体。
const body = source.replace('export const meta =', 'const meta =')
// 取得异步函数构造器，用于给固定脚本注入离线替身。
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor
// 这里只加载本项目的固定教学脚本，并注入替身；不要用于执行外部或模型生成的源码。
// 把固定脚本包装成函数；agent 和 pipeline 将由测试替身提供。
const execute = new AsyncFunction('agent', 'pipeline', body)
// 读取命令行场景参数；未提供时使用 normal。
const scenario = process.argv[2] ?? 'normal'
// 拒绝未知场景，避免拼错参数却运行另一种测试。
if (!['normal', 'cancel'].includes(scenario)) throw new Error('只接受 normal 或 cancel')
// 离线替身读取同一份虚构文件，验证编排和取消处理，不评价真实模型。
// 定义离线工作者：检查提示、读取虚构文件并返回结构检查结果。
const agent = async (prompt, options) => {
  // 从任务标签中取回待检查文件名。
  const file = options.label
  // 只允许两份约定输入，拒绝读取其他文件。
  if (!['inputs/a.md', 'inputs/b.md'].includes(file)) throw new Error('非约定输入')
  // 确认提示词确实指出当前文件，防止任务丢失输入定位。
  if (!prompt.includes(file)) throw new Error('工作者缺少文件定位')
  // 取消场景下让第二份任务返回 null，检验汇总是否诚实保留失败。
  if (scenario === 'cancel' && file === 'inputs/b.md') return null
  // 只取约定文件的末级名称，读取本地 workflow-inputs 中的虚构正文。
  const text = readFileSync(join(base, 'workflow-inputs', file.split('/').at(-1)), 'utf8')
  // 按二级标题分段，收集每个标题及其后到下一标题之前的正文。
  const sections = new Map([...text.matchAll(/^## ([^\n]+)\n([\s\S]*?)(?=^## |$(?![\s\S]))/gm)]
    // 去除标题和正文首尾空白，建立标题到正文的查找表。
    .map(match => [match[1].trim(), match[2].trim()]))
  // 列出缺少或正文为空的约定标题，并带回文件名。
  return { file, missing: ['项目目的', '安装方法', '运行示例', '许可证'].filter(key => !sections.get(key)) }
// 结束当前对象或函数调用，完成这一层结构的组装。
}
// Promise.all 保留输入顺序，便于把每份结果配回原文件。
// 为每个输入运行工作者；等待全部任务，结果顺序与输入顺序一致。
const pipeline = async (items, worker) => Promise.all(items.map(worker))
// 将两个离线替身注入固定工作流，运行并取得报告。
const result = await execute(agent, pipeline)
// 以两空格缩进输出报告，并明确标注这是离线模拟。
console.log(JSON.stringify({ mode: '离线契约模拟', ...result }, null, 2))
