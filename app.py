from flask import Flask, request, json
from flask_cors import CORS
from sentiment import get_sentiments
from send_requests import product_list_request, specific_product_request, product_reviews_request
from scrape import find_suppliers_list, find_suppliers_details

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


@app.route('/ecomm/sentiment', methods=['POST'])
def analyze_sentiment():
    sentiment_data = []
    request_data = request.get_json()

    # app.logger.info("" + request_data)
    reviews = request_data['reviews']
    sentiment_data = get_sentiments(reviews)
    # for review in reviews:
    #     roberta_result = polarity_scores_roberta(review["body"])
    #     if (roberta_result['roberta_neg'] > roberta_result['roberta_pos']):
    #         sentiment_data.append({"id": review["id"], "body": review["body"]})

    response = app.response_class(response=json.dumps(sentiment_data),
                                  status=200,
                                  mimetype='application/json')
    return response

    # return '''
    # Length: {}
    #     The sentiment of the reviews are {}.
    # '''.format(len(sentiment_data), sentiment_data)


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)