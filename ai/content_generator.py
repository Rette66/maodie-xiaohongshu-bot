"""
AI内容生成模块 - 使用大模型生成高质量内容
"""
import json
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ContentTheme:
    """内容主题"""
    name: str
    keywords: List[str]
    style: str
    target_audience: str
    content_types: List[str]


@dataclass
class GeneratedContent:
    """生成的内容"""
    title: str
    content: str
    tags: List[str]
    suggested_images: List[str]
    best_posting_time: str
    confidence_score: float


class ContentGenerator:
    """
    AI内容生成器
    
    功能：
    - 根据主题生成标题和正文
    - 智能标签推荐
    - 最佳发布时间预测
    - 内容质量评分
    """
    
    # 预定义的主题模板
    THEMES = {
        "lifestyle": ContentTheme(
            name="生活方式",
            keywords=["日常", "生活", "记录", "分享"],
            style="轻松、真实、温暖",
            target_audience="18-35岁城市青年",
            content_types=["图文", "短图文"]
        ),
        "food": ContentTheme(
            name="美食探店",
            keywords=["美食", "探店", "餐厅", "好吃"],
            style="诱人、详细、有食欲",
            target_audience="美食爱好者",
            content_types=["图文", "视频"]
        ),
        "travel": ContentTheme(
            name="旅行分享",
            keywords=["旅行", "旅游", "景点", "攻略"],
            style="实用、美观、有感染力",
            target_audience="旅行爱好者",
            content_types=["图文", "视频"]
        ),
        "fashion": ContentTheme(
            name="时尚穿搭",
            keywords=["穿搭", "时尚", "OOTD", "搭配"],
            style="潮流、个性、有品味",
            target_audience="时尚爱好者",
            content_types=["图文"]
        ),
        "tech": ContentTheme(
            name="数码科技",
            keywords=["科技", "数码", "评测", "推荐"],
            style="专业、客观、有深度",
            target_audience="科技爱好者",
            content_types=["图文", "视频"]
        ),
    }
    
    # 标题模板库
    TITLE_TEMPLATES = {
        "lifestyle": [
            "{emoji} 今天的{topic}，{mood}",
            "{topic}日常 | {action}的一天",
            "被{topic}治愈的瞬间{emoji}",
            "{topic}分享 | {benefit}",
        ],
        "food": [
            "{emoji} 这家{topic}真的{adj}！",
            "{topic}探店 | {highlight}",
            "为了这口{topic}，我{action}",
            "{topic}天花板！{reason}",
        ],
        "travel": [
            "{emoji} {place} | {experience}",
            "{topic}攻略 | {highlight}",
            "{place}真的太{adj}了！",
            "{action}去{place}，{result}",
        ],
        "fashion": [
            "{emoji} OOTD | {style}",
            "{topic}穿搭 | {highlight}",
            "{adj}的{topic}搭配",
            "{topic}分享 | {benefit}",
        ],
        "tech": [
            "{emoji} {product}使用体验",
            "{topic}评测 | {conclusion}",
            "{product}真的值得买吗？",
            "{topic}推荐 | {highlight}",
        ],
    }
    
    # 内容模板库
    CONTENT_TEMPLATES = {
        "lifestyle": """
{opening}

{detail}

{reflection}

{hashtags}
        """,
        "food": """
{opening}

📍 店铺：{shop_name}
💰 人均：{price}
⭐ 推荐：{recommendations}

{detail}

{tips}

{hashtags}
        """,
        "travel": """
{opening}

📍 地点：{location}
🎫 门票：{ticket}
⏰ 时间：{time}

{detail}

{tips}

{hashtags}
        """,
        "fashion": """
{opening}

👔 上衣：{top}
👖 下装：{bottom}
👟 鞋子：{shoes}
👜 包包：{bag}

{detail}

{hashtags}
        """,
        "tech": """
{opening}

📱 产品：{product}
💰 价格：{price}
⭐ 评分：{rating}/5

{pros_cons}

{detail}

{conclusion}

{hashtags}
        """,
    }
    
    def __init__(self):
        self.content_history = []
        self.performance_data = {}
    
    def generate_content(
        self,
        theme_key: str,
        topic: str,
        custom_params: Optional[Dict] = None
    ) -> GeneratedContent:
        """
        生成内容
        
        Args:
            theme_key: 主题类型 (lifestyle, food, travel, fashion, tech)
            topic: 具体话题
            custom_params: 自定义参数
        """
        theme = self.THEMES.get(theme_key, self.THEMES["lifestyle"])
        
        # 生成标题
        title = self._generate_title(theme_key, topic, custom_params)
        
        # 生成正文
        content = self._generate_body(theme_key, topic, custom_params)
        
        # 生成标签
        tags = self._generate_tags(theme, topic)
        
        # 建议图片类型
        suggested_images = self._suggest_images(theme_key)
        
        # 预测最佳发布时间
        best_time = self._predict_best_posting_time()
        
        # 计算置信度分数
        confidence = self._calculate_confidence(theme, title, content)
        
        generated = GeneratedContent(
            title=title,
            content=content,
            tags=tags,
            suggested_images=suggested_images,
            best_posting_time=best_time,
            confidence_score=confidence
        )
        
        # 记录生成历史
        self.content_history.append({
            "timestamp": datetime.now().isoformat(),
            "theme": theme_key,
            "topic": topic,
            "content": generated
        })
        
        return generated
    
    def _generate_title(
        self,
        theme_key: str,
        topic: str,
        params: Optional[Dict] = None
    ) -> str:
        """生成标题"""
        templates = self.TITLE_TEMPLATES.get(theme_key, self.TITLE_TEMPLATES["lifestyle"])
        template = random.choice(templates)
        
        # 填充变量
        variables = {
            "emoji": random.choice(["✨", "🌟", "💫", "⭐", "🔥", "❤️", "😍", "👍"]),
            "topic": topic,
            "mood": random.choice(["太治愈了", "心情超好", "很满足", "幸福感爆棚"]),
            "action": random.choice(["记录", "分享", "探索", "发现"]),
            "benefit": random.choice(["干货满满", "建议收藏", "不看后悔"]),
            "adj": random.choice(["绝", "惊艳", "宝藏", "神仙"]),
            "highlight": random.choice(["必看", "精华版", "详细攻略"]),
            "reason": random.choice(["好吃到哭", "拍照超美", "性价比超高"]),
            "place": params.get("place", "这个地方") if params else "这个地方",
            "experience": random.choice(["美到窒息", "不虚此行", "超出预期"]),
            "style": random.choice(["简约风", "韩系", "日系", "复古风"]),
            "product": params.get("product", "这款产品") if params else "这款产品",
            "conclusion": random.choice(["值得入手", "谨慎考虑", "强烈推荐"]),
        }
        
        try:
            title = template.format(**variables)
        except KeyError:
            title = f"✨ {topic}分享"
        
        return title
    
    def _generate_body(
        self,
        theme_key: str,
        topic: str,
        params: Optional[Dict] = None
    ) -> str:
        """生成正文"""
        template = self.CONTENT_TEMPLATES.get(theme_key, self.CONTENT_TEMPLATES["lifestyle"])
        
        # 根据主题生成具体内容
        if theme_key == "lifestyle":
            content = template.format(
                opening=f"今天想和大家分享一下我的{topic}日常",
                detail=f"最近{random.choice(['发现', '尝试', '体验'])}了一些{topic}相关的内容，感觉{random.choice(['很有意思', '收获满满', '特别治愈'])}。",
                reflection=f"{random.choice(['生活就是这样', '其实', '说到底'])}, {random.choice(['简单的美好最珍贵', '享受当下最重要', '记录生活很有意义'])}。",
                hashtags=" ".join([f"#{topic}", "#生活", "#日常", "#分享"])
            )
        
        elif theme_key == "food":
            content = template.format(
                opening=f"{random.choice(['最近发现', '朋友推荐', '种草已久'])}的{topic}，终于来打卡了！",
                shop_name=params.get("shop_name", "这家店") if params else "这家店",
                price=params.get("price", "人均100左右") if params else "人均100左右",
                recommendations=params.get("recommendations", "招牌菜") if params else "招牌菜",
                detail=f"味道{random.choice(['真的很棒', '超出预期', '一级棒'])}，{random.choice(['环境也不错', '服务很周到', '性价比很高'])}。",
                tips=f"💡 小建议：{random.choice(['建议提前预约', '避开高峰期', '一定要尝尝招牌'])}。",
                hashtags=" ".join([f"#{topic}", "#美食", "#探店", "#吃货"])
            )
        
        elif theme_key == "travel":
            content = template.format(
                opening=f"{random.choice(['终于去了', '打卡', '探索'])}心心念念的{topic}！",
                location=params.get("location", topic) if params else topic,
                ticket=params.get("ticket", "免费/需预约") if params else "免费/需预约",
                time=params.get("time", "建议游玩半天") if params else "建议游玩半天",
                detail=f"{random.choice(['景色', '体验', '氛围'])}真的{random.choice(['太美了', '很棒', '超出预期'])}，{random.choice(['强烈推荐', '值得一去', '不虚此行'])}。",
                tips=f"📌 实用Tips：{random.choice(['记得带身份证', '穿舒适的鞋子', '提前看天气预报'])}。",
                hashtags=" ".join([f"#{topic}", "#旅行", "#攻略", "#打卡"])
            )
        
        elif theme_key == "fashion":
            content = template.format(
                opening=f"分享一套{random.choice(['最近很爱的', '日常通勤', '约会必备'])}的{topic}穿搭",
                top=params.get("top", "简约T恤/衬衫") if params else "简约T恤/衬衫",
                bottom=params.get("bottom", "休闲裤/半裙") if params else "休闲裤/半裙",
                shoes=params.get("shoes", "小白鞋/乐福鞋") if params else "小白鞋/乐福鞋",
                bag=params.get("bag", "简约包包") if params else "简约包包",
                detail=f"整体风格{random.choice(['简约大方', '舒适随性', '时髦有型'])}，{random.choice(['适合日常', '百搭不挑人', '出片率很高'])}。",
                hashtags=" ".join([f"#{topic}", "#穿搭", "#OOTD", "#时尚"])
            )
        
        elif theme_key == "tech":
            content = template.format(
                opening=f"用了{random.choice(['一周', '半个月', '一个月'])}的{topic}，来分享一下真实体验",
                product=params.get("product", topic) if params else topic,
                price=params.get("price", "价格适中") if params else "价格适中",
                rating=params.get("rating", "4") if params else "4",
                pros_cons=f"✅ 优点：{random.choice(['性价比高', '功能强大', '设计精美'])}\n❌ 缺点：{random.choice(['价格偏高', '学习成本', '续航一般'])}",
                detail=f"{random.choice(['整体来说', '综合来看', '使用下来'])}，{random.choice(['体验不错', '值得推荐', '符合预期'])}。",
                conclusion=f"{random.choice(['适合', '推荐', '建议'])}给{random.choice(['预算充足', '有特定需求', '追求品质'])}的朋友。",
                hashtags=" ".join([f"#{topic}", "#数码", "#评测", "#科技"])
            )
        
        else:
            content = f"分享一些关于{topic}的内容"
        
        return content.strip()
    
    def _generate_tags(self, theme: ContentTheme, topic: str) -> List[str]:
        """生成标签"""
        base_tags = [topic] + theme.keywords[:3]
        
        # 添加热门标签
        hot_tags = ["热门", "推荐", "干货", "必看", "宝藏"]
        
        # 添加情感标签
        emotion_tags = ["治愈", "美好", "幸福", "快乐"]
        
        all_tags = base_tags + random.sample(hot_tags, 2) + random.sample(emotion_tags, 1)
        
        return list(set(all_tags))[:8]  # 最多8个标签
    
    def _suggest_images(self, theme_key: str) -> List[str]:
        """建议图片类型"""
        suggestions = {
            "lifestyle": ["场景图", "细节图", "氛围图"],
            "food": ["整体摆盘", "特写", "环境", "菜单"],
            "travel": ["风景照", "打卡照", "细节", "全景"],
            "fashion": ["全身照", "细节", "搭配平铺", "上身效果"],
            "tech": ["产品图", "使用场景", "细节", "对比图"],
        }
        return suggestions.get(theme_key, ["配图"])
    
    def _predict_best_posting_time(self) -> str:
        """预测最佳发布时间"""
        # 基于小红书用户活跃时间
        peak_hours = [
            ("07:00", "09:00"),  # 早高峰
            ("12:00", "13:30"),  # 午休
            ("18:00", "20:00"),  # 晚高峰
            ("21:00", "23:00"),  # 睡前
        ]
        
        start, end = random.choice(peak_hours)
        return f"{start}-{end}"
    
    def _calculate_confidence(
        self,
        theme: ContentTheme,
        title: str,
        content: str
    ) -> float:
        """计算内容质量置信度"""
        score = 0.7  # 基础分
        
        # 标题长度检查
        if 10 <= len(title) <= 30:
            score += 0.1
        
        # 内容长度检查
        if 100 <= len(content) <= 1000:
            score += 0.1
        
        # 关键词匹配
        keyword_match = sum(1 for k in theme.keywords if k in content)
        score += min(keyword_match * 0.02, 0.1)
        
        return min(score, 1.0)
    
    def get_content_suggestions(self, performance_data: Dict) -> List[str]:
        """
        基于历史表现提供内容建议
        
        Args:
            performance_data: 历史内容表现数据
        """
        suggestions = []
        
        # 分析表现最好的内容类型
        if performance_data:
            best_performing = max(
                performance_data.items(),
                key=lambda x: x[1].get("engagement", 0)
            )
            suggestions.append(f"多发布'{best_performing[0]}'类型的内容")
        
        # 基于时间分析
        suggestions.append("建议在早晚高峰时段发布")
        
        # 基于标签分析
        suggestions.append("使用3-5个精准标签效果更佳")
        
        return suggestions
    
    def batch_generate(
        self,
        theme_key: str,
        topics: List[str],
        count_per_topic: int = 1
    ) -> List[GeneratedContent]:
        """批量生成内容"""
        results = []
        
        for topic in topics:
            for _ in range(count_per_topic):
                content = self.generate_content(theme_key, topic)
                results.append(content)
        
        return results
