from flask import Flask, render_template
from pymongo import MongoClient

app = Flask(__name__)


cluster = MongoClient("""Mongo Cluster""")
db = cluster["IP_activity"]
collection = db["IP_activity"]


@app.route("/")
def home():
    return render_template('home.html')


@app.route("/network_activity")
def network_activity():
    return render_template('my_network_activity.html', collection=collection.find({}, {'_id': False}))


@app.route("/has_seen_list")
def all_seen():
    return render_template('has_seen_list.html', collection=collection.find({"first_seen": {"$ne": None}}, {'_id': False}))


if __name__ == '__main__':
    app.run(debug=True)