from flask.globals import request
from scraperlib.scraper import scrapData
from bs4 import BeautifulSoup
import requests
import urllib
import os
from flask import Flask, jsonify


app = Flask(__name__)


@app.route('/index')
def hello_world():
    query = request.args.get('m1')
    #query = input("Enter name of medicine : ")
    query = urllib.parse.quote(query, safe='')
    url = "https://www.1mg.com/search/all?filter=true&name=" + query

    header = {'Origin': 'https://www.1mg.com',
              'Referer': url,
              'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
              }

    html = requests.get(url=url, headers=header)
#    print("HTML Response code = ", html.status_code)
    soup = BeautifulSoup(html.text, 'lxml')

    finalProducts = scrapData(soup, header)
#    print("Total Products = ", len(finalProducts))

    return jsonify(finalProducts)


port = int(os.environ.get('PORT', 8080))
if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0', port=port)
