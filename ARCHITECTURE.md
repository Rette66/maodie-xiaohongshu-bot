# 小红书耄臲账号运营系统架构

```mermaid
C4Container
    title 耄臲账号运营系统架构

    Person(user, "运营者", "配置任务、审核发布内容、查看报表")

    System_Boundary(xhs_bot, "maodie-xiaohongshu-bot") {
        Container(smart_agent, "SmartXHSAgent", "Python asyncio", "智能主控，协调内容生成、调度、执行")
        Container(content_gen, "ContentGenerator", "Python", "基于主题模板生成标题、正文、标签")
        Container(decision_eng, "DecisionEngine", "Python", "数据驱动决策，自适应调整互动策略")
        Container(learning, "AdaptiveLearning", "Python", "分析表现数据，持续优化策略")
        Container(scheduler, "IntelligentScheduler", "Python", "任务队列管理、定时调度、自动重试")
        Container(xhs_mcp, "小红书MCP客户端", "HTTP API", "调用xhs-mcp服务发布笔记到小红书")
    }

    System_Ext(xhs_mcp_server, "xhs-mcp (Go)", "小红书API代理服务 (:18060)", "提供笔记发布、图片上传、搜索等API")
    System_Ext(xhs_platform, "小红书平台", "第三方平台", "实际内容发布和展示")
    System_Ext(maidie_collector, "maidie-collector", "Python + Playwright", "采集耄臲素材：B站视频截帧、小红书图片、爱给网爬虫")

    System_Ext(bilibili_api, "B站视频API", "数据来源", "视频cid、播放URL下载")
    System_Ext(xhs_search, "小红书搜索", "数据来源", "素材线索和图片URL")
    System_Ext(aigei, "爱给网/求表情网", "数据来源", "表情包素材")

    Rel(user, smart_agent, "配置任务")
    Rel(smart_agent, content_gen, "请求生成内容")
    Rel(smart_agent, decision_eng, "请求决策")
    Rel(smart_agent, scheduler, "任务入队/出队")
    Rel(scheduler, xhs_mcp, "调用发布API")
    Rel(xhs_mcp, xhs_mcp_server, "HTTP请求")
    Rel(xhs_mcp_server, xhs_platform, "笔记发布/互动")

    Rel(maidie_collector, bilibili_api, "采集视频数据")
    Rel(maidie_collector, xhs_search, "读取素材线索")
    Rel(maidie_collector, aigei, "爬取表情包")
    Rel(maidie_collector, smart_agent, "素材存入 image_database.json")

    Rel(decision_eng, learning, "记录决策结果")
    Rel(learning, decision_eng, "优化决策参数")
    Rel(smart_agent, learning, "反馈表现数据")
```

## 组件说明

| 组件 | 技术栈 | 职责 |
|------|--------|------|
| **SmartXHSAgent** | Python asyncio | 智能主控，协调各模块工作 |
| **ContentGenerator** | Python 模板引擎 | 生成标题、正文、标签 |
| **DecisionEngine** | Python | 决策是否互动、何时发布 |
| **AdaptiveLearning** | Python 数据分析 | 分析表现，优化策略 |
| **IntelligentScheduler** | Python | 任务队列、定时触发、自动重试 |
| **xhs-mcp** | HTTP API 客户端 | 调用 xhs-mcp 服务发布笔记 |
| **xhs-mcp (Go)** | Go 独立服务 | 绕过反爬，直接操作小红书API |
| **maidie-collector** | Python + Playwright | 采集耄臲素材（与本项目独立） |

## 数据流向

```
素材采集 (maidie-collector)
    ├── B站视频API → requests下载 → ffmpeg截帧
    ├── 小红书搜索 → xhs-mcp下载图片
    └── 爱给网/求表情网 → Playwright爬取
              ↓
    image_database.json (素材库)
              ↓
    SmartXHSAgent (读取待发图片)
              ↓
    ContentGenerator (生成标题/正文/标签)
              ↓
    IntelligentScheduler (定时发布)
              ↓
    xhs-mcp → 小红书平台 (发布笔记)
              ↓
    AdaptiveLearning (记录表现，优化策略)
```