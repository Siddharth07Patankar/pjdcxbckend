from flask import Flask,jsonify,request
from flask_cors import CORS
import requests # Install requests module first.
import pandas as pd
from datetime import date
from google.cloud import storage

app = Flask(__name__)
CORS(app, origins='*',methods=["GET", "POST", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
url = "https://api.coindcx.com/exchange/v1/markets_details"

bucket_name = "your_bucket_name"
# File name in the bucket to read
file_name = "config.csv"

@app.route('/api/get_csv_data', methods=['GET', 'OPTIONS'])
def get_csv_data():
    try:
        # Initialize a client using Application Default Credentials
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(bucket_name)
        blb = bucket.blob(file_name)
        # Download the file to a temporary location
        blb.download_to_filename("/tmp/config.csv")
        # Read the CSV file
        data = pd.read_csv("/tmp/config.csv")
        # Convert DataFrame to JSON and return
        return data.to_json(orient="records")
    except Exception as e:
        return jsonify({"statusCode": 500, "body": str(e)})

@app.route('/api/get_coins',methods=['GET', 'OPTIONS'])
def get_coin_names():
    if request.method=='OPTIONS':
        return jsonify({})
    if request.method=='GET':
        try:
            response = requests.get(url)
            coin_names = response.json()
            coin_names = {inx+1:item['target_currency_short_name'] for inx,item in enumerate(coin_names) if item['base_currency_short_name']=='INR'}
            # response = requests.get(f"{API_BASE_URL}/exchange/ticker")
            # if response.status_code == 200:
            #coin_names = ["PAIR","BONK","SOL","ETH","DOGE","BOME","MATIC","ENA","ONDO","W","ARB","WIF","BRISE","CREAM","CKB","TFUEL","FTM","BTC","SAGA","XVG","XRP","MATIC","ICP","ARKM","TOKEN","FLOKI","OM","FLM"]
            return jsonify({"statusCode":200,"body":coin_names})
            # else:
            #     return jsonify({"statusCode":500,"body":"Failed to fetch data from CoinDCX API"})
        except Exception as e:
            return jsonify({"statusCode":500,"body":str(e)})

@app.route('/api/save_csv',methods=['POST', 'OPTIONS'])
def save_csv():
    try:
        if request.method=='OPTIONS':
            return jsonify({})
        if request.method=='POST':
            event = request.get_json()
            data = [{"PAIR":coin['Coin'],"AMOUNT":coin['Amount'],"MARGIN":coin['Target'],"BUY_LOOP":1,"SELL_LOOP":1} for coin in event['coin_info']]
            data = pd.DataFrame(data)
            data.to_csv(f"../../../best_bid/config.csv",index=False)
            return jsonify({"statusCode":200,"body":"csv saved successfully"})
    except Exception as e:
        return jsonify({"statusCode":500,"body":str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 8080, debug=True)

