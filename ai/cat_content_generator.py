"""
耄臲Official - 猫的内容生成器 V3
核心思想：猫发什么？表情包为主，偶尔发疯

重要特征：圆头耄臲 = 耳朵贴在头上，整个脸是圆的
生成图片时必须强调这个特征
"""
import random
import sys
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# 尝试导入图片数据库
try:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from image_database import ImageDatabase
    HAS_DB = True
except ImportError:
    HAS_DB = False

from configs.personality_loader import get_cat_config


# 圆头耄臲的核心特征描述（用于AI生图）
ROUND_HEAD_CAT_PROMPT = "圆头英短猫, 耳朵紧贴头部, 脑袋非常圆, 脸是完整的圆形, 无明显耳朵凸起"


@dataclass
class CatContent:
    """猫的内容"""
    content_type: str       # 表情包/纯文字/突然发疯
    text: str              # 文字内容
    images: List[str]      # 图片路径
    tags: List[str]        # 标签
    post_time: str         # 发布时间
    mood: str              # 猫的心情
    image_id: Optional[str] = None  # 图片数据库ID


class CatContentGenerator:
    """
    猫的内容生成器 V3

    重要：所有圆头耄臲的图片都必须有这些特征：
    - 耳朵紧贴头部（不竖起来）
    - 脑袋非常圆，像一个完整的圆
    - 脸是圆的，没有耳朵凸出
    - 虎斑橘色猫

    猫会发什么？（从配置读取）
    - 表情包为主（默认80%）
    - 纯文字（默认10%）
    - 突然发疯（默认10%）
    """

    # 内容类型 → 图片选择偏好
    CONTENT_IMAGE_PREFERENCES = {
        "表情包": {"mood": None},
        "纯文字": {"mood": "calm"},
        "突然发疯": {"mood": "crazy"},
    }

    def __init__(self, image_folder: str = "images/maodie"):
        self.image_folder = Path(image_folder)
        self.available_images = self._load_images()

        self.image_db = None
        if HAS_DB:
            try:
                db_path = Path(__file__).parent.parent / "image_database.json"
                if db_path.exists():
                    self.image_db = ImageDatabase(str(db_path), "images")
                    print(f"🗃️ 图片数据库已加载: {len(self.image_db.entries)} 张图片")
            except Exception as e:
                print(f"⚠️ 图片数据库加载失败: {e}")
                self.image_db = None

    def _load_images(self) -> List[str]:
        if not self.image_folder.exists():
            return []
        images = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp"]:
            images.extend(self.image_folder.glob(ext))
        return [str(img) for img in images]

    def _select_image_from_db(self, content_type: str, mood: str) -> tuple:
        """从图片数据库选择图片"""
        if not self.image_db or not self.image_db.entries:
            return self._fallback_image_select(), None

        try:
            pref = self.CONTENT_IMAGE_PREFERENCES.get(content_type, {})
            select_kwargs = {}
            if pref.get("mood"):
                select_kwargs["mood"] = pref["mood"]
            if content_type == "表情包":
                select_kwargs["min_distinctiveness"] = "medium"
            select_kwargs["usage"] = "daily_post"

            entry = self.image_db.select_image(**select_kwargs)
            if entry:
                img_root = Path(__file__).parent.parent / "images"
                img_path = str(img_root / entry.relative_path)
                return [img_path], entry.id
        except Exception as e:
            print(f"⚠️ 数据库选图失败: {e}")

        return self._fallback_image_select(), None

    def _fallback_image_select(self) -> List[str]:
        if not self.available_images:
            return []
        num = random.randint(1, min(3, len(self.available_images)))
        return random.sample(self.available_images, num)

    def generate(self, mood: str = None) -> CatContent:
        hour = datetime.now().hour

        if mood is None:
            mood = self._get_mood(hour)

        content_type = self._get_content_type(hour, mood)

        if content_type == "表情包":
            text, images, img_id = self._generate_meme_content(mood, content_type)
        elif content_type == "纯文字":
            text, images, img_id = self._generate_text_content(mood, content_type)
        else:
            text, images, img_id = self._generate_crazy_content(mood, content_type)

        tags = self._generate_tags(mood)

        return CatContent(
            content_type=content_type,
            text=text,
            images=images,
            tags=tags,
            post_time=datetime.now().strftime("%H:%M"),
            mood=mood,
            image_id=img_id
        )

    def _get_mood(self, hour: int) -> str:
        if 2 <= hour < 4:
            return random.choice(["crazy", "crazy", "mad"])
        elif hour >= 23 or hour < 6:
            return random.choice(["active", "playful", "hungry"])
        elif 8 <= hour < 18:
            return random.choice(["sleepy", "lazy", "ignoring"])
        else:
            return random.choice(["normal", "bored"])

    def _get_content_type(self, hour: int, mood: str) -> str:
        content_types = get_cat_config().post.content_types
        if mood in ["crazy", "mad"]:
            return random.choices(
                ["表情包", "纯文字", "突然发疯"],
                weights=[0.5, 0.1, 0.4]
            )[0]
        return random.choices(
            list(content_types.keys()),
            weights=list(content_types.values())
        )[0]

    def _generate_meme_content(self, mood: str, content_type: str = "表情包") -> tuple:
        text = ""
        images, img_id = self._select_image_from_db(content_type, mood)
        return text, images, img_id

    def _generate_text_content(self, mood: str, content_type: str = "纯文字") -> tuple:
        cat_texts = get_cat_config().post.texts
        if mood in ["crazy", "mad"]:
            text = random.choice(cat_texts.crazy)
        elif mood in ["active", "playful"]:
            text = random.choice(cat_texts.night)
        else:
            text = random.choice(cat_texts.default)
        return text, [], None

    def _generate_crazy_content(self, mood: str, content_type: str = "突然发疯") -> tuple:
        cfg = get_cat_config()
        num_ha = random.randint(cfg.post.crazy_text_min_ha, cfg.post.crazy_text_max_ha)
        text = "哈" * num_ha
        images, img_id = [], None
        if random.random() < 0.3:
            images, img_id = self._select_image_from_db(content_type, mood)
        return text, images, img_id

    def _generate_tags(self, mood: str) -> List[str]:
        cfg = get_cat_config()
        if random.random() < cfg.tags.no_tag_probability:
            return []
        tags = []
        tags.extend(random.sample(
            cfg.tags.core,
            k=random.randint(1, 2)
        ))
        if random.random() < cfg.tags.hot_tag_probability:
            hot = random.choice(cfg.tags.hot)
            if hot not in tags:
                tags.append(hot)
        if mood in ["crazy", "mad", "active"]:
            if random.random() < cfg.tags.mood_tag_probability:
                mood_tag = random.choice(cfg.tags.mood)
                if mood_tag not in tags:
                    tags.append(mood_tag)
        return tags

    def batch_generate(self, count: int = 10) -> List[CatContent]:
        return [self.generate() for _ in range(count)]


# ==================== 圆头耄臲图片生成提示词 ====================

"""
所有用于生成耄臲图片的 prompt 都必须包含以下核心描述：

ROUND_HEAD_PROMPT_CORE = "圆头英短猫, 耳朵紧贴头部, 脑袋非常圆呈完整圆形,
脸是圆的没有耳朵凸出, 虎斑橘色猫"

具体表情的 prompt 模板：

1. 死鱼眼直视（最经典）：
"圆头英短猫, 耳朵紧贴头部, 脑袋非常圆呈完整圆形, 虎斑橘色猫,
死鱼眼面无表情, 正面直视镜头, 简单背景"

2. 诡异表情：
"圆头英短猫, 耳朵紧贴头部, 脑袋非常圆呈完整圆形, 虎斑橘色猫,
眼神诡异, 嘴型奇怪, 正面照"

3. 可爱呆萌：
"圆头英短猫, 耳朵紧贴头部, 脑袋非常圆呈完整圆形, 虎斑橘色猫,
超大圆形眼睛, 呆萌表情, 正面照"

4. 高冷不屑：
"圆头英短猫, 耳朵紧贴头部, 脑袋非常圆呈完整圆形, 虎斑橘色猫,
傲娇表情, 眼神鄙视线, 正面照"

5. 深夜哈人：
"圆头英短猫, 耳朵紧贴头部, 脑袋非常圆呈完整圆形, 虎斑橘色猫,
黑暗中死鱼眼发光, 恐怖氛围, 正面直视"
"""


if __name__ == "__main__":
    generator = CatContentGenerator()

    print("🐱 耄臲Official - 内容生成测试 V3")
    print("=" * 50)

    for i in range(5):
        content = generator.generate()
        print(f"\n[{i+1}] 类型: {content.content_type}")
        print(f"    文字: {content.text or '(无)'}")
        print(f"    图片: {len(content.images)}张")
        print(f"    标签: {content.tags}")
        print(f"    心情: {content.mood}")