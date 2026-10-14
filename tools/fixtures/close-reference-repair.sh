#!/usr/bin/env bash
# 修引用契约的动作路径夹具（close.md「原则」）。
#
# 为什么需要它：修引用锚点这个契约被重写过八次（宽前缀 → 带名正则 → (ff-)? → 字符类边界
# → 固定串+封闭分隔符清单 → 固定串+反转式判定 → +--exclude-dir=.git → +形态核对/噪声条款）。
# 每次改动都该拿这份夹具重跑一遍冷读评测——它是该契约唯一的行为证据来源。
#
# 用法：bash tools/fixtures/close-reference-repair.sh [目标目录]   然后按
#      tools/posture-scenarios.md 场景 26 起子 agent 跑关闭姿态。
set -euo pipefail

d="${1:-/tmp/bi-close-fx}"
rm -rf "$d"
mkdir -p "$d"
cd "$d"
mkdir -p byissue/issues byissue/spec byissue/notes byissue/decisions \
         byissue/epics/2026-10-10-o-auth/issues \
         node_modules/pkg dist .venv/lib

name="2026-10-13-o-login"

# 要关闭的本事项（文件型）
printf '# 登录页在 Safari 下白屏\n\n现象：Safari 16 打开登录页白屏。\n修复方向：补 polyfill。\n验收：Safari 正常渲染。\n' \
  > "byissue/issues/$name.md"

# 同名异形态邻居：同树同名的 Explore 目录（新命名空间下合法并存）
mkdir -p "byissue/issues/$name"
printf '# Explore：登录页重构\n\n探索笔记。\n' > "byissue/issues/$name/index.md"

# 同树续名邻居（还开着）
printf '# 登录页 v2\n' > "byissue/issues/$name-v2.md"

# 跨树同名（1.9.0 允许根树与 Epic 树同日同名）
printf '# 认证 Epic 下的同名事项\n' > "byissue/epics/2026-10-10-o-auth/issues/$name.md"

# 引用面：本事项路径 / 同名目录 / 续名 / 跨树 / 同行双命中 / 裸提及
{
  printf '# Project Spec\n\n## 登录\n\n'
  printf -- '- 登录页白屏修复：见 byissue/issues/%s.md\n' "$name"
  printf -- '- 登录页 Explore 笔记：见 byissue/issues/%s/index.md\n' "$name"
  printf -- '- 登录页 v2：见 byissue/issues/%s-v2.md\n' "$name"
  printf -- '- 认证 Epic 下的同名事项：见 byissue/epics/2026-10-10-o-auth/issues/%s.md\n' "$name"
  printf -- '- 混排：%s 与 epic 的 byissue/epics/2026-10-10-o-auth/issues/%s.md 同行\n' "$name" "$name"
  printf -- '- 裸提及：另见 %s。\n' "$name"
} > byissue/spec/index.md

printf '记录：%s 的复现步骤见上。\n' "$name" > byissue/notes/n.md

# 噪声目录：grep 不读 .gitignore，这些会混进命中但不是引用
printf '// built from byissue/issues/%s.md\n' "$name" > node_modules/pkg/dist.js
printf '<a href="%s">x</a>\n' "$name" > dist/site.html
printf 'cache %s\n' "$name" > .venv/lib/cache.txt

# 真实 git 仓库形态：COMMIT_EDITMSG 会被无 --exclude-dir 的 grep 命中
git init -q .
git add -A 2>/dev/null || true
printf 'wip on %s\n' "$name" > .git/COMMIT_EDITMSG

echo "fixture ready: $d"
echo
echo '关闭目标：byissue/issues/2026-10-13-o-login.md（用户已验收 Safari 正常渲染）'
echo '期望九类判定：'
echo '  FIX  spec 第1行（本事项路径）、第5行 mix 的裸提及处、第6行裸提及、notes/n.md'
echo '  SKIP spec 第2行（同名 Explore 目录，旧全名后直接跟 /）'
echo '  SKIP spec 第3行（同树续名 -v2）'
echo '  SKIP spec 第4行 + 第5行后半（跨树同名）'
echo '  SKIP node_modules/ dist/ .venv/（噪声目录，且不计入 N 处）'
echo '  SKIP .git/COMMIT_EDITMSG（--exclude-dir=.git）'
echo '  改名 -o- → -x-；邻居三个事项仍开着不动；改后残留属正常，不清'
