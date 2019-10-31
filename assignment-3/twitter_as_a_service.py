#!flask/bin/python
from flask import Flask
import twitter_filter
import json

app = Flask(__name__)

@app.route('/')
def greeting():
    return("Welcome to THE TWITTER FILTER!")

@app.route('/twitter')
def get_twitter_pronouns():
    result = twitter_filter.get_pronouns_json.delay()
    while(result.ready() == False): pass
    return result.get()

@app.route('/twitter/graph')
def get_twitter_graph():
    results = json.loads(get_twitter_pronouns())
    #return str(results)

    total = 0
    for p in results: total += results[p]
    for p in results: results[p] = int((100 * (float(results[p]) / float(total))))

    output = "<pre>"
    for p in results:
        output += "{:5}{:3}%: ".format(p, results[p])
        i = 0
        while i < results[p]:
            output += "#"
            i += 1
        output += "<br>"
    output += "</pre>"
    return output

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
