from scrape import find_best_sellers, find_product_list, find_product_details, find_product_reviews, search_asin
import time
import random
from email.header import Header
from wsgiref import headers
from torpy.http.requests import TorRequests
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def product_list_request(url, user_input):
    with TorRequests() as tor_requests:
        with tor_requests.get_session() as sess:

            # -- print the IP address of the proxy
            print(sess.get("http://httpbin.org/ip").json())

            # -- pause randomly between 1 to 3 seconds
            #time.sleep(random.randint(1, 3))

            # -- get the html content
            #html_content = sess.get(url, headers=HEADERS, timeout=10).text

            # -- your scraping code here ..
            data = find_product_list(url, user_input)
            return data


def specific_product_request(url):
    with TorRequests() as tor_requests:
        with tor_requests.get_session() as sess:

            # -- print the IP address of the proxy
            print(sess.get("http://httpbin.org/ip").json())

            # -- pause randomly between 1 to 3 seconds
            #time.sleep(random.randint(1, 3))

            # -- your scraping code here ..
            data = find_product_details(url)
            return data


def product_by_asin(url, asin):
    with TorRequests() as tor_requests:
        with tor_requests.get_session() as sess:

            # -- print the IP address of the proxy
            print(sess.get("http://httpbin.org/ip").json())

            # -- pause randomly between 1 to 3 seconds
            #time.sleep(random.randint(1, 3))

            # -- your scraping code here ..
            data = search_asin(url, asin)
            return data


def product_reviews_request(url):

    # -- your scraping code here ..
    data = find_product_reviews(url)
    return data


def best_seller_request():
    with TorRequests() as tor_requests:
        with tor_requests.get_session() as sess:

            # -- print the IP address of the proxy
            print(sess.get("http://httpbin.org/ip").json())

            # -- pause randomly between 1 to 3 seconds
            #time.sleep(random.randint(1, 3))

            # -- your scraping code here ..
            data = find_best_sellers()
            return data