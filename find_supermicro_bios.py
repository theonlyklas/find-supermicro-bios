import requests
import pdb
from bs4 import BeautifulSoup
import time
import os

import re

PAGE_SAVE_PATH = "C:/Users/Jason/find-supermicro-bios/Pages"
BASE_URL = "https://www.supermicro.com/support/resources/getfile.php?SoftwareItemID="
DEAD_PAGE_INDICES = []

def get_page(url, i):
    page = requests.get(url)
    if (page.url != url):
        save_page(page, i)
    else:
        DEAD_PAGE_INDICES.append(i)

def save_page(page, i):
    try:
        os.mkdir(PAGE_SAVE_PATH + "/" + str(i), 755)
    except Exception as e:
        #TODO: look for changes in files?
        print(e)

    print("attempting to save " + page.url)
    try:
        open(PAGE_SAVE_PATH + "/" + str(i) + "/" + page.url[page.url.rfind('/'):], 'wb').write(page.content)
    except Exception as e:
        print("failed to save " + page.url)

def save_dead_page_indices():   
    dead_page_file = open(PAGE_SAVE_PATH + "/_DEADPAGES_.TXT", 'w')

    for i in range(len(DEAD_PAGE_INDICES)):
        dead_page_file.write(str(DEAD_PAGE_INDICES[i]) + ",")
    
    dead_page_file.close()

def find_last_downloaded_file_index():
    max_so_far = 0
    for i,j,y in os.walk(PAGE_SAVE_PATH):
        directory_name_index = i.rfind('Pages\\')
        if (-1 != directory_name_index):
            directory_name_index += len("Pages\\")
            file_index = int(i[directory_name_index:])

            if (file_index > max_so_far):
                max_so_far = file_index

    return max_so_far

def main():
    try:
        os.mkdir(PAGE_SAVE_PATH, 755)
    except:
        print("lol")

    i_exception_shift = 0
    range_start = find_last_downloaded_file_index()
    print("Grabbing files starting at " + str(range_start))

    for i in range(range_start, 1000000):
        try:
            i -= i_exception_shift
            url = BASE_URL + str(i)
            get_page(url, i)

            if (i % 10 == 0):
                print(i)
                save_dead_page_indices()

            time.sleep(1)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(e)
            print("error occured WTF")
            i_exception_shift += 1
            time.sleep(10)

main()