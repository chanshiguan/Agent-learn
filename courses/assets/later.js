document.querySelectorAll('pre').forEach((pre) => {
  const button = document.createElement('button');
  button.className = 'copy'; button.textContent = '复制完整代码';
  button.addEventListener('click', async () => {
    const text = pre.textContent;
    try {
      await navigator.clipboard.writeText(text);
      button.textContent = '已复制';
    } catch {
      const selection = window.getSelection();
      const range = document.createRange(); range.selectNodeContents(pre);
      selection.removeAllRanges(); selection.addRange(range);
      button.textContent = '已选中，请按 ⌘C / Ctrl+C';
    }
  });
  pre.before(button);
});
const filter = document.querySelector('[data-source-filter]');
if (filter) {
  filter.addEventListener('input', () => {
    const query = filter.value.toLowerCase().trim();
    document.querySelectorAll('[data-source-card]').forEach((card) => {
      card.hidden = !card.textContent.toLowerCase().includes(query);
    });
  });
}
function revealTarget() {
  if (!location.hash) return;
  const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
  if (!target) return;
  for (let node = target; node; node = node.parentElement) {
    if (node.tagName === 'DETAILS') node.open = true;
  }
  target.scrollIntoView();
}
window.addEventListener('hashchange', revealTarget);
revealTarget();
