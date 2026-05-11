"""
圆头耄耋 - 图片数据库
维护图片元数据和标签，支持按标签检索最适合当前场景的图片

标签维度：
- expression: 表情 (serious/deadpan, happy, angry, sleepy, crazy, curious, cute)
- head_shape: 头型特征 (extra_round, round, wide)
- eye_color: 眼睛颜色 (amber, golden, orange, green)
- pose: 姿势 (front_face, side, looking_up, looking_down,躺着,趴着)
- mood: 情绪氛围 (calm, funny, scary, cute, sleepy, crazy)
- lighting: 光线 (natural, dramatic, dark, bright)
- background: 背景 (white, dark, blurry, solid_color)
- usage: 适用场景 (daily_post, reaction, meme, reply, night_post)
- distinctiveness: 辨识度 (high, medium, low) - 圆头耄臝特征是否明显
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import shutil


@dataclass
class ImageEntry:
    """单张图片的数据库条目"""
    id: str
    filename: str
    relative_path: str
    generation_prompt: str
    source: str  # "ai_generated", "real_photo", "from_internet"
    
    # 标签维度
    expression: str
    head_shape: str
    eye_color: str
    pose: str
    mood: str
    lighting: str
    background: str
    usage: List[str]
    distinctiveness: str
    
    # 统计
    use_count: int = 0
    last_used: Optional[str] = None
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class ImageDatabase:
    """图片数据库管理器"""
    
    def __init__(self, db_path: str = "image_database.json", images_root: str = "images"):
        self.db_path = Path(db_path)
        self.images_root = Path(images_root)
        self.entries: Dict[str, ImageEntry] = {}
        self._load()
    
    def _load(self):
        """加载数据库"""
        if self.db_path.exists():
            with open(self.db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for k, v in data.items():
                    self.entries[k] = ImageEntry(**v)
    
    def _save(self):
        """保存数据库"""
        with open(self.db_path, "w", encoding="utf-8") as f:
            data = {k: asdict(v) for k, v in self.entries.items()}
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_image(
        self,
        filepath: str,
        generation_prompt: str = "",
        source: str = "ai_generated",
        tags: Optional[Dict[str, any]] = None,
    ) -> str:
        """
        添加图片到数据库
        
        Args:
            filepath: 图片文件路径
            generation_prompt: 生成时的prompt（用于后续参考）
            source:图片来源
            tags: 标签字典
            
        Returns:
            图片ID
        """
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"图片不存在: {filepath}")
        
        # 生成ID：前缀 + 序号
        prefix = filepath.stem[:8]  # 用文件名做前缀
        existing_ids = [k for k in self.entries.keys() if k.startswith(prefix)]
        img_id = f"{prefix}_{len(existing_ids) + 1:03d}"
        
        # 如果有标签就用标签，没有就用默认值
        if tags:
            entry = ImageEntry(
                id=img_id,
                filename=filepath.name,
                relative_path=str(filepath.relative_to(self.images_root)) if filepath.is_absolute() else str(filepath),
                generation_prompt=generation_prompt,
                source=source,
                expression=tags.get("expression", "unknown"),
                head_shape=tags.get("head_shape", "round"),
                eye_color=tags.get("eye_color", "amber"),
                pose=tags.get("pose", "front_face"),
                mood=tags.get("mood", "calm"),
                lighting=tags.get("lighting", "natural"),
                background=tags.get("background", "white"),
                usage=tags.get("usage", ["daily_post"]),
                distinctiveness=tags.get("distinctiveness", "medium"),
            )
        else:
            # 标签必填
            raise ValueError("tags 参数必填，需要指定至少 expression 和 mood")
        
        self.entries[img_id] = entry
        self._save()
        return img_id
    
    def update_tags(self, img_id: str, tags: Dict[str, any]):
        """更新图片标签"""
        if img_id not in self.entries:
            raise KeyError(f"图片ID不存在: {img_id}")
        
        entry = self.entries[img_id]
        for k, v in tags.items():
            if hasattr(entry, k):
                setattr(entry, k, v)
        
        self._save()
    
    def select_image(
        self,
        expression: Optional[str] = None,
        mood: Optional[str] = None,
        usage: Optional[str] = None,
        min_distinctiveness: str = None,
        exclude_recently_used: bool = True,
    ) -> Optional[ImageEntry]:
        """
        根据条件选择最适合的图片
        
        Args:
            expression: 期望的表情
            mood: 期望的情绪
            usage: 期望的用途
            min_distinctiveness: 最低辨识度要求
            exclude_recently_used: 是否排除最近用过的
            
        Returns:
            选中的图片条目，或None
        """
        candidates = list(self.entries.values())
        
        # 过滤
        if expression:
            candidates = [c for c in candidates if c.expression == expression]
        if mood:
            candidates = [c for c in candidates if c.mood == mood]
        if usage:
            candidates = [c for c in candidates if usage in c.usage]
        if min_distinctiveness:
            dist_rank = {"high": 3, "medium": 2, "low": 1}
            min_rank = dist_rank.get(min_distinctiveness, 2)
            candidates = [
                c for c in candidates
                if dist_rank.get(c.distinctiveness, 0) >= min_rank
            ]
        
        if exclude_recently_used:
            # 排除最近用过的（用过超过3次的降低权重）
            for c in candidates:
                if c.use_count > 3:
                    candidates.remove(c)
        
        if not candidates:
            return None
        
        # 优先选辨识度高的，然后随机
        candidates.sort(key=lambda x: (
            {"high": 3, "medium": 2, "low": 1}.get(x.distinctiveness, 1),
            -x.use_count,  # 用得越少优先级越高
            random.random()
        ), reverse=True)
        
        selected = candidates[0]
        selected.use_count += 1
        selected.last_used = datetime.now().isoformat()
        self._save()
        
        return selected
    
    def batch_add_from_folder(
        self,
        folder: str,
        source: str = "ai_generated",
        require_tags: bool = True,
    ):
        """
        从文件夹批量添加图片（不自动打标签，需要后续手动或AI标注）
        """
        folder = Path(folder)
        supported = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        
        added = []
        for img_path in folder.iterdir():
            if img_path.suffix.lower() not in supported:
                continue
            if img_path.name in [e.filename for e in self.entries.values()]:
                continue  # 已存在
            
            # 先占位，标签待填
            if require_tags:
                # 添加无标签条目，后续补全
                pass
            
            added.append(img_path.name)
        
        return added
    
    def export_for_tagging(self) -> List[Dict]:
        """导出未完成标签的图片列表，供人工或AI标注"""
        return [
            {
                "id": k,
                "filename": v.filename,
                "relative_path": v.relative_path,
                "expression": v.expression,
                "head_shape": v.head_shape,
                "eye_color": v.eye_color,
                "pose": v.pose,
                "mood": v.mood,
                "lighting": v.lighting,
                "background": v.background,
                "usage": v.usage,
                "distinctiveness": v.distinctiveness,
            }
            for k, v in self.entries.items()
            if v.expression == "unknown"
        ]
    
    def get_all(self) -> List[ImageEntry]:
        """获取所有图片条目"""
        return list(self.entries.values())
    
    def get_by_id(self, img_id: str) -> Optional[ImageEntry]:
        """根据ID获取图片"""
        return self.entries.get(img_id)
    
    def stats(self) -> Dict:
        """获取数据库统计"""
        expressions = {}
        moods = {}
        usages = {}
        distinctiveness = {}
        
        for e in self.entries.values():
            expressions[e.expression] = expressions.get(e.expression, 0) + 1
            moods[e.mood] = moods.get(e.mood, 0) + 1
            distinctiveness[e.distinctiveness] = distinctiveness.get(e.distinctiveness, 0) + 1
            for u in e.usage:
                usages[u] = usages.get(u, 0) + 1
        
        return {
            "total_images": len(self.entries),
            "by_expression": expressions,
            "by_mood": moods,
            "by_usage": usages,
            "by_distinctiveness": distinctiveness,
        }


# ============================================================
# 预设标签方案（用于批量打标签时的参考）
# ============================================================

TAG_SCHEMES = {
    "expression": [
        "serious", "deadpan", "happy", "angry", "sleepy",
        "crazy", "curious", "cute", "surprised", "disdainful"
    ],
    "head_shape": ["extra_round", "round", "wide", "normal"],
    "eye_color": ["amber", "golden", "orange", "green", "blue"],
    "pose": [
        "front_face", "side", "looking_up", "looking_down",
        "lying", "sleeping", "playing"
    ],
    "mood": ["calm", "funny", "scary", "cute", "sleepy", "crazy", "meta"],
    "lighting": ["natural", "dramatic", "dark", "bright", "soft"],
    "background": ["white", "dark", "blurry", "solid_color", "gradient"],
    "usage": [
        "daily_post", "reaction", "meme", "reply",
        "night_post", "crazy_post", "pure_meme"
    ],
    "distinctiveness": ["high", "medium", "low"],
}


# ============================================================
# CLI工具：批量添加图片并导出供标注
# ============================================================

if __name__ == "__main__":
    import sys
    
    db = ImageDatabase()
    
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        stats = db.stats()
        print(f"📊 图片数据库统计:")
        print(f"   总图片数: {stats['total_images']}")
        print(f"   按表情: {stats['by_expression']}")
        print(f"   按情绪: {stats['by_mood']}")
        print(f"   按辨识度: {stats['by_distinctiveness']}")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "export":
        untagged = db.export_for_tagging()
        print(f"待标注图片 ({len(untagged)}):")
        for u in untagged:
            print(f"  - {u['filename']} ({u['relative_path']})")
    
    elif len(sys.argv) > 1 and sys.argv[1] == "select":
        # python image_database.py select --mood crazy --usage night_post
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--expression")
        parser.add_argument("--mood")
        parser.add_argument("--usage")
        parser.add_argument("--min-distinctiveness")
        args = parser.parse_args(sys.argv[2:])
        
        entry = db.select_image(
            expression=args.expression,
            mood=args.mood,
            usage=args.usage,
            min_distinctiveness=args.min_distinctiveness,
        )
        if entry:
            print(f"选中: {entry.filename} (ID: {entry.id})")
            print(f"  表情: {entry.expression}, 情绪: {entry.mood}, 用途: {entry.usage}")
            print(f"  路径: {entry.relative_path}")
        else:
            print("没有找到匹配的图片")
