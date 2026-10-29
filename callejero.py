"""
callejero.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP11B
Integrantes:
    - Jaime Tuesta de Simón
    - Ignacio Mascarell Agúndez

Descripción:
Librería con herramientas y clases auxiliares necesarias para la representación de un callejero en un grafo.
"""

import osmnx as ox
import networkx as nx
import pandas as pd
import re
import os
import matplotlib.pyplot as plt
from typing import Tuple

STREET_FILE_NAME="direcciones.csv"

PLACE_NAME = "Madrid, Spain"
MAP_FILE_NAME="madrid.graphml"

MAX_SPEEDS={'living_street': '20',
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


class ServiceNotAvailableError(Exception):
    "Excepción que indica que la navegación no está disponible en este momento"
    pass


class AddressNotFoundError(Exception):
    "Excepción que indica que una dirección buscada no existe en la base de datos"
    pass

class FormatNotValidError(Exception):
    "Excepción que indica que la dirección no se ha metido con el formato adecuado, y se debe volver a meter"
    pass

############## Parte 2 ##############


def carga_callejero() -> pd.DataFrame:

    """
    Función que carga el callejero de Madrid, lo procesa y devuelve
    un DataFrame con los datos procesados
    
    Args: None

    Returns:
        DataFrame: dataframe con los datos del callejero procesados.
    
    Raises:
        FileNotFoundError si el fichero csv con las direcciones no existe
    """

    try:
        callejero = pd.read_csv(rf'{STREET_FILE_NAME}', encoding='latin1', usecols=['VIA_CLASE', 'VIA_PAR', 'VIA_NOMBRE', 'NUMERO', 'LATITUD', 'LONGITUD'], sep=';')

        #eliminate nan values
        callejero = callejero.fillna('X')

        #transform values to float
        callejero['LATITUD'] = callejero['LATITUD'].apply(transform_to_degrees)
        callejero['LONGITUD'] = callejero['LONGITUD'].apply(transform_to_degrees)

        #return
        return callejero
    
    except FileNotFoundError as error:
        print('Error - ', error)

def transform_to_degrees(coord_text: str) -> float:

    #usar regex para identificar cada término de la coordenada
    patron_regex = re.compile(r"(\d+)[°](\d+)'(\d+\.?\d*)''\s([NSEW])")
    m = patron_regex.match(coord_text)
    if m is not None:
        grados, minutos, segundos, orientacion = int(m.group(1)), int(m.group(2)), float(m.group(3)), m.group(4)

        #formula para transformar a grados
        valor_decimal = grados + (minutos/60) + (segundos/3600)

        #returns -> actualizar a negativo si la orientación es W/S
        if orientacion == 'W' or orientacion == 'S':
            valor_decimal *= -1
        return valor_decimal
    return coord_text
    

def busca_direccion(direccion: str, callejero: pd.DataFrame) -> Tuple[float, float]:

    """ 
    Función que busca una dirección, dada en el formato calle, numero
    en el DataFrame callejero de Madrid y devuelve el par (latitud, longitud) en grados de la
    hubicación geográfica de dicha dirección
    
    Args:
        direccion (str): Nombre completo de la calle con número, en formato "Calle, num"
        callejero (DataFrame): DataFrame con la información de las calles
    
    Returns:
        Tuple[float,float]: Par de float (latitud,longitud) de la dirección buscada, expresados en grados
    
    Raises:
        AdressNotFoundError: Si la dirección no existe en la base de datos
    
    Example:
        busca_direccion("Calle de Alberto Aguilera, 23", data)=(40.42998055555555,-3.7112583333333333)
        busca_direccion("Calle de Alberto Aguilera, 25", data)=(40.43013055555555,-3.7126916666666667)
    """
    # Para que sea accesible al usuario, hemos hecho dos modos: con dirección completa (Calle de Alberto Aguilera, 23) 
    # y simplificado (Alberto Aguilera, 23)

    dir = direccion.strip().upper()

    pattern1 = re.compile(r'([\w]+)( DE LOS| DE LAS| DE LA| DEL| DE| A LA| AL)? (.+), ([\d]+)')
    pattern2 = re.compile(r"(.+), ([\d]+)")
    m1 = pattern1.match(dir)
    m2 = pattern2.match(dir)

    # Por si una dirección sin vía hace match con m1
    tipos_via = ['ACCESO', 'AUTOPISTA', 'AUTOVÍA', 'AVENIDA', 'BULEVAR', 'CALLE', 'CALLEJÓN', 'CAMINO', 'CARRERA', 'CARRETERA', 
                 'COSTANILLA', 'CUESTA', 'ESCALINATA', 'GALERÍA', 'GLORIETA', 'PARTICULAR', 'PASADIZO', 'PASAJE', 'PASEO', 
                 'PISTA', 'PLAZA', 'PLAZUELA', 'PUENTE', 'RONDA', 'TRAVESÍA']

    if m1 is not None and m1.group(1) not in tipos_via:
        m1 = None

    if m1 is not None:
        clase = m1.group(1).strip()
        if m1.group(2) is not None:   # puede no haber partícula
            part = m1.group(2).strip()
        else: 
            part = 'X'
        nombre = m1.group(3).strip()
        num = int(m1.group(4).strip())

        matches = callejero[(callejero['VIA_CLASE'] == clase) & (callejero['VIA_PAR'] == part) & (callejero['VIA_NOMBRE'] == nombre) & (callejero['NUMERO'] == num)]
        try:
            if matches.shape[0] > 1:
                print('Se puede estar refiriendo a varias ubicaciones. Elija entre:')
                for i in range(matches.shape[0]):
                    print(f'{i+1}. {matches.iloc[i, 0]} {matches.iloc[i, 1]} {matches.iloc[i, 2]}, {matches.iloc[i, 3]}')
                valid = False
                while not valid:
                    try:
                        choice = int(input('Elija una de las opciones (escriba el número): '))
                        if choice < 1 or choice > matches.shape[0]:
                            print(f'El número debe estar entre 1 y {matches.shape[0]}')
                        else:
                            n = choice - 1
                            valid = True
                    except:
                        print('La elección no es válida, escriba un número.')
            else:
                n = 0
            return matches.iloc[n, 4], matches.iloc[n, 5]
        except IndexError:
            # FUZZY SEARCH: Si la dirección no está en el callejero, imprime las tres direcciones que más se le parezcan
            # Si no hay niinguna que se le parezca, funciona de manera normal
            dirs = mejores_direcciones_fuzzy(callejero, dir, 'completo')
            if len(dirs) != 0:
                if dirs[0][1] == 0.0:
                    return dirs[0][2]
                print('La dirección no se encuentra en la base de datos. ¿Quiere decir...?')
                for i in range(len(dirs)):
                    print(f'{i+1}. {dirs[i][0]}')
                valid = False
                while not valid:
                    try:
                        choice = int(input('Elija la opción que desee (o 0 si ninguna): '))
                        if choice < 0 or choice > len(dirs):
                            print(f'El número debe estar entre 0 y {len(dirs)}')
                        elif choice == 0:
                            raise AddressNotFoundError('Vuelva a escribir la dirección.\n')
                        else:
                            n = choice - 1
                            valid = True
                    except ValueError:
                        print('La elección no es válida, escriba un número.')
                return dirs[n][2]
            raise AddressNotFoundError('La dirección no se encuentra en la base de datos.')
        
    elif m2 is not None:
        nombre = m2.group(1).strip()
        num = int(m2.group(2).strip())

        matches = callejero[(callejero['VIA_NOMBRE'] == nombre) & (callejero['NUMERO'] == num)]
        try:
            if matches.shape[0] > 1:
                print('Se puede estar refiriendo a varias ubicaciones. Elija entre:')
                for i in range(matches.shape[0]):
                    print(f'{i+1}. {matches.iloc[i, 0]} {matches.iloc[i, 1]} {matches.iloc[i, 2]}, {matches.iloc[i, 3]}')
                valid = False
                while not valid:
                    try:
                        choice = int(input('Elija una de las opciones (escriba el número): '))
                        if choice < 1 or choice > matches.shape[0]:
                            print(f'El número debe estar entre 1 y {matches.shape[0]}')
                        else:
                            n = choice - 1
                            valid = True
                    except:
                        print('La elección no es válida, escriba un número.')
            else:
                n = 0
            return matches.iloc[n, 4], matches.iloc[n, 5]
        except IndexError:
            dirs = mejores_direcciones_fuzzy(callejero, dir, 'simplificado')
            if len(dirs) != 0:
                if dirs[0][1] == 0.0:
                    return dirs[0][2]
                print('La dirección no se encuentra en la base de datos. ¿Quiere decir...?')
                for i in range(len(dirs)):
                    print(f'{i+1}. {dirs[i][0]}')
                valid = False
                while not valid:
                    try:
                        choice = int(input('Elija la opción que desee (o 0 si ninguna): '))
                        if choice < 0 or choice > len(dirs):
                            print(f'El número debe estar entre 0 y {len(dirs)}')
                        elif choice == 0:
                            raise AddressNotFoundError('Vuelva a escribir la dirección.\n')
                        else:
                            n = choice - 1
                            valid = True
                    except ValueError:
                        print('La elección no es válida, escriba un número.')
                return dirs[n][2]
            raise AddressNotFoundError('La dirección no se encuentra en la base de datos.')
        
    else:
        raise FormatNotValidError('La dirección no tiene el formato válido: <Tipo de vía> <Partícula> <Nombre>, <Número>. Recuerde que puede omitir tipo de vía y partícula.')
    
def levenshtein(a: str, b: str) -> float:
    # Distancia de Levenshtein para el fuzzy search
    n, m = len(a), len(b)
    # No se almacena la matriz entera (muy costoso), solo filas anterior y actual
    prev = list(range(m+1))   # prev[j]: coste de transformar la cadena vacía entre los primeros j caracteres de b
    curr = [0] * (m+1)

    for i in range(1, n+1):
        curr[0] = i   # coste de transformar los ultimos i caracteres de a en cadena vacía (borrar i caracteres)
        for j in range(1, m+1):
            # Coste de cambiar un caracter por otro (0 si son iguales, 1 si distintos)
            if a[i-1] == b[j-1]:
                cost = 0
            else:
                cost = 1
            # Elige el mínimo entre:
            # borrar un carácter de a (prev[j] + 1)
            # insertar un carácter de b (curr[j-1] + 1)
            # sustituirlo o mantenerlo si es igual (prev[j-1] + cost)            
            curr[j] = min(prev[j] + 1, curr[j-1] + 1, prev[j-1] + cost)
        prev, curr = curr, prev

    d = prev[m]
    l = max(n, m)  # normalización (siempre devolverá una distancia entre 0 y 1)
    return d / l

def mejores_direcciones_fuzzy(df: pd.DataFrame, texto: str, modo: str):
    if modo == 'completo':
        distances = []
        for i in range(df.shape[0]):
            dir = f'{df.iloc[i, 0]} {df.iloc[i, 1]} {df.iloc[i, 2]}, {df.iloc[i, 3]}'
            coords = (df.iloc[i, 4], df.iloc[i, 5])
            d = levenshtein(texto, dir)
            if d < 0.4:
                distances.append((dir, d, coords))
    elif modo == 'simplificado':
        distances = []
        for i in range(df.shape[0]):
            dir = f'{df.iloc[i, 2]}, {df.iloc[i, 3]}'
            coords = (df.iloc[i, 4], df.iloc[i, 5])
            d = levenshtein(texto, dir)
            if d < 0.4:
                distances.append((dir, d, coords))
 
    mejores = []
    if len(distances) < 5:
        return distances

    for i in range(5):
        # buscar índice del mínimo d
        best_idx = 0
        best_d = distances[0][1]
        for j in range(1, len(distances)):
            if distances[j][1] < best_d:
                best_d = distances[j][1]
                best_idx = j

        # añadir esa tupla al resultado y quitarla de la lista
        mejores.append(distances[best_idx])
        distances.pop(best_idx)

    return mejores

    



############## Parte 4 ##############


def carga_grafo() -> nx.MultiDiGraph:

    """
    Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    
    Args: None
    
    Returns:
        nx.MultiDiGraph: Quiver de las calles de Madrid.
    
    Raises:
        ServiceNotAvailableError: Si no es posible recuperar el grafo de OpenStreetMap.
    """
    
    if not os.path.exists('madrid.graphml'):

        #leer grafo de la web
        madrid_graphml = ox.graph_from_place("Madrid, Spain", network_type='drive')

        #guardar grafo
        ox.io.save_graphml(madrid_graphml, 'madrid.graphml')

    else:
        
        madrid_graphml = ox.load_graphml('madrid.graphml')

    return madrid_graphml


def procesa_grafo(multidigrafo: nx.MultiDiGraph) -> nx.DiGraph:

    """
    Función que recupera el quiver de calles de Madrid de OpenStreetMap.
    
    Args:
        multidigrafo: multidigrafo de las calles de Madrid obtenido de OpenStreetMap.
    
    Returns:
        nx.DiGraph: Grafo dirigido y sin bucles asociado al multidigrafo dado.
    
    Raises: None
    """
    
    #digrafo con bucles
    digraph = ox.convert.to_digraph(multidigrafo)

    #bucles
    loops = list(nx.selfloop_edges(digraph))

    #eliminar bucles
    digraph.remove_edges_from(loops)

    return digraph

    
def investigar_grafo(grafo: nx.DiGraph) -> None:

    """
    Investiga el grafo e imprime todos los nombres de atributos (claves)
    únicos que se encuentran en los nodos y aristas, usando bucles for.
    """
    
    node_keys_list = []  # Usamos una lista en lugar de un set
    edge_keys_list = []  # Usamos una lista en lugar de un set

    # 1. Recopilar todas las claves de los nodos
    # data=True devuelve (nodo, dict_de_atributos)
    for _, data in grafo.nodes(data=True):
        # data es un diccionario, data.keys() son sus claves
        for key in data.keys():
            if key not in node_keys_list:
                node_keys_list.append(key)

    # 2. Recopilar todas las claves de las aristas
    # data=True devuelve (origen, destino, dict_de_atributos)
    for _, _, data in grafo.edges(data=True):
        # data es un diccionario, data.keys() son sus claves
        for key in data.keys():
            if key not in edge_keys_list:
                edge_keys_list.append(key)

    print('--- Investigación del DiGraph (con bucles for) ---')
    print(f'Total Nodos: {grafo.number_of_nodes()}')
    print(f'Total Aristas: {grafo.number_of_edges()}')

    print('\nAtributos únicos encontrados en NODOS:')
    print(node_keys_list)

    print('\nAtributos únicos encontrados en ARISTAS:')
    print(edge_keys_list)

def dibujar_grafo_coordenadas(grafo: nx.DiGraph) -> None:
    # Crear un diccionario con la posición de todos los nodos
    pos = {}
    for n in grafo.nodes():
        pos[n] = (grafo.nodes[n]['x'], grafo.nodes[n]['y'])

    # Dibujar el grafo incluyendo el diccionario pos
    plt.figure(figsize=(10, 10))
    nx.draw_networkx_edges(grafo, pos=pos, width=0.5, arrows=False)
    plt.gca().set_aspect('equal', adjustable='box')   # Mantiene la relación de aspecto 1:1
    plt.show()