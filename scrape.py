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
    options.add_argument("--headless")
    options.add_argument(f'user-agent={user_agent})')
    options.add_argument("--window-size=1366,768")
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


def find_product_details(url):
    driver = intial_config()

    driver.get(url)

    # convert the page to beautiful soup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # find the product title
    title = soup.find(id="productTitle").get_text().strip()

    # find the product rating
    rating = soup.find('span', {'class': 'a-icon-alt'})
    rating = "" if rating is None else rating.text

    # find the product rating count
    rating_count = soup.find('span', {'id': 'acrCustomerReviewText'})
    rating_count = "" if rating_count is None else rating_count.text

    # find the product price
    price = soup.find('span', {'class': 'a-offscreen'})
    price = "" if price is None else price.text

    # find the product images
    # altImages = soup.find(id="altImages")
    # img_list = altImages.find_all(
    #     "li", {"data-csa-c-action": "image-block-alt-image-hover"})
    # img_list = [] if img_list is None else img_list

    images = []
    # for img in img_list:
    #     img = img.find("img")
    #     img = "" if img is None else img["src"]
    #     images.append(img)
    img = soup.find(id="landingImage")
    img = "" if img is None else img
    images.append(img["src"])

    # get style of product
    style = soup.find('div', {'class': 'variation_style_name'})
    style = "" if style is None else style.text

    # get attributes of product
    attibutes_table = soup.find(id="productDetails_detailBullets_sections1")
    attibutes_table = "" if attibutes_table is None else attibutes_table
    attributes = attibutes_table.find_all('tr')
    attributes = [] if attributes is None else attributes
    attb = []
    value = ""

    # find all the attributes inside the table. Both the attributes name and the values are like name-value pairs
    for element in attributes:
        name = element.find(
            'th',
            {'class': 'a-color-secondary a-size-base prodDetSectionEntry'})
        name = "" if name is None else name.text.strip()

        # Customer Reviews and Best Sellers Rank are created differently so they are handled separately
        if name != "Customer Reviews" and name != "Best Sellers Rank":
            value = element.find('td',
                                 {'class': 'a-size-base prodDetAttrValue'})
            value = "" if value is None else value.get_text(strip=True)

        elif name == "Best Sellers Rank":
            value = element.select('td span span')
            value = [val.text.strip() for val in value]
            value = " ".join(value)

        else:
            # just reusing the above variables to save memory and execution time
            value = rating_count + " " + rating

        data = {"name": name, "value": value}
        attb.append(data)

    # get featured bullets of product
    featured_list = soup.find(
        'ul', {'class': 'a-unordered-list a-vertical a-spacing-mini'})

    fl_items = featured_list.find_all('span', {'class': 'a-list-item'})
    fl_items = [] if fl_items is None else fl_items
    fl = []
    for element in fl_items:
        fl.append(element.text.strip())

    # get the description of the product
    description = soup.find(id="productDescription")
    description2 = description.find('p').span
    if (description2 is None):
        description2 = description.find_all('p')[1].span

    description_txt = "" if description2 is None else description2.text.strip()

    driver.quit()
    return {
        "product": {
            "title": title,
            "rating": rating,
            "rating_count": rating_count,
            "price": price,
            "images": images,
            "style": style,
            "attributes": attb,
            "featured_bullets": fl,
            "description": description_txt
        }
    }


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

    output = driver.find_element(By.CSS_SELECTOR,
                                 ".organic-list.app-organic-search__list")

    output2 = output.find_elements(By.CSS_SELECTOR,
                                   ".J-offer-wrapper.traffic-product-card")

    scraped_items = []

    # this i will generate a unique id for each product
    i = 0
    output2 = output2[:min(15, len(output2))]
    for row in output2:
        supplier_info = scrape_alibaba_supplier_from_rows(row, driver)
        if len(supplier_info) == 0 or len(supplier_info) < 2:
            continue
        products_info = scrape_alibaba_product_from_rows(row)

        data = {"id": i, "product": products_info, "supplier": supplier_info}
        scraped_items.append(data)
        i += 1

    driver.quit()

    return {"item_count": len(scraped_items), "results": scraped_items}


def find_suppliers_details(url):
    driver = intial_config()
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    return ""