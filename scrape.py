from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from scrape_util import scrape_amazon_product_from_rows, scrape_amazon_categories_from_rows, scrape_alibaba_product_from_rows, scrape_alibaba_supplier_from_rows, find_attributes


def intial_config():

    ua = UserAgent()
    user_agent = ua.random

    options = Options()
    options.add_argument("--headless")
    options.add_argument(f'user-agent={user_agent})')
    # add incognito mode to options
    options.add_argument("--incognito")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)

    print(options.arguments)
    print("----------------------------------------")

    driver.set_window_size(1366, 768)
    # simulate headless mode by minimizing the window
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

    # get attributes of product from different available tables. If more tables are found they can be addded to the list
    attb = []

    for id in [
            "productDetails_detailBullets_sections1",
            "productDetails_techSpec_section_1",
            "productDetails_techSpec_section_2"
    ]:
        list = find_attributes(soup, attb, rating_count, rating, id)
        attb = [*attb, *list]

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

    # get the reviews link of the product
    reviews_link = soup.find('a', {'data-hook': 'see-all-reviews-link-foot'})
    reviews_link = "" if reviews_link is None else "amazon.com" + reviews_link[
        "href"]
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
            "description": description_txt,
            "reviews_link": reviews_link
        }
    }


def find_product_reviews(url):
    driver = intial_config()

    driver.get("https://" + url)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    review_div = soup.find(id="cm_cr-review_list")
    raw_reviews = review_div.find_all('div', {'data-hook': 'review'})

    reviews = []
    for raw_item in raw_reviews:
        author = raw_item.find('span', {'class': 'a-profile-name'})
        author = "" if author is None else author.text

        rating = raw_item.find('i', {'data-hook': 'review-star-rating'})
        rating = "" if rating is None else rating.span.text.split(" ")[0]

        title = raw_item.find('a', {'data-hook': 'review-title'})
        title = "" if title is None else title.text.strip()

        body = raw_item.find('span', {'data-hook': 'review-body'})
        body = "" if body is None else body.text.strip()

        reviews.append({
            "author": author,
            "rating": rating,
            "title": title,
            "body": body
        })

    return {"reviews": reviews, "item_count": len(reviews)}


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


def find_supplier_prodcut_details(url):

    driver = intial_config()

    driver.get("https:" + url)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # get the title of the product
    title = soup.find('div', {'class': 'product-title'})
    title = "" if title is None else title.text.strip()

    # get price list of the product
    price_list = soup.find('div', {'class': 'price-list'})
    price_list = "" if price_list is None else price_list
    price_list = price_list.find_all('div', {'class': 'price-item'})
    prices = []
    if price_list is not None:
        for price_item in price_list:
            quality = price_item.find('div', {'class': 'quality'})
            quality = "" if quality is None else quality.text.strip()
            price = price_item.find('div', {'class': 'price'})
            price = "" if price is None else price.text.strip()

            prices.append({"quality": quality, "price": price})

    # find lead time
    lead_list = soup.find('div', {'class': 'lead-list'})
    lead_list = "" if lead_list is None else lead_list.table
    lead_time = []
    if lead_list is not None:
        lead_list = lead_list.find_all('tr')
        r1 = lead_list[0].find_all('td')
        r2 = lead_list[1].find_all('td')

        for i in range(1, len(r1)):
            quantity = r1[i].text.strip()
            price = r2[i].text.strip()

            lead_time.append({"quantity": quantity, "price": price})

    # find essential information
    essential_info = soup.find('div', {'data-e2e-name': 'quickDetail'})
    el = []
    if essential_info is not None:
        entry_list = essential_info.find('div', {'class': 'do-entry-list'})
        entry_list = entry_list.find_all('dl', {'class': 'do-entry-item'})
        for element in entry_list:
            key = element.find('span', {'class': 'attr-name J-attr-name'})
            key = "" if key is None else key["title"].strip()

            value = element.find('div', {'class': 'text-ellipsis'})
            value = "" if value is None else value["title"].strip()
            el.append({"key": key, "value": value})

    supply_ability = soup.find('div', {'data-e2e-name': 'supplyAbility'})
    sa = []
    if supply_ability is not None:
        entry_list = supply_ability.find('div', {'class': 'do-entry-list'})
        entry_list = entry_list.find_all('dl', {'class': 'do-entry-item'})
        for element in entry_list:
            key = element.find('dt')
            key = "" if key is None else key["title"]

            value = element.find('dd')
            value = "" if value is None else value["title"]
            sa.append({"key": key, "value": value})

    package_ability = soup.find('div', {'data-e2e-name': 'productPackaging'})
    pa = []
    if package_ability is not None:
        entry_list = package_ability.find('div', {'class': 'do-entry-list'})
        entry_list = entry_list.find_all('dl', {'class': 'do-entry-item'})[:2]
        for element in entry_list:
            key = element.find('dt')
            key = "" if key is None else key["title"].strip()

            value = element.find('span')
            value = "" if value is None else value.text.strip()
            pa.append({"key": key, "value": value})

    driver.quit()
    return {
        "title": title,
        "prices": prices,
        "lead_time": lead_time,
        "essential_info": el,
        "supply_ability": sa,
        "package_delivery": pa
    }
