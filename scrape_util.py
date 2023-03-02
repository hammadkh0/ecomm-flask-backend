from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains


def scrape_amazon_product_from_rows(url, row):
    asin = row['data-asin']

    title = row.find('span',
                     {"class": "a-size-base-plus a-color-base a-text-normal"})
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

    rating_count = row.find('span', {'class': 'a-size-base s-underline-text'})
    rating_count = "" if rating_count is None else rating_count.text

    link = row.find('span', {
        'data-component-type': 's-product-image'
    }).find('a')['href']
    link = "" if link is None else url + link

    return asin, title, img, price, rating, rating_count, link


def scrape_amazon_categories_from_rows(soup):

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

    return categories


def scrape_alibaba_product_from_rows(row):
    # find the image
    img_div = row.find('div', {"class": "seb-img-switcher__imgs"})
    img_div = "" if img_div is None else img_div['data-image']

    # find the title
    title = row.find('h2', {"class": "elements-title-normal__outter"})
    title_text = "" if title is None else title["title"]

    #find the link
    link = title.find('a')
    link = "" if link is None else link['href']

    # find the price range
    price_range = row.find('span',
                           {"class": "elements-offer-price-normal__price"})
    price_range = "" if price_range is None else price_range.text

    #find the min order quantity
    min_order = row.find('span',
                         {"class": "element-offer-minorder-normal__value"})
    min_order = "" if min_order is None else min_order.text

    #find other properties
    extras = {}
    details = row.find_all(
        'p', {"class": "organic-list-offer-center__property-item"})
    details = [] if details is None else details
    for item in details:
        spans = item.find_all('span')
        spans = [] if spans is None else spans
        key = spans[0].text if len(spans) > 0 else ""
        value = spans[1].text if len(spans) > 1 else ""
        extras[key] = value

    return {
        "title": title_text,
        "image": img_div,
        "link": link,
        "price_range": price_range,
        "min_order": min_order,
        "details": extras
    }


def scrape_alibaba_supplier_from_rows(row, driver):

    # check if supplier is verified
    isVerified = row.find(
        'i', {
            "class":
            "icbu-certificate-icon icbu-certificate-icon-verified supplier-tag-verified"
        })
    isVerified = False if isVerified is None else True

    if isVerified is False:
        return {}

    # check if the supplier data is present in row format
    supplier_row = row.find('div',
                            {"class": "list-no-v2-decisionsup__row flex-row"})
    # check if the supplier data is present in column format
    supplier_col = row.find('div',
                            {"class": "organic-list-offer-right type-simple"})
    supplier_data = {}
    # if row is None, then supplier data is in column format so scrape the column data as both have different classes and structure
    if supplier_row is None:
        supplier_data = scrape_sub_column(supplier_col)
    else:
        supplier_data = scrape_sub_row(supplier_row, driver)

    # add the verified status to the supplier data
    supplier_data["isVerified"] = isVerified

    return supplier_data


# ----------------- SCRAPING HELPERS -----------------
def scrape_sub_column(row):

    # check supplier level
    supplier_level = row.find(
        'a', {"class": "seller-start-level list-offer-seller-tag"})
    if supplier_level is None:
        supplier_level = row.find(
            'a', {"class": "seller-start-level gallery-offer-seller-tag"})

    diamonds = supplier_level.find_all('i')
    # get class name from <i> in diamonds[0]
    level = 0 if diamonds[0]['class'][3] == "dm-grey" else len(diamonds)

    if level < 2:
        return {}

    # supplier experience
    supplier_experience = row.find(
        "span", {"class": "seller-tag__year list-offer-seller-tag"})
    supplier_experience = "" if supplier_experience is None else supplier_experience.text

    # supplier country
    supplier_country = row.find(
        'span',
        {"class": "seller-tag__country list-offer-seller-tag bg-visible"})
    supplier_country = "" if supplier_country is None else supplier_country[
        "title"]

    # supplier name from a tag
    supplier_name_a = row.find('a',
                               {"class": "organic-list-offer__seller-company"})
    supplier_name = "" if supplier_name_a is None else supplier_name_a.text

    # supplier link
    supplier_link = supplier_name_a[
        'href'] if supplier_name_a is not None else ""

    # check supplier rating
    supplier_rating = row.find('span', {"class": "seb-supplier-review__score"})
    supplier_rating = "" if supplier_rating is None else supplier_rating.text

    # supplier last 6 months orders
    supplier_orders = row.find("div", {"class": "company-sinfo-item__content"})
    supplier_orders = "" if supplier_orders is None else supplier_orders.text

    return {
        "name": supplier_name,
        "level": level,
        "link": supplier_link,
        "country": supplier_country,
        "rating": supplier_rating,
        "prev_orders": supplier_orders,
        "experience": supplier_experience
    }


def scrape_sub_row(row, driver):
    # supplier level
    supplier_level = row.find(
        'a', {"class": "seller-start-level gallery-offer-seller-tag"})

    diamonds = supplier_level.find_all('i')
    # get class name from <i> in diamonds[0]
    level = 0 if diamonds[0]['class'][3] == "dm-grey" else len(diamonds)

    if level < 2:
        return {}

    # supplier experience
    supplier_experience = row.find(
        "span", {"class": "seller-tag__year flex-no-shrink"})
    supplier_experience = "" if supplier_experience is None else supplier_experience.text

    # supplier country
    supplier_country = row.find(
        'span', {"class": "seller-tag__country flex-no-shrink"})
    supplier_country = "" if supplier_country is None else supplier_country[
        "title"]

    # supplier rating
    supplier_rating = row.find(
        'span', {"class": "seb-supplier-review-gallery-test__score"})
    supplier_rating = "" if supplier_rating is None else supplier_rating.span.text.strip(
    )

    # supplier name from a tag
    supplier_popup = driver.find_element(By.CLASS_NAME, "tag-country-right")

    # craete action chain object using webdriver to hover over the element
    action = ActionChains(driver)
    action.move_to_element(supplier_popup).pause(2).perform()

    # find the supplier name and link from the popup that appears on hover
    some_div = driver.find_element(By.CLASS_NAME, "next-overlay-wrapper")

    # move to the div to make the popup stay visible and then find the elements
    action.move_to_element(some_div).perform()

    supplier_info = some_div.find_element(By.CLASS_NAME,
                                          "supplier-tag-popup__content_href")

    # supplier name
    supplier_name = supplier_info.text
    # supplier link
    supplier_link = supplier_info.get_attribute("href")

    return {
        "name": supplier_name,
        "level": level,
        "link": supplier_link,
        "country": supplier_country,
        "rating": supplier_rating,
        "experience": supplier_experience
    }
