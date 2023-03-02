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
    # add incognito mode to options
    options.add_argument("--incognito")

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

    driver.find_element(
        By.XPATH,
        '//*[@id="J_SC_header"]/header/div[3]/div/div/div[2]/div/div[1]/div/input'
    ).send_keys(input_term)

    # click the input field to submit the search query
    driver.find_element(
        By.XPATH,
        '//*[@id="J_SC_header"]/header/div[3]/div/div/div[2]/div/div[1]/div/button'
    ).click()

    soup = BeautifulSoup(driver.page_source, "html.parser")

    output = soup.find('div',
                       {'class': 'organic-list app-organic-search__list'})

    # In the has_classes function, tag is a parameter that represents an element in the HTML document. When you pass this function to the find_all method of a BeautifulSoup object, it will call this function for each element in the document and pass the element as an argument to the function.
    def has_classes(tag):
        classes = tag.get('class', [])
        classes = [] if classes is None else classes
        #The function will then return True if the element matches the criteria and False if it doesn’t. The find_all method will then return a list of elements that match the criteria.
        return 'J-offer-wrapper' in classes and 'traffic-product-card' in classes

    output2 = output.find_all(has_classes)

    scraped_items = []

    # this i will generate a unique id for each product
    i = 0
    for row in output2:

        products_info = scrape_alibaba_product_from_rows(row)

        # supplier_info = scrape_alibaba_supplier_from_rows(row)
        supplier_info = {}

        data = {"id": i, "product": products_info, "supplier": supplier_info}
        scraped_items.append(data)
        i += 1

    driver.quit()

    return {"item_count": len(scraped_items), "results": scraped_items}
