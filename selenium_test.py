import argparse
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username for Alto', required=True)
    parser.add_argument('-p', '--password', help='Password for Alto', required=True)
    parser.add_argument('-s', '--silent', action='store_true', help='Run silent (headless)', default=False)
    args = parser.parse_args()
    options = Options()
    if args.silent:
        options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    login_alto(driver, args.username, args.password)
    driver.get("https://login.vebraalto.com/#home/enquiries")
    time.sleep(2)
    get_table_elements(driver)
    driver.close()

def login_alto(driver: webdriver, username: str, password: str):
    driver.get("https://login.vebraalto.com/sign-in")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    time.sleep(2)
    driver.find_element(By.NAME, "action").click()
    time.sleep(2)

def get_table_elements(driver):
    table_elements = []
    table_id = driver.find_element(By.CLASS_NAME, "body")
    table_headers= table_id.find_elements(By.TAG_NAME, "th")
    headers = [header.text for header in table_headers]
    rows = table_id.find_elements(By.TAG_NAME, "tr") # get all of the rows in the table
    for row in rows:
        if row.get_attribute("class") != "row":
            continue
        columns = row.find_elements(By.TAG_NAME, "td")
        column_text = []
        for column in columns:
            if col_text := column.text:
                column_text.append(col_text)
                continue
            if contained_images := column.find_elements(By.TAG_NAME, "img"):
                if img_title := contained_images[0].get_attribute("title"):
                    column_text.append(img_title)
                    continue
            if contained_divs := column.find_elements(By.TAG_NAME, "div"):
                if div_class := contained_divs[0].get_attribute("class"):
                    column_text.append(div_class.split(" ")[-1])
                    continue
            column_text.append("")

        table_elements.append(dict(zip(headers, column_text)))

    with open("enquiries.json", "w") as f:
        json.dump({"enquiries":table_elements}, f, indent=4)





if __name__ == '__main__':
    main()