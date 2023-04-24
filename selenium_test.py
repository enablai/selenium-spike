import argparse
import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', help='Username for Alto', required=True)
    parser.add_argument('-p', '--password', help='Password for Alto', required=True)
    args = parser.parse_args()
    driver = webdriver.Chrome()
    login_alto(driver, args.username, args.password)
    driver.get("https://login.vebraalto.com/#home/enquiries")
    time.sleep(2)
    get_table_elements(driver)
    driver.close()

def login_alto(driver: webdriver, username: str, password: str):
    driver.get("https://login.vebraalto.com/sign-in")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
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
        column_text = [column.text for column in columns]
        table_elements.append(dict(zip(headers, column_text)))

    with open("table.json", "w") as f:
        json.dump({"table_elements":table_elements}, f, indent=4)





if __name__ == '__main__':
    main()