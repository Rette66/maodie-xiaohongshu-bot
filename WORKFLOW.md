# 耄臲账号运营工作流

```mermaid
flowchart TD
    %% ===== 素材采集 =====
    subgraph采集阶段["📥 素材采集"]
        CollectStart[配置采集任务]
        CollectStart --> SourceType{来源}
        SourceType -->|B站视频| BiliAPI[调用B站API获取cid]
        BiliAPI --> BiliDown[requests下载视频]
        BiliDown --> FFmpegCap[ffmpeg每2秒截1帧]
        SourceType -->|小红书| XHSSearch[小红书MCP搜索]
        XHSSearch --> XHSDown[批量下载图片]
        SourceType -->|表情网| EmojiCrawl[Playwright爬取]
        EmojiCrawl --> EmojiDown[下载GIF/图片]
        FFmpegCap --> RawSave[(原始素材)]
        XHSDown --> RawSave
        EmojiDown --> RawSave
    end

    %% ===== 素材筛选 =====
    subgraph筛选阶段["🔍 AI筛选"]
        RawSave --> BasicFilter[基础过滤：尺寸/去重/格式]
        BasicFilter --> CodexScreen[Codex逐张识别耄臲]
        CodexScreen --> IsMaodie{是圆头耄臲?}
        IsMaodie -->|否| Discard[丢弃]
        IsMaodie -->|是| Approve[(入库 approved/)]
    end

    %% ===== 发布准备 =====
    subgraph发布准备["📝 发布准备"]
        Approve --> DBUpdate[更新 image_database.json]
        DBUpdate --> ReadDB[读取 use_count=0 的图片]
        ReadDB --> GenContent[ContentGenerator 生成文案]
        GenContent --> GenTitle[生成标题]
        GenContent --> GenBody[生成正文]
        GenContent --> GenTags[生成标签]
    end

    %% ===== 定时发布 =====
    subgraph定时发布["⏰ 定时发布"]
        GenTags --> Enqueue[任务入队]
        Enqueue --> Scheduler{定时触发}
        Scheduler -->|高峰期| PeakHours[高峰时段发布]
        Scheduler -->|低峰| OffPeak[低峰时段发布]
        PeakHours --> XHSMCP[调用 xhs-mcp 发布]
        OffPeak --> XHSMCP
    end

    %% ===== 学习反馈 =====
    subgraph学习反馈["🧠 学习反馈"]
        XHSMCP --> UpdateCount[更新 use_count+1]
        UpdateCount --> CollectStats[收集表现数据]
        CollectStats --> Learning[AdaptiveLearning 分析]
        Learning --> Optimize[优化策略参数]
        Optimize -->|下次| DecisionEngine
    end

    %% ===== 决策回路 =====
    Discard --> ManualReview{人工复核}
    ManualReview -->|确认丢弃| End1([结束])
    ManualReview -->|重新入库| Approve

    %% 样式
    classDef采集 fill:#e1f5fe,stroke:#01579b
    classDef筛选 fill:#f3e5f5,stroke:#4a148c
    classDef发布 fill:#e8f5e9,stroke:#1b5e20
    classDef学习 fill:#fff3e0,stroke:#e65100

    class CollectStart,BiliAPI,BiliDown,FFmpegCap,XHSSearch,XHSDown,EmojiCrawl,EmojiDown,RawSave采集
    class BasicFilter,CodexScreen,IsMaodie,Discard,Approve筛选
    class DBUpdate,ReadDB,GenContent,GenTitle,GenBody,GenTags,Enqueue,Scheduler,PeakHours,OffPeak,XHSMCP发布
    class UpdateCount,CollectStats,Learning,Optimize,DecisionEngine学习
```

## 流程说明

### 1. 素材采集

| 来源 | 方法 | 说明 |
|------|------|------|
| **B站视频** | requests API + ffmpeg | 通过B站API获取cid→播放URL→下载→ffmpeg每2秒截1帧 |
| **小红书** | xhs-mcp | 搜索关键词，批量下载笔记图片 |
| **爱给网** | Playwright | 爬取表情包网站 |

### 2. AI筛选

- **基础过滤**：尺寸 < 200x200 删除，去重，校验格式
- **Codex识别**：逐张查看图片，判断是否为"圆头英短橘猫 + 死鱼眼表情"
- **通过**：移入 `data/approved/`，更新数据库
- **未通过**：标记丢弃，可人工复核

### 3. 发布准备

- `image_database.json` 中 `use_count == 0` 的图片进入待发队列
- `ContentGenerator` 基于"猫的逻辑"生成文案
- 标题/正文/标签都有固定风格

### 4. 定时发布

- `IntelligentScheduler` 管理任务队列
- 分散在全天高峰时段（7-8点、12-13点、18-22点）
- 调用 `xhs-mcp /api/v1/publish` 实际发布到小红书
- 失败自动重试（最多3次）

### 5. 学习反馈

- 发布后记录表现数据（点赞、收藏、评论）
- `AdaptiveLearning` 分析各主题/时段效果
- 动态调整决策参数

## 关键文件

```
maodie-xiaohongshu-bot/
├── smart_agent.py          # SmartXHSAgent 主控
├── ai/
│   ├── content_generator.py   # 内容生成
│   ├── decision_engine.py     # 决策引擎
│   └── learning_system.py     # 自适应学习
├── image_database.json     # 素材元数据
├── images/maodie/           # 已采集的耄臲图 (29张)
├── images/crawled/          # 爬取的原始图
└── xhs-mcp (独立进程)       # 小红书API代理 (:18060)
```