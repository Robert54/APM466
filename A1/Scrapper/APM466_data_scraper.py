import sys
print("Sublime is using: ", sys.version)
###################

from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
import random
import numpy as np
import pandas as pd
import re
import csv

driver = webdriver.Chrome('/Users/zhangtingyu/Desktop/Crap_code/chromedriver')
driver.get("https://markets.businessinsider.com/bonds/finder?borrower=71&maturity=shortterm&yield=&bondtype=2%2c3%2c4%2c16&coupon=&currency=184&rating=&country=19")
content = driver.find_elements_by_xpath("//*[@id=\"bond-searchresults-container\"]/div[2]/div[1]/table")
# or self::th

def divide_chunks(l, n):    
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

# for i in range(2, 19):
#     content = driver.find_elements_by_xpath("//*[@id=\"bond-searchresults-container\"]/div[2]/div[1]/tabletbody/tr[2]/td[1]/a")
#     for i in content:
#         i.click()
    # //*[@id="bond-searchresults-container"]/div[2]/div[1]/table/tbody/tr[2]/td[1]/a
    # //*[@id="bond-searchresults-container"]/div[2]/div[1]/table/tbody/tr[3]/td[1]/a
    # //*[@id="bond-searchresults-container"]/div[2]/div[1]/table/tbody/tr[18]/td[1]/a
link_junk = []
list_links = driver.find_elements_by_tag_name('a')
for i in list_links:
    link = i.get_attribute('href')
    if type(link) == str:
        m = re.match(r'https://markets.businessinsider.com/bonds/{1,}.', link)
        if m is not None:
            print(link)
            link_junk.append(link)

print("--------------")

driver.get("https://markets.businessinsider.com/bonds/finder?borrower=71&maturity=midterm&yield=&bondtype=2%2c3%2c4%2c16&coupon=&currency=184&rating=&country=19")
content = driver.find_elements_by_xpath("//*[@id=\"bond-searchresults-container\"]/div[2]/div[1]/table")

list_links = driver.find_elements_by_tag_name('a')
for i in list_links:
    link = i.get_attribute('href')
    if type(link) == str:
        m = re.match(r'https://markets.businessinsider.com/bonds/{1,}.', link)
        if m is not None:
            print(link)
            link_junk.append(link)
print("--------------")

def link_process(page_index):
    test_link = link_junk[page_index]
    driver.get(test_link)
    content = driver.find_elements_by_xpath("//*[@id=\"site\"]/div/div[2]/div[3]/div/div[18]/div[2]/table/tbody")
    data_dict = {}
    for table in content:
        for item in table.find_elements_by_xpath(".//*[self::tr]"):
            item_l = item.text.split(" ")
            if (len(item_l) > 1):
                side_l = [side.text for side in item.find_elements_by_xpath(".//*[self::td]")]
                left = side_l[0]
                right = side_l[1]
                if left in ["Coupon", "ISIN", "Issue Date", "Maturity Date"]:
                    data_dict[left] = right
    new_dict = dict(sorted(data_dict.items()))
    row_entry = list(new_dict.values())
    return row_entry

csv_header = ["Coupon", "ISIN", "Issue Date", "Maturity Date"]
row_list = []
row_list.append(csv_header)
for i in range(len(link_junk)):
    row_list.append(link_process(i))

with open('32bonds.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(row_list)




driver.quit()