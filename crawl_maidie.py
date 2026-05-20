"""
耄耋表情包爬虫 - B站 & 贴吧
使用 Playwright 模拟浏览器访问，支持 Stealth 模式绕过反爬
"""
import asyncio
import json
import re
import time
from pathlib import Path
from playwright.async_api import async_playwright, Page

OUTPUT_DIR = Path(__file__).parent / "images" / "crawled"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# B站搜索关键词
BILIBILI_KEYWORDS = ["耄耋", "耄耋表情包", "耄耋meme", "圆头耄耋"]
# 贴吧搜索关键词
TIEBA_KEYWORDS = ["耄耋表情包", "耄耋猫", "圆头耄耋"]


async def download_image(page: Page, url: str, filename: str, timeout: int = 15) -> bool:
    """下载单张图片"""
    try:
        response = await page.request.get(url, timeout=timeout * 1000)
        if response.ok:
            content = await response.body()
            if len(content) > 5000:  # 过滤太小无效图片
                ext = url.split("?")[0].split(".")[-1]
                if ext.lower() not in ["jpg", "jpeg", "png", "webp", "gif"]:
                    ext = "jpg"
                filepath = OUTPUT_DIR / f"{filename}.{ext}"
                with open(filepath, "wb") as f:
                    f.write(content)
                print(f"  ✓ 下载: {filepath.name} ({len(content)} bytes)")
                return True
    except Exception as e:
        print(f"  ✗ 失败: {url[:60]}... ({e})")
    return False


async def crawl_bilibili(playwright, headless: bool = True) -> int:
    """爬取B站搜索结果中的图片"""
    print("\n{'='*50}")
    print("B站 爬取开始")
    print("="*50)

    downloaded = 0
    browser = await playwright.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-web-security",
        ]
    )
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )
    page = await context.new_page()

    # 拦截图片请求
    image_urls = []

    async def handle_response(response):
        if response.headers.get("content-type", "").startswith("image/"):\
                or "图片" in response.url:
            url = response.url
            if any(kw in url.lower() for kw in ["jpg", "jpeg", "png", "webp"]) and len(url) < 500:
                image_urls.append(url)

    page.on("response", handle_response)

    for keyword in BILIBILI_KEYWORDS:
        print(f"\n搜索 B站: {keyword}")
        try:
            # 搜索
            search_url = f"https://search.bilibili.com/all?keyword={keyword}&order=totalrank"
            await page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(3)

            # 向下滚动加载更多
            for _ in range(3):
                await page.evaluate("window.scrollBy(0, 500)")
                await asyncio.sleep(1)

            # 提取页面中的图片链接
            img_elements = await page.query_selector_all("img")
            for img in img_elements:
                src = await img.get_attribute("src")
                if src and any(ext in src for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    if src.startswith("//"):
                        src = "https:" + src
                    if src not in image_urls:
                        image_urls.append(src)

            # 从 URL 模式匹配图片（缩略图）
            page_content = await page.content()
            found_urls = re.findall(r'https?://i[0-9]\.hdslb\.com[^\s"\'<>]+', page_content)
            for url in found_urls:
                if url not in image_urls and any(ext in url for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    image_urls.append(url)

            print(f"  发现 {len(image_urls)} 张图片")

        except Exception as e:
            print(f"  ✗ 错误: {e}")
            continue

    # 下载发现的图片（最多30张）
    print(f"\n开始下载 {min(len(image_urls), 30)} 张图片...")
    for i, url in enumerate(image_urls[:30]):
        if await download_image(page, url, f"bilibili_maidie_{i+1}"):
            downloaded += 1
        await asyncio.sleep(0.3)

    await browser.close()
    print(f"\nB站下载完成: {downloaded} 张")
    return downloaded


async def crawl_tieba(playwright, headless: bool = True) -> int:
    """爬取贴吧搜索结果中的图片"""
    print("\n" + "="*50)
    print("贴吧 爬取开始")
    print("="*50)

    downloaded = 0
    browser = await playwright.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
        ]
    )
    context = await browser.new_context(
        viewport={"width": 1920, "height": 1080},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    )
    page = await context.new_page()

    image_urls = []

    async def handle_response(response):
        if "image" in response.headers.get("content-type", ""):
            url = response.url
            if any(ext in url for ext in [".jpg", ".jpeg", ".png", ".webp"]) and len(url) < 500:
                image_urls.append(url)

    page.on("response", handle_response)

    for keyword in TIEBA_KEYWORDS:
        print(f"\n搜索 贴吧: {keyword}")
        try:
            search_url = f"https://tieba.baidu.com/f/search/res?ie=utf-8&kw={keyword}&qw={keyword}"
            await page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
            await asyncio.sleep(3)

            # 提取帖子中的图片
            img_elements = await page.query_selector_all("img[src]")
            for img in img_elements:
                src = await img.get_attribute("src")
                if src and not src.startswith("data:"):
                    if src.startswith("//"):
                        src = "https:" + src
                    if src not in image_urls:
                        image_urls.append(src)

            # 也从页面 HTML 匹配真实图片 URL
            page_content = await page.content()
            found_urls = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|webp|gif)', page_content)
            for url in found_urls:
                if url not in image_urls and "tbpic" in url.lower():
                    image_urls.append(url)

            print(f"  发现 {len(image_urls)} 张图片")

        except Exception as e:
            print(f"  ✗ 错误: {e}")
            continue

    # 下载（最多30张）
    print(f"\n开始下载 {min(len(image_urls), 30)} 张图片...")
    for i, url in enumerate(image_urls[:30]):
        if await download_image(page, url, f"tieba_maidie_{i+1}"):
            downloaded += 1
        await asyncio.sleep(0.5)

    await browser.close()
    print(f"\n贴吧下载完成: {downloaded} 张")
    return downloaded


async def main():
    print("耄耋表情包爬虫 - B站 & 贴吧")
    print("="*50)

    async with async_playwright() as playwright:
        total = 0
        total += await crawl_bilibili(playwright, headless=True)
        total += await crawl_tieba(playwright, headless=True)

    print("\n" + "="*50)
    print(f"全部完成! 共下载 {total} 张图片")
    print(f"保存目录: {OUTPUT_DIR}")
    print("="*50)


if __name__ == "__main__":
    asyncio.run(main())
