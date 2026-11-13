# 并行启动 `subagent` 与重建 `cwd` 目录会触发伪装成缺二进制的 `spawn node ENOENT`

> **读者：** 在本仓库用 `subagent` 跑行为评测或探针的人——准备 `/tmp` 夹具目录和启动 `subagent` 必须分两轮调用。

**结论：** Node.js / libuv 的 `uv_spawn` 在 `options.cwd` 目录不存在时，抛出的错误是 `spawn <executable_path> ENOENT`（例如 `spawn /Users/.../node ENOENT`），表面看起来像 `node` 可执行文件丢失，真实原因是 `subagent` 启动瞬间 `cwd` 目录尚不存在。

**何时用：** 按 `tools/posture-scenarios.md` 或 `tools/prompt-review.md` 在 `/tmp/` 下搭建临时仓库夹具并起 `subagent` 跑行为探针时。

**细节与证据：**
- 2026-10-29 会话中，在同一轮工具调用里并行发起了 `bash`（执行 `rm -rf /tmp/bi-partial-commit-probe && mkdir -p /tmp/bi-partial-commit-probe ...`）与 `subagent(cwd: "/tmp/bi-partial-commit-probe")`。
- `subagent`（`sub_f18120cd612e`）在 `rm -rf` 刚删掉目录、`mkdir -p` 尚未跑完的毫秒级窗口内执行 `spawn`，当场失败报错：`spawn /Users/zijie/.local/share/mise/installs/node/24.22.1/bin/node ENOENT`；而该路径下的 `node` 二进制实际完好存在，下一轮目录就绪后用完全相同的参数重启 `sub_b7e4802c5216` 即一次成功。
- 规避方式：先在单独一轮 `bash` 调用中完成 `/tmp` 夹具目录的清理、`mkdir` 与 `git init`，等该工具返回确认目录就绪后，下一轮再并发调用 `subagent`。

**相关：** `tools/posture-scenarios.md`；`byissue/issues/2026-10-29-x-ff-sediment-decoupled-from-close-and-shortcut-plugged.md`。
