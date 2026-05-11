"""
智能决策引擎 - 基于数据驱动的决策系统
"""
import json
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path


@dataclass
class DecisionContext:
    """决策上下文"""
    account_age_days: int
    follower_count: int
    recent_engagement_rate: float
    content_performance: Dict
    time_of_day: int
    day_of_week: int
    daily_actions_taken: Dict


@dataclass
class ActionDecision:
    """行动决策"""
    action_type: str
    priority: int
    parameters: Dict
    expected_outcome: float
    confidence: float
    reasoning: str


class DecisionEngine:
    """
    智能决策引擎
    
    功能：
    - 基于历史数据做决策
    - 动态调整操作策略
    - 预测最佳行动时机
    - 风险评估和控制
    """
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 加载历史决策数据
        self.decision_history = self._load_decision_history()
        
        # 策略参数
        self.strategy_params = {
            "base_like_probability": 0.7,
            "base_comment_probability": 0.3,
            "base_follow_probability": 0.1,
            "engagement_threshold_high": 0.1,
            "engagement_threshold_low": 0.02,
        }
        
        # 学习到的最佳实践
        self.learned_patterns = self._load_learned_patterns()
    
    def make_interaction_decision(
        self,
        context: DecisionContext,
        target_content: Optional[Dict] = None
    ) -> List[ActionDecision]:
        """
        做出互动决策
        
        Args:
            context: 当前决策上下文
            target_content: 目标内容信息
        
        Returns:
            决策列表
        """
        decisions = []
        
        # 1. 评估是否应该互动
        should_interact = self._evaluate_interaction_necessity(context)
        
        if not should_interact:
            return [ActionDecision(
                action_type="skip",
                priority=0,
                parameters={},
                expected_outcome=0.0,
                confidence=1.0,
                reasoning="当前不适合互动"
            )]
        
        # 2. 决定互动类型
        # 点赞决策
        like_decision = self._decide_like(context, target_content)
        if like_decision:
            decisions.append(like_decision)
        
        # 评论决策
        comment_decision = self._decide_comment(context, target_content)
        if comment_decision:
            decisions.append(comment_decision)
        
        # 关注决策
        follow_decision = self._decide_follow(context, target_content)
        if follow_decision:
            decisions.append(follow_decision)
        
        # 按优先级排序
        decisions.sort(key=lambda x: x.priority, reverse=True)
        
        return decisions
    
    def make_content_decision(
        self,
        context: DecisionContext,
        available_themes: List[str]
    ) -> ActionDecision:
        """
        做出内容发布决策
        
        Args:
            context: 决策上下文
            available_themes: 可用主题列表
        """
        # 分析历史表现最好的主题
        best_theme = self._analyze_best_performing_theme(context.content_performance)
        
        # 选择主题
        if best_theme and best_theme in available_themes:
            selected_theme = best_theme
            confidence = 0.8
        else:
            selected_theme = random.choice(available_themes)
            confidence = 0.5
        
        # 决定发布时间
        best_time = self._predict_optimal_posting_time(context)
        
        return ActionDecision(
            action_type="publish",
            priority=8,
            parameters={
                "theme": selected_theme,
                "optimal_time": best_time,
                "content_count": self._decide_content_count(context)
            },
            expected_outcome=0.75 if confidence > 0.7 else 0.5,
            confidence=confidence,
            reasoning=f"选择'{selected_theme}'主题，基于历史表现分析"
        )
    
    def make_timing_decision(
        self,
        context: DecisionContext,
        action_type: str
    ) -> ActionDecision:
        """
        做出时机决策
        
        Args:
            context: 决策上下文
            action_type: 行动类型
        """
        # 分析当前时段的活跃度
        current_hour = context.time_of_day
        
        # 高峰时段
        peak_hours = [7, 8, 12, 13, 18, 19, 20, 21, 22]
        
        if current_hour in peak_hours:
            urgency = "high"
            expected_reach = 0.8
        elif 9 <= current_hour <= 17:
            urgency = "medium"
            expected_reach = 0.5
        else:
            urgency = "low"
            expected_reach = 0.3
        
        # 根据账号阶段调整
        if context.follower_count < 1000:
            # 新账号，更积极
            should_act = True
            priority = 9
        elif context.follower_count < 10000:
            # 成长期
            should_act = urgency != "low"
            priority = 7
        else:
            # 成熟期，更谨慎
            should_act = urgency == "high"
            priority = 5
        
        return ActionDecision(
            action_type=action_type if should_act else "wait",
            priority=priority,
            parameters={
                "urgency": urgency,
                "expected_reach": expected_reach,
                "current_hour": current_hour
            },
            expected_outcome=expected_reach,
            confidence=0.7,
            reasoning=f"当前时段活跃度: {urgency}"
        )
    
    def _evaluate_interaction_necessity(self, context: DecisionContext) -> bool:
        """评估是否需要互动"""
        # 检查每日限额
        if context.daily_actions_taken.get("likes", 0) >= 100:
            return False
        
        # 检查账号状态
        if context.follower_count < 100:
            # 新账号，需要更多互动
            return True
        
        # 检查最近的互动率
        if context.recent_engagement_rate < 0.01:
            # 互动率太低，需要增加互动
            return True
        
        # 基于时间判断
        if context.time_of_day in [7, 8, 12, 13, 18, 19, 20, 21]:
            return True
        
        return random.random() < 0.3
    
    def _decide_like(
        self,
        context: DecisionContext,
        target_content: Optional[Dict]
    ) -> Optional[ActionDecision]:
        """决定是否点赞"""
        base_prob = self.strategy_params["base_like_probability"]
        
        # 根据互动率调整
        if context.recent_engagement_rate > 0.05:
            base_prob += 0.1
        elif context.recent_engagement_rate < 0.02:
            base_prob -= 0.2
        
        # 根据目标内容调整
        if target_content:
            content_quality = target_content.get("quality_score", 0.5)
            base_prob *= (0.5 + content_quality)
        
        # 根据账号阶段调整
        if context.follower_count < 1000:
            base_prob = min(base_prob * 1.2, 0.9)
        
        if random.random() < base_prob:
            return ActionDecision(
                action_type="like",
                priority=5,
                parameters={"probability": base_prob},
                expected_outcome=0.3,
                confidence=base_prob,
                reasoning=f"点赞概率: {base_prob:.2f}"
            )
        
        return None
    
    def _decide_comment(
        self,
        context: DecisionContext,
        target_content: Optional[Dict]
    ) -> Optional[ActionDecision]:
        """决定是否评论"""
        base_prob = self.strategy_params["base_comment_probability"]
        
        # 高质量内容更可能评论
        if target_content:
            content_quality = target_content.get("quality_score", 0.5)
            if content_quality > 0.8:
                base_prob += 0.2
        
        # 根据历史评论效果调整
        comment_success_rate = self._get_comment_success_rate()
        base_prob *= comment_success_rate
        
        # 控制频率
        recent_comments = context.daily_actions_taken.get("comments", 0)
        if recent_comments > 20:
            base_prob *= 0.5
        
        if random.random() < base_prob:
            comment_type = self._select_comment_type(target_content)
            return ActionDecision(
                action_type="comment",
                priority=7,
                parameters={
                    "probability": base_prob,
                    "comment_type": comment_type
                },
                expected_outcome=0.5,
                confidence=base_prob,
                reasoning=f"评论概率: {base_prob:.2f}, 类型: {comment_type}"
            )
        
        return None
    
    def _decide_follow(
        self,
        context: DecisionContext,
        target_content: Optional[Dict]
    ) -> Optional[ActionDecision]:
        """决定是否关注"""
        base_prob = self.strategy_params["base_follow_probability"]
        
        # 优质创作者更可能关注
        if target_content:
            author_quality = target_content.get("author_score", 0.5)
            content_relevance = target_content.get("relevance", 0.5)
            base_prob *= (author_quality * content_relevance)
        
        # 控制关注频率
        recent_follows = context.daily_actions_taken.get("follows", 0)
        if recent_follows > 10:
            base_prob *= 0.3
        
        if random.random() < base_prob:
            return ActionDecision(
                action_type="follow",
                priority=6,
                parameters={"probability": base_prob},
                expected_outcome=0.2,
                confidence=base_prob,
                reasoning=f"关注概率: {base_prob:.2f}"
            )
        
        return None
    
    def _analyze_best_performing_theme(self, performance: Dict) -> Optional[str]:
        """分析表现最好的主题"""
        if not performance:
            return None
        
        # 计算每个主题的平均表现
        theme_scores = {}
        for theme, data in performance.items():
            if isinstance(data, list) and len(data) > 0:
                avg_engagement = sum(d.get("engagement", 0) for d in data) / len(data)
                theme_scores[theme] = avg_engagement
        
        if theme_scores:
            return max(theme_scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _predict_optimal_posting_time(self, context: DecisionContext) -> str:
        """预测最佳发布时间"""
        # 基于目标受众的活跃时间
        if context.follower_count < 1000:
            # 新账号，选择竞争较小的时段
            options = ["10:00", "14:00", "16:00"]
        else:
            # 有一定粉丝基础，选择黄金时段
            options = ["07:30", "12:00", "18:30", "21:00"]
        
        return random.choice(options)
    
    def _decide_content_count(self, context: DecisionContext) -> int:
        """决定发布内容数量"""
        if context.follower_count < 500:
            return 1
        elif context.follower_count < 5000:
            return random.randint(1, 2)
        else:
            return random.randint(1, 3)
    
    def _select_comment_type(self, target_content: Optional[Dict]) -> str:
        """选择评论类型"""
        comment_types = [
            "appreciation",  # 赞赏
            "question",      # 提问
            "sharing",       # 分享经验
            "compliment",    #  compliment
        ]
        
        if target_content:
            content_type = target_content.get("type", "general")
            if content_type == "tutorial":
                return "appreciation"
            elif content_type == "question":
                return "sharing"
        
        return random.choice(comment_types)
    
    def _get_comment_success_rate(self) -> float:
        """获取评论成功率"""
        # 基于历史数据
        if not self.decision_history:
            return 0.5
        
        comment_decisions = [
            d for d in self.decision_history
            if d.get("action_type") == "comment"
        ]
        
        if not comment_decisions:
            return 0.5
        
        successful = sum(1 for d in comment_decisions if d.get("success", False))
        return successful / len(comment_decisions)
    
    def learn_from_outcome(
        self,
        decision: ActionDecision,
        outcome: Dict
    ):
        """
        从结果中学习
        
        Args:
            decision: 执行的决策
            outcome: 执行结果
        """
        # 记录决策和结果
        record = {
            "timestamp": datetime.now().isoformat(),
            "decision": {
                "action_type": decision.action_type,
                "parameters": decision.parameters,
                "confidence": decision.confidence
            },
            "outcome": outcome,
            "success": outcome.get("engagement_increase", 0) > 0
        }
        
        self.decision_history.append(record)
        
        # 更新策略参数
        self._update_strategy_params(decision, outcome)
        
        # 保存历史
        self._save_decision_history()
    
    def _update_strategy_params(
        self,
        decision: ActionDecision,
        outcome: Dict
    ):
        """更新策略参数"""
        engagement_increase = outcome.get("engagement_increase", 0)
        
        if decision.action_type == "like":
            if engagement_increase > 0.05:
                self.strategy_params["base_like_probability"] = min(
                    self.strategy_params["base_like_probability"] * 1.05,
                    0.9
                )
            elif engagement_increase < 0:
                self.strategy_params["base_like_probability"] *= 0.95
        
        elif decision.action_type == "comment":
            if engagement_increase > 0.1:
                self.strategy_params["base_comment_probability"] = min(
                    self.strategy_params["base_comment_probability"] * 1.1,
                    0.5
                )
    
    def _load_decision_history(self) -> List[Dict]:
        """加载决策历史"""
        history_file = self.data_dir / "decision_history.json"
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_decision_history(self):
        """保存决策历史"""
        history_file = self.data_dir / "decision_history.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.decision_history[-1000:], f, ensure_ascii=False, indent=2)
    
    def _load_learned_patterns(self) -> Dict:
        """加载学习到的模式"""
        patterns_file = self.data_dir / "learned_patterns.json"
        if patterns_file.exists():
            with open(patterns_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "best_posting_times": [],
            "high_performing_themes": [],
            "effective_comment_types": []
        }
    
    def generate_strategy_report(self) -> str:
        """生成策略报告"""
        total_decisions = len(self.decision_history)
        
        if total_decisions == 0:
            return "暂无决策数据"
        
        # 统计各类型决策
        action_counts = {}
        success_counts = {}
        
        for record in self.decision_history:
            action_type = record["decision"]["action_type"]
            action_counts[action_type] = action_counts.get(action_type, 0) + 1
            
            if record.get("success", False):
                success_counts[action_type] = success_counts.get(action_type, 0) + 1
        
        # 生成报告
        report = f"""
📊 智能决策引擎报告
━━━━━━━━━━━━━━━━━━━━━━━━━━━
总决策数: {total_decisions}

决策分布:
"""
        
        for action, count in action_counts.items():
            success = success_counts.get(action, 0)
            rate = success / count * 100 if count > 0 else 0
            report += f"  - {action}: {count}次 (成功率: {rate:.1f}%)\n"
        
        report += f"""
当前策略参数:
  - 点赞概率: {self.strategy_params['base_like_probability']:.2f}
  - 评论概率: {self.strategy_params['base_comment_probability']:.2f}
  - 关注概率: {self.strategy_params['base_follow_probability']:.2f}
━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        
        return report
