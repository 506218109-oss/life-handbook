#!/usr/bin/env python3
"""Search the local copy of 《高性价比人生指南》 (references/guide.md).

Usage:
  python3 lookup.py --map                    # show the 33-section map
  python3 lookup.py --section 19             # print every entry in section 19
  python3 lookup.py "关键词" "关键词2"        # keyword search, top matches
  python3 lookup.py --top 3 "体检"           # limit result count

Keywords should be concrete nouns (体检 / 裁员 / 头盔 / 户口), not whole
sentences. Title and meta-line hits weigh more than body hits.
"""
import argparse
import os
import re
import sys

WEIGHT_TITLE, WEIGHT_META, WEIGHT_SECTION, WEIGHT_BODY = 5, 3, 3, 1


def skill_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_entries(path: str):
    sections = {}  # num -> (title, count)
    entries = []  # dict(sec, idx, title, meta, body_lines)
    cur_sec = None
    cur = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            m = re.match(r"^## 第 (\d+) 节 (.+?)（(\d+) 条）$", line)
            if m:
                cur_sec = int(m.group(1))
                sections[cur_sec] = [m.group(2), int(m.group(3))]
                cur = None
                continue
            m = re.match(r"^### (\d+)\.(\d+) (.*)$", line)
            if m:
                cur = {
                    "sec": int(m.group(1)),
                    "idx": int(m.group(2)),
                    "title": m.group(3),
                    "meta": "",
                    "body": [],
                }
                entries.append(cur)
                continue
            if cur is not None:
                if line.startswith("〔") and line.endswith("〕"):
                    cur["meta"] = line[1:-1]
                elif line.strip():
                    cur["body"].append(line)
    return sections, entries


def score(entry: dict, section_title: str, keywords) -> int:
    s = 0
    title = entry["title"]
    meta = entry["meta"]
    sec_title = section_title
    body = " ".join(entry["body"])
    for kw in keywords:
        k = kw.lower()
        s += WEIGHT_TITLE * title.lower().count(k)
        s += WEIGHT_META * meta.lower().count(k)
        s += WEIGHT_SECTION * sec_title.lower().count(k)
        s += WEIGHT_BODY * body.lower().count(k)
    return s


def print_entry(e: dict) -> None:
    print(f"### {e['sec']}.{e['idx']} {e['title']}")
    if e["meta"]:
        print(f"〔{e['meta']}〕")
    for line in e["body"]:
        print(line)
    print()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("keywords", nargs="*")
    ap.add_argument("--map", action="store_true")
    ap.add_argument("--section", type=int)
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--file", default=os.path.join(skill_root(), "references", "guide.md"))
    args = ap.parse_args()

    if not os.path.exists(args.file):
        print(f"guide.md not found at {args.file}")
        print("run: python3 scripts/fetch_guide.py   (downloads from the original site)")
        sys.exit(2)

    sections, entries = load_entries(args.file)

    if args.map or (not args.keywords and args.section is None):
        print(f"《高性价比人生指南》共 {len(sections)} 节 {len(entries)} 条（作者 cdyforever）")
        for n in sorted(sections):
            print(f"  第 {n:>2} 节  {sections[n][0]}（{sections[n][1]} 条）")
        print('\n用法: python3 lookup.py "关键词"  /  --section 节号  /  --map')
        return

    if args.section is not None:
        sec_entries = sorted(
            (e for e in entries if e["sec"] == args.section), key=lambda e: e["idx"]
        )
        if not sec_entries:
            print(f"第 {args.section} 节不存在（范围 1-{max(sections)}）")
            sys.exit(1)
        kws = args.keywords
        for e in sec_entries:
            if not kws or score(e, sections[e["sec"]][0], kws) > 0:
                print_entry(e)
        return

    kws = args.keywords
    ranked = sorted(
        ((score(e, sections[e["sec"]][0], kws), i) for i, e in enumerate(entries)),
        key=lambda x: -x[0],
    )
    hits = [(s, entries[i]) for s, i in ranked if s > 0]
    if not hits:
        print("没查到相关条目。试试更短的词（如「体检」「裁员」「头盔」），或用 --map 看节目录。")
        sys.exit(1)
    sec_hits = {}
    for s, e in hits:
        sec_hits.setdefault(e["sec"], 0)
        sec_hits[e["sec"]] += s
    print(
        "相关节："
        + " ｜ ".join(f"第 {n} 节 {sections[n][0]}（命中分 {v}）" for n, v in sorted(sec_hits.items(), key=lambda x: -x[1])[:4])
    )
    print()
    for s, e in hits[: args.top]:
        print_entry(e)


if __name__ == "__main__":
    main()
