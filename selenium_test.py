import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By


def main():
    driver = webdriver.Chrome()
    login_alto(driver)
    driver.get("https://login.vebraalto.com/#home/enquiries")
    time.sleep(5)
    get_table_elements(driver)
    driver.close()

def login_alto(driver):
    driver.get("https://login.vebraalto.com/sign-in")
    driver.find_element(By.ID, "username").send_keys("info@residemanchester.com")
    driver.find_element(By.ID, "password").send_keys("BA8pSJ^@sN%LmPbK")
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