from flask import Flask, request, json
from flask_cors import CORS
from sentiment import get_sentiment
from send_requests import product_by_asin, product_list_request, specific_product_request, product_reviews_request
from scrape import find_suppliers_list, find_suppliers_details, find_supplier_prodcut_details
from summarize import generate_summary
from trends import get_related_results, get_trends_by_region

# create the Flask app
app = Flask(__name__)
CORS(app)


@app.route('/ecomm/products', methods=['POST', 'OPTIONS'])
def get_products():
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin':
            '*',
            'Access-Control-Allow-Methods':
            'POST',
            'Access-Control-Allow-Headers':
            'Content-Type, Authorization, Access-Control-Allow-Origin'
        }
        return ('', 204, headers)
    else:
        request_data = request.get_json()
        url = request_data['url']
        input_term = request_data['input_term']
        try:
            products_data = product_list_request(url, input_term)
            response = app.response_class(response=json.dumps(products_data),
                                          status=200,
                                          mimetype='application/json')
            return response
        except Exception as e:
            print(e)
            response = app.response_class(response=json.dumps({
                "ERROR": str(e),
                "status": 500
            }),
                                          status=500,
                                          mimetype='application/json')
            return response


@app.route('/ecomm/products/<asin>/reviews', methods=['POST'])
def get_reviews(asin):
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin':
            '*',
            'Access-Control-Allow-Methods':
            'POST',
            'Access-Control-Allow-Headers':
            'Content-Type, Authorization, Access-Control-Allow-Origin'
        }
        return ('', 204, headers)
    else:
        request_data = request.get_json()
        url = request_data['reviews_link']

        try:
            reviews = product_reviews_request(url)

            return app.response_class(response=json.dumps(reviews),
                                      status=200,
                                      mimetype='application/json')
        except Exception as e:
            response = app.response_class(response=json.dumps({
                "ERROR": str(e),
                "status": 500
            }),
                                          status=500,
                                          mimetype='application/json')
            return response


@app.route('/ecomm/products/<asin>', methods=['POST'])
def get_single_product(asin):
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin':
            '*',
            'Access-Control-Allow-Methods':
            'POST',
            'Access-Control-Allow-Headers':
            'Content-Type, Authorization, Access-Control-Allow-Origin'
        }
        return ('', 204, headers)
    else:
        request_data = request.get_json()
        url = request_data['link']

        try:
            details = specific_product_request(url)

            return app.response_class(response=json.dumps(details),
                                      status=200,
                                      mimetype='application/json')
        except Exception as e:
            response = app.response_class(response=json.dumps({
                "ERROR": str(e),
                "status": 500
            }),
                                          status=500,
                                          mimetype='application/json')
            return response


@app.route('/ecomm/products/search/<asin>', methods=['POST'])
def get_search_product(asin):
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin':
            '*',
            'Access-Control-Allow-Methods':
            'POST',
            'Access-Control-Allow-Headers':
            'Content-Type, Authorization, Access-Control-Allow-Origin'
        }
        return ('', 204, headers)
    else:
        request_data = request.get_json()
        asin = request_data['asin']
        url = request_data['url']

        try:
            details = product_by_asin(url, asin)

            return app.response_class(response=json.dumps(details),
                                      status=200,
                                      mimetype='application/json')
        except Exception as e:
            response = app.response_class(response=json.dumps({
                "ERROR": str(e),
                "status": 500
            }),
                                          status=500,
                                          mimetype='application/json')
            return response


@app.route("/ecomm/suppliers", methods=['POST'])
def get_suppliers():
    request_data = request.get_json()

    input_term = request_data['input_term']
    suppliers_data = {}
    try:
        suppliers_data = find_suppliers_list(input_term)
        response = app.response_class(response=json.dumps(suppliers_data),
                                      status=200,
                                      mimetype='application/json')
        return response

    except Exception as e:
        print(e)
        response = app.response_class(response=json.dumps({
            "error": str(e),
            "status": 500
        }),
                                      status=500,
                                      mimetype='application/json')
        return response


@app.route('/ecomm/suppliers/details', methods=['POST'])
def get_supplier_details():
    request_data = request.get_json()

    url = request_data['url']
    try:
        supplier_details = find_suppliers_details(url)
        return app.response_class(response=json.dumps(supplier_details),
                                  status=200,
                                  mimetype='application/json')
    except Exception as e:
        print(e)
        response = app.response_class(response=json.dumps({
            "error": str(e),
            "status": 500
        }),
                                      status=500,
                                      mimetype='application/json')
        return response


@app.route('/ecomm/suppliers/product/details', methods=['POST'])
def get_supplier_product_details():
    request_data = request.get_json()

    url = request_data['product_link']
    try:
        supplier_details = find_supplier_prodcut_details(url)
        return app.response_class(response=json.dumps(supplier_details),
                                  status=200,
                                  mimetype='application/json')
    except Exception as e:
        print(e)
        response = app.response_class(response=json.dumps({
            "error": str(e),
            "status": 500
        }),
                                      status=500,
                                      mimetype='application/json')
        return response


@app.route('/ecomm/sentiment', methods=['POST'])
def analyze_sentiment():
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin':
            '*',
            'Access-Control-Allow-Methods':
            'POST',
            'Access-Control-Allow-Headers':
            'Content-Type, Authorization, Access-Control-Allow-Origin'
        }
        return ('', 204, headers)
    else:
        sentiment_data = []
        request_data = request.get_json()

        # app.logger.info("" + request_data)
        reviews = request_data['reviews']
        sentiment_data = get_sentiment(reviews)

        response = app.response_class(response=json.dumps(sentiment_data),
                                      status=200,
                                      mimetype='application/json')
        return response


@app.route('/ecomm/summary', methods=['POST'])
def get_summary():
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin':
            '*',
            'Access-Control-Allow-Methods':
            'POST',
            'Access-Control-Allow-Headers':
            'Content-Type, Authorization, Access-Control-Allow-Origin'
        }
        return ('', 204, headers)
    else:
        request_data = request.get_json()
        text = request_data['reviewsText']
        summary = generate_summary(text)
        response = app.response_class(response=json.dumps(summary),
                                      status=200,
                                      mimetype='application/json')
        return response


@app.route('/ecomm/trends', methods=['POST'])
def get_trends():
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin':
            '*',
            'Access-Control-Allow-Methods':
            'POST',
            'Access-Control-Allow-Headers':
            'Content-Type, Authorization, Access-Control-Allow-Origin'
        }
        return ('', 204, headers)
    else:
        try:
            request_data = request.get_json()
            keywords = request_data['keywords']
            trends1 = get_trends_by_region(keywords)
            trends2 = get_related_results(keywords)
            response = app.response_class(response=json.dumps({
                "trending_regions":
                trends1,
                "related_results":
                trends2
            }),
                                          status=200,
                                          mimetype='application/json')
            return response
        except Exception as e:
            response = app.response_class(response=json.dumps({
                "error": str(e),
                "status": 500
            }),
                                          status=500,
                                          mimetype='application/json')
            return response


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)