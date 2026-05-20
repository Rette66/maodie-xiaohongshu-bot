"""
耄臲Official - 猫的发布调度器
核心思想：猫想发就发，不想发就不发

配置化：通过 configs/cat_personality.json 配置猫的作息
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from configs.personality_loader import get_cat_config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False


class CatActivity(Enum):
    """猫的活动状态"""
    SLEEPING = "sleeping"       # 睡觉
    WAKING = "waking"           # 醒来
    ACTIVE = "active"           # 活跃
    CRAZY = "crazy"             # 发疯
    HUNTING = "hunting"         # 狩猎（互动）
    IGNORING = "ignoring"       # 不理你


@dataclass
class CatSchedule:
    """猫的日程"""
    activity: CatActivity
    start_hour: int
    end_hour: int
    post_probability: float
    reply_probability: float


# 默认的猫作息表（配置文件缺失时使用）
DEFAULT_CAT_SCHEDULES = [
    CatSchedule(CatActivity.CRAZY, 2, 4, 0.8, 0.2),
    CatSchedule(CatActivity.ACTIVE, 4, 6, 0.3, 0.15),
    CatSchedule(CatActivity.WAKING, 6, 8, 0.1, 0.05),
    CatSchedule(CatActivity.SLEEPING, 8, 12, 0.02, 0.01),
    CatSchedule(CatActivity.SLEEPING, 12, 14, 0.03, 0.02),
    CatSchedule(CatActivity.SLEEPING, 14, 18, 0.02, 0.01),
    CatSchedule(CatActivity.WAKING, 18, 20, 0.1, 0.05),
    CatSchedule(CatActivity.ACTIVE, 20, 23, 0.15, 0.1),
    CatSchedule(CatActivity.ACTIVE, 23, 24, 0.3, 0.15),
    CatSchedule(CatActivity.CRAZY, 0, 2, 0.5, 0.2),
]


def _load_schedules_from_config() -> List[CatSchedule]:
    """从配置加载猫的作息表"""
    if not HAS_CONFIG:
        return DEFAULT_CAT_SCHEDULES

    try:
        cfg = get_cat_config()
        schedules = []
        for entry in cfg.post.schedule:
            activity_map = {
                "sleeping": CatActivity.SLEEPING,
                "waking": CatActivity.WAKING,
                "active": CatActivity.ACTIVE,
                "crazy": CatActivity.CRAZY,
            }
            activity = activity_map.get(entry.activity, CatActivity.ACTIVE)
            schedules.append(CatSchedule(
                activity=activity,
                start_hour=entry.hour_start,
                end_hour=entry.hour_end,
                post_probability=entry.probability,
                reply_probability=entry.probability * 0.25,  # 回复概率约为发布的1/4
            ))
        return schedules if schedules else DEFAULT_CAT_SCHEDULES
    except Exception:
        return DEFAULT_CAT_SCHEDULES


# 从配置加载（如果可用）
CAT_SCHEDULES = _load_schedules_from_config()


class CatScheduler:
    """
    猫的调度器

    猫的作息（从配置读取）：
    - 白天睡觉（8:00-18:00）
    - 傍晚醒来（18:00-23:00）
    - 深夜活跃（23:00-4:00）
    - 凌晨发疯（2:00-4:00）
    """

    def __init__(self):
        self.current_activity = CatActivity.SLEEPING
        self.is_running = False
        self.post_handlers: Dict[str, Callable] = {}

    def get_current_schedule(self) -> CatSchedule:
        """获取当前时段的日程"""
        hour = datetime.now().hour

        for schedule in CAT_SCHEDULES:
            if schedule.start_hour <= hour < schedule.end_hour:
                return schedule

        return CAT_SCHEDULES[0]  # 默认

    def get_activity(self) -> CatActivity:
        """获取当前活动状态"""
        return self.get_current_schedule().activity

    def should_post(self) -> bool:
        """猫要不要发内容？"""
        schedule = self.get_current_schedule()
        return random.random() < schedule.post_probability

    def should_reply(self) -> bool:
        """猫要不要回复？"""
        schedule = self.get_current_schedule()
        return random.random() < schedule.reply_probability

    def get_next_post_time(self) -> Optional[datetime]:
        """
        预测下次发布时间

        猫的逻辑：想发就发，所以这个只是参考
        """
        now = datetime.now()

        # 如果是白天，等到傍晚
        if 8 <= now.hour < 18:
            next_time = now.replace(hour=18, minute=0, second=0)
            delay = random.randint(0, 180)
            next_time += timedelta(minutes=delay)
            return next_time

        if random.random() < 0.3:
            delay = random.randint(60, 180)
            return now + timedelta(minutes=delay)

        if now.hour < 23:
            next_time = now.replace(hour=23, minute=random.randint(0, 59))
            return next_time
        else:
            delay = random.randint(30, 120)
            return now + timedelta(minutes=delay)

    def reload_schedules(self):
        """热重载猫的作息表（从配置重新读取）"""
        global CAT_SCHEDULES
        CAT_SCHEDULES = _load_schedules_from_config()

    async def run_cat_loop(self, post_callback: Callable, check_interval: int = 300):
        """
        运行猫的循环

        Args:
            post_callback: 发布回调函数
            check_interval: 检查间隔（秒），默认5分钟
        """
        self.is_running = True

        print("🐱 猫开始运行了...")

        while self.is_running:
            try:
                activity = self.get_activity()
                if activity != self.current_activity:
                    self.current_activity = activity
                    print(f"😺 猫现在的状态: {activity.value}")

                if self.should_post():
                    print("🐱 猫想发内容了！")
                    await post_callback()

                sleep_time = self._get_sleep_time()
                await asyncio.sleep(sleep_time)

            except Exception as e:
                print(f"❌ 猫出错了: {e}")
                await asyncio.sleep(60)

    def _get_sleep_time(self) -> int:
        """获取睡眠时间（秒）"""
        activity = self.get_activity()

        if not HAS_CONFIG:
            # 默认值
            if activity == CatActivity.SLEEPING:
                return random.randint(600, 1800)
            elif activity == CatActivity.CRAZY:
                return random.randint(60, 300)
            else:
                return random.randint(300, 600)

        try:
            cfg = get_cat_config()
            if activity == CatActivity.SLEEPING:
                return random.randint(cfg.sleep_seconds.sleeping_min, cfg.sleep_seconds.sleeping_max)
            elif activity == CatActivity.CRAZY:
                return random.randint(cfg.sleep_seconds.crazy_min, cfg.sleep_seconds.crazy_max)
            else:
                return random.randint(cfg.sleep_seconds.normal_min, cfg.sleep_seconds.normal_max)
        except Exception:
            return random.randint(300, 600)

    def stop(self):
        """停止猫的循环"""
        self.is_running = False
        print("🐱 猫去睡觉了...")

    def get_status_report(self) -> str:
        """获取状态报告"""
        schedule = self.get_current_schedule()
        now = datetime.now()

        report = f"""
🐱 耄臲Official 状态报告
━━━━━━━━━━━━━━━━━━━━━━━━━━
当前时间: {now.strftime('%Y-%m-%d %H:%M')}
猫的状态: {schedule.activity.value}
发布概率: {schedule.post_probability:.0%}
回复概率: {schedule.reply_probability:.0%}

猫的作息（从配置读取）:
  08:00-18:00  😴 睡觉
  18:00-23:00  😺 醒来观察
  23:00-02:00  😼 深夜活跃
  02:00-04:00  😹 疯狂时间
━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        return report


# ==================== 使用示例 ====================

async def example_post():
    """示例发布函数"""
    print("  → 发了一条内容：哈")


async def main():
    """测试猫的调度器"""
    scheduler = CatScheduler()

    print(scheduler.get_status_report())

    for i in range(10):
        activity = scheduler.get_activity()
        should_post = scheduler.should_post()
        next_time = scheduler.get_next_post_time()

        print(f"[{i+1}] 状态: {activity.value}, 发? {should_post}")
        if next_time:
            print(f"    预计下次: {next_time.strftime('%H:%M')}")

        await asyncio.sleep(1)


if __name__ == "__main__":
    from pathlib import Path
    asyncio.run(main())

    # 实际运行（取消注释）
    # scheduler = CatScheduler()
    # asyncio.run(scheduler.run_cat_loop(example_post))