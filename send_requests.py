from agent_list import AGENT_LIST
from scrape import find_product_list
from pprint import pprint
import time
import random
from email.header import Header
from wsgiref import headers
from torpy.http.requests import TorRequests
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def product_list_request(url, HEADERS, user_input):
    with TorRequests() as tor_requests:
        with tor_requests.get_session() as sess:

            # -- print the IP address of the proxy
            print(sess.get("http://httpbin.org/ip").json())

            # -- pause randomly between 1 to 3 seconds
            #time.sleep(random.randint(1, 3))

            # -- get the html content
            #html_content = sess.get(url, headers=HEADERS, timeout=10).text

            # -- your scraping code here ..
            data = find_product_list(url, HEADERS, user_input)
            #pprint(data)
            # print("\n\n", len(data))

            return data


def specific_product_request():
    pass