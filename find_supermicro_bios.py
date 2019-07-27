import requests
import pdb
from bs4 import BeautifulSoup
import time

import re


base_url = "https://www.supermicro.com/support/resources/getfile.php?SoftwareItemID="

for i in range(0, 100000):
    try:
        url = base_url + str(i)
        page = requests.get(url)
        if (page.url != url):
            if (page.url.find("H11SSL") > -1):
                print(page.url)
            elif (page.url.find("H11") > -1):
                print(page.url)

        if (i % 10 == 0):
            print(i)

        time.sleep(1)
    except KeyboardInterrupt:
        raise
    except:
        print("error occured")