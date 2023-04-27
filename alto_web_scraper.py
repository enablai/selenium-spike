import argparse
import json
import logging
import time

import attr
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


@attr.s
class AltoWebScraper:
    driver = attr.ib()

    def login(self, username: str, password: str):
        self.driver.get("https://login.vebraalto.com/sign-in")
        self.wait_for_element_to_be_loaded(By.ID, "username")
        self.driver.find_element(By.ID, "username").send_keys(username)
        self.driver.find_element(By.ID, "password").send_keys(password)
        self.driver.find_element(By.NAME, "action").click()

    def get_all_enquiries(self):
        self.wait_for_element_to_be_loaded(By.ID, "sidebar")
        self.driver.get("https://login.vebraalto.com/#home/enquiries")
        self.get_table_elements()

    def wait_for_element_to_be_loaded(self, by_method: str, element: str, max_timeout: int = 10):
        logger.info(f"Waiting for {element} to be loaded by {by_method}")
        try:
            WebDriverWait(self.driver, max_timeout).until(EC.presence_of_element_located((by_method, element)))
        except TimeoutException as e:
            logger.error(f"Element {element} was not loaded in {max_timeout} seconds")
            raise TimeoutException from e

    def get_table_elements(self):
        self.wait_for_element_to_be_loaded(By.XPATH, "//*[@id='dashboard-leads-lead']/div/div/div[2]")
        head = self.driver.find_element(By.TAG_NAME, "thead")
        table_body = self.driver.find_element(By.TAG_NAME, "tbody")
        table_headers = head.find_elements(By.TAG_NAME, "th")
        headers = [header.text for header in table_headers]
        logger.info(f"Headers: {headers}")
        rows = table_body.find_elements(By.TAG_NAME, "tr")
        logger.info(f"Found {len(rows)} rows")
        logger.info("Getting row details...")
        table_elements = [self.get_row_details(row, headers) for row in rows if row.get_attribute("class") == "row"]
        with open("enquiries.json", "w") as f:
            json.dump({"enquiries": table_elements}, f, indent=4)

    def get_row_details(self, row, headers: list):
        columns = row.find_elements(By.TAG_NAME, "td")
        assert len(columns) == len(headers), "Number of columns and headers do not match"
        column_text = []
        for column in columns:
            if col_text := column.text:
                column_text.append(col_text)
                continue
            if contained_images := column.find_elements(By.TAG_NAME, "img"):
                assert len(contained_images) == 1, "More than one image found in column"
                if img_title := contained_images[0].get_attribute("title"):
                    column_text.append(img_title)
                    continue
            if contained_divs := column.find_elements(By.TAG_NAME, "div"):
                if div_class := contained_divs[0].get_attribute("class"):
                    column_text.append(div_class.split(" ")[-1])
                    continue
            column_text.append("")

        return dict(zip(headers, column_text))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="Username for Alto", required=True)
    parser.add_argument("-p", "--password", help="Password for Alto", required=True)
    parser.add_argument("-s", "--silent", action="store_true", help="Run silent (headless)", default=False)
    args = parser.parse_args()
    options = Options()
    if args.silent:
        options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    alto_web_scraper = AltoWebScraper(driver)
    alto_web_scraper.login(args.username, args.password)
    alto_web_scraper.get_all_enquiries()


if __name__ == "__main__":
    main()
