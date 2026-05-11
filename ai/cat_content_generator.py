"""
耄耋Official - 猫的内容生成器
核心思想：猫发什么？表情包为主，偶尔发疯
"""
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class CatContent:
    """猫的内容"""
    content_type: str       # 表情包/纯文字/突然发疯
    text: str              # 文字内容
    images: List[str]      # 图片路径
    tags: List[str]        # 标签
    post_time: str         # 发布时间
    mood: str              # 猫的心情


class CatContentGenerator:
    """
    猫的内容生成器
    
    猫会发什么？
    - 80% 表情包（盯着你、哈人、诡异）
    - 10% 纯文字（哈、哈哈、哈哈哈）
    - 10% 突然发疯（连发一堆哈）
    """
    
    # 内容类型权重
    CONTENT_TYPES = {
        "表情包": 0.8,
        "纯文字": 0.1,
        "突然发疯": 0.1,
    }
    
    # 猫的文字库
    CAT_TEXTS = {
        "default": ["哈", "哈哈", "哈哈哈"],
        "short": ["哈", "哈。", ".."],
        "crazy": ["哈哈哈哈哈", "哈哈哈哈哈哈", "哈哈哈哈哈哈哈哈哈"],
        "night": ["哈", "哈", "哈哈", "..."],
        "mad": ["哈" * 10, "哈" * 15, "哈" * 20],
    }
    
    # 标签库
    TAGS = {
        "core": ["耄耋", "圆头耄耋", "哈人", "抽象"],
        "hot": ["哈基米", "猫meme", "搞笑猫"],
        "mood": ["深夜", "发疯", "整活"],
    }
    
    def __init__(self, image_folder: str = "images/maodie"):
        """
        初始化
        
        Args:
            image_folder: 表情包图片文件夹路径
        """
        self.image_folder = Path(image_folder)
        self.available_images = self._load_images()
    
    def _load_images(self) -> List[str]:
        """加载可用图片"""
        if not self.image_folder.exists():
            return []
        
        images = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp"]:
            images.extend(self.image_folder.glob(ext))
        
        return [str(img) for img in images]
    
    def generate(self, mood: str = None) -> CatContent:
        """
        生成猫的内容
        
        Args:
            mood: 猫的心情（可选）
        """
        hour = datetime.now().hour
        
        # 确定心情
        if mood is None:
            mood = self._get_mood(hour)
        
        # 确定内容类型
        content_type = self._get_content_type(hour, mood)
        
        # 生成内容
        if content_type == "表情包":
            text, images = self._generate_meme_content(mood)
        elif content_type == "纯文字":
            text, images = self._generate_text_content(mood)
        else:  # 突然发疯
            text, images = self._generate_crazy_content(mood)
        
        # 生成标签
        tags = self._generate_tags(mood)
        
        return CatContent(
            content_type=content_type,
            text=text,
            images=images,
            tags=tags,
            post_time=datetime.now().strftime("%H:%M"),
            mood=mood
        )
    
    def _get_mood(self, hour: int) -> str:
        """根据时间判断猫的心情"""
        if 2 <= hour < 4:
            return random.choice(["crazy", "crazy", "mad"])
        elif hour >= 23 or hour < 6:
            return random.choice(["active", "playful", "hungry"])
        elif 8 <= hour < 18:
            return random.choice(["sleepy", "lazy", "ignoring"])
        else:
            return random.choice(["normal", "bored"])
    
    def _get_content_type(self, hour: int, mood: str) -> str:
        """确定内容类型"""
        # 深夜疯狂时间更容易发疯
        if mood in ["crazy", "mad"]:
            return random.choices(
                ["表情包", "纯文字", "突然发疯"],
                weights=[0.5, 0.1, 0.4]
            )[0]
        
        # 正常情况
        return random.choices(
            list(self.CONTENT_TYPES.keys()),
            weights=list(self.CONTENT_TYPES.values())
        )[0]
    
    def _generate_meme_content(self, mood: str) -> tuple:
        """生成表情包内容"""
        # 纯表情包，不配文字
        text = ""
        
        # 随机选图片
        images = []
        if self.available_images:
            num = random.randint(1, min(3, len(self.available_images)))
            images = random.sample(self.available_images, num)
        
        return text, images
    
    def _generate_text_content(self, mood: str) -> tuple:
        """生成纯文字内容"""
        # 根据心情选文字
        if mood in ["crazy", "mad"]:
            text = random.choice(self.CAT_TEXTS["mad"])
        elif mood in ["active", "playful"]:
            text = random.choice(self.CAT_TEXTS["night"])
        else:
            text = random.choice(self.CAT_TEXTS["default"])
        
        return text, []
    
    def _generate_crazy_content(self, mood: str) -> tuple:
        """生成突然发疯内容"""
        # 连发一堆哈
        num_ha = random.randint(5, 25)
        text = "哈" * num_ha
        
        # 可能也发图
        images = []
        if self.available_images and random.random() < 0.3:
            images = [random.choice(self.available_images)]
        
        return text, images
    
    def _generate_tags(self, mood: str) -> List[str]:
        """生成标签"""
        # 30%概率不带标签
        if random.random() < 0.3:
            return []
        
        tags = []
        
        # 核心标签
        tags.extend(random.sample(
            self.TAGS["core"],
            k=random.randint(1, 2)
        ))
        
        # 偶尔加热门标签
        if random.random() < 0.2:
            hot = random.choice(self.TAGS["hot"])
            if hot not in tags:
                tags.append(hot)
        
        # 深夜加心情标签
        if mood in ["crazy", "mad", "active"]:
            if random.random() < 0.3:
                mood_tag = random.choice(self.TAGS["mood"])
                if mood_tag not in tags:
                    tags.append(mood_tag)
        
        return tags
    
    def batch_generate(self, count: int = 10) -> List[CatContent]:
        """批量生成内容"""
        contents = []
        for _ in range(count):
            contents.append(self.generate())
        return contents


# ==================== 预设内容模板 ====================

# 深夜哈人模板
NIGHT_TEMPLATES = [
    {
        "text": "",
        "description": "纯表情包，盯着你",
    },
    {
        "text": "哈",
        "description": "一个哈",
    },
    {
        "text": "..",
        "description": "两个点",
    },
]

# 突然发疯模板
CRAZY_TEMPLATES = [
    {
        "text": "哈" * 10,
        "description": "10个哈",
    },
    {
        "text": "哈" * 15,
        "description": "15个哈",
    },
    {
        "text": "哈\n哈\n哈\n哈\n哈",
        "description": "竖着的哈",
    },
]

# meta整活模板
META_TEMPLATES = [
    {
        "text": "你在看猫\n猫也在看你",
        "description": "meta整活",
    },
    {
        "text": "不要停下来",
        "description": "无限循环",
    },
    {
        "text": "它知道你的位置",
        "description": "哈人",
    },
]


# ==================== 使用示例 ====================

if __name__ == "__main__":
    generator = CatContentGenerator()
    
    print("🐱 耄耋Official - 内容生成测试")
    print("=" * 50)
    
    # 生成10条内容
    for i in range(10):
        content = generator.generate()
        print(f"\n[{i+1}] 类型: {content.content_type}")
        print(f"    文字: {content.text or '(无)'}")
        print(f"    图片: {len(content.images)}张")
        print(f"    标签: {content.tags}")
        print(f"    心情: {content.mood}")
        print(f"    时间: {content.post_time}")
