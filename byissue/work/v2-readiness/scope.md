# 范围覆盖

## 事实源

归档基线为 Git 提交 `471cd65abb7fe07aadff8302941cbc649f95fe08`。移动前逐文件枚举五个旧工作目录和旧复盘，保存 SHA-256；旧 spec 从该提交提取，归档前的 v2 项目约束进入当前 Memory。

完整的 73 项来源、目标和摘要保存在 [archive-manifest.json](archive-manifest.json)。以下按来源目录汇总，同一行中的每个文件都已逐项比对摘要。

| 来源项 | 所属行为单元 | 覆盖状态 | 覆盖依据 |
|---|---|---|---|
| 旧 decisions 的 14 个文件 | 旧记录归档 | 已覆盖 | manifest 中对应 14 项与目标 SHA-256 相等 |
| 旧 epics 的 20 个文件 | 旧记录归档 | 已覆盖 | manifest 中对应 20 项与目标 SHA-256 相等 |
| 旧 issues 的 26 个文件 | 旧记录归档 | 已覆盖 | manifest 中对应 26 项与目标 SHA-256 相等 |
| 旧 notes 的 6 个文件 | 旧记录归档 | 已覆盖 | manifest 中对应 6 项与目标 SHA-256 相等 |
| 旧 talks 的 5 个文件 | 旧记录归档 | 已覆盖 | manifest 中对应 5 项与目标 SHA-256 相等 |
| 基线 spec 的 1 个文件 | 旧记录归档 | 已覆盖 | Git 基线字节与归档目标相等 |
| 旧复盘的 1 个文件 | 旧记录归档 | 已覆盖 | manifest 对应项与目标 SHA-256 相等 |
| 中英文 README、AGENTS、WHY、NOTICE | 当前入口 | 已覆盖 | 安装指向 v2；当前材料指向 work 与 memory；历史入口单独标明 |
| checker、自测与 release-check | 维护检查 | 已覆盖 | checker 自测 22/22、初始化测试、安装副本比较通过 |
| pi 安装与两轮任务 | 实际行为验证 | 已覆盖 | 运行结果见 evaluation/README.md；业务通过，工作流执行缺口如实保留 |

## 复核方式

在仓库根目录运行以下检查。它同时对照基线追踪文件集合，防止 manifest 自己遗漏来源：

```bash
python3 - <<'PY'
import hashlib, json, subprocess
from pathlib import Path
root = Path.cwd()
manifest = json.loads((root / 'byissue/work/v2-readiness/archive-manifest.json').read_text())
expected = set(subprocess.check_output([
    'git', 'ls-tree', '-r', '--name-only', manifest['baseline'],
    'byissue', 'tools/retro-failure-modes.md',
], text=True).splitlines())
assert expected == {item['source'] for item in manifest['files']}
for item in manifest['files']:
    data = (root / item['target']).read_bytes()
    assert hashlib.sha256(data).hexdigest() == item['sha256'], item['target']
assert set(p.name for p in (root / 'byissue').iterdir()) <= {'work', 'memory', 'vision'}
print(f"{len(expected)} archived files verified")
PY
```
