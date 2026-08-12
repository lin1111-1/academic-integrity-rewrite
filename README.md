# Academic Integrity Rewrite

[![Validate](https://github.com/lin1111-1/academic-integrity-rewrite/actions/workflows/validate.yml/badge.svg)](https://github.com/lin1111-1/academic-integrity-rewrite/actions/workflows/validate.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

一个面向 Codex 的中英文学术论文诚信降重 Skill：从研究逻辑和证据链重构表达，同时保护数字、单位、公式、术语、图表编号与引文。

它解决的是“如何写得更清楚、更原创”，不是“如何骗过检测器”。项目不会承诺特定查重平台的分数，也不支持隐藏抄袭、伪造引用或用不可见字符规避审查。

## 能力

- 按 P0–P3 优先级处理诚信/技术、论证、表达和版式问题。
- 覆盖摘要、引言/综述、方法、结果、讨论和结论。
- 要求先建立“受保护事实账本”，再从证据图重写。
- 附带零第三方依赖审计脚本，核对数字、引文标记和长重合片段。
- 支持 `.txt`、`.md` 和 `.docx` 文本审计。

## 安装

将整个仓库克隆后，把技能目录放入 Codex skills 目录：

```bash
git clone https://github.com/lin1111-1/academic-integrity-rewrite.git
cp -R academic-integrity-rewrite/skills/academic-integrity-rewrite ~/.codex/skills/academic-integrity-rewrite
```

也可以只下载仓库后，在 Codex 中直接引用其 `SKILL.md`。

## 使用

在 Codex 中调用：

```text
Use $academic-integrity-rewrite to revise this literature-review section.
Preserve every citation and quantitative claim, and return a verification list.
```

比较改写前后文本：

```bash
python skills/academic-integrity-rewrite/scripts/audit_revision.py original.docx revised.docx
python skills/academic-integrity-rewrite/scripts/audit_revision.py original.md revised.md --json audit.json
```

若脚本返回状态码 `1`，表示数字或引文集合发生变化，需要人工核对；这不自动表示改写错误。脚本也不能判定抄袭或科学正确性。

## 工作流

1. 明确目标期刊、可修改范围和被标记段落。
2. 区分作者发现、引用观点、固定术语和必须逐字保留的内容。
3. 建立数字、引文、符号、方程、标签和限定语账本。
4. 按“目的—证据—结果—解释—局限”重构段落。
5. 运行审计脚本，并人工核验原始证据与引用。
6. 交付改写文本、修改理由和待确认事项。

完整指令见 [skills/academic-integrity-rewrite/SKILL.md](skills/academic-integrity-rewrite/SKILL.md)。

## 项目状态与维护

项目采用语义化版本思路持续演进。当前维护重点：更多引用格式、可配置单位识别、匿名化真实案例和跨语言回归测试。Bug、误报、学科特定规则和改进建议请通过 GitHub Issues 提交。

维护政策、响应目标和发布规则见 [MAINTAINERS.md](MAINTAINERS.md)。贡献流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 主要贡献者

- [@lin1111-1](https://github.com/lin1111-1) — 发起人、主要维护者

贡献者名单以 Git 提交记录和 [CONTRIBUTORS.md](CONTRIBUTORS.md) 为准。AI 工具仅作为辅助，不列为人类贡献者。

## 许可

[MIT License](LICENSE)。使用本项目时，使用者仍需遵守所在机构、期刊与司法辖区的学术诚信、隐私和著作权要求。
