"""
耄耋Official Bot - 测试模式
不实际登录小红书，只测试猫的逻辑
"""
import asyncio
import random
from datetime import datetime


class CatLogic:
    """猫的逻辑引擎（测试版）"""

    @staticmethod
    def should_post() -> bool:
        """猫要不要发内容？"""
        hour = datetime.now().hour
        if 8 <= hour < 18:
            return random.random() < 0.05       # 白天5%
        elif 18 <= hour < 23:
            return random.random() < 0.15       # 傍晚15%
        elif 23 <= hour or hour < 2:
            return random.random() < 0.35       # 深夜35%
        else:
            return random.random() < 0.7        # 凌晨2-4点70%

    @staticmethod
    def should_reply_comment(comment_text: str = "") -> bool:
        """猫要不要回复评论？"""
        if len(comment_text) > 50:
            return random.random() < 0.02       # 长评论几乎不回
        hour = datetime.now().hour
        if 8 <= hour < 18:
            return random.random() < 0.03       # 白天3%
        elif 23 <= hour or hour < 4:
            return random.random() < 0.15       # 深夜15%
        return random.random() < 0.08

    @staticmethod
    def should_reply_dm(dm_text: str = "") -> bool:
        """猫要不要回复私聊？"""
        return random.random() < 0.03

    @staticmethod
    def get_reply() -> str:
        """猫回复什么？"""
        replies = ["哈", "哈哈", "哈哈哈", "哈。", ".."]
        return random.choice(replies)

    @staticmethod
    def get_post_text() -> str:
        """猫发什么文字？"""
        r = random.random()
        if r < 0.7:
            return ""                            # 70%不配文
        elif r < 0.9:
            return random.choice(["哈", "哈哈", "哈哈哈"])
        else:
            return "哈" * random.randint(5, 20)

    @staticmethod
    def get_tags() -> list:
        """猫带什么标签？"""
        if random.random() < 0.3:
            return []
        return random.sample(
            ["耄耋", "圆头耄耋", "哈人", "抽象"],
            k=random.randint(1, 2)
        )

    @staticmethod
    def get_sleep_seconds() -> int:
        """猫的检查间隔"""
        hour = datetime.now().hour
        if 8 <= hour < 18:
            return random.randint(600, 1800)     # 白天10-30分钟
        elif 2 <= hour < 4:
            return random.randint(60, 300)       # 疯狂时间1-5分钟
        else:
            return random.randint(180, 600)      # 其他3-10分钟


class TestBot:
    """测试版Bot"""

    def __init__(self):
        self.is_running = False
        self.post_count = 0
        self.reply_count = 0
        self.dm_count = 0

    async def start(self):
        """启动测试"""
        print("🐱 耄耋Official - 测试模式")
        print("=" * 50)
        print("⚠️  这是测试模式，不会实际登录小红书")
        print("   只测试猫的逻辑决策")
        print("=" * 50)
        print()

        self.is_running = True

        # 模拟运行10轮
        for i in range(10):
            if not self.is_running:
                break

            await self._run_cycle(i + 1)
            await asyncio.sleep(2)  # 测试间隔2秒

        print()
        print("=" * 50)
        print("📊 测试完成！统计：")
        print(f"   发帖次数: {self.post_count}")
        print(f"   回复评论: {self.reply_count}")
        print(f"   回复私聊: {self.dm_count}")
        print("=" * 50)

    async def _run_cycle(self, cycle: int):
        """运行一轮测试"""
        hour = datetime.now().hour
        mood = self._get_mood_emoji(hour)

        print(f"\n[{cycle}/10] 🐱 [{datetime.now().strftime('%H:%M:%S')}] 状态: {mood}")
        print("-" * 50)

        # 测试发帖
        if CatLogic.should_post():
            text = CatLogic.get_post_text()
            tags = CatLogic.get_tags()
            print(f"📤 发帖: 文字='{text or '(纯图)'}' 标签={tags}")
            self.post_count += 1
        else:
            print(f"📤 发帖: 猫不想发")

        # 测试回复评论
        test_comments = [
            "好可爱！",
            "哈哈哈哈",
            "这是什么梗？",
            "太搞笑了" + "！" * 100,
        ]
        for comment in test_comments:
            if CatLogic.should_reply_comment(comment):
                reply = CatLogic.get_reply()
                print(f"💬 回复: '{comment[:20]}...' → '{reply}'")
                self.reply_count += 1
            else:
                print(f"💬 回复: '{comment[:20]}...' → (猫不理)")

        # 测试回复私聊
        if CatLogic.should_reply_dm():
            reply = CatLogic.get_reply()
            print(f"📨 私聊回复: '{reply}'")
            self.dm_count += 1
        else:
            print(f"📨 私聊: 猫不想回")

        sleep_time = CatLogic.get_sleep_seconds()
        print(f"😴 休息 {sleep_time} 秒")

    def _get_mood_emoji(self, hour: int) -> str:
        """获取心情emoji"""
        if 2 <= hour < 4:
            return "😹 疯狂时间"
        elif 4 <= hour < 8:
            return "😼 还没睡"
        elif 8 <= hour < 18:
            return "😴 睡觉中"
        elif 18 <= hour < 23:
            return "😺 醒来了"
        else:
            return "🙀 深夜活跃"


if __name__ == "__main__":
    bot = TestBot()
    asyncio.run(bot.start())
