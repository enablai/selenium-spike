import argparse
import asyncio
import re
import time

from playwright.async_api import Page, Playwright, async_playwright


async def login(page: Page, username: str, password: str):
    await page.goto("https://login.vebraalto.com/sign-in")
    await page.wait_for_load_state("networkidle")
    await page.locator("#username").fill(username)
    await page.locator("#password").fill(password)
    await page.click("[name=action]")
    await page.wait_for_load_state("networkidle")


async def run(playwright: Playwright, username: str, password: str, silent: bool):
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = await chromium.launch(headless=silent)
    page = await browser.new_page()
    await login(page, username, password)
    await page.get_by_role("navigation").filter(has_text="Enquiries").click()
    await page.wait_for_selector("#dashboard-leads-lead > div > div > div.tablex.list.lead.mr1")
    # await page.pause()
    rows = []
    headers = []
    for row in await page.get_by_role("row").all():
        content = await row.text_content()
        if content is not None:
            content = content.replace("\n", " ").strip()
            content = re.sub(r"\s\s+", "-", content)
            content_list = content.split("-")
        if await row.get_attribute("class") == "row":
            rows.append(content_list)
        else:
            headers = content_list
    print(rows[0])
    print(headers)
    print(len(rows[0]))
    print(len(headers))
    await browser.close()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="Username for Alto", required=True)
    parser.add_argument("-p", "--password", help="Password for Alto", required=True)
    parser.add_argument("-s", "--silent", action="store_true", help="Run silent (headless)", default=False)
    args = parser.parse_args()
    async with async_playwright() as playwright:
        await run(playwright, args.username, args.password, args.silent)


if __name__ == "__main__":
    asyncio.run(main())
