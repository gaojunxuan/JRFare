import networkx as nx
import csv
import sqlite3
import math
from flask import Flask,request,jsonify
app = Flask(__name__)

yamanoteStations=["東京","神田","秋葉原","御徒町","上野","鶯谷","日暮里","西日暮里","田端","駒込","巣鴨","大塚","池袋","目白","高田馬場","新大久保","新宿","代々木","原宿","渋谷","恵比寿","目黒","五反田","大崎","品川","田町","浜松町","新橋","有楽町",]
db=sqlite3.connect("fare.sqlite",check_same_thread=False)
cursor=db.cursor()
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

@app.route('/jr', methods=['GET'])
def getAll():
    f = request.args.get('from')
    t = request.args.get('to')
    if f is not None and t is not None:
        try:
            result={
            'ticketFare':getNormalFare(f,t),
            'icCardFare':getICFare(f,t),
            'childTicketFare':math.floor(getNormalFare(f,t)/2),
            'childIcFare':math.floor(getICFare(f,t)/2)
            }
            return jsonify(result)
        except nx.exception.NetworkXNoPath:
            return "Error: node is not reachable"
        
    else:
        return "Please pass the required parameters on the query string or in the request body."

if __name__ == '__main__':
  app.run()
