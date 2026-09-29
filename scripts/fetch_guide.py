#!/usr/bin/env python3
"""Fetch and convert 《高性价比人生指南》 into a local plain-text copy.

Downloads the single-file page from the original site (or reads a saved
copy via --from-file) and flattens every entry (title / meta chips /
summary / cost / benefit / note / sources) into references/guide.md.

Local personal use only — the text belongs to the original author:
https://cdyforever.github.io/how-to-live-better/  (GitHub: cdyforever)

Usage:
  python3 fetch_guide.py [output_path]
  python3 fetch_guide.py [output_path] --from-file saved_page.html
"""
import html as htmllib
import os
import re
import sys
import urllib.request

SOURCE = "https://cdyforever.github.io/how-to-live-better/"
AUTHOR = "cdyforever"


def fetch(url: str) -> str:
    data = b""
    last_err = None
    for attempt in range(6):
        headers = {"User-Agent": "Mozilla/5.0"}
        if data:
            headers["Range"] = f"bytes={len(data)}-"
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=90) as resp:
                if resp.status == 200 and data:  # server ignored Range: start over
                    data = b""
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    data += chunk
            return data.decode("utf-8", errors="replace")
        except Exception as e:  # truncated / dropped mid-read: resume what we have
            last_err = e
    raise SystemExit(f"download failed after retries: {last_err}")


def consistent(page: str) -> bool:
    """A resumed download can splice two CDN versions together; verify the
    page is internally consistent before trusting it."""
    ids = set(re.findall(r'<article class="card" id="(s\d+-\d+)"', page))
    toc = set(re.findall(r'href="#(s\d+-\d+)"', page))
    counter = re.search(r"(\d+) / \d+ 条", page)
    if not ids or ids != toc:
        return False
    return not counter or int(counter.group(1)) == len(ids)


def strip_tags(s: str) -> str:
    s = re.sub(r"<[^>]+>", "", s)
    s = htmllib.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def extract_field(article: str, name: str) -> str:
    m = re.search(
        r'<div class="f(?: note)?"><b>' + name + r"</b><div>(.*?)</div></div>",
        article,
        re.S,
    )
    return strip_tags(m.group(1)) if m else ""


def convert(page: str) -> str:
    sections = {}
    for m in re.finditer(r"<h2[^>]*>\s*(\d+)\.\s*(.*?)</h2>", page):
        sections[int(m.group(1))] = strip_tags(m.group(2))

    entries = []  # (sec, idx, article_html)
    for m in re.finditer(
        r'<article class="card" id="s(\d+)-(\d+)"[^>]*>(.*?)</article>', page, re.S
    ):
        entries.append((int(m.group(1)), int(m.group(2)), m.group(3)))

    if not sections or not entries:
        raise SystemExit("parse failed: site structure may have changed")

    out = []
    out.append("# 高性价比人生指南 · 本地文本副本")
    out.append("")
    out.append(f"- 作者：{AUTHOR}（原文：{SOURCE}）")
    out.append(
        f"- 生成时间：{__import__('datetime').date.today().isoformat()}，"
        f"共 {len(sections)} 节 {len(entries)} 条"
    )
    out.append("- 本文件仅供本机个人使用，请勿再分发；引用请保留作者署名与原站链接。")
    out.append("")

    by_sec = {}
    for sec, idx, art in entries:
        by_sec.setdefault(sec, []).append((idx, art))

    for sec in sorted(by_sec):
        title = sections.get(sec, "未知")
        items = by_sec[sec]
        out.append(f"## 第 {sec} 节 {title}（{len(items)} 条）")
        out.append("")
        for idx, art in sorted(items):
            chips = re.search(r'<div class="chips">(.*?)</div>', art, re.S)
            meta = (
                re.findall(r'<span class="(?:badge|tag)[^"]*">([^<]+)</span>', chips.group(1))
                if chips
                else []
            )
            title_m = re.search(r"<h3>(.*?)</h3>", art, re.S)
            etitle = strip_tags(title_m.group(1)) if title_m else ""
            plain = re.search(r'<p class="plain">(.*?)</p>', art, re.S)
            src = re.search(r'<details class="src">(.*?)</details>', art, re.S)
            links = re.findall(r'href="(http[^"]+)"', src.group(1)) if src else []

            out.append(f"### {sec}.{idx} {etitle}")
            if meta:
                out.append(f"〔{' | '.join(m.strip() for m in meta)}〕")
            if plain:
                out.append(f"白话：{strip_tags(plain.group(1))}")
            for name in ("成本", "收益", "备注"):
                val = extract_field(art, name)
                if val:
                    out.append(f"{name}：{val}")
            if links:
                out.append(f"来源（{len(links)}条）：{' ; '.join(links)}")
            out.append("")
    return "\n".join(out) + "\n"


def main() -> None:
    skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    args = [a for a in sys.argv[1:] if a != "--from-file"]
    from_file = sys.argv[sys.argv.index("--from-file") + 1] if "--from-file" in sys.argv else None
    out_path = args[0] if args else os.path.join(skill_root, "references", "guide.md")

    if from_file:
        with open(from_file, encoding="utf-8") as f:
            page = f.read()
    else:
        page = fetch(SOURCE)
        tries = 0
        while not consistent(page) and tries < 3:  # spliced/partial copy: refetch whole page
            tries += 1
            page = fetch(SOURCE)

    text = convert(page)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"OK -> {out_path}")
    print(
        f"sections={text.count(chr(10) + '## 第')} "
        f"entries={text.count(chr(10) + '### ')} bytes={os.path.getsize(out_path)}"
    )


if __name__ == "__main__":
    main()
