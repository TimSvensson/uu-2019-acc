#!flask/bin/python
from flask import Flask
from twitter_filter import get_pronouns_json as get_p_json

app = Flask(__name__)

@app.route('/twitter/json')
def get_twitter_pronouns():
    result = get_p_json.delay()
    while(result.ready() == False): pass
    return result.get()

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
