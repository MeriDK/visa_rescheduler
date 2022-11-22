# -*- coding: utf8 -*-
import time
import random
import configparser
from datetime import datetime
import argparse

import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


parser = argparse.ArgumentParser()
parser.add_argument("--config", default='config10.ini')
args, unknown = parser.parse_known_args()

config = configparser.RawConfigParser()
config.read(args.config)

USERNAME = config['USVISA']['USERNAME']
PASSWORD = config['USVISA']['PASSWORD']
SCHEDULE_ID = config['USVISA']['SCHEDULE_ID']
COUNTRY_CODE = config['USVISA']['COUNTRY_CODE']

PUSH_TOKEN = config['PUSHOVER']['PUSH_TOKEN']
PUSH_USER = config['PUSHOVER']['PUSH_USER']

LOCAL_USE = config['CHROMEDRIVER'].getboolean('LOCAL_USE')
HUB_ADDRESS = config['CHROMEDRIVER']['HUB_ADDRESS']

REGEX_CONTINUE = "//a[contains(text(),'Continue')]"


STEP_TIME = 0.5  # time between steps (interactions with forms): 0.5 seconds
RETRY_TIME = 60 * 10  # wait time between retries/checks for available dates: 10 minutes
EXCEPTION_TIME = 60 * 30  # wait time when an exception occurs: 30 minutes
COOLDOWN_TIME = 60 * 60  # wait time when temporary banned (empty list): 60 minutes

CONTINUE_URL = f"https://ais.usvisa-info.com/en-ca/niv/schedule/{SCHEDULE_ID}/continue_actions"
CONTINUE_URL2 = f"https://ais.usvisa-info.com/en-ca/niv/schedule/{SCHEDULE_ID}/continue"


def send_notification(msg):
    print(f"Sending notification.")

    if PUSH_TOKEN:
        url = "https://api.pushover.net/1/messages.json"
        data = {
            "token": PUSH_TOKEN,
            "user": PUSH_USER,
            "message": msg
        }
        requests.post(url, data)


def get_driver():
    if LOCAL_USE:
        dr = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    else:
        dr = webdriver.Remote(command_executor=HUB_ADDRESS, options=webdriver.ChromeOptions())
    return dr


driver = get_driver()


def login():
    # Bypass reCAPTCHA
    driver.get(f"https://ais.usvisa-info.com/{COUNTRY_CODE}/niv")
    time.sleep(STEP_TIME)
    a = driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(STEP_TIME)

    print("Login start...")
    href = driver.find_element(By.XPATH, '//*[@id="header"]/nav/div[2]/div[1]/ul/li[3]/a')
    href.click()
    time.sleep(STEP_TIME)
    Wait(driver, 60).until(EC.presence_of_element_located((By.NAME, "commit")))

    print("\tclick bounce")
    a = driver.find_element(By.XPATH, '//a[@class="down-arrow bounce"]')
    a.click()
    time.sleep(STEP_TIME)

    do_login_action()


def do_login_action():
    print("\tinput email")
    user = driver.find_element(By.ID, 'user_email')
    user.send_keys(USERNAME)
    time.sleep(random.randint(1, 3))

    print("\tinput pwd")
    pw = driver.find_element(By.ID, 'user_password')
    pw.send_keys(PASSWORD)
    time.sleep(random.randint(1, 3))

    print("\tclick privacy")
    box = driver.find_element(By.CLASS_NAME, 'icheckbox')
    box .click()
    time.sleep(random.randint(1, 3))

    print("\tcommit")
    btn = driver.find_element(By.NAME, 'commit')
    btn.click()
    time.sleep(random.randint(1, 3))

    Wait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, REGEX_CONTINUE)))
    print("\tlogin successful!")


def get_dates_new():

    time.sleep(STEP_TIME)
    driver.get(CONTINUE_URL)

    time.sleep(STEP_TIME)
    driver.get(CONTINUE_URL2)

    time.sleep(STEP_TIME)
    dates = driver.find_element(By.CLASS_NAME, 'for-layout').text

    return dates


def main():
    login()
    retry_count = 0

    while retry_count < 6:
        try:
            print("------------------")
            print(datetime.today())
            print(f"Retry count: {retry_count}")

            dates = get_dates_new()
            print(dates)
            if 'October, 2022' in dates or 'November, 2022' in dates:
                for el in dates.split('\n'):
                    if '2022' in el:
                        send_notification(el)
                        print(el)

            if dates == 'Calgary No Appointments Available\nHalifax No Appointments Available\n' \
                        'Montreal No Appointments Available\nOttawa No Appointments Available\n' \
                        'Quebec City No Appointments Available\nToronto No Appointments Available\n' \
                        'Vancouver No Appointments Available':
                print('Banned')
                time.sleep(COOLDOWN_TIME)
                login()
            else:
                time.sleep(RETRY_TIME)

            print()

        except Exception as e:
            print(e)
            print('Banned')
            send_notification('Error')

            retry_count += 1
            time.sleep(EXCEPTION_TIME)


if __name__ == "__main__":
    main()
