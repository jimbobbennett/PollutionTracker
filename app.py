import os, json
from flask import Flask, render_template, request, redirect, url_for
import requests

MAP_KEY = os.environ["MAP_KEY"]
POLLUTION_API_KEY = os.environ["POLLUTION_API_KEY"]
POLLUTION_API_URL = "https://api.waqi.info/map/bounds/?latlng={lat1},{lon1},{lat2},{lon2}&token={token}"

app = Flask(__name__)

def build_page_data():
    return { "map_key" : MAP_KEY }

def get_color(aqi):
    if aqi <= 50:
        return "#009966"
    if aqi <= 100:
        return "#ffde33"
    if aqi <= 150:
        return "#ff9933"
    if aqi <= 200:
        return "#cc0033"
    if aqi <= 300:
        return "#660099"

    return "#7e0023"

def load_pollution_data(lat1, lon1, lat2, lon2):
    url = POLLUTION_API_URL.format(lat1 = lat1, lon1 = lon1, lat2 = lat2, lon2 = lon2, token=POLLUTION_API_KEY)
    print(url)
    pollution_data = requests.get(url)

    # create feature collection
    feature_collection = {
        "type" : "FeatureCollection",
        "features" : []
    }

    for value in pollution_data.json()["data"]:
        try:
            aqi = int(value["aqi"])
            feature_collection["features"].append({
                "type" : "Feature",
                "properties" : {
                    "Name" : value["station"]["name"],
                    "aqi" : value["aqi"],
                    "color" : get_color(aqi)
                },
                "geometry" : {
                    "type":"Point",
                    "coordinates":[value['lon'], value['lat']]
                }
             })
        except ValueError:
            pass

    print(feature_collection)

    return feature_collection

@app.route("/")
def home():
    data = build_page_data()
    return render_template("home.html", data = data)

@app.route("/get-pollution", methods = ["GET"])
def get_pollution():
    bounds_str = request.args["bounds"]
    bounds = bounds_str.split(",")
    lon1 = bounds[0]
    lat1 = bounds[1]
    lon2 = bounds[2]
    lat2 = bounds[3]

    return json.dumps(load_pollution_data(lat1, lon1, lat2, lon2))