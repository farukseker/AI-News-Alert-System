from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import asyncio


CF_INDICATORS = [
    "challenges.cloudflare.com",
    "__cf_chl",
    "cf-challenge",
    "challenge-platform"
]


async def has_cloudflare(page) -> bool:
    html = await page.content()
    if 'Just a moment...' in html.title():
        return True

    if any(x in html for x in CF_INDICATORS):
        return True

    # iframe based challenge check
    frames = page.frames
    for f in frames:
        if any(x in (f.url or "") for x in CF_INDICATORS):
            return True

    return False


async def try_cloudflare_once(page):
    for frame in page.frames:
        if "challenges.cloudflare.com" not in (frame.url or ""):
            continue

        checkbox = frame.locator("input[type='checkbox']")
        if await checkbox.count() == 0:
            return

        try:
            await checkbox.first.click(timeout=2000)
            await page.wait_for_load_state("networkidle", timeout=5000)
        except:
            return

async def scraper(url: str) -> str | None:
    async with async_playwright() as p:
        try:
            browser = await p.webkit.launch(headless=True)
            page = await browser.new_page()

            await page.goto(
                url,
                wait_until="domcontentloaded"
            )

            if await has_cloudflare(page):
                await try_cloudflare_once(page)

            if await has_cloudflare(page):
                return None

            return await page.content()
        finally:
            await browser.close()

def sync_scraper(url: str) -> str | None:
    return asyncio.run(scraper(url))

