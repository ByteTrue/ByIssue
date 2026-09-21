# `edit` 工具对含中文的 oldText 会静默损坏

> **读者：** 在这个仓库里批量改中文 markdown 的人——报错骗人，别去怀疑文件内容。

**结论：** pi 的 `edit` 工具在本环境下，传入含中文的 `oldText` 时参数会被破坏（到达时变成纯换行之类的残片），报错却只说「Could not find the exact text / must match exactly」。**看到这个报错先怀疑工具，不要先怀疑文件。**

**何时用：** 改 `skills/bi/**/*.md`、`byissue/**/*.md`、README 等中文文档时。2026-09-21 的 1.2.0 审计和后续实现里连续踩了 7 次，每次都浪费一轮。

**绕法（按可靠性排序）：**

1. **用 `python3` 脚本做字符串替换**，并带断言——这是首选，还顺带防了「匹配到多处」：

   ```bash
   python3 - <<'PY'
   from pathlib import Path
   p = Path("skills/bi/references/close.md")
   t = p.read_text(encoding="utf-8")
   old = "按物理归属回写，路径是权威来源："
   assert t.count(old) == 1
   p.write_text(t.replace(old, "新内容"), encoding="utf-8")
   PY
   ```

2. **整文件 `write` 重写**——文件短（模板、decision）时最省事，`write` 对中文没问题。
3. **`edit` 全程用 `\uXXXX` 转义**——能用，但手工转义长段中文极易出错，不推荐。

**注意：** `write` 工具和 bash heredoc 里的中文都是好的，只有 `edit` 的参数通道有问题。所以「用脚本改」不是在绕开文件系统，只是换一条参数通道。

**相关：** `byissue/issues/002-o-project-spec-slimming-rule.md`、`byissue/issues/001-o-harvest-contract-at-close.md` 的改动都是用绕法 1 做的。
