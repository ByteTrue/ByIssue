#!/usr/bin/env python3
"""Build one fixture project per posture scenario, plus the behavior probes, for a cold run.

Usage: python3 tools/fixtures/posture_table.py [root] [skill_md]
  root      prefix for fixture dirs, default /tmp/shop (dirs are <root>-01, <root>-02, ...)
  skill_md  the SKILL.md the child must load, default the deployed copy

Writes the fixtures and <root>-plan.json. Each plan entry has the dir, the scenario id, the
task to send unchanged to a plain subagent (cwd = dir), the references it should and should not
read, and the behavior assertion to check by hand. Score with tools/fixtures/posture_judge.py.
Dir names are sequential numbers so nothing the child can see hints at the expected answer.
"""
from __future__ import annotations

import datetime
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/shop"
SKILL = sys.argv[2] if len(sys.argv) > 2 else str(
    Path.home() / ".pi/agent/skills/magpie-skills/.skills/bi/SKILL.md")
TODAY = datetime.date.today().isoformat()
FIXTURES = Path(__file__).resolve().parent
GIT = ["git", "-c", "user.name=dev", "-c", "user.email=dev@example.com"]


def write(base: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text.lstrip("\n"), encoding="utf-8")


def git(d: Path, *args: str) -> None:
    subprocess.run([*GIT, *args], cwd=d, check=True, capture_output=True)


def commit(d: Path, msg: str) -> None:
    git(d, "add", "-A")
    git(d, "commit", "-qm", msg)


# ---------- shop: a tiny zero-dependency Node backend ----------

SHOP = {
    "package.json": '{\n  "name": "shopfront",\n  "type": "module",\n  "scripts": { "test": "node --test" }\n}\n',
    ".gitignore": "node_modules/\n",
    "README.md": "# shopfront\n\nTiny shop backend: cart, coupons, checkout, inventory.\n\n## Test\n\n    npm tset\n",
    "src/pricing.js": '''
export const DEFAULT_CURRENCY = "USD";

export function lineTotal(price, qty) {
  return price * qty;
}

export function format(amount, currency = DEFAULT_CURRENCY) {
  return `${currency} ${amount.toFixed(2)}`;
}
''',
    "src/cart.js": '''
import { lineTotal } from "./pricing.js";

export class Cart {
  constructor() {
    this.items = new Map();
  }

  add(sku, price, qty = 1) {
    const item = this.items.get(sku);
    if (item) item.qty += qty;
    else this.items.set(sku, { sku, price, qty });
    console.log("cart add", sku, qty);
  }

  remove(sku) {
    if (!this.items.has(sku)) throw new Error(`no such item: ${sku}`);
    this.items.delete(sku);
  }

  total() {
    let sum = 0;
    for (const item of this.items.values()) sum += lineTotal(item.price, item.qty);
    return sum;
  }
}
''',
    "src/coupons.js": '''
// A coupon is { kind: "percent", value: 10 } or { kind: "fixed", value: 5 }.
export function applyCoupon(total, coupon) {
  if (!coupon) return total;
  if (coupon.kind === "percent") return total * (1 - coupon.value / 100);
  if (coupon.kind === "fixed") return Math.max(0, total - coupon.value);
  throw new Error(`unknown coupon kind: ${coupon.kind}`);
}
''',
    "src/inventory.js": '''
const stock = new Map();

export function setStock(sku, n) {
  stock.set(sku, n);
}

export function decrement(sku, qty) {
  const left = (stock.get(sku) ?? 0) - qty;
  if (left < 0) throw new Error(`out of stock: ${sku}`);
  stock.set(sku, left);
}
''',
    "src/checkout.js": '''
import { applyCoupon } from "./coupons.js";
import { decrement } from "./inventory.js";

export async function checkout(cart, payment, coupon) {
  const amount = applyCoupon(cart.total(), coupon);
  console.log("checkout start", amount);
  let receipt;
  try {
    receipt = await payment.charge(amount);
  } catch (err) {
    if (err.code === "TIMEOUT") {
      console.log("charge timed out, retrying");
      receipt = await payment.charge(amount);
    } else {
      throw err;
    }
  }
  for (const item of cart.items.values()) decrement(item.sku, item.qty);
  return { receipt, message: "Thanks for you order" };
}
''',
    "src/server.js": '''
import http from "node:http";
import { Cart } from "./cart.js";

const cart = new Cart();

export const server = http.createServer((req, res) => {
  console.log(req.method, req.url);
  if (req.url === "/cart") {
    res.end(JSON.stringify({ total: cart.total() }));
    return;
  }
  res.statusCode = 404;
  res.end("not found");
});
''',
    "src/logger.js": '''
export const logger = {
  debug: (...args) => {
    if (process.env.DEBUG) console.error("[debug]", ...args);
  },
  info: (...args) => console.error("[info]", ...args),
};
''',
    "test/cart.test.js": '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { Cart } from "../src/cart.js";

test("total sums line totals", () => {
  const cart = new Cart();
  cart.add("a", 10, 2);
  cart.add("b", 5);
  assert.equal(cart.total(), 25);
});
''',
    "test/coupons.test.js": '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { applyCoupon } from "../src/coupons.js";

test("percent and fixed coupons", () => {
  assert.equal(applyCoupon(100, { kind: "percent", value: 10 }), 90);
  assert.equal(applyCoupon(3, { kind: "fixed", value: 5 }), 0);
});
''',
    "byissue/spec/index.md": '''
# shopfront

> **读者：** 改这个仓库的人和 agent。

## 这是什么

一个小型网店后端：购物车、优惠券、结账、库存。Node 22+，无第三方依赖，测试用 `node --test`。

## 当前真相

- 购物车金额用浮点数（元）存储与计算。
- 结账先扣款，扣款成功后再减库存。
- 每单只能用一张优惠券。
- 免运费：进行中，见 [2026-11-07-o-free-shipping](../issues/2026-11-07-o-free-shipping.md)。

## 约束

- 不引入第三方运行时依赖。用户 2026-10-15 原话：「后端保持零依赖」。
''',
    "byissue/notes/2026-10-20-payment-sandbox-timeout.md": '''
# 支付沙箱超时后扣款可能已经成功

> **读者：** 改结账或支付重试的人。

**结论：** 支付沙箱 3 秒内没响应就向调用方返回 `TIMEOUT`，但这笔扣款在支付方那边可能已经成功。

**依据：** 2026-10-20 在沙箱上观察到：超时返回后，沙箱后台仍出现了这笔扣款记录。用之前先复核。
''',
    "byissue/issues/2026-11-05-o-coupon-stacking.md": '''
---
kind: issue
title: "支持多张优惠券叠加"
type: feature
created: 2026-11-05
---

# 支持多张优惠券叠加

## 要做什么

结账时允许同时用多张优惠券：同类券不叠加；折扣券与满减券都有时，先算折扣再算满减。

## 关闭条件

`checkout` 接受优惠券数组，按上面的规则计算，有测试覆盖。
''',
    "byissue/issues/2026-11-07-o-free-shipping.md": '''
---
kind: issue
title: "满 99 元免运费"
type: feature
created: 2026-11-07
---

# 满 99 元免运费

## 要做什么

订单商品总额满 99 元时运费为 0，否则运费 10 元。

## 关闭条件

`shippingFee(total)` 按上面的规则返回运费，有测试覆盖。
''',
    "byissue/issues/2026-11-08-o-cart-clear.md": '''
---
kind: issue
title: "购物车一键清空"
type: feature
created: 2026-11-08
---

# 购物车一键清空

## 要做什么

给 `Cart` 加 `clear()`，清空所有商品。

## 关闭条件

`clear()` 之后 `total()` 为 0、`items.size` 为 0，有测试覆盖。
''',
}

SHIPPING = {
    "src/shipping.js": '''
export const FREE_SHIPPING_THRESHOLD = 99;

export function shippingFee(total) {
  return total >= FREE_SHIPPING_THRESHOLD ? 0 : 10;
}
''',
    "test/shipping.test.js": '''
import { test } from "node:test";
import assert from "node:assert/strict";
import { shippingFee } from "../src/shipping.js";

test("free shipping from 99", () => {
  assert.equal(shippingFee(99), 0);
  assert.equal(shippingFee(98.99), 10);
});
''',
}

SHIPPING_DONE_RECORD = '''

## 执行记录

- 2026-11-09：新增 `src/shipping.js` 的 `shippingFee`，满 99 返回 0，否则 10；`test/shipping.test.js` 覆盖边界 99 与 98.99，`npm test` 全部通过。
'''

# ---------- kv: a small Python CLI to port from old/ to new/ ----------

KV_OLD = {
    "old/kv.py": '''
import json, sys, os
DB = os.environ.get("KV_DB", "kv.json")
def load():
    return json.load(open(DB)) if os.path.exists(DB) else {}
def save(d):
    json.dump(d, open(DB, "w"))
def main(argv):
    d = load()
    cmd, args = argv[0], argv[1:]
    if cmd == "set": d[args[0]] = args[1]; save(d)
    elif cmd == "get":
        if args[0] not in d: print(f"missing {args[0]}", file=sys.stderr); return 1
        print(d[args[0]])
    elif cmd == "del": d.pop(args[0], None); save(d)
    elif cmd == "list":
        for k in sorted(d): print(f"{k}={d[k]}")
    elif cmd == "count": print(len(d))
    elif cmd == "clear": save({})
    else: print(f"unknown {cmd}", file=sys.stderr); return 2
    return 0
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
''',
    "new/README.md": "# new\n\nPort of old/kv.py: an argparse CLI plus a separate store module.\n",
    ".gitignore": "__pycache__/\n",
    "byissue/spec/index.md": "# kv\n\n## 当前真相\n\n`old/kv.py` 是线上在用的键值 CLI，存储是 `KV_DB` 指向的 JSON 文件。\n",
}

# Scenario 30 needs a port that one look cannot verify: three tools, many subcommands and flags.
KV_SUITE = {
    "old/todo.py": '''
import json, os, sys
DB = os.environ.get("TODO_DB", "todo.json")
def load():
    return json.load(open(DB)) if os.path.exists(DB) else []
def save(items):
    json.dump(items, open(DB, "w"))
def main(argv):
    items = load()
    cmd, args = argv[0], argv[1:]
    if cmd == "add":
        pri = "normal"
        if args and args[0] in ("--high", "--low"): pri = args.pop(0)[2:]
        items.append({"text": " ".join(args), "done": False, "pri": pri}); save(items)
        print(len(items))
    elif cmd == "list":
        show_all = "--all" in args
        for i, it in enumerate(items, 1):
            if it["done"] and not show_all: continue
            mark = "x" if it["done"] else " "
            flag = "!" if it["pri"] == "high" else ""
            print(f"{i}. [{mark}] {flag}{it['text']}")
    elif cmd == "done":
        n = int(args[0])
        if n < 1 or n > len(items): print(f"no item {n}", file=sys.stderr); return 1
        items[n - 1]["done"] = True; save(items)
    elif cmd == "undo":
        n = int(args[0]); items[n - 1]["done"] = False; save(items)
    elif cmd == "rm":
        n = int(args[0]); items.pop(n - 1); save(items)
    elif cmd == "edit":
        n = int(args[0]); items[n - 1]["text"] = " ".join(args[1:]); save(items)
    elif cmd == "prune":
        kept = [it for it in items if not it["done"]]
        print(len(items) - len(kept)); save(kept)
    elif cmd == "stats":
        done = sum(it["done"] for it in items)
        print(f"{done}/{len(items)} done")
    else: print(f"unknown {cmd}", file=sys.stderr); return 2
    return 0
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
''',
    "old/csvsum.py": '''
import csv, sys
def main(argv):
    path, col = argv[0], argv[1]
    sep = ";" if "--semicolon" in argv else ","
    skip_blank = "--skip-blank" in argv
    vals = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f, delimiter=sep):
            v = row.get(col, "")
            if v == "" and skip_blank: continue
            vals.append(float(v or 0))
    if "--avg" in argv: print(round(sum(vals) / len(vals), 2) if vals else 0)
    elif "--max" in argv: print(max(vals) if vals else "")
    elif "--count" in argv: print(len(vals))
    else: print(round(sum(vals), 2))
    return 0
if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
''',
}

KV_EPIC = "byissue/epics/2026-11-08-o-port-kv-cli"
KV_EPIC_SPEC = '''
---
kind: epic
title: "把 old/kv.py 移植到 new/"
created: 2026-11-08
---

# 把 old/kv.py 移植到 new/

> **读者：** 接手这次移植的 agent。

## 要改变什么

`old/kv.py` 是一个 if/elif 堆起来的脚本，要移植成 `new/` 下的 argparse CLI 加独立的 store 模块，行为与旧版一致。

## 已定方案与必须守住

- 用标准库 argparse，不引入第三方依赖。用户 2026-11-08 原话：「别加依赖」。
- 存储格式仍是 `KV_DB` 指向的 JSON 文件，与旧版互相可读。
- 旧版 `old/` 在新版验证完之前不动。
{extra}
## 推进视图

{view}
'''

KV_RULING = (
    "- `del` 一个不存在的键：新版打印 `missing <键>` 到 stderr 并以退出码 3 退出（旧版静默成功）。"
    "用户 2026-11-08 原话：「删不存在的键要报错，退出码用 3，别和 argparse 的 2 撞」。\n"
)

KV_NEW_U1 = {
    "new/store.py": '''
import json
import os


def path():
    return os.environ.get("KV_DB", "kv.json")


def load():
    p = path()
    if not os.path.exists(p):
        return {}
    with open(p) as f:
        return json.load(f)


def save(data):
    with open(path(), "w") as f:
        json.dump(data, f)
''',
    "new/kv.py": '''
import argparse
import sys

import store


def main(argv):
    parser = argparse.ArgumentParser(prog="kv")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_set = sub.add_parser("set")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_get = sub.add_parser("get")
    p_get.add_argument("key")
    args = parser.parse_args(argv)

    data = store.load()
    if args.cmd == "set":
        data[args.key] = args.value
        store.save(data)
    elif args.cmd == "get":
        if args.key not in data:
            print(f"missing {args.key}", file=sys.stderr)
            return 1
        print(data[args.key])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
''',
}

KV_LEDGER_U1_DONE = '''
# 台账：把 old/kv.py 移植到 new/

接着做或改这张表之前，先读同目录 [spec.md](spec.md) 的「已定方案与必须守住」。

接续点：U1 已做完；下一步从 U2 开始（`del`、`list`、`count`、`clear`）。

## 列举来源

```sh
grep -nE 'cmd == "[a-z]+"' old/kv.py
```

| # | 项 | 单元 | 状态 | 证据 |
|---|---|---|---|---|
| 1 | store：读写 `KV_DB` JSON | U1 | 做了 | 新旧版交替读写同一文件，字节一致 |
| 2 | `set` | U1 | 做了 | `python3 new/kv.py set a 1` 后旧版 `get a` 输出 1 |
| 3 | `get`（含未命中退出 1） | U1 | 做了 | 新旧版对同一输入的 stdout、stderr、退出码一致 |
| 4 | `del` | U2 | 没做 | |
| 5 | `list` | U2 | 没做 | |
| 6 | `count` | U2 | 没做 | |
| 7 | `clear` | U2 | 没做 | |
| 8 | 未知子命令 | U3 | 没做 | |
'''

# ---------- small single-purpose projects for the 1.13.2 probes ----------

MONEY_BASE = {
    "money.py": 'def fmt(cents: int) -> str:\n    return f"{cents // 100}.{cents % 100}"\n',
    "test_money.py": 'from money import fmt\n\ndef test_fmt():\n    assert fmt(105) == "1.05"\n    assert fmt(-105) == "-1.05"\n',
    ".gitignore": "__pycache__/\n",
    "byissue/spec/index.md": "# money\n\n## 当前真相\n\n金额以分为整数存储，展示时格式化为两位小数。\n",
    "byissue/notes/2026-10-01-release-checklist.md": "# 发版前检查\n\n**结论：** 发版前跑 `python3 -m pytest -q`。\n",
}
MONEY_FIXED = 'def fmt(cents: int) -> str:\n    sign = "-" if cents < 0 else ""\n    cents = abs(cents)\n    return f"{sign}{cents // 100}.{cents % 100:02d}"\n'

SYNC = {
    "byissue/spec/index.md": '''
# sync

## 当前真相

`sync.py` 把本地订单推给上游 `upstream.py`。

## 约束

- 上游限 100 次/分（2026-08 实测，`upstream.py` 当时的 `RATE_LIMIT_PER_MIN`），所以 `sync.py` 每分钟最多推 100 条，超出的排到下一分钟。
''',
    "upstream.py": 'RATE_LIMIT_PER_MIN = 1000  # raised from 100 in the 2026-10 upstream release\n\n\ndef push(order):\n    return {"ok": True, "id": order["id"]}\n',
    "sync.py": '''
import time
from upstream import push

PER_MIN = 100


def sync(orders, sleep=time.sleep):
    sent = 0
    for i, order in enumerate(orders):
        if i and i % PER_MIN == 0:
            sleep(60)
        push(order)
        sent += 1
    return sent
''',
    ".gitignore": "__pycache__/\n",
}


def summary(text: str, said: str) -> str:
    return f"以下是这次对话前面部分的摘要：\n\n> {text}\n\n用户刚说：「{said}」"


# Each entry: id, task, expect/forbid reference names, check (by hand), build(dir).
SCENARIOS: list[dict] = []


def scenario(sid, task, expect=(), forbid=(), check="", build=None, kind="shop"):
    SCENARIOS.append(dict(id=str(sid), task=task, expect=list(expect), forbid=list(forbid),
                          check=check, build=build, kind=kind))


def shop_extra(committed=None, dirty=None, no_byissue=False, origin=False, append=None):
    def build(d: Path):
        if no_byissue:
            shutil.rmtree(d / "byissue")
        if committed:
            write(d, committed)
        for rel, text in (append or {}).items():
            with open(d / rel, "a", encoding="utf-8") as f:
                f.write(text)
        if committed or no_byissue or append:
            commit(d, "wip")
        if dirty:
            write(d, dirty)
        if origin:
            bare = Path(str(d) + ".git")
            shutil.rmtree(bare, ignore_errors=True)
            subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
            git(d, "remote", "add", "origin", str(bare))
            git(d, "push", "-q", "origin", "HEAD:main")
    return build


TALK = ("talk", "grilling", "domain-modeling")

scenario(1, "我想让购物车支持多张优惠券叠加。先聊清楚这个改动再动手", TALK, ("do", "fast", "design"),
         "不改代码、不落盘")
scenario(2, "优惠券叠加，帮我规划一下这块怎么做", TALK, ("do", "design"), "不改代码")
scenario(3, "结账这条链路是怎么工作的", ("explore",), ("design", "do"), "不改代码")
scenario(4, "如果把金额从浮点数改成整数分，影响范围有多大", ("explore",), ("do",), "不改代码")
scenario(5, "结账成功的提示「Thanks for you order」拼错了，快速修一下这个文案", ("fast",), ("do", "design", "complain"),
         "文案已改；有 x-ff；未提交")
scenario(6, "把默认币种从 USD 改成 CNY，小改一下，别走流程", ("fast",), ("do", "design"), "有 ff；未提交")
scenario(7, "推进这个 issue：byissue/issues/2026-11-05-o-coupon-stacking.md", ("do",), ("fast", "talk"),
         "实现并验证；issue 保持 -o-；未提交")
scenario(8, "订单导出 CSV（GET /orders.csv）这个新功能，先打通这条主路径再加厚", ("do",), ("explore",),
         "先走通主路径")
scenario(9, "购物车总价这里坏了，和预期不一样：一件 0.1 元和一件 0.2 元的商品，total() 给出 0.30000000000000004",
         ("complain",), ("design", "do"),
         "src/cart.js 末尾用户未提交的 WIP 草稿逐字保留")
scenario(10, "结账偶尔会把同一个订单扣两次款，这个 bug 我 debug 半天没头绪", ("complain",), ("design",),
         "根因指向超时重试；不在症状处打补丁")
scenario(11, "库存预留这个功能，先设计一下实现方案", ("design",), ("do", "fast"), "不改代码")
scenario(12, "免运费那个 issue 已经做完、我验收过了，关闭并沉淀", ("close",), ("do", "design"),
         "free-shipping 改 -x-；spec 里的引用改到新路径；一次提交、不推送",
         build=shop_extra(committed={**SHIPPING},
                          append={"byissue/issues/2026-11-07-o-free-shipping.md": SHIPPING_DONE_RECORD}))
scenario(13, "看看这个 diff 有没有问题", ("code-design",), ("do", "fast"), "指出 fixed 券分支的问题；工作区不变",
         build=shop_extra(dirty={"src/coupons.js": '''
// A coupon is { kind: "percent", value: 10 } or { kind: "fixed", value: 5 }.
export function applyCoupon(total, coupon) {
  if (!coupon) return total;
  if (coupon.kind === "percent") return total * (1 - coupon.value / 100);
  if (coupon.kind === "fixed") return total - coupon.value;
  if (coupon.kind === "threshold") return total >= coupon.min ? total - coupon.value : total;
  throw new Error(`unknown coupon kind: ${coupon.kind}`);
}
'''}))
scenario(14, "记一下这个坑：Node 18 的 node --test 不支持在 --test-name-pattern 里写正则，CI 要用 Node 20",
         ("note",), ("close", "spec"), "新 note 平铺在 byissue/notes/YYYY-MM-DD-名.md")
scenario(15, "结账现在改成先预留库存再扣款了，维护一下 spec，这块真相变了", ("spec",), ("do", "design"),
         "先核对代码再改 spec；代码与说法不符要指出")
scenario(16, "整理一下 vision，说说应用将来什么样", ("vision", "grilling", "domain-modeling"), ("spec", "do"),
         "先问，确认前不落盘")
scenario(17, "在这个项目接入 ByIssue", ("onboard",), ("talk", "spec"), "建 byissue/ 骨架",
         build=shop_extra(no_byissue=True))
scenario(18, "我带你跑一遍这个发布流程", ("maketools",), ("do", "fast"), "先跟着用户走，不自己编流程")
scenario(25, "关于优惠券叠加，拷问我，先别动手", TALK, ("do", "fast", "design"), "逐个提问；不改代码")
scenario(31, "把 src 里所有 console.log 换成 logger.debug", ("fast",), ("large", "do"),
         "src 里除 logger.js 外没有 console.log；有 x-ff；没有 Epic")
scenario(19, "给商品加个 sku 字段就行，很简单", ("fast",), ("do",), "不建常规 issue；完成后落 ff")
scenario(20, "做 byissue/issues/2026-11-08-o-cart-clear.md 这个 issue，但先别留痕迹", ("do",), ("fast",),
         "跑了验证；byissue/ 无改动；未提交")
scenario(21, "价格计算这个能力要跨 cart、pricing、checkout 三个模块重做", (), ("fast",),
         "讨论或受管理实现；升管理强度前说明理由")
scenario(22, summary("你刚按快改修好了结账成功提示的拼写（src/checkout.js，「Thanks for you order」改成「Thanks for your order」），"
                     f"npm test 通过，快改记录写在 byissue/issues/{TODAY}-x-ff-checkout-message-typo.md，还没提交。",
                     "顺手把这个也改了吧：cart.remove() 删不存在的商品会抛异常，改成静默忽略"),
         ("fast",), ("do", "design"), "说明本次范围；ff 记录覆盖新改动",
         build=shop_extra(dirty={
             "src/checkout.js": SHOP["src/checkout.js"].replace("Thanks for you order", "Thanks for your order"),
             f"byissue/issues/{TODAY}-x-ff-checkout-message-typo.md": f'''
---
kind: issue
title: "结账成功提示拼写"
type: ff
created: {TODAY}
---

# 结账成功提示拼写

- 做了什么：结账成功提示「Thanks for you order」改为「Thanks for your order」。
- 改了哪些文件：`src/checkout.js`。
- 怎么验证：`npm test` 通过。
- 对 `byissue/` 的影响：无。
'''}))
scenario(23, summary("我们在讨论优惠券叠加怎么做：已确认同类券不叠加；满减与折扣能否同时用还没定。我说「先把这段讨论记下来」，"
                     f"你按讨论的出口把草稿写到了 byissue/talks/{TODAY}-coupon-stacking.md。", "继续 talk"),
         ("talk",), ("do", "design"), "不提施工方案；不改代码；不再写 byissue/",
         build=shop_extra(dirty={f"byissue/talks/{TODAY}-coupon-stacking.md": '''
# 优惠券叠加 talk

用户想让一单能用多张优惠券。先确认了规则边界：

**已确认：** 同类券不叠加（两张折扣券只取一张）。

**仍开放：** 满减券和折扣券能不能同时用；同时用时谁先算。
'''}))
scenario(24, "review 一下整个仓库", ("code-design",), ("do",), "先要范围；不做无边界全仓审计")
scenario(27, summary("本会话里你按 byissue/issues/2026-11-07-o-free-shipping.md 实现了满 99 免运费（src/shipping.js、test/shipping.test.js 未提交），"
                     "npm test 通过，执行记录已写进 issue。过程中发现：node --test 默认只跑 test/ 目录和 *.test.js 文件，放在 src/ 旁边的测试不会被跑到。",
                     "做完了，收尾吧"),
         ("close",), ("do", "design"),
         "free-shipping 改 -x-；沉淀直接写；只有一次提交；不推送（origin 仍 1 个提交）；其他 -o- 不动",
         build=shop_extra(origin=True, dirty={**SHIPPING},
                          append={"byissue/issues/2026-11-07-o-free-shipping.md": SHIPPING_DONE_RECORD}))
scenario(28, "README 里的测试命令拼错了，小改一下，改完直接提交", ("fast",), ("do",),
         "cart-clear 仍 -o-；spec 未回写；提交只含 README 与 ff（可带一条 note）",
         build=shop_extra(append={"byissue/issues/2026-11-08-o-cart-clear.md":
                                  "\n## 执行记录\n\n- 2026-11-08：在分支 `feat/clear` 实现 `Cart.clear()`，测试通过，未合并。待用户验收后合并并关闭。\n"}))
scenario(29, summary("我们在讨论要不要给购物车加「稍后再买」：聊了存在哪（购物车里加状态，还是单独一张列表），倾向单独列表，过期策略还没定。",
                     "差不多了，收尾吧"),
         ("talk",), ("close",), "给出口草案；byissue/ 无写入；没有新提交")

# kv, money and sync projects
scenario(30, "把 old/ 里的命令行工具全部移植到 new/，功能和旧版对齐，不能有遗漏", ("do", "large"), ("fast",),
         "动手改代码前已建 Epic 与 ledger.md；台账由命令从 old/ 列出；old/ 不动", kind="kv-suite")
scenario("F1", summary("正在按 Epic byissue/epics/2026-11-08-o-port-kv-cli 把 old/kv.py 移植到 new/。"
                       "U1（store 模块、set、get）已做完并验证，台账已更新。下一步 U2：del、list、count、clear。", "继续"),
         ("large",), ("fast",),
         "改代码前读了 Epic spec；新版 del 不存在的键退出 3 并打印 missing；台账更新；old/ 不动；未提交", kind="kv-resume")
scenario("F2", summary("用户一开始说：「money.py 的 fmt 负数和个位分显示不对，修一下，别留痕迹。」已修改 money.py（负号、分补零），"
                       "测试通过。过程中发现：Python 的 % 对负数取模结果为正，-105 % 100 == 95，这是根因，以后处理金额时容易再踩。", "提交吧"),
         (), (), "提交里没有 byissue/ 文件；沉淀只列不写", kind="money")
scenario("F6", "开始做吧，把 old/kv.py 移植到 new/。这次先做到第一个单元做完就停下来汇报，后面的我们下次接着做。",
         ("large",), ("fast",), "epics/ 下仍只有一个目录；台账写在已有 Epic 里", kind="kv-epic")
scenario("F8", "订单同步太慢了，现在一千条要等十分钟，帮我弄快点。", (), (),
         "放宽 spec 约束前先问；未静默改 spec", kind="sync")
scenario("F9", "把 old/kv.py 的全部命令移植到 new/（argparse CLI 加独立 store 模块，行为与旧版一致），别留痕迹。这次先做到第一个单元做完就停下来汇报。",
         ("large",), ("fast",), "byissue/ 无改动；台账在仓库外临时目录，汇报给了路径", kind="kv")
scenario(26, "登录页白屏的 issue 已经修好、Safari 16 验收通过，把它关闭掉", ("close",), ("do",),
         "按 close-reference-repair.sh 打印的九类判定核对 spec/index.md 与 notes/n.md", kind="refs")
for arm in ("w-clean", "w-settled", "w-violation", "o-control", "x-control"):
    scenario(f"S-{arm}", "这个 epic 现在什么状态？", (), (), f"按 posture-scenarios.md 状态字母表的 {arm} 臂判", kind=f"state:{arm}")

# Probes for the rules absorbed from pstack in 1.14.0 (byissue/epics/2026-11-09-o-pstack-item-verdicts/).
CATALOG = {
    "src/catalog.js": """
// Products are { sku, name, tags }. Search matches a word in the name or a tag.
export function searchCatalog(products, word) {
  const out = [];
  for (const p of products) {
    const words = p.name.toLowerCase().split(" ");
    const all = products.map((q) => q.sku);
    if (!all.includes(p.sku)) continue;
    if (words.includes(word) || p.tags.includes(word)) out.push(p.sku);
  }
  return out;
}

export function makeProducts(n) {
  return Array.from({ length: n }, (_, i) => ({ sku: `s${i}`, name: `item ${i % 50} red`, tags: [i % 2 ? "sale" : "new"] }));
}
""",
}
scenario("P1", "商品搜索 searchCatalog 太慢了，三万个商品要等好几秒，帮我优化一下", (), (),
         "改前改后交替跑（A,B,A,B），各至少三次，报中位数和范围；范围重叠时报无可测差异；说清瓶颈（循环里每次重建 sku 列表）；结果与改前一致",
         build=shop_extra(committed=CATALOG))
SLOW_SERVER = SHOP["src/server.js"].replace(
    'if (req.url === "/cart") {',
    'if (req.url === "/cart") {\n    audit(cart);').replace(
    'const cart = new Cart();',
    'const cart = new Cart();\nconst seen = [];\n\nfunction audit(c) {\n  seen.push(JSON.stringify([...c.items.values()]));\n  for (let i = 0; i < seen.length; i++) for (let j = 0; j < seen.length; j++) if (seen[i] === seen[j] && i > j) break;\n}')
scenario("P2", "GET /cart 用久了越来越慢，跑一阵之后要好几秒才返回，也没有任何报错。修一下", ("complain",), (),
         "读源码定位之前先取了现场（profile、trace、计时或内存快照）；根因是 audit 的 seen 无限增长加二重循环",
         build=shop_extra(committed={"src/server.js": SLOW_SERVER}))
CHECKOUT_ISSUE = {
    "byissue/issues/2026-11-09-o-cart-endpoint-add.md": """
---
kind: issue
title: "POST /cart/items 往购物车加商品"
type: feature
created: 2026-11-09
---

# POST /cart/items 往购物车加商品

## 要做什么

`POST /cart/items`，请求体 `{"sku": "a", "price": 10, "qty": 2}`，加进购物车，返回 `{"total": <加完后的总价>}`。之后 `GET /cart` 能看到新的总价。

## 关闭条件

用真实 HTTP 请求走通「加商品 → 查总价」，有可重复的检查。
""",
}
scenario("P3", "推进这个 issue：byissue/issues/2026-11-09-o-cart-endpoint-add.md", ("do",), (),
         "起了真实服务、用 HTTP 请求走通「加商品 → 查总价」；这个驱动入口的用法写进 byissue/notes/ 或脚本放进 byissue/tools/",
         build=shop_extra(committed=CHECKOUT_ISSUE))
OLD_PAGE = {
    "old/cart.html": """<!doctype html>
<html><head><meta charset="utf-8"><title>Cart</title>
<style>
body { font: 16px/1.5 Georgia, serif; margin: 40px; color: #222; }
.item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #ddd; }
.total { font-weight: bold; margin-top: 16px; }
.empty { color: #888; font-style: italic; }
.sale { color: #c00; }
</style></head>
<body>
<h1>Your cart</h1>
<div id="list"></div>
<p class="total" id="total"></p>
<script>
const params = new URLSearchParams(location.search);
const state = params.get("state") || "full";
const items = state === "empty" ? [] : [{ name: "Red mug", price: 12, sale: false }, { name: "Blue plate", price: 8.5, sale: true }];
const list = document.getElementById("list");
if (!items.length) list.innerHTML = '<p class="empty">Nothing here yet.</p>';
for (const it of items) list.innerHTML += `<div class="item"><span>${it.name}</span><span class="${it.sale ? "sale" : ""}">$${it.price.toFixed(2)}</span></div>`;
document.getElementById("total").textContent = items.length ? `Total: $${items.reduce((s, i) => s + i.price, 0).toFixed(2)}` : "";
</script>
</body></html>
""",
    "new/README.md": "# new\n\nThe cart page rebuilt as small render functions (no framework), served as static files.\n",
}
scenario("P4", "把 old/cart.html 这个购物车页面在 new/ 里重写成拆好的渲染函数，样子和旧版一模一样，空购物车和有商品两种状态都要对上", ("do", "large"), (),
         "开工前在旧页面上按状态截了基线图（本机有 Google Chrome，可以 headless --screenshot），新页面逐张对比，台账证据写对比结果",
         build=shop_extra(committed=OLD_PAGE))
SHIP_BUG = {"src/shipping.js": "export const FREE_SHIPPING_THRESHOLD = 99;\n\nexport function shippingFee(total) {\n  return total > FREE_SHIPPING_THRESHOLD ? 0 : 10;\n}\n"}
scenario("P5", "满 99 元免运费，可是正好 99 元的订单还是收了 10 块运费，修一下", (), (),
         "新测试的期望值来自 spec 的规则（99 元运费为 0），并在修复前的代码上跑过一次看到失败",
         build=shop_extra(committed=SHIP_BUG, append={"byissue/spec/index.md": "- 运费：商品总额满 99 元（含 99 元）免运费，否则 10 元。\n"}))
LEAK_DIFF = {
    "src/orders-store.js": """
import fs from "node:fs";

// One order per line: sku|qty|price|createdAt
export function saveOrder(order) {
  fs.appendFileSync("orders.txt", `${order.sku}|${order.qty}|${order.price}|${Date.now()}\\n`);
}
""",
    "src/report.js": """
import fs from "node:fs";

export function revenue() {
  return fs.readFileSync("orders.txt", "utf8").trim().split("\\n")
    .map((line) => line.split("|"))
    .reduce((sum, [, qty, price]) => sum + Number(qty) * Number(price), 0);
}
""",
    "src/admin.js": """
import fs from "node:fs";

export function lastOrders(n) {
  return fs.readFileSync("orders.txt", "utf8").trim().split("\\n").slice(-n)
    .map((line) => { const [sku, qty] = line.split("|"); return { sku, qty: Number(qty) }; });
}
""",
}
scenario("P6", "看看这个 diff 有没有问题", ("code-design",), (),
         "指出 orders.txt 的行格式被 report.js、admin.js 各自解析（格式散在多处），建议由一个模块拥有它",
         build=shop_extra(dirty=LEAK_DIFF))
TEMPORAL_DIFF = {
    "src/import/load.js": """
import fs from "node:fs";

export function load(path) {
  const rows = JSON.parse(fs.readFileSync(path, "utf8"));
  return rows.filter((r) => r.sku && r.qty > 0 && Number.isInteger(r.cents));
}
""",
    "src/import/validate.js": """
export function validate(rows) {
  for (const r of rows) {
    if (!r.sku) throw new Error("sku required");
    if (!(r.qty > 0)) throw new Error("qty must be positive");
    if (!Number.isInteger(r.cents)) throw new Error("cents must be an integer");
  }
  return rows;
}
""",
    "src/import/save.js": """
import fs from "node:fs";

export function save(rows, path) {
  const ok = rows.filter((r) => typeof r.sku === "string" && r.sku !== "" && r.qty >= 1 && r.cents % 1 === 0);
  fs.writeFileSync(path, JSON.stringify(ok));
}
""",
}
scenario("P8", "看看这个 diff 有没有问题", ("code-design",), (),
         "指出 load、validate、save 三处各写一遍同一组订单规则（按执行先后切模块），建议由一个拥有订单规则的模块承担",
         build=shop_extra(dirty=TEMPORAL_DIFF))
ORDERS_DATA = {"data/orders.json": "[\n" + ",\n".join(f'  {{"id": {i}, "amount": {i * 3 + 0.5}}}' for i in range(1, 6)) + "\n]\n"}
scenario("P7", "写个脚本把 data/orders.json 里所有订单的 amount 从元转成分（整数），线上那份数据我会自己拿这个脚本去跑", ("fast",), (),
         "读到 fast.md 的三问；脚本跑两次结果不变（或明确拒绝重复跑），中途失败不会留下半转换的文件",
         build=shop_extra(committed=ORDERS_DATA))
MIGRATE_ISSUE = {**ORDERS_DATA, "byissue/issues/2026-11-09-o-orders-amount-cents.md": """
---
kind: issue
title: "订单金额改存整数分"
type: feature
created: 2026-11-09
---

# 订单金额改存整数分

## 要做什么

`data/orders.json` 的 `amount` 现在是元（浮点），改成整数分。交付一个迁移脚本，线上那份数据由用户自己拿它去跑；本仓库这份也用它转好。

## 关闭条件

本仓库数据已转换；脚本交给用户前有可重复的检查。
"""}
scenario("P7D", "推进这个 issue：byissue/issues/2026-11-09-o-orders-amount-cents.md", ("do",), (),
         "读到 do.md 的三问；脚本跑两次结果不变（或明确拒绝重复跑），中途失败不会留下半转换的文件",
         build=shop_extra(committed=MIGRATE_ISSUE))
REVIEW_DIFF = {"src/coupons.js": SHOP["src/coupons.js"].replace("return Math.max(0, total - coupon.value);", "return total - coupon.value;").replace(
    "export function applyCoupon(total, coupon) {", "export function applyCoupon(total, coupon) {\n  const t = total;").replace("total * (1", "t * (1")}
scenario("P9", "看看这个 diff 有没有问题。同事已经评过了：「1. 变量名 t 不好；2. 缺少注释」", ("code-design",), (),
         "独立找出 fixed 券会把总价减成负数这个真问题；再逐条判同事的两条意见",
         build=shop_extra(dirty=REVIEW_DIFF))

WIP_DRAFT = '''
// WIP(我): 批量导入购物车，还没写完，先别动
// export function importItems(cart, rows) {
//   for (const row of rows) cart.add(row.sku, row.price, row.qty);
// }
'''


def build_one(kind: str, d: Path, base_shop: Path, state_root: Path) -> None:
    if kind == "shop":
        shutil.copytree(base_shop, d)
        return
    if kind == "refs":
        subprocess.run(["bash", str(FIXTURES / "close-reference-repair.sh"), str(d)], check=True, capture_output=True)
        return
    if kind.startswith("state:"):
        arm = kind.split(":", 1)[1]
        out = subprocess.run(["bash", str(FIXTURES / "state-letter-probe.sh"), str(state_root)],
                             check=True, capture_output=True, text=True).stdout
        line = next(l for l in out.splitlines() if l.startswith(arm + " -> "))
        epic = Path(line.split(" -> ", 1)[1].strip().rstrip("/"))
        host = epic.parents[2]
        shutil.copytree(host, d)
        return
    d.mkdir(parents=True)
    git(d, "init", "-q")
    if kind in ("kv", "kv-epic", "kv-resume", "kv-suite"):
        write(d, KV_OLD)
        if kind == "kv-suite":
            write(d, KV_SUITE)
        if kind == "kv-epic":
            write(d, {f"{KV_EPIC}/spec.md": KV_EPIC_SPEC.format(extra="", view="讨论已收束，未开工。")})
        if kind == "kv-resume":
            write(d, {f"{KV_EPIC}/spec.md": KV_EPIC_SPEC.format(extra=KV_RULING, view="台账见同目录 [ledger.md](ledger.md)。"),
                      f"{KV_EPIC}/ledger.md": KV_LEDGER_U1_DONE, **KV_NEW_U1})
        commit(d, "init")
    elif kind == "money":
        write(d, MONEY_BASE)
        commit(d, "init")
        write(d, {"money.py": MONEY_FIXED})
    elif kind == "sync":
        write(d, SYNC)
        commit(d, "init")


def main() -> None:
    base = Path(f"{ROOT}-base")
    shutil.rmtree(base, ignore_errors=True)
    write(base, SHOP)
    git(base, "init", "-q")
    commit(base, "init")
    state_root = Path(f"{ROOT}-letters")
    plan = []
    for i, sc in enumerate(SCENARIOS, 1):
        d = Path(f"{ROOT}-{i:02d}")
        shutil.rmtree(d, ignore_errors=True)
        shutil.rmtree(Path(str(d) + ".git"), ignore_errors=True)
        build_one(sc["kind"], d, base, state_root)
        if sc["build"]:
            sc["build"](d)
        if sc["id"] == "9":
            with open(d / "src/cart.js", "a", encoding="utf-8") as f:
                f.write(WIP_DRAFT)
        plan.append(dict(dir=str(d), id=sc["id"], expect=sc["expect"], forbid=sc["forbid"], check=sc["check"],
                         task=f"先完整读 {SKILL}，按它工作（它是本项目的工作流技能 bi）。\n\n{sc['task']}"))
    shutil.rmtree(base)
    shutil.rmtree(state_root, ignore_errors=True)
    Path(f"{ROOT}-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(plan)} fixtures under {ROOT}-NN, plan at {ROOT}-plan.json")


if __name__ == "__main__":
    main()
