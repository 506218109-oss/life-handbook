# life-handbook 🧭

A ZCode skill that turns the open web guide *How to Live Better* — 《高性价比人生指南》 by [cdyforever](https://cdyforever.github.io/how-to-live-better/) (33 sections, 600+ recommendations, each graded by cost / benefit / evidence level) — into an on-demand life advisor.

一个 ZCode skill：把开源网页书《高性价比人生指南》（作者 cdyforever，33 节 600+ 条建议，每条带成本/收益/证据等级）变成随问随答的生活顾问。

## How it works / 工作方式

1. **Classify 归类** — the agent maps your question to one of the 33 sections automatically (no manual category picking).
   AI 自动把你的问题映射到 33 节之一，不需要手动选分类。
2. **Search 检索** — `scripts/lookup.py` finds matching entries in the local full text.
   按关键词在本地全文里检索对应条目。
3. **Answer 回答** — fixed format: verdict → cost (money/time/willpower) / benefit / evidence grade (A/B/C) → source link.
   固定格式输出：结论 → 性价比（钱/时间/毅力/收益/证据等级）→ 原文出处。

Emergency guardrail built in: chest pain, stroke signs, heavy bleeding, suicidal thoughts → call 120 / 110 / 119 / 12356 / 96110 **first**, handbook second.
内置急救红线：疑似急症先打急救电话，再查手册。

## Install / 安装

```bash
git clone https://github.com/506218109-oss/life-handbook.git
./life-handbook/install.sh
```

Then just ask / 然后直接问：

- “体检中心推销 7000 块的全身 PET-CT，做吗？”
- “公司让我签主动辞职，签吗？”
- “我妈被卖保健品的骗了怎么办？”

First install downloads the guide text from the author's site (~2 MB, one time).
首次安装会从原站下载正文（约 2MB，仅一次）。

## Files / 结构

```
life-handbook/
├── SKILL.md               # routing rules, 33-section map, output format / 路由规则、33节地图、输出格式
├── scripts/fetch_guide.py # download & flatten the guide text / 下载并转换正文
├── scripts/lookup.py      # keyword search over the local text / 本地全文检索
└── references/guide.md    # generated local full text (not in this repo) / 本地正文（脚本生成，不入库）
```

## License & credits / 许可与致谢

- Skill code: [MIT](LICENSE)
- Guide content © [cdyforever](https://github.com/cdyforever/how-to-live-better) — **not included in this repo**. The guide has no open license; `fetch_guide.py` fetches it from the author's site for personal, local use only. Please keep it that way.
- 本 skill 代码采用 MIT；指南正文版权归原作者 cdyforever 所有，本仓库不含正文，安装脚本从原站获取，仅供个人本地使用，请勿再分发。
- Not medical / legal advice. Figures and policies may be outdated — verify with official sources. 本内容不构成医疗或法律建议，具体数字与政策以官方最新口径为准。
