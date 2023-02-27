from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from scrape_util import scrape_amazon_product_from_rows, scrape_amazon_categories_from_rows, scrape_alibaba_product_from_rows, scrape_alibaba_supplier_from_rows


def intial_config():

    ua = UserAgent()
    user_agent = ua.random

    options = Options()
    #options.add_argument("--headless")
    options.add_argument(f'user-agent={user_agent})')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)

    print(options.arguments)
    print("----------------------------------------")

    # simulate headless mode by minimizing the window
    driver.set_window_size(1366, 768)
    #driver.set_window_position(-2000, 0)
    return driver


def find_product_list(url, user_input):

    driver = intial_config()

    #load page with beautiful soup
    driver.get(url)
    #driver.get_screenshot_as_file("screenshot1.png")

    # find the search bar and enter the input
    driver.find_element(By.ID, "twotabsearchtextbox").send_keys(user_input)
    # click the search button
    driver.find_element(By.ID, "nav-search-submit-button").click()

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # find all the search results on single page
    output = soup.find_all('div', {'data-component-type': 's-search-result'})

    # wait 1 second for the page to load
    driver.implicitly_wait(1)

    categories = scrape_amazon_categories_from_rows(soup)

    scraped_items = []
    # find the data from the search results
    for row in output:
        asin, title, img, price, rating, rating_count, link = scrape_amazon_product_from_rows(
            url, row)

        data = {
            "asin": asin,
            "title": title,
            "image": img,
            "price": price,
            "rating": rating,
            "rating_count": rating_count,
            "link": link,
            "categories": categories
        }
        scraped_items.append(data)

    total_items = len(scraped_items)
    driver.quit()
    return {"products": scraped_items, "item_count": total_items}


def find_suppliers_list(input_term):
    driver = intial_config()

    driver.get("https://alibaba.com")

    driver.find_element(By.CLASS_NAME,
                        "ui-searchbar-keyword").send_keys(input_term)

    # click the input field to submit the search query
    driver.find_element(By.CLASS_NAME, "ui-searchbar-submit").click()

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # find all the search results on single page by div
    output = soup.find_all(
        'div', {
            'class':
            'organic-list-offer-inner m-gallery-product-item-v2 img-switcher-parent'
        })

    scraped_items = []
    for row in output:
        products_info = scrape_alibaba_product_from_rows(row)

        supplier_info = scrape_alibaba_supplier_from_rows(row)

        data = {"product": products_info, "supplier": supplier_info}
        scraped_items.append(data)

    driver.quit()

    return {"item_count": len(scraped_items), "results": scraped_items}
