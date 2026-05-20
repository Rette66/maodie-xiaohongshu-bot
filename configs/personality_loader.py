"""
耄臲Official - 猫格配置加载器
单例模式，支持热重载
"""
import json
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================
# DataClasses 定义（对应 JSON 结构）
# ============================================================

@dataclass
class ReplyPhrases:
    default: List[str] = field(default_factory=lambda: ["哈", "哈哈", "哈哈哈"])
    short: List[str] = field(default_factory=lambda: ["哈", "哈。"])
    crazy: List[str] = field(default_factory=lambda: ["哈哈哈哈哈", "哈哈哈哈哈哈"])
    night: List[str] = field(default_factory=lambda: ["哈", "哈", "哈哈"])


@dataclass
class ReplyConfig:
    phrases: ReplyPhrases = field(default_factory=ReplyPhrases)
    dm_phrases: List[str] = field(default_factory=lambda: ["哈", "哈哈", "..", "？", ""])
    no_reply_phrases: List[str] = field(default_factory=lambda: ["太长了", "不看", "懒得回"])
    probability_day: float = 0.03
    probability_evening: float = 0.08
    probability_night: float = 0.15
    probability_long_comment: float = 0.02
    max_comment_length: int = 50
    delay_min_seconds: int = 300
    delay_max_seconds: int = 86400


@dataclass
class PostTextConfig:
    default: List[str] = field(default_factory=lambda: ["哈", "哈哈", "哈哈哈"])
    short: List[str] = field(default_factory=lambda: ["哈", "哈。", ".."])
    crazy: List[str] = field(default_factory=lambda: ["哈哈哈哈哈", "哈哈哈哈哈哈", "哈哈哈哈哈哈哈哈哈"])
    night: List[str] = field(default_factory=lambda: ["哈", "哈", "哈哈", "..."])


@dataclass
class ScheduleEntry:
    hour_start: int
    hour_end: int
    probability: float
    activity: str  # sleeping/waking/active/crazy


@dataclass
class PostConfig:
    content_types: Dict[str, float] = field(default_factory=lambda: {
        "表情包": 0.8,
        "纯文字": 0.1,
        "突然发疯": 0.1,
    })
    texts: PostTextConfig = field(default_factory=PostTextConfig)
    schedule: List[ScheduleEntry] = field(default_factory=list)
    crazy_text_min_ha: int = 5
    crazy_text_max_ha: int = 20


@dataclass
class TagConfig:
    core: List[str] = field(default_factory=lambda: ["耄臲", "圆头耄臲", "哈人", "抽象"])
    hot: List[str] = field(default_factory=lambda: ["哈基米", "猫meme", "搞笑猫"])
    mood: List[str] = field(default_factory=lambda: ["深夜", "发疯", "整活"])
    no_tag_probability: float = 0.3
    hot_tag_probability: float = 0.2
    mood_tag_probability: float = 0.3


@dataclass
class InteractionConfig:
    like_probability: float = 0.05
    follow_probability: float = 0.02
    comment_probability_day: float = 0.03
    comment_probability_night: float = 0.1


@dataclass
class SleepConfig:
    sleeping_min: int = 600
    sleeping_max: int = 1800
    crazy_min: int = 60
    crazy_max: int = 300
    normal_min: int = 300
    normal_max: int = 600


@dataclass
class CatPersonalityConfig:
    """完整的猫格配置"""
    account_name: str = "耄臲Official"
    cat_name: str = "圆头耄臲"
    reply: ReplyConfig = field(default_factory=ReplyConfig)
    post: PostConfig = field(default_factory=PostConfig)
    tags: TagConfig = field(default_factory=TagConfig)
    interaction: InteractionConfig = field(default_factory=InteractionConfig)
    sleep_seconds: SleepConfig = field(default_factory=SleepConfig)


# ============================================================
# 配置加载器（单例模式）
# ============================================================

class PersonalityLoader:
    """
    猫格配置加载器

    特性：
    - 单例模式
    - 热重载支持
    - 默认值回退（配置文件缺失时使用硬编码默认值）
    """

    _instance: Optional["PersonalityLoader"] = None
    _config: Optional[CatPersonalityConfig] = None
    _config_path: Optional[Path] = None

    def __new__(cls, config_path: str = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: str = None):
        if config_path is not None:
            self._config_path = Path(config_path)
        elif self._config_path is None:
            self._config_path = Path(__file__).parent / "cat_personality.json"

    def load(self, force: bool = False) -> CatPersonalityConfig:
        """加载配置"""
        if self._config is not None and not force:
            return self._config

        if self._config_path.exists():
            try:
                with open(self._config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._config = self._parse_config(data)
                print(f"✅ 猫格配置已加载: {self._config_path}")
            except Exception as e:
                print(f"⚠️ 配置加载失败，使用默认值: {e}")
                self._config = CatPersonalityConfig()
        else:
            print(f"⚠️ 配置文件不存在，使用默认值: {self._config_path}")
            self._config = CatPersonalityConfig()

        return self._config

    def _parse_config(self, data: dict) -> CatPersonalityConfig:
        """解析 JSON 到 dataclass"""
        return CatPersonalityConfig(
            account_name=data.get("account", {}).get("name", "耄臲Official"),
            cat_name=data.get("account", {}).get("cat_name", "圆头耄臲"),
            reply=self._parse_reply(data.get("reply", {})),
            post=self._parse_post(data.get("post", {})),
            tags=self._parse_tags(data.get("tags", {})),
            interaction=self._parse_interaction(data.get("interaction", {})),
            sleep_seconds=self._parse_sleep(data.get("sleep_seconds", {})),
        )

    def _parse_reply(self, data: dict) -> ReplyConfig:
        phrases_data = data.get("phrases", {})
        return ReplyConfig(
            phrases=ReplyPhrases(
                default=phrases_data.get("default", ["哈", "哈哈", "哈哈哈"]),
                short=phrases_data.get("short", ["哈", "哈。"]),
                crazy=phrases_data.get("crazy", ["哈哈哈哈哈", "哈哈哈哈哈哈"]),
                night=phrases_data.get("night", ["哈", "哈", "哈哈"]),
            ),
            dm_phrases=data.get("dm_phrases", ["哈", "哈哈", "..", "？", ""]),
            no_reply_phrases=data.get("no_reply_phrases", ["太长了", "不看", "懒得回"]),
            probability_day=data.get("probability_day", 0.03),
            probability_evening=data.get("probability_evening", 0.08),
            probability_night=data.get("probability_night", 0.15),
            probability_long_comment=data.get("probability_long_comment", 0.02),
            max_comment_length=data.get("max_comment_length", 50),
            delay_min_seconds=data.get("delay_min_seconds", 300),
            delay_max_seconds=data.get("delay_max_seconds", 86400),
        )

    def _parse_post(self, data: dict) -> PostConfig:
        texts_data = data.get("texts", {})
        schedule_data = data.get("schedule", [])
        return PostConfig(
            content_types=data.get("content_types", {
                "表情包": 0.8,
                "纯文字": 0.1,
                "突然发疯": 0.1,
            }),
            texts=PostTextConfig(
                default=texts_data.get("default", ["哈", "哈哈", "哈哈哈"]),
                short=texts_data.get("short", ["哈", "哈。", ".."]),
                crazy=texts_data.get("crazy", ["哈哈哈哈哈", "哈哈哈哈哈哈", "哈哈哈哈哈哈哈哈哈"]),
                night=texts_data.get("night", ["哈", "哈", "哈哈", "..."]),
            ),
            schedule=[ScheduleEntry(**s) for s in schedule_data],
            crazy_text_min_ha=data.get("crazy_text_min_ha", 5),
            crazy_text_max_ha=data.get("crazy_text_max_ha", 20),
        )

    def _parse_tags(self, data: dict) -> TagConfig:
        return TagConfig(
            core=data.get("core", ["耄臲", "圆头耄臲", "哈人", "抽象"]),
            hot=data.get("hot", ["哈基米", "猫meme", "搞笑猫"]),
            mood=data.get("mood", ["深夜", "发疯", "整活"]),
            no_tag_probability=data.get("no_tag_probability", 0.3),
            hot_tag_probability=data.get("hot_tag_probability", 0.2),
            mood_tag_probability=data.get("mood_tag_probability", 0.3),
        )

    def _parse_interaction(self, data: dict) -> InteractionConfig:
        return InteractionConfig(
            like_probability=data.get("like_probability", 0.05),
            follow_probability=data.get("follow_probability", 0.02),
            comment_probability_day=data.get("comment_probability_day", 0.03),
            comment_probability_night=data.get("comment_probability_night", 0.1),
        )

    def _parse_sleep(self, data: dict) -> SleepConfig:
        return SleepConfig(
            sleeping_min=data.get("sleeping_min", 600),
            sleeping_max=data.get("sleeping_max", 1800),
            crazy_min=data.get("crazy_min", 60),
            crazy_max=data.get("crazy_max", 300),
            normal_min=data.get("normal_min", 300),
            normal_max=data.get("normal_max", 600),
        )

    def get_config(self) -> CatPersonalityConfig:
        """获取配置（延迟加载）"""
        if self._config is None:
            return self.load()
        return self._config

    def reload(self) -> CatPersonalityConfig:
        """热重载配置"""
        self._config = None
        return self.load()


# ============================================================
# 全局访问函数
# ============================================================

_loader: Optional[PersonalityLoader] = None


def get_cat_config() -> CatPersonalityConfig:
    """获取猫格配置（全局单例）"""
    global _loader
    if _loader is None:
        _loader = PersonalityLoader()
    return _loader.get_config()


def reload_cat_config() -> CatPersonalityConfig:
    """热重载猫格配置"""
    global _loader
    if _loader is None:
        _loader = PersonalityLoader()
    return _loader.reload()