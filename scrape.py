from agent_list import AGENT_LIST
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


def scrape_data(url, HEADERS, input):
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
    driver.set_window_size(1920, 1080)
    driver.set_window_position(-2000, 0)

    #load page with beautiful soup
    driver.get(url)

    # find the search bar and enter the input
    driver.find_element(By.ID, "twotabsearchtextbox").send_keys(input)
    # click the search button
    driver.find_element(By.ID, "nav-search-submit-button").click()

    soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.get_screenshot_as_file("screenshot3.png")

    scraped_items = find_product_list(url, soup=soup)
    driver.quit()
    return scraped_items


def find_product_list(url, soup):

    #soup2 = BeautifulSoup(driver.page_source, "html.parser")
    output = soup.find_all('div', {'data-component-type': 's-search-result'})
    print(len(output))
    scraped_items = []
    for row in output:
        asin = row['data-asin']

        title = row.find('span',
                         {"class": "a-size-medium a-color-base a-text-normal"})
        title = "" if title == None else title.text

        img = row.find('img', {"class": "s-image"})
        img = "" if img == None else img['src']

        price = row.find('span', {'class': 'a-offscreen'})
        price = "" if price == None else price.text

        rating = row.find('div', {
            "class": "a-row a-size-small"
        }).find('span', {'class': 'a-icon-alt'})
        rating = "" if rating == None else rating.text

        rating_count = row.find('span',
                                {'class': 'a-size-base s-underline-text'})
        rating_count = "" if rating_count == None else rating_count.text

        link = row.find('span', {
            'data-component-type': 's-product-image'
        }).find('a')['href']
        link = "" if link == None else url + link
        data = {
            "asin": asin,
            "title": title,
            "img": img,
            "price": price,
            "rating": rating,
            "rating_count": rating_count,
            "link": link,
        }
        scraped_items.append(data)

    # driver.quit()
    return scraped_items
