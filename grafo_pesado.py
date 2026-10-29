"""
grafo_pesado.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP11B
Integrantes:
    - Jaime Tuesta de Simón
    - Ignacio Mascarell Agúndez

Descripción:
Librería para el análisis de grafos pesados.
"""

from typing import List,Tuple,Dict,Callable,Union
import networkx as nx
import heapq
import sys

import heapq #Librería para la creación de colas de prioridad

INFTY=sys.float_info.max #Distincia "infinita" entre nodos de un grafo

"""
En las siguientes funciones, las funciones de peso son funciones que reciben un grafo o digrafo y dos vértices y devuelven un real (su peso)
Por ejemplo, si las aristas del grafo contienen en sus datos un campo llamado 'valor', una posible función de peso sería:

def mi_peso(G:nx.Graph,u:object, v:object):
    return G[u][v]['valor']

y, en tal caso, para calcular Dijkstra con dicho parámetro haríamos

camino=dijkstra(G,mi_peso,origen, destino)


"""

def dijkstra(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]], origen:object)-> Dict[object,object]:

    """ Calcula un Árbol de Caminos Mínimos para el grafo pesado partiendo
    del vértice "origen" usando el algoritmo de Dijkstra. Calcula únicamente
    el árbol de la componente conexa que contiene a "origen".
    
    Args:
        origen (object): vértice del grafo de origen
    Returns:
        Dict[object,object]: Devuelve un diccionario que indica, para cada vértice alcanzable
            desde "origen", qué vértice es su padre en el árbol de caminos mínimos.
    Raises:
        TypeError: Si origen no es "hashable".
    Example:
        Si G.dijkstra(1)={2:1, 3:2, 4:1} entonces 1 es padre de 2 y de 4 y 2 es padre de 3.
        En particular, un camino mínimo desde 1 hasta 3 sería 1->2->3.
    """

    #valor inicial de distancias, padres, visitados -> inf, None, False
    distancias, padres, visitados = {}, {}, {}
    for vertice in G.nodes():
        distancias[vertice] = float('inf')
        padres[vertice] = None
        visitados[vertice] = False

    #lista vacía -> funciona como cola de prioridad
    cola_prioridad = []

    #añadir origen a montículo
    distancias[origen] = 0
    heapq.heappush(cola_prioridad, (0, origen)) # (distancia, vertice)

    #bucle principal: mientras la cola de prioridad no esté vacía
    while cola_prioridad: 

        #sacar nodo con menor distancia
        dist_actual, vertice_actual = heapq.heappop(cola_prioridad)

        #si no lo hemos visitado -> evaluarlo
        if visitados[vertice_actual] == False:

            #actualizar valor a visitado
            visitados[vertice_actual] = True

            #mirar vecinos del vértice actual
            for vecino in G.neighbors(vertice_actual):
                
                if visitados[vecino] == False:

                    #usar función coste -> calcula el coste de ir desde vértice actual al vecino evaluado
                    peso_arista = peso(G, vertice_actual, vecino)
                    nueva_dist = dist_actual + peso_arista

                    #si la nueva distancia es menor (camino mejor) -> actualizar
                    if distancias[vecino] >  nueva_dist:
                        distancias[vecino] = nueva_dist
                        padres[vecino] = vertice_actual

                        #nnuevo camino, mejorado -> añadir
                        heapq.heappush(cola_prioridad, (nueva_dist, vecino))

    return padres


def camino_minimo(G:Union[nx.Graph, nx.DiGraph], peso:Union[Callable[[nx.Graph,object,object],float], Callable[[nx.DiGraph,object,object],float]] ,origen:object,destino:object)->List[object]:
    """ Calcula el camino mínimo desde el vértice origen hasta el vértice
    destino utilizando el algoritmo de Dijkstra.
   
    Args:
        G (nx.Graph o nx.Digraph): grafo a grado dirigido
        peso (función): función que recibe un grafo o grafo dirigido y dos vértices del mismo y devuelve el peso de la arista que los conecta
        origen (object): vértice del grafo de origen
        destino (object): vértice del grafo de destino
    Returns:
        List[object]: Devuelve una lista con los vértices del grafo por los que pasa
            el camino más corto entre el origen y el destino. El primer elemento de
            la lista es origen y el último destino.
    Example:
        Si dijksra(G,peso,1,4)=[1,5,2,4] entonces el camino más corto en G entre 1 y 4 es 1->5->2->4.
    Raises:
        TypeError: Si origen o destino no son "hashable".
    """
    path = []
 
    parent = dijkstra(G, peso, origen)
    if destino not in parent:
        return None   # no alcanzable
    if destino != origen and parent[destino] is None:
        return None   # destino sin padre en el árbol: no alcanzable desde origen
   
    curr = destino
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
 
    return path


def prim(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> Dict[object,object]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo pesado,
    siguiendo la estructura literal del pseudocódigo de la asignatura.
    """
    
   # Inicializamos padres, coste_minimo y visitados
    padres, coste_min, visitados = {}, {}, {}
    for vertice in G.nodes():
        padres[vertice] = None
        coste_min[vertice] = float('inf')
        visitados[vertice] = False

    #lista vacía -> funciona como cola de prioridad
    cola_prioridad = []

    #añadir vértices a cola de prioridad con coste inicial (inf)
    for vertice in G.nodes():
        heapq.heappush(cola_prioridad, (coste_min[vertice], vertice))

    #bucle principal: mientras la cola de prioridad no esté vacía
    while cola_prioridad:

        #extraer vértice con menor coste de cola de prioridad
        coste_actual, vert_actual = heapq.heappop(cola_prioridad)

        if visitados[vert_actual] == False:

            visitados[vert_actual] = True

            #analizar cada vecino del vértice actual
            for vecino in G.neighbors(vert_actual):

                if visitados[vecino] == False:

                    #calcular coste de la arista de vert_actual a vecino
                    peso_vert_vec = peso(G, vert_actual, vecino)

                    #si peso_vert_vec < coste_min[vecino] -> actualizar la cola
                    if peso_vert_vec < coste_min[vecino]:

                        coste_min[vecino] = peso_vert_vec
                        padres[vecino] = vert_actual

                        #actualizar peso de vecino en la cola
                        heapq.heappush(cola_prioridad, (peso_vert_vec, vecino))

    return padres
                

def kruskal(G:nx.Graph, peso:Callable[[nx.Graph,object,object],float])-> List[Tuple[object,object]]:
    """ Calcula un Árbol Abarcador Mínimo para el grafo
    usando el algoritmo de Kruskal.
    
    Args:
        G (nx.Graph): grafo
        peso (función): función que recibe un grafo y dos vértices del grafo y devuelve el peso de la arista que los conecta
    Returns:
        List[Tuple[object,object]]: Devuelve una lista [(s1,t1),(s2,t2),...,(sn,tn)]
            de los pares de vértices del grafo que forman las aristas
            del arbol abarcador mínimo.
    Raises: None
    Example:
        En el ejemplo anterior en que prim(G,peso)={1:None, 2:1, 3:2, 4:1} podríamos tener, por ejemplo,
        kruskal(G,peso)=[(1,2),(1,4),(3,2)]
    """
    # Lista de aristas L (siendo u, v cada arista) ordenada por su peso c
    L = []
    for u, v in G.edges:
        c = peso(G, u, v)
        i = 0
        while i < len(L) and L[i][2] <= c:
            i += 1
        L.insert(i, (u, v, c))
 
    # Crear una componente distinta para cada vértice (bosque)
    C = {}
    for v in G.nodes:
        C[v] = v
 
    aristas_aam = []
    while L:
        u, v, c = L.pop(0)   # se extrae la arista de menor peso (árbol abarcador MÍNIMO)
        if C[u] != C[v]:
            # si los vértices pertenecen a componentes distintas, se añade (si pertenecen a la misma se genera ciclo)
            aristas_aam.append((u, v))
       
            # Unificar las componentes de u y v (todos los vértices que pertenezan a C[v] pasan a C[u])
            old = C[v]
            new = C[u]
            for w in C:
                if C[w] == old:
                    C[w] = new
 
    return aristas_aam

