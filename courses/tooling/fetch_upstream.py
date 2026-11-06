"""只读获取已固定版本的 MIT 课程源码；不执行下载的代码。"""
import concurrent.futures
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA = "9ef03ca034704bf9cdd403673b3116fda7ec8672"
BASE = f"https://raw.githubusercontent.com/WenyuChiou/awesome-agentic-ai-zh/{SHA}/"


def wanted(path):
    if path in {"LICENSE", "README.zh-Hans.md", "ROADMAP.zh-Hans.md", "CAPSTONE.zh-Hans.md"}:
        return True
    if path.startswith(("stages/", "tracks/cli/", "branches/", "resources/")):
        return path.endswith(".zh-Hans.md")
    if path.startswith("examples/"):
        return not path.endswith((".en.md", ".png", ".jpg", ".svg", ".lock")) and (
            not path.endswith(".md") or path.endswith(".zh-Hans.md") or Path(path).name == "SKILL.md"
        )
    return False


def main():
    tree = json.loads(Path("/private/tmp/ai-learn-upstream-tree.json").read_text())
    paths = [x["path"] for x in tree["tree"] if x["type"] == "blob" and wanted(x["path"])]
    target = ROOT / "_sources" / "upstream"

    def download(path):
        data = urllib.request.urlopen(BASE + path, timeout=45).read()
        destination = target / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        return path

    failures = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(download, path): path for path in paths}
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as exc:
                failures.append((futures[future], str(exc)))
    (target.parent / "snapshot.json").write_text(json.dumps({"repository": "WenyuChiou/awesome-agentic-ai-zh", "sha": SHA, "date": "2026-11-03", "files": len(paths), "failures": failures}, ensure_ascii=False, indent=2))
    print(json.dumps({"files": len(paths), "failures": failures}, ensure_ascii=False))
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
