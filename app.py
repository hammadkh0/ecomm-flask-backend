from flask import Flask, request, json
from logging.config import dictConfig
from flask_cors import CORS
from sentiment import polarity_scores_roberta

# create the Flask app
app = Flask(__name__)
CORS(app)


@app.route('/sentiment', methods=['POST'])
def analyze_sentiment():
    sentiment_data = []
    request_data = request.get_json(force=True)
    # app.logger.info("" + request_data)
    reviews = request_data['reviews']

    for review in reviews:
        roberta_result = polarity_scores_roberta(review)
        if (roberta_result['roberta_neg'] > roberta_result['roberta_pos']):
            sentiment_data.append({"review": review, "result": roberta_result})

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