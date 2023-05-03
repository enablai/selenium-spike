import argparse
import json
import logging
import re
from dataclasses import dataclass

from playwright.sync_api import Locator, Page, sync_playwright


@dataclass
class AltoAPI:
    page: Page

    def login(self, username, password):
        self.page.goto("https://login.vebraalto.com/sign-in")
        self.page.wait_for_load_state("networkidle")
        self.page.locator("#username").fill(username)
        self.page.locator("#password").fill(password)
        self.page.click("[name=action]")
        self.page.wait_for_load_state("networkidle")

    def write_enquiries_to_file(self, filename: str):
        with open(filename, "w") as f:
            json.dump({"enquiries": self.get_all_enquiries()}, f, indent=4)

    def get_all_enquiries(self):
        self.page.get_by_role("navigation").filter(has_text="Enquiries").click()
        self.page.wait_for_selector("#dashboard-leads-lead > div > div > div.tablex.list.lead.mr1")
        table_headers = self.get_table_headers()
        rows_locators = self.page.locator("#dashboard-leads-lead > div > div > div.tablex.list.lead.mr1 > div.body > table > tbody > tr").all()
        return self.get_both_row_details(rows_locators=rows_locators, headers=table_headers)

    def get_table_headers(self) -> list:
        headers = []
        header_locators = self.page.locator(
            "#dashboard-leads-lead > div > div > div.tablex.list.lead.mr1 > div.header > table > thead > tr > th"
        ).all()
        for i, header in enumerate(header_locators):
            content = header.text_content()
            if content is not None:
                content = self.clean_text(content)
                if content == "":
                    headers.append(str(i))
                    continue
                headers.append(content)
        headers.append("extra_info")
        return headers

    def get_both_row_details(self, rows_locators: list[Locator], headers: list):
        headers.append("extra_info")
        chunked_list: list = self.split_list(rows_locators, 2)
        all_row_details = []
        for locators_list in chunked_list:
            assert len(locators_list) == 2
            assert locators_list[0].get_attribute("class") == "row"
            assert locators_list[1].get_attribute("class") == "extra-info-row hidden"
            details = self.handle_row(locators_list[0])
            details.append(self.handle_extra_info_row(locators_list[1]))
            all_row_details.append(dict(zip(headers, details)))
        return all_row_details

    def handle_extra_info_row(self, row_locator: Locator):
        return {"extra_info": "extra_info"}

    def handle_row(self, row_locator: Locator) -> list:
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
                column_text.append(self.clean_text(content))
                continue

            column_text.append("")
        return column_text

    @staticmethod
    def clean_text(text: str) -> str:
        text = text.replace("\n", " ").strip()
        return re.sub(r"\s\s+", " ", text)

    @staticmethod
    def split_list(input_list, n):
        for i in range(0, len(input_list), n):
            yield input_list[i : i + n]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="Username for Alto", required=True)
    parser.add_argument("-p", "--password", help="Password for Alto", required=True)
    parser.add_argument("-s", "--silent", action="store_true", help="Run silent (headless)", default=False)
    args = parser.parse_args()
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=args.silent)
        alto_api = AltoAPI(page=browser.new_page())
        alto_api.login(args.username, args.password)
        alto_api.write_enquiries_to_file("enquiries.json")


if __name__ == "__main__":
    main()
