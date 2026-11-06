document.querySelectorAll(".code-panel").forEach((panel) => {
  const button = panel.querySelector(".copy-button");
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(panel.querySelector("code").textContent);
      button.textContent = "已复制";
    } catch {
      button.textContent = "请选中代码复制";
    }
  });
});

const simulator = document.querySelector("[data-loop-simulator]");
if (simulator) {
  const steps = [
    ["1 · Schema", "程序告诉模型：get_weather 接收 city。此时没有执行任何天气查询。"],
    ["2 · Call", '模型返回请求：id=c1，name=get_weather，arguments={"city":"台北"}。这还不是天气答案。'],
    ["3 · Execute", "程序检查白名单和参数，执行本地 get_weather，取得固定教学数据 26°C。"],
    ["4 · Result", "程序将结果写成 role=tool、tool_call_id=c1，连同原 assistant 请求一起回传。"],
    ["5 · Answer", "第二轮模型收到结果，回答：台北的教学气温为摄氏 26 度，非实时天气。无新工具请求，循环结束。"],
  ];
  let index = 0;
  const render = () => {
    simulator.querySelector("strong").textContent = steps[index][0];
    simulator.querySelector("p").textContent = steps[index][1];
    simulator.querySelector("button").textContent = index === steps.length - 1 ? "从头演示" : "下一步";
  };
  simulator.querySelector("button").addEventListener("click", () => {
    index = (index + 1) % steps.length;
    render();
  });
  render();
}
