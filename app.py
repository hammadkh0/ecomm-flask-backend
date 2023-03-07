from flask import Flask, request, json
from flask_cors import CORS
from sentiment import get_sentiments
from send_requests import product_list_request, specific_product_request
from scrape import find_suppliers_list

# create the Flask app
app = Flask(__name__)
CORS(app)


@app.route('/ecomm/products', methods=['POST'])
def get_products():
    request_data = request.get_json()
    url = request_data['url']
    input_term = request_data['input_term']
    products_data = {}
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


@app.route('/ecomm/products/<asin>', methods=['POST'])
def get_single_product(asin):
    request_data = request.get_json()
    url = request_data['link']
    asin = request_data['asin']

    try:
        specific_product_request()
    except Exception as e:
        print(e)
        pass

    return '''
        The product is {}.
    '''.format(asin)


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