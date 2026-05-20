"""
耄耋Official - 全自动运营Bot
核心思想：让圆头耄耋本猫来运营这个账号

功能：
1. 自动发帖（表情包为主，猫的逻辑决定何时发、发什么）
2. 自动回复评论（大部分不回，偶尔回一个"哈"）
3. 自动回复私聊（几乎不回，偶尔回一个"哈"）
4. 全自动主循环（猫的作息：白天睡、深夜活跃）
"""
import asyncio
import random
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from playwright.async_api import Page, Browser_context


# 尝试导入配置加载器
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from configs.personality_loader import get_cat_config
    HAS_CONFIG = True
except ImportError:
    HAS_CONFIG = False


# ============================================================
# 配置
# ============================================================

IMAGE_FOLDER = "images/maodie"  # 表情包图片文件夹


def _get_cat_replies():
    """获取猫的回复话术（从配置）"""
    if not HAS_CONFIG:
        return ["哈", "哈哈", "哈哈哈", "哈。", ".."]
    try:
        return get_cat_config().reply.phrases.default
    except Exception:
        return ["哈", "哈哈", "哈哈哈", "哈。", ".."]


def _get_dm_replies():
    """获取猫的私聊回复话术（从配置）"""
    if not HAS_CONFIG:
        return ["哈", "哈哈", "..", "？", ""]
    try:
        return get_cat_config().reply.dm_phrases
    except Exception:
        return ["哈", "哈哈", "..", "？", ""]


# ============================================================
# 猫的逻辑引擎（轻量版，不依赖外部模块）
# ============================================================

class CatLogic:
    """猫的行为逻辑"""

    @staticmethod
    def should_post() -> bool:
        """猫要不要发内容？（从配置读取）"""
        if not HAS_CONFIG:
            hour = datetime.now().hour
            if 8 <= hour < 18:
                return random.random() < 0.05
            elif 18 <= hour < 23:
                return random.random() < 0.15
            elif 23 <= hour or hour < 2:
                return random.random() < 0.35
            else:
                return random.random() < 0.7
        try:
            cfg = get_cat_config()
            hour = datetime.now().hour
            for entry in cfg.post.schedule:
                if entry.hour_start <= hour < entry.hour_end:
                    return random.random() < entry.probability
            return False
        except Exception:
            return random.random() < 0.1

    @staticmethod
    def should_reply_comment(comment_text: str = "") -> bool:
        """猫要不要回复评论？（从配置读取）"""
        if not HAS_CONFIG:
            if len(comment_text) > 50:
                return random.random() < 0.02
            hour = datetime.now().hour
            if 8 <= hour < 18:
                return random.random() < 0.03
            elif 23 <= hour or hour < 4:
                return random.random() < 0.15
            return random.random() < 0.08
        try:
            cfg = get_cat_config()
            if len(comment_text) > cfg.reply.max_comment_length:
                return random.random() < cfg.reply.probability_long_comment
            hour = datetime.now().hour
            if 8 <= hour < 18:
                return random.random() < cfg.reply.probability_day
            elif 23 <= hour or hour < 4:
                return random.random() < cfg.reply.probability_night
            return random.random() < cfg.reply.probability_evening
        except Exception:
            return random.random() < 0.08

    @staticmethod
    def should_reply_dm(dm_text: str = "") -> bool:
        """猫要不要回复私聊？（从配置读取）"""
        if not HAS_CONFIG:
            return random.random() < 0.03
        try:
            return random.random() < get_cat_config().reply.probability_day
        except Exception:
            return random.random() < 0.03

    @staticmethod
    def get_reply() -> Optional[str]:
        """猫回复什么？（从配置读取）"""
        return random.choice(_get_cat_replies())

    @staticmethod
    def get_dm_reply() -> Optional[str]:
        """猫私聊回复什么？（从配置读取）"""
        reply = random.choice(_get_dm_replies())
        return reply if reply else None

    @staticmethod
    def get_post_text() -> str:
        """猫发什么文字？（从配置读取）"""
        if not HAS_CONFIG:
            r = random.random()
            if r < 0.7:
                return ""
            elif r < 0.9:
                return random.choice(["哈", "哈哈", "哈哈哈"])
            else:
                return "哈" * random.randint(5, 20)
        try:
            cfg = get_cat_config()
            r = random.random()
            texts = cfg.post.texts
            if r < 0.7:
                return ""
            elif r < 0.9:
                return random.choice(texts.default)
            else:
                return "哈" * random.randint(cfg.post.crazy_text_min_ha, cfg.post.crazy_text_max_ha)
        except Exception:
            return "哈"

    @staticmethod
    def get_tags() -> List[str]:
        """猫带什么标签？"""
        if random.random() < 0.3:
            return []                            # 30%不带标签
        return random.sample(
            ["耄耋", "圆头耄耋", "哈人", "抽象", "哈基米", "猫meme"],
            k=random.randint(1, 2)
        )

    @staticmethod
    def get_sleep_seconds() -> int:
        """猫的检查间隔（秒）"""
        hour = datetime.now().hour
        if 8 <= hour < 18:
            return random.randint(600, 1800)     # 白天10-30分钟
        elif 2 <= hour < 4:
            return random.randint(60, 300)       # 疯狂时间1-5分钟
        else:
            return random.randint(180, 600)      # 其他3-10分钟


# ============================================================
# 浏览器操作层（Playwright）
# ============================================================

class XHSBrowser:
    """小红书浏览器操作"""

    BASE_URL = "https://www.xiaohongshu.com"
    CREATOR_URL = "https://creator.xiaohongshu.com"

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page: Optional[Page] = None

    async def init(self, headless: bool = False):
        """初始化浏览器"""
        from playwright.async_api import async_playwright

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            slow_mo=100
        )

        # 尝试加载cookie
        cookie_file = Path("cookies.json")
        context_options = {
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }
        if cookie_file.exists():
            try:
                with open(cookie_file, "r") as f:
                    storage = json.load(f)
                context_options["storage_state"] = storage
            except Exception:
                pass

        self.context = await self.browser.new_context(**context_options)

        # 反检测
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        self.page = await self.context.new_page()
        print("✅ 浏览器初始化完成")

    async def save_cookies(self):
        """保存cookies"""
        if self.context:
            storage = await self.context.storage_state()
            with open("cookies.json", "w") as f:
                json.dump(storage, f, indent=2)
            print("✅ Cookies已保存")

    async def goto(self, url: str):
        """访问页面"""
        await self.page.goto(url, wait_until="networkidle")
        await asyncio.sleep(random.uniform(2, 4))

    async def is_logged_in(self) -> bool:
        """检查是否已登录（检查创作者平台）"""
        try:
            await self.goto(f"{self.CREATOR_URL}/user/profile/home")
            await asyncio.sleep(2)
            # 如果页面上没有登录按钮或跳转到登录页，说明已登录
            login_btn = await self.page.query_selector('text="登录"')
            if login_btn:
                return False
            # 检查是否有创作者平台特有的元素
            current_url = self.page.url
            return "/login" not in current_url
        except Exception:
            return False

    async def login_by_qr(self) -> bool:
        """二维码登录"""
        print("📱 请扫描二维码登录...")
        await self.goto(f"{self.CREATOR_URL}/login")

        try:
            # 等待二维码出现
            await self.page.wait_for_selector(
                'canvas, img[class*="qr"], [class*="qrcode"], [class*="qr-code"]',
                timeout=10000
            )
            print("📷 二维码已显示，请用小红书APP扫描")

            # 等待登录成功（最多120秒）
            for _ in range(60):
                await asyncio.sleep(2)
                login_btn = await self.page.query_selector('text="登录"')
                if login_btn is None:
                    print("✅ 登录成功！")
                    await self.save_cookies()
                    return True

            print("❌ 登录超时")
            return False
        except Exception as e:
            print(f"❌ 登录出错: {e}")
            return False

    async def ensure_login(self) -> bool:
        """确保已登录"""
        if await self.is_logged_in():
            print("✅ 已登录")
            return True
        return await self.login_by_qr()

    async def close(self):
        """关闭浏览器"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# ============================================================
# 自动发帖模块
# ============================================================

class AutoPoster:
    """自动发帖（猫的逻辑）"""

    def __init__(self, browser: XHSBrowser, image_folder: str = IMAGE_FOLDER):
        self.browser = browser
        self.page: Page = browser.page
        self.image_folder = Path(image_folder)
        self.image_folder.mkdir(parents=True, exist_ok=True)
        self.images = self._load_images()

    def _load_images(self) -> List[str]:
        """加载表情包图片"""
        images = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.webp"]:
            images.extend(self.image_folder.glob(ext))
        return [str(p.resolve()) for p in images]

    async def post(self) -> bool:
        """
        猫发一条内容

        流程：
        1. 猫决定要不要发 → CatLogic.should_post()
        2. 猫决定发什么 → 选图片 + 生成文字
        3. 打开发布页 → 上传图片 → 填写文字 → 发布
        """
        if not CatLogic.should_post():
            return False

        print("🐱 猫想发内容了...")

        # 生成内容
        text = CatLogic.get_post_text()
        tags = CatLogic.get_tags()

        # 选择图片
        selected_images = []
        if self.images:
            num = random.randint(1, min(3, len(self.images)))
            selected_images = random.sample(self.images, num)

        if not selected_images:
            print("⚠️ 没有可用的表情包图片，跳过")
            return False

        try:
            # 打开发布页面
            await self._open_publish_page()

            # 上传图片
            await self._upload_images(selected_images)

            # 填写标题（用文字内容）
            title = text if text else "哈"
            await self._fill_title(title)

            # 填写正文
            if text:
                await self._fill_content(text)

            # 添加标签
            if tags:
                await self._add_tags(tags)

            # 发布
            success = await self._submit()
            if success:
                print(f"✅ 发帖成功！文字: {text or '(纯图)'} 标签: {tags}")
            else:
                print("❌ 发帖失败")

            return success

        except Exception as e:
            print(f"❌ 发帖出错: {e}")
            return False

    async def _open_publish_page(self):
        """打开发布页面 - 直接跳转到创作者平台发布页"""
        # 直接导航到创作者平台的图文发布页
        await self.browser.goto(f"{self.browser.CREATOR_URL}/publish/publish?target=image")
        await asyncio.sleep(3)

    async def _upload_images(self, images: List[str]):
        """上传图片"""
        # 等待文件上传控件出现
        file_input = await self.page.wait_for_selector(
            'input[type="file"]',
            timeout=15000
        )
        if file_input:
            await file_input.set_input_files(images)
            print(f"  📷 上传 {len(images)} 张图片...")
            # 等待上传完成 - 图片需要时间处理
            await asyncio.sleep(5)

    async def _fill_title(self, title: str):
        """填写标题（小红书标题最多20字）"""
        title = title[:20] if len(title) > 20 else title
        title_input = await self.page.wait_for_selector(
            'input[placeholder="填写标题会有更多赞哦"], '
            'input[placeholder*="填写标题"], '
            'input[placeholder*="标题"]',
            timeout=10000
        )
        if title_input:
            await title_input.fill(title)
            await asyncio.sleep(1)

    async def _fill_content(self, content: str):
        """填写正文"""
        content_input = await self.page.wait_for_selector(
            'textarea[placeholder="输入正文摘录"], '
            'textarea[placeholder*="正文摘录"], '
            'textarea[placeholder*="输入正文"], '
            'textarea[placeholder*="正文"]',
            timeout=10000
        )
        if content_input:
            await content_input.fill(content)
            await asyncio.sleep(1)

    async def _add_tags(self, tags: List[str]):
        """添加标签 - 追加到正文末尾"""
        if not tags:
            return
        tag_text = "\n\n" + " ".join([f"#{tag}" for tag in tags])
        content_input = await self.page.wait_for_selector(
            'textarea[placeholder="输入正文摘录"], '
            'textarea[placeholder*="正文摘录"], '
            'textarea[placeholder*="输入正文"], '
            'textarea[placeholder*="正文"]',
            timeout=10000
        )
        if content_input:
            # 获取当前内容长度，在末尾追加标签
            current = await content_input.input_value()
            new_content = current + tag_text if current else tag_text
            await content_input.fill(new_content)
            await asyncio.sleep(1)

    async def _submit(self) -> bool:
        """提交发布"""
        submit_btn = await self.page.wait_for_selector(
            'button:has-text("发布"), '
            '[class*="publish-btn"], '
            '[class*="submit"]:not([class*="cancel"])',
            timeout=10000
        )
        if submit_btn:
            await submit_btn.click()
            await asyncio.sleep(5)

            # 检查是否发布成功
            try:
                # 可能出现成功提示或跳转到新页面
                await self.page.wait_for_selector(
                    'text="发布成功", [class*="success"], text="笔记发布成功"',
                    timeout=15000
                )
                return True
            except Exception:
                # 即使没看到成功提示，也可能发布成功了（页面跳转）
                # 检查是否还在发布页，不在则可能成功
                await asyncio.sleep(2)
                return "/publish" not in self.page.url
        return False


# ============================================================
# 自动回复评论模块
# ============================================================

class AutoCommentReplier:
    """自动回复评论（猫的逻辑）"""

    def __init__(self, browser: XHSBrowser):
        self.browser = browser
        self.page: Page = browser.page
        self._replied_comments = set()  # 已回复的评论ID，避免重复回复

    async def check_and_reply(self):
        """
        检查新评论并回复

        流程：
        1. 访问个人主页
        2. 找到最新笔记
        3. 查看评论
        4. 猫决定要不要回 → CatLogic.should_reply_comment()
        5. 回复"哈"
        """
        try:
            print("💬 猫在检查评论...")

            # 访问个人主页
            await self._go_to_profile()

            # 获取最新笔记
            note_links = await self.page.query_selector_all(
                '[class*="note"] a, [class*="cover"] a'
            )
            if not note_links:
                print("  ℹ️ 没有找到笔记")
                return

            # 检查最近3篇笔记的评论
            for note_link in note_links[:3]:
                href = await note_link.get_attribute("href")
                if not href:
                    continue

                full_url = href if href.startswith("http") else f"https://www.xiaohongshu.com{href}"
                await self.browser.goto(full_url)
                await asyncio.sleep(random.uniform(2, 4))

                # 获取评论列表
                await self._scroll_to_comments()
                comments = await self._get_comments()

                for comment in comments:
                    comment_id = comment.get("id", "")
                    comment_text = comment.get("text", "")

                    # 跳过已回复的
                    if comment_id in self._replied_comments:
                        continue

                    # 猫决定要不要回
                    if CatLogic.should_reply_comment(comment_text):
                        reply = CatLogic.get_reply()
                        if reply:
                            success = await self._reply_to_comment(comment, reply)
                            if success:
                                self._replied_comments.add(comment_id)
                                print(f"  ✅ 回复了评论: {comment_text[:20]}... → {reply}")
                                await asyncio.sleep(random.uniform(5, 15))
                    else:
                        # 不回复也记录下来
                        self._replied_comments.add(comment_id)

                await asyncio.sleep(random.uniform(3, 8))

        except Exception as e:
            print(f"  ❌ 检查评论出错: {e}")

    async def _go_to_profile(self):
        """访问个人主页"""
        # 点击头像/个人中心
        profile_btn = await self.page.wait_for_selector(
            '[class*="avatar"], [class*="profile"], text="我"',
            timeout=10000
        )
        if profile_btn:
            await profile_btn.click()
            await asyncio.sleep(3)

    async def _scroll_to_comments(self):
        """滚动到评论区"""
        for _ in range(3):
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)

    async def _get_comments(self) -> List[Dict]:
        """获取评论列表"""
        comments = []
        try:
            comment_elements = await self.page.query_selector_all(
                '[class*="comment"], [class*="reply"]'
            )
            for elem in comment_elements:
                try:
                    text_elem = await elem.query_selector('[class*="content"], [class*="text"]')
                    text = await text_elem.text_content() if text_elem else ""

                    # 获取评论ID（用文本哈希作为简易ID）
                    comment_id = str(hash(text.strip())) if text.strip() else ""

                    comments.append({
                        "id": comment_id,
                        "text": text.strip(),
                        "element": elem,
                    })
                except Exception:
                    continue
        except Exception:
            pass
        return comments

    async def _reply_to_comment(self, comment: Dict, reply_text: str) -> bool:
        """回复评论"""
        try:
            # 查找回复输入框
            reply_input = await self.page.query_selector(
                'input[placeholder*="回复"], textarea[placeholder*="回复"], '
                'input[placeholder*="评论"], textarea[placeholder*="评论"]'
            )
            if not reply_input:
                # 尝试点击评论旁的回复按钮
                reply_btn = await comment["element"].query_selector(
                    'text="回复", [class*="reply-btn"]'
                )
                if reply_btn:
                    await reply_btn.click()
                    await asyncio.sleep(1)
                    reply_input = await self.page.query_selector(
                        'input[placeholder*="回复"], textarea[placeholder*="回复"]'
                    )

            if reply_input:
                await reply_input.click()
                await asyncio.sleep(0.5)
                await reply_input.fill(reply_text)
                await asyncio.sleep(1)

                # 点击发送
                send_btn = await self.page.query_selector(
                    'text="发送", [class*="send"], button[type="submit"]'
                )
                if send_btn:
                    await send_btn.click()
                    await asyncio.sleep(2)
                    return True

            return False
        except Exception as e:
            print(f"    ❌ 回复出错: {e}")
            return False


# ============================================================
# 自动回复私聊模块
# ============================================================

class AutoDMReplier:
    """自动回复私聊（猫的逻辑）"""

    def __init__(self, browser: XHSBrowser):
        self.browser = browser
        self.page: Page = browser.page
        self._replied_users = set()  # 已回复的用户

    async def check_and_reply(self):
        """
        检查新私聊并回复

        流程：
        1. 打开消息页面
        2. 查看未读消息
        3. 猫决定要不要回 → CatLogic.should_reply_dm()
        4. 回复"哈"
        """
        try:
            print("📨 猫在检查私聊...")

            # 打开消息页面
            await self._open_messages()

            # 获取未读消息列表
            unread_msgs = await self._get_unread_messages()

            if not unread_msgs:
                print("  ℹ️ 没有新私聊")
                return

            for msg in unread_msgs:
                user_id = msg.get("user_id", "")
                user_name = msg.get("user_name", "未知用户")
                msg_text = msg.get("text", "")

                # 跳过已回复的
                if user_id in self._replied_users:
                    continue

                print(f"  📩 收到私聊: {user_name}: {msg_text[:30]}...")

                # 猫决定要不要回
                if CatLogic.should_reply_dm(msg_text):
                    reply = CatLogic.get_dm_reply()
                    if reply:
                        success = await self._reply_dm(msg, reply)
                        if success:
                            self._replied_users.add(user_id)
                            print(f"  ✅ 回复了私聊: {user_name} → {reply}")
                            await asyncio.sleep(random.uniform(5, 15))
                    else:
                        self._replied_users.add(user_id)
                        print(f"  😼 猫选择不回复: {user_name}")
                else:
                    self._replied_users.add(user_id)
                    print(f"  😼 猫选择不回复: {user_name}")

                await asyncio.sleep(random.uniform(3, 8))

        except Exception as e:
            print(f"  ❌ 检查私聊出错: {e}")

    async def _open_messages(self):
        """打开消息页面"""
        # 点击消息图标
        msg_btn = await self.page.wait_for_selector(
            '[class*="message"], [class*="chat"], text="消息"',
            timeout=10000
        )
        if msg_btn:
            await msg_btn.click()
            await asyncio.sleep(3)
        else:
            # 直接访问消息页面
            await self.browser.goto("https://www.xiaohongshu.com/messages")

    async def _get_unread_messages(self) -> List[Dict]:
        """获取未读消息列表"""
        messages = []
        try:
            # 查找带有未读标记的消息
            msg_elements = await self.page.query_selector_all(
                '[class*="message-item"], [class*="chat-item"], [class*="conversation"]'
            )
            for elem in msg_elements:
                try:
                    # 检查是否有未读标记
                    unread_dot = await elem.query_selector(
                        '[class*="unread"], [class*="badge"], [class*="dot"]'
                    )

                    name_elem = await elem.query_selector('[class*="name"], [class*="title"]')
                    name = await name_elem.text_content() if name_elem else ""

                    text_elem = await elem.query_selector('[class*="content"], [class*="text"], [class*="desc"]')
                    text = await text_elem.text_content() if text_elem else ""

                    user_id = str(hash(name.strip())) if name.strip() else ""

                    if unread_dot or text.strip():
                        messages.append({
                            "user_id": user_id,
                            "user_name": name.strip(),
                            "text": text.strip(),
                            "element": elem,
                        })
                except Exception:
                    continue
        except Exception:
            pass
        return messages

    async def _reply_dm(self, msg: Dict, reply_text: str) -> bool:
        """回复私聊"""
        try:
            # 点击进入聊天
            await msg["element"].click()
            await asyncio.sleep(2)

            # 找到输入框
            input_box = await self.page.wait_for_selector(
                'input[placeholder*="发消息"], textarea[placeholder*="发消息"], '
                'input[placeholder*="输入"], [contenteditable="true"]',
                timeout=5000
            )

            if input_box:
                await input_box.click()
                await asyncio.sleep(0.5)
                await input_box.fill(reply_text)
                await asyncio.sleep(1)

                # 点击发送
                send_btn = await self.page.query_selector(
                    'text="发送", [class*="send"], button[type="submit"]'
                )
                if send_btn:
                    await send_btn.click()
                    await asyncio.sleep(2)
                    return True

            return False
        except Exception as e:
            print(f"    ❌ 回复私聊出错: {e}")
            return False


# ============================================================
# 全自动主循环
# ============================================================

class MaoDieBot:
    """
    耄耋Official 全自动运营Bot

    猫的作息：
    - 白天（8:00-18:00）：睡觉，偶尔醒来
    - 傍晚（18:00-23:00）：醒来观察
    - 深夜（23:00-4:00）：活跃，发内容
    - 凌晨（2:00-4:00）：疯狂时间
    """

    def __init__(self, headless: bool = False, image_folder: str = IMAGE_FOLDER):
        self.browser = XHSBrowser()
        self.headless = headless
        self.image_folder = image_folder
        self.poster: Optional[AutoPoster] = None
        self.comment_replier: Optional[AutoCommentReplier] = None
        self.dm_replier: Optional[AutoDMReplier] = None
        self.is_running = False

    async def start(self):
        """启动Bot"""
        print("🐱 耄耋Official - 全自动运营Bot")
        print("=" * 50)

        # 1. 初始化浏览器
        await self.browser.init(headless=self.headless)

        # 2. 登录
        if not await self.browser.ensure_login():
            print("❌ 登录失败，Bot无法启动")
            await self.browser.close()
            return

        # 3. 初始化模块
        self.poster = AutoPoster(self.browser, self.image_folder)
        self.comment_replier = AutoCommentReplier(self.browser)
        self.dm_replier = AutoDMReplier(self.browser)

        # 4. 启动主循环
        self.is_running = True
        print("🚀 Bot已启动，猫开始运营了...")
        print()

        await self._main_loop()

    async def _main_loop(self):
        """主循环"""
        while self.is_running:
            try:
                hour = datetime.now().hour
                mood = self._get_mood_emoji(hour)

                print(f"{'='*50}")
                print(f"🐱 [{datetime.now().strftime('%H:%M:%S')}] 猫的状态: {mood}")
                print(f"{'='*50}")

                # 任务1: 自动发帖
                await self._try_post()

                # 任务2: 自动回复评论
                await self._try_reply_comments()

                # 任务3: 自动回复私聊
                await self._try_reply_dm()

                # 猫休息一下
                sleep_time = CatLogic.get_sleep_seconds()
                print(f"😴 猫要休息 {sleep_time} 秒...")
                print()

                await asyncio.sleep(sleep_time)

            except KeyboardInterrupt:
                print("\n🛑 收到停止信号")
                self.is_running = False
            except Exception as e:
                print(f"❌ 主循环出错: {e}")
                await asyncio.sleep(60)

        # 关闭
        await self.browser.close()
        print("👋 猫去睡觉了...")

    async def _try_post(self):
        """尝试发帖"""
        if CatLogic.should_post():
            print("📝 猫决定发一条内容...")
            await self.poster.post()
        else:
            print("📝 猫不想发内容")

    async def _try_reply_comments(self):
        """尝试回复评论"""
        if CatLogic.should_reply_comment():
            print("💬 猫决定看看评论...")
            await self.comment_replier.check_and_reply()
        else:
            print("💬 猫不想看评论")

    async def _try_reply_dm(self):
        """尝试回复私聊"""
        if CatLogic.should_reply_dm():
            print("📨 猫决定看看私聊...")
            await self.dm_replier.check_and_reply()
        else:
            print("📨 猫不想看私聊")

    def _get_mood_emoji(self, hour: int) -> str:
        """获取猫的心情emoji"""
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

    def stop(self):
        """停止Bot"""
        self.is_running = False


# ============================================================
# 启动入口
# ============================================================

async def run():
    """启动耄耋Official Bot"""
    import sys

    # 解析命令行参数
    headless = "--headless" in sys.argv
    image_folder = IMAGE_FOLDER

    # 查找 --images 参数
    for i, arg in enumerate(sys.argv):
        if arg == "--images" and i + 1 < len(sys.argv):
            image_folder = sys.argv[i + 1]

    bot = MaoDieBot(headless=headless, image_folder=image_folder)
    await bot.start()


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════╗
    ║     🐱 耄耋Official 全自动Bot      ║
    ║                                      ║
    ║  用法:                               ║
    ║    python maodie_bot.py              ║
    ║    python maodie_bot.py --headless   ║
    ║    python maodie_bot.py --images ./my_images ║
    ║                                      ║
    ║  猫的作息:                           ║
    ║    08:00-18:00  😴 睡觉              ║
    ║    18:00-23:00  😺 醒来              ║
    ║    23:00-04:00  😼 活跃              ║
    ║    02:00-04:00  😹 疯狂              ║
    ╚══════════════════════════════════════╝
    """)
    asyncio.run(run())
