from flask import Flask, render_template, jsonify, send_file
from pymongo import MongoClient
import csv
from io import BytesIO, StringIO
from dotenv import load_dotenv
import json
# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# MongoDB setup
mongodb_uri = "mongodb+srv://iitjammu7:W95nUBv78dUKI6si@cluster1.0pamvyh.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongodb_uri)
db = client["bluetooth"]

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_collections')
def get_collections():
    collections = db.list_collection_names()
    return jsonify(collections)

@app.route('/get_data/<collection_name>')
def get_data(collection_name):
    collection = db[collection_name]
    data = list(collection.find({}, {"_id": 0}))
    return jsonify(data)

@app.route('/download_csv/<collection_name>')
def download_csv(collection_name):
    collection = db[collection_name]
    data = list(collection.find({}, {"_id": 0}))

    # Convert data to CSV format using StringIO
    csv_data = StringIO()
    csv_writer = csv.DictWriter(csv_data, fieldnames=data[0].keys())
    csv_writer.writeheader()
    csv_writer.writerows(data)

    # Create a response with CSV content
    response = send_file(
        BytesIO(csv_data.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{collection_name}.csv'
    )

    return response

@app.route('/download_json/<collection_name>')
def download_json(collection_name):
    collection = db[collection_name]
    data = list(collection.find({}, {"_id": 0}))

    # Create a response with JSON content
    response = send_file(
        BytesIO(json.dumps(data, indent=2).encode('utf-8')),
        mimetype='application/json',
        as_attachment=True,
        download_name=f'{collection_name}.json'
    )

    return response

if __name__ == "__main__":
    app.run(debug=True)
