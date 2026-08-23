# 可复现审计案例

这些文件是项目维护者创建的最小测试数据，不是用户论文或第三方使用证言。它们用于证明审计脚本的公开行为，并可在 Windows、macOS 和 Linux 上复现。

## 事实保持案例

`original.txt` 与 `revised-preserved.txt` 使用不同句法表达，但保留 `Re = 450`、`12.4%`、`25 °C` 和引文 `[12]`。

```bash
python skills/academic-integrity-rewrite/scripts/audit_revision.py examples/original.txt examples/revised-preserved.txt
```

预期状态码为 `0`，三个关键变更集合均为空：

```json
{
  "numbers": {"missing_or_reduced": {}, "added_or_increased": {}},
  "measurements": {"missing_or_reduced": {}, "added_or_increased": {}},
  "citations": {"missing_or_reduced": {}, "added_or_increased": {}}
}
```

## 数字变化案例

`revised-changed.txt` 把 `12.4%` 改成 `12.8%`，用于验证审计警告。

```bash
python skills/academic-integrity-rewrite/scripts/audit_revision.py examples/original.txt examples/revised-changed.txt
```

预期状态码为 `1`，输出包含：

```json
{
  "numbers": {
    "missing_or_reduced": {"12.4%": 1},
    "added_or_increased": {"12.8%": 1}
  },
  "measurements": {
    "missing_or_reduced": {"12.4%": 1},
    "added_or_increased": {"12.8%": 1}
  }
}
```

状态码 `1` 表示需要人工核对，不等同于科学结论错误。审计脚本也不能独立证明原创性或引用适当性。
