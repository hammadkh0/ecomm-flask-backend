from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


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

    # find the category div and the list of categories in it
    departments = soup.find('ul', {'aria-labelledby': 'n-title'})
    departments = [] if departments is None else departments
    categories_container = departments.find_all('li',
                                                {'class': 'a-spacing-micro'})
    categories_container = [] if categories_container is None else categories_container

    categories = []
    for item in categories_container:
        # check if no item has class "a-spacing-micro s-navigation-indent-1" to aoid subcategories
        # classes are split by whitespaces so check if length is 2
        if (len(item['class']) == 2):
            continue

        item2 = item.find('span', {'class': 'a-size-base a-color-base'})
        item2 = "" if item2 is None else item2.text
        categories.append(item2)

    scraped_items = []
    # find the data from the search results
    for row in output:
        asin = row['data-asin']

        title = row.find(
            'span', {"class": "a-size-base-plus a-color-base a-text-normal"})
        title = "" if title is None else title.text

        img = row.find('img', {"class": "s-image"})
        img = "" if img is None else img['src']

        price = row.find('span', {'class': 'a-offscreen'})
        price = "" if price is None else price.text

        rating = row.find('div', {
            "class": "a-row a-size-small"
        }).find('span', {'class': 'a-icon-alt'})
        rating = "" if rating is None else rating.text
        # rating = 4.4 out of 5 stars so split by whitespace and take the first element
        rating = rating.split(" ")[0]

        rating_count = row.find('span',
                                {'class': 'a-size-base s-underline-text'})
        rating_count = "" if rating_count is None else rating_count.text

        link = row.find('span', {
            'data-component-type': 's-product-image'
        }).find('a')['href']
        link = "" if link is None else url + link

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
    return scraped_items, total_items


def find_suppliers_list():
    driver = intial_config()

    driver.get("https://alibaba.com")

    driver.get_screenshot_as_file("screenshot.png")
    driver.find_element(
        By.CLASS_NAME,
        "ui-searchbar-keyword").send_keys("carburator motorcycle")

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
        # find the image
        img_div = row.find('div', {"class": "seb-img-switcher__imgs"})
        img_div = "" if img_div is None else img_div['data-image']

        # find the title
        title = row.find('p',
                         {"class": "elements-title-normal__content medium"})
        title = "" if title is None else title.text

        data = {
            "title": title,
            "image": img_div,
        }
        scraped_items.append(img_div)

    print(len(scraped_items), scraped_items)
    driver.quit()


find_suppliers_list()
