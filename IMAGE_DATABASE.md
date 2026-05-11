# 🗃️ 图片数据库

## 概述

维护圆头耄臝的表情包素材库，每张图都有标签，支持按场景/情绪/表情选图。

## 文件

```
image_database.py    # 数据库管理代码
image_database.json  # 数据库文件（自动生成）
init_database.py     # 初始化脚本
```

## 标签维度

| 维度 | 可选值 |
|------|--------|
| expression | serious, deadpan, happy, angry, sleepy, crazy, curious, cute, surprised, disdainful |
| head_shape | extra_round, round, wide, normal |
| eye_color | amber, golden, orange, green, blue |
| pose | front_face, side, looking_up, looking_down, lying, sleeping, playing |
| mood | calm, funny, scary, cute, sleepy, crazy, meta |
| lighting | natural, dramatic, dark, bright, soft |
| background | white, dark, blurry, solid_color, gradient |
| usage | daily_post, reaction, meme, reply, night_post, crazy_post, pure_meme |
| distinctiveness | high, medium, low |

## 使用方式

### Python API

```python
from image_database import ImageDatabase

db = ImageDatabase()

# 按条件选图
entry = db.select_image(
    mood="crazy",
    usage="night_post",
    min_distinctiveness="high"
)
if entry:
    print(f"选中: {entry.filename}, 路径: {entry.relative_path}")

# 添加新图片
db.add_image(
    filepath="images/new_cat.jpg",
    generation_prompt="描述...",
    source="ai_generated",
    tags={
        "expression": "crazy",
        "head_shape": "extra_round",
        "mood": "crazy",
        "usage": ["night_post", "crazy_post"],
        "distinctiveness": "high",
    }
)

# 查看统计
stats = db.stats()
print(f"总图片: {stats['total_images']}")
```

### CLI

```bash
# 查看统计
python image_database.py stats

# 选图测试
python image_database.py select --mood crazy --usage night_post

# 导出待标注列表
python image_database.py export
```

### CatContentGenerator 集成

`ai/cat_content_generator.py` 已自动接入数据库：
- 每次生成内容时从数据库选图
- 优先选高辨识度图
- 记录使用次数，避免同一张图被重复使用

## 工作流程

1. **添加图片** → 放入 `images/maodie/` 或 `images/maodie-generated/`
2. **打标签** → 修改 `image_database.json` 或调用 `db.add_image()`
3. **生成内容** → `CatContentGenerator.generate()` 自动按标签选图

## 未来方向

- [ ] LLM 自动打标签（上传图片 → AI 分析 → 自动填入标签）
- [ ] 网页管理界面
- [ ] 按表情/场景批量生图
