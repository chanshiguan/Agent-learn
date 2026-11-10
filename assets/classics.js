document.querySelectorAll("pre").forEach((pre) => {
  const code = pre.querySelector("code");
  const shell = code?.classList.contains("language-bash");
  const original = pre.textContent;
  // Shell 注释供阅读；复制只取命令，避免 zsh 的交互注释设置影响粘贴执行。
  const copyText = shell ? original.split("\n").filter(line => !line.trimStart().startsWith("#")).join("\n").trim() : original;
  const wrap = document.createElement("div");
  wrap.className = "code-wrap";
  pre.before(wrap);
  wrap.append(pre);
  const toolbar = document.createElement("div");
  toolbar.className = "code-toolbar";
  const hint = document.createElement("span");
  hint.textContent = shell ? "终端命令 · # 行是说明，复制时不包含" : "示例内容 · 复制保留注释";
  const button = document.createElement("button");
  button.className = "copy-code";
  button.type = "button";
  button.textContent = shell ? "复制命令" : "复制代码";
  button.setAttribute("aria-live", "polite");
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(copyText);
      button.textContent = "已复制";
    } catch {
      // 离线页面可能无法访问剪贴板；提供可选择的纯命令，仍不混入说明文字。
      let field = wrap.querySelector("textarea");
      if (!field) {
        field = document.createElement("textarea");
        field.className = "manual-copy";
        field.readOnly = true;
        field.rows = 5;
        field.setAttribute("aria-label", shell ? "待复制的终端命令" : "待复制的示例内容");
        wrap.append(field);
      }
      field.value = copyText;
      field.focus();
      field.select();
      button.textContent = "已选中，请手动复制";
    }
  });
  toolbar.append(hint, button);
  wrap.prepend(toolbar);
  if (shell) {
    code.replaceChildren();
    original.split("\n").forEach((line, i) => {
      const span = document.createElement("span");
      if (line.trimStart().startsWith("#")) span.className = "code-comment";
      span.textContent = line + (i < original.split("\n").length - 1 ? "\n" : "");
      code.append(span);
    });
  }
});

document.querySelectorAll("table").forEach((table) => {
  const wrap = document.createElement("div");
  wrap.className = "table-scroll";
  wrap.tabIndex = 0;
  wrap.setAttribute("role", "region");
  wrap.setAttribute("aria-label", "对照表，可横向滚动");
  table.before(wrap);
  wrap.append(table);
});

const currentUnit = document.body.dataset.currentUnit;
if (currentUnit) {
  try { localStorage.setItem("classics-last-unit", currentUnit); } catch {}
}
const links = [...document.querySelectorAll("[data-unit-link]")];
if (links.length) {
  let completed = 0;
  try {
    links.forEach(link => {
      if (localStorage.getItem(`classics-study:${link.dataset.unitLink}`) === "done") {
        link.classList.add("is-done");
        link.querySelector("[data-unit-status]").textContent = "· 已手动标记";
        completed++;
      }
    });
    const last = localStorage.getItem("classics-last-unit");
    const previous = links.find(link => link.dataset.unitLink === last);
    if (previous) {
      const start = document.getElementById("continue-learning");
      start.href = previous.href;
      start.textContent = "继续上次阅读 →";
      document.getElementById("resume-note").textContent = `上次读到：${previous.querySelector(".lesson-name").firstChild.textContent}`;
    }
    document.getElementById("course-progress").textContent = `已手动标记 ${completed} / ${links.length} 个单元（含两个二选一路线单元）。`;
  } catch {
    document.getElementById("resume-note").textContent = "此浏览器未启用进度存储，可从下面的章节列表继续。";
  }
}

const railMenu = document.querySelector(".rail-menu");
if (railMenu && matchMedia("(max-width: 760px)").matches) railMenu.open = false;

// 将来路放在内部链接上；连续阅读拓展页后，仍能回到出发的单元。
const params = new URLSearchParams(location.search);
const from = currentUnit || params.get("from");
const returnSection = /^(section-\d+|optional-reading|main-content)$/.test(params.get("from-section") || "") ? params.get("from-section") : "optional-reading";
if (from && /^00(?:0[89]|[1-6][0-9]|7[0-3])-[a-z-]+(?:-\d{2})?$/.test(from)) {
  document.querySelectorAll(".page-lesson main a, .page-knowledge main a, .page-knowledge .reading-rail a").forEach(link => {
    const url = new URL(link.href);
    if (url.origin === location.origin && /\/knowledge\/[^/]+\.html$/.test(url.pathname) && !link.hasAttribute("data-return-to-lesson")) {
      url.searchParams.set("from", from);
      const preceding = currentUnit ? [...document.querySelectorAll("main h2[id]")].filter(heading => heading.compareDocumentPosition(link) & Node.DOCUMENT_POSITION_FOLLOWING).at(-1) : null;
      url.searchParams.set("from-section", currentUnit ? (link.closest(".optional-box") ? "optional-reading" : preceding?.id || "main-content") : returnSection);
      link.href = url.href;
    }
  });
  document.querySelectorAll("[data-return-to-lesson]").forEach(link => {
    const fallback = new URL(link.href);
    fallback.pathname = fallback.pathname.replace(/[^/]+\.html$/, `${from}.html`);
    fallback.hash = returnSection;
    link.href = fallback.href;
    link.textContent = "← 回到刚才的主线单元";
  });
}

document.querySelectorAll("[data-study-check]").forEach((input) => {
  const key = `classics-study:${input.dataset.studyCheck}`;
  try { input.checked = localStorage.getItem(key) === "done"; } catch {}
  input.addEventListener("change", () => {
    try { localStorage.setItem(key, input.checked ? "done" : "pending"); } catch {}
  });
});

// 课程地图按阶段折叠；深链接和返回章节时自动展开所在阶段。
function revealStage() {
  const target=document.getElementById(decodeURIComponent(location.hash.slice(1)));
  if(target){const group=target.closest(".stage-group");if(group)group.open=true;target.scrollIntoView({block:"start"});}
}
window.addEventListener("hashchange",revealStage);
revealStage();
