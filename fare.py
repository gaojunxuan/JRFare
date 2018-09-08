import networkx as nx
import csv
import sqlite3
import math
from flask import Flask,request,jsonify
app = Flask(__name__)

yamanoteStations=["東京","神田","秋葉原","御徒町","上野","鶯谷","日暮里","西日暮里","田端","駒込","巣鴨","大塚","池袋","目白","高田馬場","新大久保","新宿","代々木","原宿","渋谷","恵比寿","目黒","五反田","大崎","品川","田町","浜松町","新橋","有楽町",]
tsukubaDistance={
    "秋葉原": 0,
    "新御徒町": 1,
    "浅草": 3,
    "南千住": 5.7,
    "北千住": 8,
    "青井": 10.6,
    "六町": 12,
    "八潮": 15.7,
    "三郷中央": 19,
    "南流山": 22.1,
    "流山セントラルパーク": 24,
    "流山おおたかの森": 26.5,
    "柏の葉キャンパス": 30,
    "柏たなか": 32,
    "守谷": 38,
    "みらい平": 44.3,
    "みどりの": 48,
    "万博記念公園": 51.8,
    "研究学園": 55,
    "つくば": 58.3,
}
db=sqlite3.connect("fare.sqlite",check_same_thread=False)
station_db=sqlite3.connect("station.sqlite",check_same_thread=False)
tsukuba_db=sqlite3.connect("tsukubafare.sqlite",check_same_thread=False)
cursor=db.cursor()
station_cursor=station_db.cursor()
tsukuba_cursor=tsukuba_db.cursor()
G = nx.Graph()

with open("tokyo.csv",mode="r",encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    for row in reader:
        G.add_edge(row[0],row[1],weight=float(row[2]))


def isYamanoteStation(staName:str):
    return staName in yamanoteStations

def getDistance(src:str,dst:str):
    return nx.dijkstra_path_length(G,src,dst)

def getNormalFare(src:str,dst:str):
    distance=getDistance(src,dst)
    if isYamanoteStation(src) and isYamanoteStation(dst):
        cursor.execute("SELECT normalFare FROM fare WHERE minDistance<=? AND maxDistance>=? AND line='Yamanote'",(round(distance),round(distance)))
        return cursor.fetchone()[0]
    else:
        cursor.execute("SELECT normalFare FROM fare WHERE minDistance<=? AND maxDistance>=? AND line='TokuteiKukan'",(round(distance),round(distance)))
        return cursor.fetchone()[0]

def getICFare(src:str,dst:str):
    distance=getDistance(src,dst)
    if isYamanoteStation(src) and isYamanoteStation(dst):
        cursor.execute("SELECT icFare FROM fare WHERE minDistance<=? AND maxDistance>=? AND line='Yamanote'",(round(distance),round(distance)))
        return cursor.fetchone()[0]
    else:
        cursor.execute("SELECT icFare FROM fare WHERE minDistance<=? AND maxDistance>=? AND line='TokuteiKukan'",(round(distance),round(distance)))
        return cursor.fetchone()[0]

def getJapaneseStationName(en):
    station_cursor.execute("SELECT ja FROM stations WHERE name=?",(en,))
    result=station_cursor.fetchone()
    if result is not None:
        return result[0]

def getTsukubaDistance(src:str,dst:str):
    return math.ceil(math.fabs(tsukubaDistance[dst]-tsukubaDistance[src]))

def getTsukubaNormalFare(src:str,dst:str):
    distance=getTsukubaDistance(src,dst)
    tsukuba_cursor.execute("SELECT normalFare FROM tsukubafare WHERE minDistance<=? AND maxDistance>=? AND line='TsukubaExpress'",(distance,distance))
    return tsukuba_cursor.fetchone()[0]

def getTsukubaICFare(src:str,dst:str):
    distance=getTsukubaDistance(src,dst)
    tsukuba_cursor.execute("SELECT icFare FROM tsukubafare WHERE minDistance<=? AND maxDistance>=? AND line='TsukubaExpress'",(distance,distance))
    return tsukuba_cursor.fetchone()[0]

def getTsukubaChildFare(src:str,dst:str):
    distance=getTsukubaDistance(src,dst)
    tsukuba_cursor.execute("SELECT childFare FROM tsukubafare WHERE minDistance<=? AND maxDistance>=? AND line='TsukubaExpress'",(distance,distance))
    return tsukuba_cursor.fetchone()[0]

def getTsukubaChildIcFare(src:str,dst:str):
    distance=getTsukubaDistance(src,dst)
    tsukuba_cursor.execute("SELECT childIcFare FROM tsukubafare WHERE minDistance<=? AND maxDistance>=? AND line='TsukubaExpress'",(distance,distance))
    return tsukuba_cursor.fetchone()[0]

@app.route('/jr', methods=['GET'])
def getAll():
    f=request.args.get("from")
    t=request.args.get("to")
    if f is not None and t is not None:
        f=getJapaneseStationName(f)
        t=getJapaneseStationName(t)
        if f is None or t is None:
            return "Error: station not found"
        try:
            
            result={
            'ticketFare':getNormalFare(f,t),
            'icCardFare':getICFare(f,t),
            'childTicketFare':math.floor(getNormalFare(f,t)/2),
            'childIcCardFare':math.floor(getICFare(f,t)/2)
            }
            return jsonify(result)
        except nx.exception.NetworkXNoPath:
            return "Error: node is not reachable"
    else:
        return "Please pass the required parameters on the query string or in the request body."

@app.route('/tsukubaexpress', methods=['GET'])
def getTsukuba():
    f=request.args.get("from")
    t=request.args.get("to")
    if f is not None and t is not None:
        f=getJapaneseStationName(f)
        t=getJapaneseStationName(t)
        if f is None or t is None:
            return "Error: station not found"
        else:
            result={
            'ticketFare':getTsukubaNormalFare(f,t),
            'icCardFare':getTsukubaICFare(f,t),
            'childTicketFare':getTsukubaChildFare(f,t),
            'childIcCardFare':getTsukubaChildIcFare(f,t)
            }
            return jsonify(result)
    else:
        return "Please pass the required parameters on the query string or in the request body."

if __name__ == '__main__':
        app.run()