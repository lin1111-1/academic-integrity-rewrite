# Academic Integrity Rewrite

[![CI](https://github.com/lin1111-1/academic-integrity-rewrite/actions/workflows/validate.yml/badge.svg?branch=main)](https://github.com/lin1111-1/academic-integrity-rewrite/actions/workflows/validate.yml)
[![Release](https://img.shields.io/github/v/release/lin1111-1/academic-integrity-rewrite)](https://github.com/lin1111-1/academic-integrity-rewrite/releases/latest)
[![License: MIT](https://img.shields.io/github/license/lin1111-1/academic-integrity-rewrite)](LICENSE)
[![Tests](https://img.shields.io/github/actions/workflow/status/lin1111-1/academic-integrity-rewrite/validate.yml?branch=main&label=tests)](https://github.com/lin1111-1/academic-integrity-rewrite/actions/workflows/validate.yml)

一个面向 Codex 的中英文学术论文诚信降重 Skill：从研究逻辑和证据链重构表达，同时保护数字、单位、公式、术语、图表编号与引文。

它解决的是“如何写得更清楚、更原创”，不是“如何骗过检测器”。项目不会承诺特定查重平台的分数，也不支持隐藏抄袭、伪造引用或用不可见字符规避审查。

## 能力

- 按 P0–P3 优先级处理诚信/技术、论证、表达和版式问题。
- 覆盖摘要、引言/综述、方法、结果、讨论和结论。
- 要求先建立“受保护事实账本”，再从证据图重写。
- 附带零第三方依赖审计脚本，核对数字、带单位测量值、引文标记和长重合片段。
- 支持 `.txt`、`.md` 和 `.docx` 文本审计。

## 核心差异

- **本地审计**：审计脚本在用户设备上运行，默认不上传论文、相似度报告或研究数据。
- **受保护事实优先**：先建立数字、单位、公式、术语、图表编号和引文账本，再调整语言与论证结构。
- **可验证而非“保证降重”**：对改写前后事实标记进行确定性比较，并明确要求人工回查原始证据。
- **诚信边界明确**：拒绝规避检测、隐藏抄袭、伪造引用和不可见字符等用途。

## 安装

### 前置条件

- Git。
- Codex desktop、Codex CLI 或 Codex IDE 扩展。
- Python 3.10 或更高版本（仅运行审计脚本和项目测试时需要）。

Codex 会从用户级 `$HOME/.agents/skills` 或仓库级 `.agents/skills` 发现 Skill。以下命令安装到当前用户；如果 Codex 没有立即显示新 Skill，请重启客户端。

### Windows（PowerShell）

```powershell
git clone https://github.com/lin1111-1/academic-integrity-rewrite.git
Set-Location academic-integrity-rewrite

$source = Resolve-Path ".\skills\academic-integrity-rewrite"
$destination = Join-Path $HOME ".agents\skills\academic-integrity-rewrite"
New-Item -ItemType Directory -Force -Path $destination | Out-Null
Copy-Item -Path (Join-Path $source "*") -Destination $destination -Recurse -Force

Test-Path (Join-Path $destination "SKILL.md")
py -3 --version
```

`Test-Path` 应返回 `True`。如果系统没有 `py` 启动器，可将后续命令中的 `py -3` 换成 `python`。

### macOS

```bash
git clone https://github.com/lin1111-1/academic-integrity-rewrite.git
cd academic-integrity-rewrite

mkdir -p "$HOME/.agents/skills/academic-integrity-rewrite"
cp -R skills/academic-integrity-rewrite/. "$HOME/.agents/skills/academic-integrity-rewrite/"

test -f "$HOME/.agents/skills/academic-integrity-rewrite/SKILL.md" && echo "Skill installed"
python3 --version
```

如未安装 Python，可使用 Homebrew：`brew install python`。Git 可通过 Xcode Command Line Tools（`xcode-select --install`）或 Homebrew 安装。

### Linux

先用发行版包管理器安装 Git 和 Python 3.10+。例如 Ubuntu/Debian：

```bash
sudo apt update
sudo apt install -y git python3

git clone https://github.com/lin1111-1/academic-integrity-rewrite.git
cd academic-integrity-rewrite

mkdir -p "$HOME/.agents/skills/academic-integrity-rewrite"
cp -R skills/academic-integrity-rewrite/. "$HOME/.agents/skills/academic-integrity-rewrite/"

test -f "$HOME/.agents/skills/academic-integrity-rewrite/SKILL.md" && echo "Skill installed"
python3 --version
```

Fedora 可使用 `sudo dnf install git python3`；Arch Linux 可使用 `sudo pacman -S git python`。

### 仅为当前仓库安装

如果不想安装到用户目录，可把 `skills/academic-integrity-rewrite` 复制到目标项目的 `.agents/skills/academic-integrity-rewrite`。Codex 在该项目中工作时会发现它，适合团队随仓库固定 Skill 版本。

## 最小可运行示例

先在刚克隆的仓库根目录创建两个保留相同数字与引文的文本，然后运行审计。

Windows PowerShell：

```powershell
Set-Content -Encoding utf8 original.txt "At Re = 450, efficiency increased to 1.41 [12]."
Set-Content -Encoding utf8 revised.txt "At Re = 450, the measured efficiency reached 1.41 [12]."
py -3 .\skills\academic-integrity-rewrite\scripts\audit_revision.py .\original.txt .\revised.txt
```

macOS / Linux：

```bash
printf '%s\n' 'At Re = 450, efficiency increased to 1.41 [12].' > original.txt
printf '%s\n' 'At Re = 450, the measured efficiency reached 1.41 [12].' > revised.txt
python3 skills/academic-integrity-rewrite/scripts/audit_revision.py original.txt revised.txt
```

预期结果中 `numbers`、`measurements` 和 `citations` 的变更集合均为空，进程状态码为 `0`。如果数字、带单位测量值或引文集合发生变化，脚本返回状态码 `1`，提示必须人工核对；这不自动表示改写错误，也不能判定抄袭或科学正确性。

随后可在 Codex 中显式调用 Skill：

```text
Use $academic-integrity-rewrite to revise this literature-review section.
Preserve every citation and quantitative claim, and return a verification list.
```

审计也支持 `.docx` 和 JSON 报告：

```bash
python3 skills/academic-integrity-rewrite/scripts/audit_revision.py original.docx revised.docx
python3 skills/academic-integrity-rewrite/scripts/audit_revision.py original.md revised.md --json audit.json
```

`.docx` 审计会读取正文中的普通段落、表格与内嵌文本框，以及脚注和尾注。当前不会读取页眉、页脚、批注、已删除的修订文字，或未以 WordprocessingML 文本保存的绘图内容；包含这些结构的文档仍需人工核对。

引用审计支持 IEEE/GB/T 数字引文以及 APA、GB/T 作者—年份形式；中英文混合文本可使用半角或全角括号、逗号和分号，例如 `（张伟，2020，第15页）`。叙述式引文（如 `Placeholder (2020) showed ...`）仍不会自动识别，以避免将普通的括号年份误当成引文；请将其纳入人工事实账本核对。

## 可复现案例与示例输出

仓库提供一个事实保持案例和一个故意改变百分比的失败案例。示例数据由维护者创建，不包含用户论文，也不作为第三方采用证据。

```bash
# 保留 Re = 450、12.4%、25 °C 和引文 [12]；预期状态码 0
python skills/academic-integrity-rewrite/scripts/audit_revision.py examples/original.txt examples/revised-preserved.txt

# 将 12.4% 改为 12.8%；预期状态码 1
python skills/academic-integrity-rewrite/scripts/audit_revision.py examples/original.txt examples/revised-changed.txt
```

成功案例的 `numbers`、`measurements` 和 `citations` 变更集合均为空。失败案例会同时报告缺失的 `12.4%` 和新增的 `12.8%`：

```json
{
  "numbers": {
    "missing_or_reduced": {"12.4%": 1},
    "added_or_increased": {"12.8%": 1}
  }
}
```

完整输入、预期输出和复现说明见 [examples/README.md](examples/README.md)。

## 工作流

1. 明确目标期刊、可修改范围和被标记段落。
2. 区分作者发现、引用观点、固定术语和必须逐字保留的内容。
3. 建立数字、引文、符号、方程、标签和限定语账本。
4. 按“目的—证据—结果—解释—局限”重构段落。
5. 运行审计脚本，并人工核验原始证据与引用。
6. 交付改写文本、修改理由和待确认事项。

完整指令见 [skills/academic-integrity-rewrite/SKILL.md](skills/academic-integrity-rewrite/SKILL.md)。

## 项目状态与维护

项目遵循语义化版本思路持续演进。当前优先级、目标版本与发布门槛见 [ROADMAP.md](ROADMAP.md)。路线图时间窗口是规划目标，不构成交付承诺。

### 公开采用与反馈证据

[![GitHub stars](https://img.shields.io/github/stars/lin1111-1/academic-integrity-rewrite?style=flat&label=stars)](https://github.com/lin1111-1/academic-integrity-rewrite/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/lin1111-1/academic-integrity-rewrite?style=flat&label=forks)](https://github.com/lin1111-1/academic-integrity-rewrite/forks)

- Stars、Forks、发布记录和贡献者以 GitHub 的实时公开数据为准；这些指标不等同于活跃用户数或学术影响力。
- 项目目前没有可公开核验的安装量、下载量或引用量，因此不声明这些数字。
- 项目目前没有经过核验的第三方用户证言。欢迎通过 [Anonymous usage feedback](https://github.com/lin1111-1/academic-integrity-rewrite/issues/new?template=usage_feedback.yml) 提交不含稿件内容的公开反馈。
- 任何采用或反馈声明都必须链接到可核验来源；维护者不会虚构用户、机构或使用效果。

### Codex 维护计划

Codex 将作为维护辅助工具，用于生成和审查回归测试、定位审计规则边界、扩展 APA/IEEE/GB/T 7714 引用形式、构造中英混合测试样例，以及研究 `.docx` 表格、脚注和文本框支持。所有行为变化仍需人工审查、确定性测试和 CI 验证；Codex 不代替维护者作出学术正确性或引用适当性判断。

Bug、误报和改进建议请通过对应的 [GitHub Issue 模板](https://github.com/lin1111-1/academic-integrity-rewrite/issues/new/choose)提交。公开样例必须最小化并匿名；请勿上传未发表稿件、个人数据或敏感材料。安全漏洞请使用[私密安全报告](https://github.com/lin1111-1/academic-integrity-rewrite/security/advisories/new)。

维护政策、响应目标和发布规则见 [MAINTAINERS.md](MAINTAINERS.md)。贡献流程见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 主要贡献者

- [@lin1111-1](https://github.com/lin1111-1) — 发起人、主要维护者

贡献者名单以 Git 提交记录和 [CONTRIBUTORS.md](CONTRIBUTORS.md) 为准。AI 工具仅作为辅助，不列为人类贡献者。

## 许可

[MIT License](LICENSE)。使用本项目时，使用者仍需遵守所在机构、期刊与司法辖区的学术诚信、隐私和著作权要求。
