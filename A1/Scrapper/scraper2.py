from selenium import webdriver
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import json
import time
import random
import numpy as np
import pandas as pd
import re
import csv
from time import sleep
import time

driver = webdriver.Chrome('/Users/zhangtingyu/Desktop/Crap_code/chromedriver')

with open("bondslink.txt") as f:
    content = f.readlines()

def link_process(link):
    driver.get(link)
    isin_div = driver.find_element_by_class_name("aktien-time")
    ISIN = isin_div.text
    bond_div = driver.find_element_by_xpath("//*[@id=\"site\"]/div/div[2]/div[1]/div/div[1]/div[1]/div[1]/div[2]/h1")
    bond_tag = bond_div.text
    print(ISIN)
    print(bond_tag)
    s1 = Select(driver.find_element_by_id("historic-prices-start-day"))
    s1.select_by_value("2")
    s2 = Select(driver.find_element_by_id("historic-prices-end-day"))
    s2.select_by_value("15")
    s3 = Select(driver.find_element_by_id("historic-prices-end-month"))
    s3.select_by_visible_text("January")
    s4 = Select(driver.find_element_by_id("historic-prices-stock-market"))
    try:
        s4.select_by_value("FSE")
        content = driver.find_element_by_xpath("//*[@id=\"request-historic-price\"]")
        content.click()
        entry_list = []
        entry_list.append([bond_tag, ISIN])
        entry_list.append(["Date", "Closing Price"])
        temp = []
        time.sleep(1)
        table = driver.find_element_by_xpath("//*[@id=\"historic-price-list\"]/div/div[2]/table/tbody")
        for item in table.find_elements_by_xpath(".//*[self::tr]"):
            entry = item.text.split(" ")
            entry.pop(1)
            # print(entry)
            temp.append(entry)
        for e in list(reversed(temp)):
            entry_list.append(e)
        name = ISIN + ".csv"
        with open(name, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(entry_list)
    except:
        print("!!!!!!!!!!!!!!!!")
        print(ISIN)
        pass

if __name__ == '__main__':
    for link in content:
        link_process(link)
    # link_process(content[0])
    driver.quit()

