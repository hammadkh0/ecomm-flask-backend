import asyncio
from flask import Flask, request, json, Response, stream_with_context
from flask_cors import CORS
from flask_caching import Cache
from configs import make_search_asin_cache_key

from sentiment import get_sentiment

from send_requests import best_seller_request, product_list_request, specific_product_request, product_reviews_request

from scrape import find_suppliers_list, find_suppliers_details, find_supplier_prodcut_details
from summarize import generate_summary
from trends import get_related_results, get_trends_by_region

import math
import json

# create the Flask app
app = Flask(__name__)
CORS(app)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})


def replace_nan_with_null(obj):
    if isinstance(obj, float) and math.isnan(obj):
        return "-"
    elif isinstance(obj, dict):
        return {k: replace_nan_with_null(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan_with_null(v) for v in obj]
    else:
        return obj


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
    cached_response = cache.get(asin)
    if cached_response:
        return cached_response

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
            response = app.response_class(response=json.dumps(reviews),
                                          status=200,
                                          mimetype='application/json')

            cache.set(asin, response, timeout=60)
            return response
        except Exception as e:
            cache.delete(asin)
            response = app.response_class(response=json.dumps({
                "ERROR": str(e),
                "status": 500
            }),
                status=500,
                mimetype='application/json')
            return response


@app.route('/ecomm/products/search/<asin>', methods=['POST'])
@cache.cached(key_prefix='search_product',
              make_cache_key=make_search_asin_cache_key)
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
        url = url + asin
        try:
            details = specific_product_request(url, asin)
            # no product found for the asin
            if details["status"] == 404:
                # throw error
                raise Exception(details)

            # normal response
            return app.response_class(response=json.dumps(details),
                                      status=200,
                                      mimetype='application/json')
        except Exception as e:
            # delete the request from cache because no data was found
            cache_key = make_search_asin_cache_key(asin=asin)
            cache.delete(cache_key)
            # send error as response
            error = e.args[0]
            response = app.response_class(response=json.dumps({"e": str(e)}),
                                          status=error.get('status') or 500,
                                          mimetype='application/json')
            return response


@app.route('/ecomm/products/best-sellers', methods=['GET', 'OPTIONS'])
def get_best_sellers():
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
            data = best_seller_request()

            return app.response_class(response=json.dumps(data),
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
        # Retrieve the reviews from the request
        reviews = request.get_json().get('reviews')
        batch_size = 1

        # Define a generator function to yield batches of results
        def generate():
            # Iterate over the reviews in batches
            for i in range(0, len(reviews), batch_size):
                # Extract the current batch of reviews
                batch = reviews[i:i + batch_size]

                # Perform sentiment analysis on the batch of reviews
                results = get_sentiment(batch)

                # Yield the results as a JSON response
                yield json.dumps({'results': results, 'analyzed': (i+batch_size), 'total_reviews': len(reviews)}) + '\n'

        # Return the generator function wrapped in Flask's stream_with_context function
        return Response(stream_with_context(generate()), content_type='application/json')


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
            response = app.response_class(response=json.dumps(
                replace_nan_with_null({
                    "trending_regions": trends1,
                    "related_results": trends2
                }),
                sort_keys=False),
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


@app.route('/about')
def about():
    return 'About'


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)
