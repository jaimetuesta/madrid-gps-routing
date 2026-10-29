"""
pesos.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP11B
Integrantes:
    - Jaime Tuesta de Simón
    - Ignacio Mascarell Agúndez

Descripción:
Librería adicional que contiene las tres funciones que pueden actuar como peso (por longitud, tiempo y tiempo teniendo en cuenta semáforos).
"""

import networkx as nx
from typing import Union
import re

MAX_SPEEDS = {'living_street': '20',
 'residential': '30',
 'primary_link': '40',
 'unclassified': '40',
 'secondary_link': '40',
 'trunk_link': '40',
 'secondary': '50',
 'tertiary': '50',
 'primary': '50',
 'trunk': '50',
 'tertiary_link':'50',
 'busway': '50',
 'motorway_link': '70',
 'motorway': '100'}

DEFAULT_SPEED = 30   # km/h, velocidad usada si la arista no tiene un maxspeed legible ni un tipo de vía conocido

def length_weight(G: Union[nx.Graph, nx.DiGraph], u: object, v: object) -> float:
    return float(G[u][v]['length'])
    
def time_weight(G: Union[nx.Graph, nx.DiGraph], u: object, v: object) -> float:
    length_m = float(G[u][v]['length'])
    try:
        maxspeed_km_h_raw = G[u][v]['maxspeed']
        maxspeed_km_h = parse_maxspeed(maxspeed_km_h_raw)
    except (KeyError, IndexError):   # sin maxspeed, o maxspeed sin número (p. ej. 'none')
        maxspeed_km_h = float(DEFAULT_SPEED)
        for way in MAX_SPEEDS.keys():
            if G[u][v].get('highway') == way:
                maxspeed_km_h = float(MAX_SPEEDS[way])
                break
            if type(G[u][v].get('highway')) is list:
                values = []
                for way in G[u][v]['highway']:
                    values.append(float(MAX_SPEEDS.get(way, DEFAULT_SPEED)))
                maxspeed_km_h = max(values)

    maxspeed_m_s = maxspeed_km_h * (1000/3600)    
    time_s = length_m / maxspeed_m_s
    return time_s

def stoplights_weight(G: Union[nx.Graph, nx.DiGraph], u: object, v: object) -> float:
    # si un nodo tiene 2 o menos aristas (ya sea que entran o que salgan), no es una intersección
    if G.in_degree(v) + G.out_degree(v) > 2:
        p = 0.8
    else:
        p = 0

    return time_weight(G, u, v) + (p * 30)

def parse_maxspeed(speed):
    if type(speed) is list:
        values = []
        for v in speed:
            v = v.strip().lower()
            regex = r'\d+'   # una secuencia de dígitos
            num = re.findall(regex, v)
            value = int(num[0])
            values.append(value)
        return float(max(values))   # si la calle tiene varias velocidades, se asume que se rige por la menos restrictiva
    else:
        speed = speed.strip().lower()
        regex = r'\d+' 
        num = re.findall(regex, speed)
        value = int(num[0])
    return float(value)
        

