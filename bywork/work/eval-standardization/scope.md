# 标准评测范围

## 事实源

首次评测中的两份业务提示、三份 CSV 和独立验收提升为标准场景。来源为 `bywork/work/v2-readiness/evaluation/`；其余 trace、指标和产物继续作为历史证据。

| 来源项 | 所属行为单元 | 覆盖状态 | 覆盖依据 |
|---|---|---|---|
| phase-1.txt | 迁移与暂停 | 已覆盖 | 标准 ledger 提示逐字节相同 |
| phase-2.txt | 接续与新约束 | 已覆盖 | 标准 ledger 提示逐字节相同 |
| legacy/01.csv | 递归迁移 | 已覆盖 | 标准夹具逐字节相同 |
| legacy/02.csv | 递归迁移 | 已覆盖 | 标准夹具逐字节相同 |
| legacy/nested/03.csv | 递归迁移 | 已覆盖 | 标准嵌套夹具逐字节相同 |
| acceptance.py | 独立验收 | 已覆盖 | 只适配 fixture 位置与阶段参数；期望值、真实 CLI 调用与全部断言保留 |
| 首次 trace 中的新约束晚写 | 检查点协议 | 已覆盖 | SKILL 绑定独立 work 写入；change 引用该协议；ledger 第二阶段审查动作顺序 |
| 首次 Memory 中的临时与实现事实 | Memory 筛选 | 已覆盖 | Memory reference 与模板筛选跨工作内容；ledger 与正向记忆场景同时验证 |
| 首次哈希算法误标 | 证据准确性 | 已覆盖 | prove 要求核对实际命令；审查表核对算法、参数与输出 |
| 复测中长期结论越界 | Memory 已确认范围 | 已覆盖 | Memory reference 与模板将推演策略留作候选；正向场景确认长期决定保留且未增加重试策略 |
| 复测中待做 report 的格式遗漏 | 跨会话契约保留 | 已覆盖 | prove 与 work 模板保留待做输入输出契约；原始 JSON 验收不变 |
| 真实运行与后续接入 | 维护入口 | 已覆盖 | 运行器、离线检查、发布检查、中英文 README、评审与复盘入口已连接 |

## 复核命令

```bash
python3 - <<'PY'
from pathlib import Path
old = Path('bywork/work/v2-readiness/evaluation')
new = Path('tools/evaluation/cases/ledger')
inputs = [*sorted(old.glob('phase-*.txt')), *sorted((old / 'legacy').rglob('*.csv'))]
assert len(inputs) == 5
for source in inputs:
    relative = source.relative_to(old)
    target = new / relative if source.suffix == '.txt' else new / 'project' / relative
    assert source.read_bytes() == target.read_bytes(), relative
print('5 prompt/data files byte-identical; oracle adaptation reviewed separately')
PY
```

验收适配的差异仅为入口说明、显式阶段参数（1 或 2）和 `project/legacy` 路径。离线检查在首次正确实现上通过，在空操作 CLI 和第二版真实错误实现上失败。第三版两个场景的实际结果见 [评测记录](evaluation/README.md)。
