"""
耄耋Official - 猫的逻辑Agent配置
核心思想：让圆头耄耋本猫来运营这个账号
"""
from .personality_loader import get_cat_config, CatPersonalityConfig
import random
from datetime import datetime
from typing import Optional, List, Dict
from dataclasses import dataclass


@dataclass
class CatConfig:
    """猫的配置"""
    # 账号信息
    account_name: str = "耄耋Official"
    cat_name: str = "圆头耄耋"
    
    # 回复配置（猫的逻辑）
    reply_probability: float = 0.1      # 只有10%的评论会回复
    max_reply_length: int = 3           # 最多回复3个字
    reply_delay_min: int = 300          # 最少延迟5分钟
    reply_delay_max: int = 86400        # 最多延迟24小时
    
    # 发布配置（猫的作息）
    post_probability_day: float = 0.05      # 白天5%概率发
    post_probability_evening: float = 0.1   # 傍晚10%概率发
    post_probability_night: float = 0.3     # 深夜30%概率发
    post_probability_mad_hour: float = 0.8  # 凌晨2-4点80%概率发
    
    # 内容配置
    content_type_weights: Dict = None
    
    # 标签配置
    core_tags: List[str] = None
    hot_tags: List[str] = None
    no_tag_probability: float = 0.3    # 30%概率不带标签
    
    def __post_init__(self):
        if self.content_type_weights is None:
            self.content_type_weights = {
                "表情包": 0.8,
                "纯文字": 0.1,
                "突然发疯": 0.1,
            }
        if self.core_tags is None:
            self.core_tags = ["耄耋", "圆头耄耋", "哈人", "抽象"]
        if self.hot_tags is None:
            self.hot_tags = ["哈基米", "猫meme", "搞笑猫"]


# 猫的回复话术库
CAT_REPLIES = {
    "default": ["哈", "哈哈", "哈哈哈"],
    "short": ["哈", "哈。"],
    "crazy": ["哈哈哈哈哈", "哈哈哈哈哈哈"],
    "night": ["哈", "哈", "哈哈"],  # 深夜更活跃
}

# 猫不回复的情况
NO_REPLY_PHRASES = [
    # 太长了不看
    "太长了",
    "不看",
    "懒得回",
]


class CatLogicEngine:
    """
    猫的逻辑引擎
    
    所有决策都基于猫的行为逻辑：
    - 高冷、不在乎人类
    - 想干嘛就干嘛
    - 不解释、不讨好
    - 深夜活跃、白天消失
    - 偶尔突然发疯
    """
    
    def __init__(self, config: CatConfig = None):
        self.config = config or CatConfig()
    
    # ==================== 回复逻辑 ====================
    
    def should_reply(self, comment: str = "") -> bool:
        """
        猫要不要回复？
        
        猫的逻辑：
        - 大部分时候不理你
        - 深夜更容易回复（猫醒了）
        - 白天基本不回（在睡觉）
        """
        # 评论太长不看
        if len(comment) > 50:
            return random.random() < 0.02  # 只有2%概率回
        
        hour = datetime.now().hour
        
        # 白天睡觉（8:00-18:00）
        if 8 <= hour < 18:
            return random.random() < 0.03  # 3%概率回
        
        # 深夜活跃（23:00-4:00）
        if hour >= 23 or hour < 4:
            return random.random() < 0.15  # 15%概率回
        
        # 其他时间
        return random.random() < self.config.reply_probability
    
    def get_reply(self, comment: str = "") -> Optional[str]:
        """
        猫怎么回复？
        
        猫的逻辑：
        - 能发一个字就不发两个字
        - 能发"哈"就不发别的
        """
        if not self.should_reply(comment):
            return None  # 不回复
        
        hour = datetime.now().hour
        
        # 深夜可能更疯狂
        if hour >= 1 and hour < 4:
            if random.random() < 0.2:  # 20%概率发疯
                return random.choice(CAT_REPLIES["crazy"])
        
        # 正常回复
        return random.choice(CAT_REPLIES["default"])
    
    # ==================== 发布逻辑 ====================
    
    def should_post(self) -> bool:
        """
        猫要不要发内容？
        
        猫的逻辑：
        - 白天睡觉，不怎么发
        - 傍晚醒来，偶尔发
        - 深夜活跃，经常发
        - 凌晨2-4点可能突然发疯
        """
        hour = datetime.now().hour
        
        # 白天睡觉（8:00-18:00）
        if 8 <= hour < 18:
            return random.random() < self.config.post_probability_day
        
        # 傍晚醒来（18:00-23:00）
        if 18 <= hour < 23:
            return random.random() < self.config.post_probability_evening
        
        # 深夜活跃（23:00-4:00）
        if hour >= 23 or hour < 4:
            # 凌晨2-4点是疯狂时间
            if 2 <= hour < 4:
                return random.random() < self.config.post_probability_mad_hour
            return random.random() < self.config.post_probability_night
        
        # 其他时间
        return random.random() < 0.05
    
    def get_content_type(self) -> str:
        """
        猫发什么类型的内容？
        
        猫的逻辑：
        - 80%发表情包
        - 10%发纯文字
        - 10%突然发疯
        """
        types = list(self.config.content_type_weights.keys())
        weights = list(self.config.content_type_weights.values())
        
        return random.choices(types, weights=weights)[0]
    
    def get_content(self, image_paths: List[str] = None) -> Dict:
        """
        生成猫要发的内容
        
        Args:
            image_paths: 可用的表情包图片路径列表
        
        Returns:
            内容字典
        """
        content_type = self.get_content_type()
        hour = datetime.now().hour
        
        content = {
            "type": content_type,
            "text": "",
            "images": [],
            "tags": self._get_tags(),
        }
        
        if content_type == "表情包":
            # 纯表情包，不配文
            if image_paths:
                # 随机选1-3张
                num_images = min(random.randint(1, 3), len(image_paths))
                content["images"] = random.sample(image_paths, num_images)
            # 不配文字
            content["text"] = ""
        
        elif content_type == "纯文字":
            # 纯文字
            content["text"] = random.choice(["哈", "哈哈", "哈哈哈"])
        
        elif content_type == "突然发疯":
            # 深夜发疯
            num_ha = random.randint(5, 20)
            content["text"] = "哈" * num_ha
            
            # 可能也发图
            if image_paths and random.random() < 0.5:
                content["images"] = [random.choice(image_paths)]
        
        return content
    
    # ==================== 标签逻辑 ====================
    
    def _get_tags(self) -> List[str]:
        """
        猫带什么标签？
        
        猫的逻辑：
        - 想带就带，不想带就不带
        - 带几个看心情
        """
        # 30%概率不带标签
        if random.random() < self.config.no_tag_probability:
            return []
        
        # 随机选1-2个标签
        tags = random.sample(
            self.config.core_tags,
            k=random.randint(1, min(2, len(self.config.core_tags)))
        )
        
        # 偶尔蹭热度
        if random.random() < 0.2:
            hot_tag = random.choice(self.config.hot_tags)
            if hot_tag not in tags:
                tags.append(hot_tag)
        
        return tags
    
    # ==================== 互动逻辑 ====================
    
    def should_like(self) -> bool:
        """猫要不要点赞别人的内容？"""
        # 猫很少点赞
        return random.random() < 0.05
    
    def should_follow(self) -> bool:
        """猫要不要关注别人？"""
        # 猫几乎不关注
        return random.random() < 0.02
    
    def should_comment(self) -> bool:
        """猫要不要评论别人的内容？"""
        # 猫很少评论
        hour = datetime.now().hour
        if hour >= 23 or hour < 4:
            return random.random() < 0.1  # 深夜活跃一点
        return random.random() < 0.03
    
    def get_comment(self) -> str:
        """猫评论什么？"""
        return random.choice(["哈", "哈哈", "哈。"])
    
    # ==================== 工具方法 ====================
    
    def is_night(self) -> bool:
        """是不是深夜？"""
        hour = datetime.now().hour
        return hour >= 23 or hour < 6
    
    def is_mad_hour(self) -> bool:
        """是不是疯狂时间（凌晨2-4点）？"""
        hour = datetime.now().hour
        return 2 <= hour < 4
    
    def get_mood(self) -> str:
        """猫现在什么心情？"""
        if self.is_mad_hour():
            return random.choice(["crazy", "crazy", "active"])
        elif self.is_night():
            return random.choice(["active", "playful", "hungry"])
        else:
            return random.choice(["sleepy", "lazy", "ignoring_you"])


# 全局配置实例
cat_config = CatConfig()
cat_engine = CatLogicEngine(cat_config)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 测试猫的逻辑
    
    print("🐱 耄耋Official - 猫的逻辑测试")
    print("=" * 50)
    
    # 测试回复
    print("\n💬 回复测试:")
    for comment in ["好可爱！", "这是什么？", "哈哈哈哈", "太搞笑了" + "！" * 100]:
        reply = cat_engine.get_reply(comment)
        print(f"  评论: {comment[:20]}...")
        print(f"  回复: {reply}")
        print()
    
    # 测试发布
    print("\n📅 发布测试:")
    for _ in range(10):
        if cat_engine.should_post():
            content = cat_engine.get_content(["cat1.jpg", "cat2.jpg", "cat3.jpg"])
            print(f"  类型: {content['type']}")
            print(f"  文字: {content['text'] or '(无)'}")
            print(f"  标签: {content['tags']}")
            print()
    
    # 测试心情
    print("\n😺 心情测试:")
    for _ in range(5):
        print(f"  当前心情: {cat_engine.get_mood()}")
