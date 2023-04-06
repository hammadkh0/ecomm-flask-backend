import time
import concurrent.futures

from itertools import chain
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from configs import selenium_config

from scrape_util import scrape_amazon_product_from_rows, scrape_amazon_categories_from_rows, scrape_alibaba_product_from_rows, scrape_alibaba_supplier_from_rows, find_attributes, scrape_amazon_reviews

from summarize import get_keywords


def find_product_list(url, user_input):

    driver = selenium_config()

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


def find_product_details(url, asin):

    driver = selenium_config()
    driver.get(url)

    # convert the page to beautiful soup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # find the product title
    title = soup.find(id="productTitle").get_text().strip()
    if title is None:
        return {
            "error": f"No items were found for the asin: {asin}",
            "status": 404
        }
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
    reviews_link = "" if reviews_link is None else reviews_link["href"]
    keywords_list = get_keywords(title)
    driver.quit()
    return {
        "status": 200,
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
            "reviews_link": reviews_link,
            "keywords_list": keywords_list
        }
    }


def find_product_reviews(url, asin='B098FKXT8L'):

    urls = []
    reviews = []
    for i in range(1, 5):
        urls.append(
            f"https://www.amazon.com/{url}&sortBy=recent&pageNumber={i}")

    # Create a list of variable values from 1 to the length of urls
    variable_values = list(range(1, len(urls) + 1))

    # Zip the urls and the variable values together
    url_variable_pairs = zip(urls, variable_values)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = executor.map(scrape_amazon_reviews, url_variable_pairs)
        if results is None:
            pass
        else:
            #reviews = [*reviews, *list(results)]
            reviews = reviews + list(chain(*results))

    return {"reviews": reviews, "item_count": len(reviews)}


def find_best_sellers():
    driver = selenium_config()
    action = ActionChains(driver)
    driver.get("https://www.amazon.com/Best-Sellers/zgbs")

    best_categories = driver.find_elements(By.CSS_SELECTOR,
                                           ".a-section.a-spacing-large")

    best_sellers = []
    for i, category in enumerate(best_categories):
        if (i == len(best_categories)):
            break
        try:
            action.move_to_element(category).perform()
            category_name = category.find_element(
                By.CSS_SELECTOR, '.a-carousel-heading.a-inline-block').text
        except:
            category_name = ""

        sub_list = []
        for i in range(2):
            best_items = category.find_elements(By.CSS_SELECTOR,
                                                '.a-carousel-card')

            best_items = [
                BeautifulSoup(element.get_attribute("outerHTML"),
                              "html.parser") for element in best_items
            ]

            for product in best_items:
                item = product.find('div',
                                    {'class': 'p13n-sc-uncoverable-faceout'})
                item = "" if item is None else item
                asin = "" if item is None else item['id']

                # id of the item div

                image_tag = item.find('img')
                image = "" if image_tag is None else image_tag['src']
                title = "" if image_tag is None else image_tag["alt"]

                link_tag = item.find('a', {'class': 'a-link-normal'})
                link = "" if link_tag is None else link_tag['href']

                rating_div = item.find('div', {'class': 'a-icon-row'})
                rating = "" if rating_div is None else rating_div.a[
                    'title'].split(" ")[0]

                rating_count = item.find('span', {'class': 'a-size-small'})
                rating_count = "" if rating_count is None else rating_count.text

                price = item.find('span', {'class': 'a-color-secondary'})
                if price is None:
                    price = item.find('span',
                                      {'class': '_cDEzb_p13n-sc-price_3mJ9Z'})
                price = "" if price is None else price.text
                sub_list.append({
                    "asin": asin,
                    "image": image,
                    "title": title,
                    "link": link,
                    "rating": rating,
                    "rating_count": rating_count,
                    "price": price
                })

            category.find_elements(By.CSS_SELECTOR,
                                   ".a-button-inner")[0].click()
            time.sleep(1.7)
        best_sellers.append({"category": category_name, "items": sub_list})

    return best_sellers


def find_suppliers_list(input_term):
    driver = selenium_config()

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
    driver = selenium_config()
    driver.get("https:" + url)

    L = driver.find_elements(By.CSS_SELECTOR,
                             "li.detail-next-tabs-tab.details-tab-pane")
    for i in L:
        if i.text == "Company profile":
            i.click()
            break

    # wait untill the company profile tab is loaded
    time.sleep(3)

    company_1 = driver.find_element(By.ID, "block-tab-company")
    company = BeautifulSoup(company_1.get_attribute('innerHTML'),
                            "html.parser")

    overview = company.find('div', {'class': 'block-bottom'})
    overview = "" if overview is None else overview
    ow = []
    overview_rows = overview.find_all('tr')
    if overview_rows is not None:
        for row in overview_rows:
            tds = row.find_all('td')
            key = tds[0].text.strip()
            value = tds[1].find('div', {'class': 'content-value'})
            value = "" if value is None else value.text.strip()

            ow.append({"key": key, "value": value})
            key = tds[2].text.strip()
            value = tds[3].find('div', {'class': 'content-value'})
            if value is None:
                value = tds[3].find('a', {'class': 'content-value'})
            value = "" if value is None else value.text.strip()
            ow.append({"key": key, "value": value})

    prod_capacity = company.find(
        'div', {'module-name': 'icbu-pc-cpProductionCapacity'})
    prod_tables = prod_capacity.find_all('div',
                                         {'class': 'infoList-mod-field'})
    pc = []

    for i, infos in enumerate(prod_tables):
        title = infos.find('div', {'class': 'title'}).text.strip()
        if title == "COOPERATE FACTORY INFORMATION":
            print(title)
            sub_tbl = []
            table = infos.find('table')
            trs = table.find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')

                key = tds[0].text.strip()
                value = tds[1].text.strip()
                sub_tbl.append({"key": key, "value": value})
            pc.append({
                "title": title,
                "cooperate_factory_information": sub_tbl
            })

        elif title == "Production Equipment":
            print(title)

            table_body = infos.find('div', {'class': 'next-table-body'})
            table = table_body.find('table')
            tds = table.find_all('td')

            name = tds[0].text.strip()
            no = tds[1].text.strip()
            quantity = tds[2].text.strip()
            verified = tds[3].text.strip()

            pc.append({
                "title": title,
                "production_equipment": {
                    "name": name,
                    "NO": no,
                    "quantity": quantity,
                    "verified": verified
                }
            })
        elif title == "Factory Information":
            print(title)
            try:
                driver.find_element(
                    By.XPATH,
                    '//*[@id="module_ali_site"]/div/div[2]/div/div/div/div[2]/div/div[2]/div'
                ).click()
                sub_tbl = []
                table = infos.find('table', {'class': 'icbu-shop-table-col'})
                trs = table.find_all('tr')
                for tr in trs:
                    tds = tr.find_all('td')

                    key = tds[0].text.strip()
                    value = tds[1].text.strip()
                    sub_tbl.append({"key": key, "value": value})

                pc.append({"title": title, "factory_information": sub_tbl})
            except:
                sub_tbl = []
                table = infos.find('table', {'class': 'icbu-shop-table-col'})
                trs = table.find_all('tr')
                for tr in trs:
                    tds = tr.find_all('td')

                    key = tds[0].text.strip()
                    value = tds[1].text.strip()
                    sub_tbl.append({"key": key, "value": value})

                pc.append({"title": title, "factory_information": sub_tbl})

        elif title == "Annual Production Capacity":
            print(title)

            table_body = infos.find('div', {'class': 'next-table-body'})
            table = table_body.find('table')
            tds = table.find_all('td')

            name = tds[0].text.strip()
            line_capac = tds[1].text.strip()
            units_produced = tds[2].text.strip()
            verified = tds[3].text.strip()

            pc.append({
                "title": title,
                "annual_prod_capacity": {
                    "name": name,
                    "line_capacity": line_capac,
                    "units_produced": units_produced,
                    "verified": verified
                }
            })

    quality_control = company.find(
        'div', {'module-name': 'icbu-pc-cpQualityControlCapacity'})
    qc = []
    if quality_control is not None:
        qc_table = quality_control.find('div', {
            'class': 'next-table-body'
        }).table
        trs = qc_table.find_all('tr')
        if trs is not None:
            for tr in trs:
                tds = tr.find_all('td')
                if tds is not None:
                    key = tds[0].text.strip()
                    value = tds[1].text.strip()
                    qc.append({"key": key, "value": value})

    rnd_capacity = company.find('div', {'module-name': 'icbu-pc-cpRDCapacity'})
    rnd = []
    if rnd_capacity is not None:
        rnd_table = rnd_capacity.find('div', {'class': 'next-table-body'})
        if rnd_table is not None:
            rnd_table = rnd_table.table
            tr = rnd_table.find('tr')
            tds = tr.find_all('td')

            img = tds[0].find('img')
            img = "" if img is None else img['src']

            trademark_no = tds[1].text.strip()
            trademark_name = tds[2].text.strip()
            trademark_catg = tds[3].text.strip()
            trademark_date = tds[4].text.strip()
            verified = tds[5].text.strip()

            rnd.append({
                "trademark": {
                    "img": img,
                    "trademark_number": trademark_no,
                    "trademark_name": trademark_name,
                    "trademark_category": trademark_catg,
                    "available_date": trademark_date,
                    "verified": verified
                }
            })

    trade_capability = company.find(
        'div', {'module-name': 'icbu-pc-cpTradeCapability'})
    trade = []
    if trade_capability is not None:
        driver.find_element(
            By.XPATH,
            '//*[@id="module_ali_site"]/div/div[5]/div/div/div/div[2]/div/div[2]/div'
        ).click()

        trade_table = trade_capability.find_all(
            'div', {'class': 'infoList-mod-field'})
        for i, infos in enumerate(trade_table):
            title = infos.find('div', {'class': 'title'}).text.strip()
            if title == "Main Markets & Product(s)":
                table_body = infos.find('div', {'class': 'next-table-body'})
                table = table_body.find('table')

                trs = table.find_all('tr')
                main_market_info = []
                for tr in trs:
                    tds = tr.find_all('td')
                    if tds is not None:
                        main_market_info.append({
                            "main_market":
                            tds[0].text.strip(),
                            "total_revenue":
                            tds[1].text.strip(),
                            "main_products":
                            tds[2].text.strip(),
                            "verified":
                            tds[3].text.strip()
                        })
                trade.append({
                    "title": title,
                    "main_market_info": main_market_info
                })

            elif title == "Trade Ability" or title == "Business Terms":
                table = infos.find('table')
                trs = table.find_all('tr')
                tt = []
                if trs is not None:
                    for tr in trs:
                        tds = tr.find_all('td')
                        if tds is not None:
                            key = tds[0].text.strip()
                            value = tds[1].text.strip()
                            tt.append({"key": key, "value": value})
                    if title == "Trade Ability":
                        trade.append({"title": title, "trade_ability": tt})
                    elif title == "Business Terms":
                        trade.append({"title": title, "business_terms": tt})

    driver.quit()

    return {
        "overview": ow,
        "production_capacity": pc,
        "quality_control": qc,
        "rnd_capacity": rnd,
        "trade_capability": trade
    }


def find_supplier_prodcut_details(url):

    driver = selenium_config()

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
        entry_list = "" if entry_list is None else entry_list

        entry_list = entry_list.find_all('dl', {'class': 'do-entry-item'})
        entry_list = [] if entry_list is None else entry_list

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
        entry_list = "" if entry_list is None else entry_list

        entry_list = entry_list.find_all('dl', {'class': 'do-entry-item'})
        entry_list = [] if entry_list is None else entry_list

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
        entry_list = "" if entry_list is None else entry_list

        entry_list = entry_list.find_all('dl', {'class': 'do-entry-item'})[:2]
        entry_list = [] if entry_list is None else entry_list

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
