from celery import Celery
from collections import Counter
import os
import json

tweet_folder_path = os.path.join(os.getcwd(), "tweets")
retweet_key = "retweeted_status"
pronouns = ["han", "hon", "den", "det", "denna", "denne", "hen"]

# msg broker: RabbitMQ
# backend:    RPC
app = Celery('twitter_filter', backend='rpc://', broker='pyamqp://')

@app.task
def hello_world():
    return "Hello, World!"

@app.task
def get_folder_path():
    return tweet_folder_path

@app.task
def get_files_in_folder(folder):
    return [os.path.join(folder, f) for f in os.listdir(folder)]

def is_retweet(tweet):
    return (retweet_key in tweet)

def count_pronouns(tweet, counter):
    if "text" not in tweet:
        print("!! NO TEXT IN TWEET !!")
        return
    text = tweet["text"]
    counter.update(text.lower().split())
    return counter

@app.task
def twitter_count_file(file_name):
    counter = Counter(pronouns)
    with open(file_name) as tweets:
        for line in tweets:
            if line == "\n": continue
            tweet = json.loads(line)
            if is_retweet(tweet): continue
            counter = count_pronouns(tweet, counter)
    return counter

@app.task
def twitter_count_folder(folder):
    files = get_files_in_folder(folder)
    results = Counter()
    for f in files:
        results.update(twitter_count_file(f))
    return results

@app.task
def twitter_pronouns_json():
    words = twitter_count_folder(get_folder_path())
    prons = dict()
    for p in pronouns:
        prons[p] = words[p]
    with open("out.json", "w") as out: out.write(json.dumps(prons))
    return json.dumps(prons)

@app.task
def get_pronouns_json():
    out_path = os.path.join(os.getcwd(), "out.json")
    result = ""
    if os.path.isfile(out_path):
        with open(out_path, "r") as out:
            result = out.read()
    else:
        result = twitter_pronouns_json()
    return result
                    

if __name__ == "__main__":
    results = twitter_count_folder(get_folder_path())
    with open("out.json", "w") as out:
        res = dict()
        for p in pronouns:
            res[p] = results[p]
        res = json.dumps(res)
        out.write(res)
