import random
from flask import Flask, request, json
from logging.config import dictConfig
from flask_cors import CORS
from sentiment import polarity_scores_roberta
from rotate_ip import send_request, AGENT_LIST

# create the Flask app
app = Flask(__name__)
CORS(app)


@app.route('/find-products', methods=['POST'])
def get_products():
    request_data = request.get_json()
    url = request_data['url']
    input_term = request_data['input_term']
    products_list = []
    try:
        products_list = send_request(url,
                                     {"User-Agent": random.choice(AGENT_LIST)},
                                     input_term)
    except Exception as e:
        print(e)
        pass

    response = app.response_class(response=json.dumps(products_list),
                                  status=200,
                                  mimetype='application/json')
    return response


@app.route('/sentiment', methods=['POST'])
def analyze_sentiment():
    sentiment_data = []
    request_data = request.get_json()

    # app.logger.info("" + request_data)
    reviews = request_data['reviews']

    for review in reviews:
        roberta_result = polarity_scores_roberta(review["body"])
        if (roberta_result['roberta_neg'] > roberta_result['roberta_pos']):
            sentiment_data.append({"id": review["id"], "body": review["body"]})

    response = app.response_class(response=json.dumps(sentiment_data),
                                  status=200,
                                  mimetype='application/json')
    return response

    # return '''
    # Length: {}
    #     The sentiment of the reviews are {}.
    # '''.format(len(sentiment_data), sentiment_data)


@app.route("/ml", methods=['POST'])
def ml():
    attri = request.get_json()

    print(attri)

    return 'DONE', 201


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, port=5000)