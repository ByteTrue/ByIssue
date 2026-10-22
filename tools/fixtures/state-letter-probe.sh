#!/usr/bin/env bash
# 状态字母读法探针（`o` / `x` / `w`）。
#
# 为什么需要它：状态字母是路径里唯一表达状态的字符，它的含义没有消歧信息，只能靠先验读。
# `d` 曾在这个位置被读成 draft（真实事故）；换成 `w` 之后，竞争先验是 `wip`（in progress）
# ——那是比 draft 更糟的错读，因为「进行中」会把一个已放弃的事项当成活跃事项。
#
# 四臂对照，判据是子 agent 报出的状态，不是它的自述推理：
#   w-clean     Epic `-w-`，无子 issue           → 必须读成「放弃 / 不做」，不得出现「进行中 / 还没做 / 在做」
#   w-settled   Epic `-w-`，内部一个 `-x-` 子 issue → 同上；已关的子 issue 不改变 Epic 状态
#   w-violation Epic `-w-`，内部一个 `-o-` 子 issue → 反向断言：必须指出这违反 close.md 的关闭前置条件
#                （关闭 epic 要求内部事项已关或明确废弃/移出），不得把 Epic 读成进行中
#   o-control   Epic `-o-`                       → 必须读成「进行中 / 开着」（防「一律答放弃」）
#   x-control   Epic `-x-`                       → 必须读成「已交付 / 关闭」（防「字母被整体忽略」）
#
# 用法：bash tools/fixtures/state-letter-probe.sh [根目录]   然后按
#      tools/posture-scenarios.md 场景 27 起子 agent 逐臂跑。
set -euo pipefail

root="${1:-/tmp/bi-letter}"
rm -rf "$root"
mkdir -p "$root"

# 项目外壳：真项目实施时是 git 仓库且有依赖产物目录，夹具要长得像它。
for arm in w-clean w-settled w-violation o-control x-control; do
  d="$root/$arm"
  mkdir -p "$d/src" "$d/node_modules/pkg" "$d/dist"
  git -C "$d" init -q
  printf 'export function normalize(input: string) {\n  return input.trim();\n}\n' > "$d/src/normalize.ts"
  chmod +x "$d/src" 2>/dev/null || true

  mkdir -p "$d/byissue"/{talks,vision,spec,issues,epics,notes,decisions,tools}

  cat > "$d/byissue/spec/index.md" <<'EOF'
---
kind: spec
---

# 项目规格

## 当前能力

- 客户端只处理本地文件的规范化。

## 长期约束

- 所有客户端代码走同一份规范化实现。
EOF

  case "$arm" in
    w-clean|w-settled|w-violation) letter=w ;;
    o-control)                     letter=o ;;
    x-control)                     letter=x ;;
  esac

  epic="$d/byissue/epics/2026-09-09-$letter-client-plugin"
  mkdir -p "$epic/issues"

  cat > "$epic/spec.md" <<'EOF'
---
kind: epic
created: 2026-09-09
---

# 客户端插件

## 目标

让第三方插件在宿主进程内注册自己的规范化器，宿主按注册顺序串起来。

## 边界

插件只能注册规范化器，不能替换宿主的文件读取路径。

## 设计

宿主暴露 `registerNormalizer(fn)`；同名注册按后到者覆盖。
EOF

  case "$arm" in
  w-settled|w-violation) child_letter=o ;;
  *) child_letter= ;;
  esac
  [ "$arm" = w-settled ] && child_letter=x
  if [ -n "$child_letter" ]; then
    cat > "$epic/issues/2026-09-12-$child_letter-plugin-hooks.md" <<'EOF'
---
kind: issue
title: "插件注册钩子"
type: feature
created: 2026-09-12
---

# 插件注册钩子

## 目标

宿主暴露 `registerNormalizer(fn)`，按注册顺序串行调用。
EOF
  fi

  printf '# 客户端插件\n\n未决问题：插件生命周期由谁负责。\n' > "$d/byissue/notes/2026-09-10-plugin-lifecycle.md"
done

echo "fixtures ready under $root"
for arm in w-clean w-settled w-violation o-control x-control; do
  ls -d "$root/$arm"/byissue/epics/*/
done
