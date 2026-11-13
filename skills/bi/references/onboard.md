# 接入 ByIssue

接入只初始化新工作入口，不替用户填写业务目标，也不整理项目历史。

## 行动

优先运行技能包里的脚本。脚本路径从已安装的 `bi` 技能目录解析：

```bash
python3 <bi-skill>/scripts/init_byissue.py --project .
```

脚本会创建或保留：

```text
byissue/
├── work/
└── memory/
```

已有文件和旧目录保持原样。脚本不覆盖内容，不创建空的业务文档，也不替用户生成 Vision；用户明确整理方向时再按 [memory-direction](memory-direction.md) 建立 `byissue/vision/index.md`。

初始化后确认两个目录存在，并告诉用户哪些路径是新建的、哪些已存在而保留。下一步按用户意图进入澄清、改变、理解与审查或记忆与方向。

## 边界

接入可以观察 README、代码、配置、测试和 git，得到的只能作为后续调查线索。业务目标、路线图、长期取舍和明确不做什么，需要用户确认或已有可信记录作为依据。
