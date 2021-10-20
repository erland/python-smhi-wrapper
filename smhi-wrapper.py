from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from dateutil import tz
from json import dumps
import requests
from datetime import datetime

app = Flask(__name__)
api = Api(app)

@app.get("/now")
def get_now():
    api_url = "http://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/22.030160/lat/65.646230/data.json"
    response = requests.get(api_url)
    timeSeries = response.json()["timeSeries"]
    return extractSeries(timeSeries, 0, 1)

@app.route("/next/<hours>")
def get_next(hours):
    api_url = "http://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/22.030160/lat/65.646230/data.json"
    response = requests.get(api_url)
    timeSeries = response.json()["timeSeries"]
    return extractSeries(timeSeries, 0, int(hours))

@app.route("/days/<day>")
def get_day(day):
    api_url = "http://opendata-download-metfcst.smhi.se/api/category/pmp3g/version/2/geotype/point/lon/22.030160/lat/65.646230/data.json"
    response = requests.get(api_url)
    timeSeries = response.json()["timeSeries"]
    return extractDaySeries(timeSeries, int(day))

def extractSeries(timeSeries, seriePosition, serieNumber):
    temperature = None
    temperatureMin = None
    temperatureMax = None
    symbol = None
    wind = None
    windMin = None
    windMax = None
    precipitation = None
    if len(timeSeries)>seriePosition:
        for pos in range(seriePosition, seriePosition+serieNumber):
            for parameters in timeSeries[pos]["parameters"]:
                if parameters["name"] == "t":
                    if temperature is None:
                        temperature = 0.0
                    temperature = temperature + parameters["values"][0]
                    if temperatureMin is None or temperatureMin>parameters["values"][0]:
                        temperatureMin = parameters["values"][0]
                    if temperatureMax is None or temperatureMax<parameters["values"][0]:
                        temperatureMax = parameters["values"][0]
                elif parameters["name"] == "ws":
                    if wind is None:
                        wind = 0.0
                    wind = wind + parameters["values"][0]
                    if windMin is None or windMin>parameters["values"][0]:
                        windMin = parameters["values"][0]
                elif parameters["name"] == "gust":
                    if windMax is None or windMax < parameters["values"][0]:
                        windMax = parameters["values"][0]
                elif parameters["name"] == "Wsymb2":
                    if serieNumber == 1:
                        symbol = translateSymbol(parameters["values"][0])
                elif parameters["name"] == "pmean":
                    if precipitation is None:
                        precipitation = 0.0
                    precipitation = precipitation + parameters["values"][0]

        if temperature is not None:
            temperature = round(temperature / serieNumber, 1)
        
        if wind is not None:
            wind = round(wind / serieNumber,1)

        if precipitation is not None:
            precipitation = round(precipitation, 1)

        if temperature is not None:
            result = {
                "time": timeSeries[seriePosition]["validTime"],
                "windAvg": wind,
                "windMin": windMin,
                "windMax": windMax,
                "tempAvg": temperature,
                "tempMin": temperatureMin,
                "tempMax": temperatureMax,
                "precipitationTotal": precipitation,
            }
            if symbol is not None:
                result["symbol"] = symbol
            return jsonify(result)
        else:
            return jsonify("{error: 2}")
    else:
        return jsonify("{error: 1}")

def extractDaySeries(timeSeries, day):
    temperature = None
    temperatureMin = None
    temperatureMax = None
    symbol = None
    wind = None
    windMin = None
    windMax = None
    precipitation = None

    initialTime = timeFromString(timeSeries[0]["validTime"])
    usedTime = None
    series = 0    
    for serie in timeSeries:
        time = timeFromString(serie["validTime"])
        if time.timetuple().tm_yday - initialTime.timetuple().tm_yday == day:
            if usedTime is None:
                usedTime = time
            
            series += 1
            for parameters in serie["parameters"]:
                if parameters["name"] == "t":
                    if temperature is None:
                        temperature = 0.0
                    temperature = temperature + parameters["values"][0]
                    if temperatureMin is None or temperatureMin>parameters["values"][0]:
                        temperatureMin = parameters["values"][0]
                    if temperatureMax is None or temperatureMax<parameters["values"][0]:
                        temperatureMax = parameters["values"][0]
                elif parameters["name"] == "ws":
                    if wind is None:
                        wind = 0.0
                    wind = wind + parameters["values"][0]
                    if windMin is None or windMin>parameters["values"][0]:
                        windMin = parameters["values"][0]
                elif parameters["name"] == "gust":
                    if windMax is None or windMax < parameters["values"][0]:
                        windMax = parameters["values"][0]
                elif parameters["name"] == "pmean":
                    if precipitation is None:
                        precipitation = 0.0
                    precipitation = precipitation + parameters["values"][0]

    if temperature is not None:
        temperature = round(temperature / series, 1)
        
    if wind is not None:
        wind = round(wind / series,1)

    if precipitation is not None:
        precipitation = round(precipitation, 1)

    if temperature is not None:
        result = {
            "time": usedTime.strftime("%Y-%m-%d"),
            "windAvg": wind,
            "windMin": windMin,
            "windMax": windMax,
            "tempAvg": temperature,
            "tempMin": temperatureMin,
            "tempMax": temperatureMax,
            "precipitationTotal": precipitation,
        }
        return jsonify(result)
    else:
        return jsonify("{error: 2}")

def timeFromString(timeString):
    time = datetime.strptime(timeString, '%Y-%m-%dT%H:%M:%SZ')
    return time.replace(tzinfo=tz.tzutc()).astimezone(tz.gettz('Europe/Stockholm'))


def translateSymbol(symbol):
    if symbol == 1:
        return "Klart"
    elif symbol == 2:	
        return "Lätt molninghet"
    elif symbol == 3:	
        return "Halvklart"
    elif symbol == 4:
        return "Molnigt"
    elif symbol == 5:	
        return "Mycket moln"
    elif symbol == 6:	
        return "Mulet"
    elif symbol == 7:	
        return "Dimma"
    elif symbol == 8:	
        return "Lätt regnskur"
    elif symbol == 9:
        return "Regnskur"
    elif symbol == 10:	
        return "Kraftig regnskur"
    elif symbol == 11:	
        return "Åskskur"
    elif symbol == 12:	
        return "Lätt by av regn och snö"
    elif symbol == 13:	
        return "By av regn och snö"
    elif symbol == 14:	
        return "Kraftig by av regn och snö"
    elif symbol == 15:	
        return "Lätt snöby"
    elif symbol == 16:	
        return "Snöby"
    elif symbol == 17:	
        return "Kraftig snöby"
    elif symbol == 18:
        return "Lätt regn"
    elif symbol == 19:	
        return "Regn"
    elif symbol == 20:	
        return "Kraftigt regn"
    elif symbol == 21:
        return "Åska"
    elif symbol == 22:	
        return "Lätt snöblandat regn"
    elif symbol == 23:	
        return "Snöblandat regn"
    elif symbol == 24:
        return "Kraftigt snöblandat regn"
    elif symbol == 25:	
        return "Lätt snöfall"
    elif symbol == 26:	
        return "Snöfall"
    elif symbol == 27:	
        return "Ymnigt snöfall"
    else:
        return ""

if __name__ == '__main__':
     app.run(host="0.0.0.0")
