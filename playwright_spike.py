import argparse
import json
import re
import time

from playwright.sync_api import Locator, Page, Playwright, sync_playwright


def login(page: Page, username: str, password: str):
    page.goto("https://login.vebraalto.com/sign-in")
    page.wait_for_load_state("networkidle")
    page.locator("#username").fill(username)
    page.locator("#password").fill(password)
    page.click("[name=action]")
    page.wait_for_load_state("networkidle")


def clean_text(text: str) -> str:
    text = text.replace("\n", " ").strip()
    return re.sub(r"\s\s+", " ", text)


def get_row_details(rows_locator: list[Locator], headers: list):
    row_details = []
    for row_locator in rows_locator:
        print(row_locator.get_attribute("class"))
        if row_locator.get_attribute("class") != "row":
            continue
        column_text = []
        for column_locator in row_locator.locator("td").all():
            if column_locator.locator("img").count() == 1:
                column_text.append(column_locator.locator("img").first.get_attribute("title"))
                continue
            if column_locator.locator("div").count() == 1:
                class_name = column_locator.locator("div").first.get_attribute("class")
                if class_name is not None:
                    column_text.append(class_name.split(" ")[-1])
                continue
            if (content := column_locator.text_content()) is not None:
                column_text.append(clean_text(content))
                continue

            column_text.append("")
        print(f"column_text: {len(column_text)}, headers: {len(headers)}")
        row_details.append(dict(zip(headers, column_text)))
    return row_details


def run(playwright: Playwright, username: str, password: str, silent: bool):
    chromium = playwright.chromium  # or "firefox" or "webkit".
    browser = chromium.launch(headless=silent)
    page = browser.new_page()
    login(page, username, password)
    page.get_by_role("navigation").filter(has_text="Enquiries").click()
    page.wait_for_selector("#dashboard-leads-lead > div > div > div.tablex.list.lead.mr1")
    table_headers_text = []
    header_locator = page.locator("#dashboard-leads-lead > div > div > div.tablex.list.lead.mr1 > div.header > table > thead > tr > th").all()
    for i, header in enumerate(header_locator):
        content = header.text_content()
        if content is not None:
            content = clean_text(content)
            if content == "":
                table_headers_text.append(str(i))
                continue
            table_headers_text.append(content)
    print(table_headers_text)
    rows_locator = page.locator("#dashboard-leads-lead > div > div > div.tablex.list.lead.mr1 > div.body > table > tbody > tr").all()
    row_details = get_row_details(rows_locator, table_headers_text)
    with open("enquiries.json", "w") as f:
        json.dump({"enquiries": row_details}, f, indent=4)
    browser.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="Username for Alto", required=True)
    parser.add_argument("-p", "--password", help="Password for Alto", required=True)
    parser.add_argument("-s", "--silent", action="store_true", help="Run silent (headless)", default=False)
    args = parser.parse_args()
    with sync_playwright() as playwright:
        run(playwright, args.username, args.password, args.silent)


if __name__ == "__main__":
    main()
