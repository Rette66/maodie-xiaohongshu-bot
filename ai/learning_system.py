"""
自适应学习系统 - 持续优化运营策略
"""
import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


@dataclass
class PerformanceMetrics:
    """性能指标"""
    timestamp: str
    content_type: str
    likes: int
    comments: int
    shares: int
    views: int
    engagement_rate: float
    follower_change: int
    
    def total_engagement(self) -> int:
        return self.likes + self.comments + self.shares


@dataclass
class LearnedStrategy:
    """学习到的策略"""
    strategy_id: str
    content_theme: str
    posting_time: str
    tags: List[str]
    success_rate: float
    avg_engagement: float
    usage_count: int
    last_used: str


class AdaptiveLearningSystem:
    """
    自适应学习系统
    
    功能：
    - 分析内容表现数据
    - 识别成功模式
    - 自动优化策略
    - A/B测试支持
    """
    
    def __init__(self, data_dir: str = "data/learning"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 性能历史
        self.performance_history: List[PerformanceMetrics] = []
        
        # 学习到的策略
        self.learned_strategies: List[LearnedStrategy] = []
        
        # 主题表现统计
        self.theme_performance: Dict[str, List[PerformanceMetrics]] = defaultdict(list)
        
        # 时段表现统计
        self.time_performance: Dict[str, List[PerformanceMetrics]] = defaultdict(list)
        
        # 标签效果统计
        self.tag_performance: Dict[str, List[PerformanceMetrics]] = defaultdict(list)
        
        # 加载历史数据
        self._load_data()
    
    def record_performance(self, metrics: PerformanceMetrics):
        """记录性能数据"""
        self.performance_history.append(metrics)
        
        # 更新主题统计
        self.theme_performance[metrics.content_type].append(metrics)
        
        # 更新时段统计
        hour = datetime.fromisoformat(metrics.timestamp).hour
        self.time_performance[str(hour)].append(metrics)
        
        # 触发学习
        self._learn_from_data()
        
        # 保存数据
        self._save_data()
    
    def _learn_from_data(self):
        """从数据中学习"""
        if len(self.performance_history) < 5:
            return
        
        # 分析主题表现
        self._analyze_theme_performance()
        
        # 分析最佳发布时间
        self._analyze_optimal_timing()
        
        # 分析标签效果
        self._analyze_tag_effectiveness()
        
        # 生成优化策略
        self._generate_strategies()
    
    def _analyze_theme_performance(self):
        """分析主题表现"""
        print("📊 分析主题表现...")
        
        theme_stats = {}
        for theme, metrics_list in self.theme_performance.items():
            if len(metrics_list) < 3:
                continue
            
            avg_engagement = np.mean([m.engagement_rate for m in metrics_list])
            avg_likes = np.mean([m.likes for m in metrics_list])
            
            theme_stats[theme] = {
                "avg_engagement": avg_engagement,
                "avg_likes": avg_likes,
                "count": len(metrics_list)
            }
        
        # 找出表现最好的主题
        if theme_stats:
            best_theme = max(theme_stats.items(), key=lambda x: x[1]["avg_engagement"])
            print(f"  🏆 最佳主题: {best_theme[0]} (互动率: {best_theme[1]['avg_engagement']:.3f})")
    
    def _analyze_optimal_timing(self):
        """分析最佳发布时间"""
        print("📊 分析最佳发布时间...")
        
        time_stats = {}
        for hour, metrics_list in self.time_performance.items():
            if len(metrics_list) < 2:
                continue
            
            avg_engagement = np.mean([m.engagement_rate for m in metrics_list])
            time_stats[int(hour)] = avg_engagement
        
        if time_stats:
            # 找出表现最好的时段
            best_hours = sorted(time_stats.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"  🕐 最佳时段: {[f'{h}:00' for h, _ in best_hours]}")
    
    def _analyze_tag_effectiveness(self):
        """分析标签效果"""
        print("📊 分析标签效果...")
        
        tag_stats = {}
        for tag, metrics_list in self.tag_performance.items():
            if len(metrics_list) < 2:
                continue
            
            avg_engagement = np.mean([m.engagement_rate for m in metrics_list])
            tag_stats[tag] = avg_engagement
        
        if tag_stats:
            best_tags = sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"  🏷️ 最佳标签: {[tag for tag, _ in best_tags]}")
    
    def _generate_strategies(self):
        """生成优化策略"""
        print("🎯 生成优化策略...")
        
        # 基于分析结果生成策略
        for theme, metrics_list in self.theme_performance.items():
            if len(metrics_list) < 5:
                continue
            
            # 计算成功率
            successful = sum(1 for m in metrics_list if m.engagement_rate > 0.05)
            success_rate = successful / len(metrics_list)
            
            # 计算平均互动
            avg_engagement = np.mean([m.engagement_rate for m in metrics_list])
            
            # 找出该主题的最佳时段
            best_hour = self._find_best_hour_for_theme(theme)
            
            # 创建策略
            strategy = LearnedStrategy(
                strategy_id=f"{theme}_{datetime.now().strftime('%Y%m%d')}",
                content_theme=theme,
                posting_time=f"{best_hour}:00" if best_hour else "12:00",
                tags=self._get_recommended_tags(theme),
                success_rate=success_rate,
                avg_engagement=avg_engagement,
                usage_count=0,
                last_used=datetime.now().isoformat()
            )
            
            # 更新或添加策略
            existing = [s for s in self.learned_strategies if s.content_theme == theme]
            if existing:
                self.learned_strategies.remove(existing[0])
            
            self.learned_strategies.append(strategy)
            
            print(f"  ✅ 生成策略: {theme} (成功率: {success_rate:.2f})")
    
    def _find_best_hour_for_theme(self, theme: str) -> Optional[int]:
        """找出主题的最佳发布时段"""
        hour_performance = {}
        
        for hour, metrics_list in self.time_performance.items():
            theme_metrics = [m for m in metrics_list if m.content_type == theme]
            if theme_metrics:
                avg_engagement = np.mean([m.engagement_rate for m in theme_metrics])
                hour_performance[int(hour)] = avg_engagement
        
        if hour_performance:
            return max(hour_performance.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _get_recommended_tags(self, theme: str) -> List[str]:
        """获取推荐标签"""
        # 基于该主题的历史表现选择标签
        theme_metrics = self.theme_performance.get(theme, [])
        
        # 这里简化处理，实际应该分析哪些标签带来了更好的表现
        base_tags = {
            "lifestyle": ["生活", "日常", "分享"],
            "food": ["美食", "探店", "吃货"],
            "travel": ["旅行", "攻略", "打卡"],
            "fashion": ["穿搭", "OOTD", "时尚"],
            "tech": ["数码", "评测", "科技"],
        }
        
        return base_tags.get(theme, ["分享", "生活"])
    
    def get_recommendations(self, context: Dict) -> Dict:
        """
        获取个性化推荐
        
        Args:
            context: 当前上下文
                {
                    "follower_count": int,
                    "account_age_days": int,
                    "recent_performance": List[PerformanceMetrics]
                }
        """
        recommendations = {
            "content_theme": None,
            "posting_time": None,
            "tags": [],
            "confidence": 0.0
        }
        
        follower_count = context.get("follower_count", 0)
        
        # 根据粉丝数选择策略
        if follower_count < 1000:
            # 新账号策略
            recommendations["content_theme"] = self._get_best_theme_for_new_account()
        else:
            # 基于历史表现选择
            recommendations["content_theme"] = self._get_best_theme_overall()
        
        # 选择最佳发布时间
        recommendations["posting_time"] = self._get_optimal_posting_time()
        
        # 推荐标签
        if recommendations["content_theme"]:
            recommendations["tags"] = self._get_recommended_tags(
                recommendations["content_theme"]
            )
        
        # 计算置信度
        recommendations["confidence"] = self._calculate_confidence(recommendations)
        
        return recommendations
    
    def _get_best_theme_for_new_account(self) -> Optional[str]:
        """获取适合新账号的主题"""
        # 新账号应该选择竞争较小但容易获得互动的主题
        theme_scores = {}
        
        for theme, metrics_list in self.theme_performance.items():
            if len(metrics_list) < 3:
                continue
            
            # 新账号更关注互动率而不是绝对数量
            avg_engagement = np.mean([m.engagement_rate for m in metrics_list])
            
            # 考虑内容数量（避免过度竞争的领域）
            content_count = len(metrics_list)
            competition_factor = 1 / (1 + content_count / 10)
            
            theme_scores[theme] = avg_engagement * competition_factor
        
        if theme_scores:
            return max(theme_scores.items(), key=lambda x: x[1])[0]
        
        return "lifestyle"  # 默认主题
    
    def _get_best_theme_overall(self) -> Optional[str]:
        """获取整体表现最好的主题"""
        if not self.learned_strategies:
            return None
        
        best_strategy = max(
            self.learned_strategies,
            key=lambda s: s.avg_engagement
        )
        
        return best_strategy.content_theme
    
    def _get_optimal_posting_time(self) -> str:
        """获取最佳发布时间"""
        if not self.time_performance:
            return "12:00"
        
        # 计算每个时段的平均表现
        hour_scores = {}
        for hour, metrics_list in self.time_performance.items():
            if len(metrics_list) >= 2:
                avg_engagement = np.mean([m.engagement_rate for m in metrics_list])
                hour_scores[int(hour)] = avg_engagement
        
        if hour_scores:
            best_hour = max(hour_scores.items(), key=lambda x: x[1])[0]
            return f"{best_hour:02d}:00"
        
        return "12:00"
    
    def _calculate_confidence(self, recommendations: Dict) -> float:
        """计算推荐置信度"""
        confidence = 0.5  # 基础置信度
        
        # 基于历史数据量调整
        total_records = len(self.performance_history)
        if total_records > 50:
            confidence += 0.2
        elif total_records > 20:
            confidence += 0.1
        
        # 基于策略成功率调整
        if recommendations.get("content_theme"):
            theme = recommendations["content_theme"]
            strategies = [s for s in self.learned_strategies if s.content_theme == theme]
            if strategies:
                confidence += strategies[0].success_rate * 0.2
        
        return min(confidence, 1.0)
    
    def run_ab_test(
        self,
        variant_a: Dict,
        variant_b: Dict,
        duration_days: int = 7
    ) -> Dict:
        """
        运行A/B测试
        
        Args:
            variant_a: 变体A配置
            variant_b: 变体B配置
            duration_days: 测试持续时间
        """
        print(f"🧪 启动A/B测试 (持续{duration_days}天)")
        print(f"  变体A: {variant_a}")
        print(f"  变体B: {variant_b}")
        
        # 这里应该实际执行测试并收集数据
        # 简化版本，仅返回测试配置
        return {
            "test_id": f"ab_test_{datetime.now().strftime('%Y%m%d')}",
            "variant_a": variant_a,
            "variant_b": variant_b,
            "duration_days": duration_days,
            "status": "started"
        }
    
    def generate_insights_report(self) -> str:
        """生成洞察报告"""
        if not self.performance_history:
            return "暂无足够数据生成报告"
        
        # 计算关键指标
        total_posts = len(self.performance_history)
        avg_engagement = np.mean([m.engagement_rate for m in self.performance_history])
        total_likes = sum(m.likes for m in self.performance_history)
        
        # 趋势分析
        recent = self.performance_history[-10:]
        older = self.performance_history[-20:-10] if len(self.performance_history) >= 20 else []
        
        recent_avg = np.mean([m.engagement_rate for m in recent]) if recent else 0
        older_avg = np.mean([m.engagement_rate for m in older]) if older else recent_avg
        
        trend = "📈 上升" if recent_avg > older_avg * 1.1 else "📉 下降" if recent_avg < older_avg * 0.9 else "➡️ 平稳"
        
        report = f"""
📊 自适应学习系统洞察报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 整体表现:
  - 总发布数: {total_posts}
  - 平均互动率: {avg_engagement:.3f}
  - 总获赞数: {total_likes}
  - 趋势: {trend}

🎯 最佳策略:
"""
        
        # 添加最佳策略
        sorted_strategies = sorted(
            self.learned_strategies,
            key=lambda s: s.avg_engagement,
            reverse=True
        )[:3]
        
        for i, strategy in enumerate(sorted_strategies, 1):
            report += f"""
  {i}. {strategy.content_theme}
     - 成功率: {strategy.success_rate:.1%}
     - 平均互动: {strategy.avg_engagement:.3f}
     - 推荐时间: {strategy.posting_time}
"""
        
        report += f"""
💡 优化建议:
  1. 在最佳时段发布内容
  2. 多使用表现好的标签
  3. 保持内容主题一致性
  4. 持续记录数据以优化策略

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        return report
    
    def _load_data(self):
        """加载学习数据"""
        # 加载性能历史
        history_file = self.data_dir / "performance_history.json"
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.performance_history = [
                    PerformanceMetrics(**m) for m in data
                ]
        
        # 加载策略
        strategies_file = self.data_dir / "learned_strategies.json"
        if strategies_file.exists():
            with open(strategies_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.learned_strategies = [
                    LearnedStrategy(**s) for s in data
                ]
    
    def _save_data(self):
        """保存学习数据"""
        # 保存性能历史
        history_file = self.data_dir / "performance_history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(
                [asdict(m) for m in self.performance_history[-500:]],
                f,
                ensure_ascii=False,
                indent=2
            )
        
        # 保存策略
        strategies_file = self.data_dir / "learned_strategies.json"
        with open(strategies_file, 'w', encoding='utf-8') as f:
            json.dump(
                [asdict(s) for s in self.learned_strategies],
                f,
                ensure_ascii=False,
                indent=2
            )
