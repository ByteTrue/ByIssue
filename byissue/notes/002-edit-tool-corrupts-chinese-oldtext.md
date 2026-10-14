# `edit` 工具对含中文的 oldText 曾静默损坏（已不复现）

> **读者：** 在这个仓库里批量改中文 markdown 的人——先读「当前状态」，再看历史记录。

**当前状态（2026-10-13 复测，pi 0.85.1）：** 不再复现。`edit` 对中文 `oldText` 的批测全部通过——8 个单块替换（短句 / 反引号 / 全角标点 / 160 字长文 / emoji 与 ①②③ / 路径 / 中英混排 / 特殊字符）、一次调用 5 个块、多行块、以及 221 字含反斜杠与花括号的段落，**无一失败**。

**因此：直接用它。** 遇到「Could not find the exact text / must match exactly」时，先按普通方式排查（确认字符串确实唯一、字节一致）；只有在排查无果且内容是中文时，才怀疑参数通道，退回下面的绕法 1。

**为什么留着这条：** 这不是无凭据的担心。2026-09-21 的 1.2.0 审计里连续踩了 7 次，每次都浪费一轮，失败形态是**参数到达时变成纯换行之类的残片**、报错却只说找不到文本。当时的规避手段被写进了工作流，并在后续多个 issue 里沿用（例如 `byissue/issues/007`）。本次复测证明那个形态已经不在了，但没找到它是什么时候、被哪个改动修掉的，所以不删本条。

**绕法（仅在上述疑虑成立时用）：**

1. **用 `python3` 脚本做字符串替换**，并带断言——顺带防了「匹配到多处」：

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

2. **整文件 `write` 重写**——文件短（模板、decision）时最省事。

3. **`edit` 全程用 `\uXXXX` 转义**——能用，但手工转义长段中文极易出错，不推荐。

**复测方法（怀疑时自己重跑）：** 造一个含中文的临时文件，用 `edit` 替换其中的中文块，确认替换落地且报错为空；再逐级加压——长段落、多块、多行。上文那批用例就是按这个顺序做的。

**相关：** `byissue/issues/002-x-project-spec-slimming-rule.md`、`byissue/issues/001-x-harvest-contract-at-close.md` 的改动是用绕法 1 做的；`byissue/issues/007-x-description-and-posture-table-are-two-trigger-sets.md` 明确写了「遵 notes/002 用 python 替换」——那一步现在不再是必需的。
