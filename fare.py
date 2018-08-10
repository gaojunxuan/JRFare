import networkx as nx
import csv
import sqlite3

yamanoteStations=["東京","神田","秋葉原","御徒町","上野","鶯谷","日暮里","西日暮里","田端","駒込","巣鴨","大塚","池袋","目白","高田馬場","新大久保","新宿","代々木","原宿","渋谷","恵比寿","目黒","五反田","大崎","品川","田町","浜松町","新橋","有楽町",]
db=sqlite3.connect("fare.sqlite")
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

f=input("from: ")
t=input("to: ")
print(getNormalFare(f,t))
print(getICFare(f,t))
