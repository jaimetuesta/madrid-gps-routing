"""
gps.py

Matemática Discreta - IMAT
ICAI, Universidad Pontificia Comillas

Grupo: GP11B
Integrantes:
    - Jaime Tuesta de Simón
    - Ignacio Mascarell Agúndez

Descripción:
Programa principal del GPS, que pide direcciones de origen y destino junto con el método de cálculo de ruta, y devuelve instrucciones
y un mapa con la ruta pintada.
"""

import pandas as pd
import callejero as c
import grafo_pesado as g
import pesos as p
import networkx as nx
import osmnx as ox
import math
import matplotlib.pyplot as plt

def imprimir_intro() -> None:
	print('Bienvenido al GPS.')
	print('Se le pedirán dos direcciones, una de origen y una de destino, las cuales se pueden introducir de dos maneras:')
	print(' - Completa: con tipo de vía (ej. Calle de Alberto Aguilera, 23)')
	print(' - Simplificada: sin tipo de vía (ej. Alberto Aguilera, 23)')
	print('\nSe le pedirá también el método para calcular la ruta: más corta, más rápida, o más rápida optimizada con semáforos.')
	print('Recibirá instrucciones detalladas de como llegar a su destino y un mapa con la ruta dibujada.')
	print('Para salir, basta con introducir una dirección vacía.')

def cargar_procesar_grafo() -> pd.DataFrame:
    multigraph = c.carga_grafo()
    graph = c.procesa_grafo(multigraph)

    return graph

def pedir_coordenadas(G: nx.DiGraph, df: pd.DataFrame) -> tuple[tuple[float,float],tuple[float,float]]:
	same_place = True
	while same_place:
		print('\n-- ORIGEN --')
		valid = False
		while not valid:
			direccion_global = input(f'Introduzca la dirección de origen:\n - Dirección: ')
			if len(direccion_global) != 0:
				try:
					lat1, lon1 = c.busca_direccion(direccion_global, df)
					valid = True
				except c.AddressNotFoundError as error:
					print(error)
				except c.FormatNotValidError as error:
					print(error)
			else:
				return None, None

		print('\n-- DESTINO --')
		valid = False
		while not valid:
			direccion_global = input(f'Introduzca la dirección de destino:\n - Dirección: ')
			if len(direccion_global) != 0:
				try:
					lat2, lon2 = c.busca_direccion(direccion_global, df)
					valid = True
				except c.AddressNotFoundError as error:
					print(error)
				except c.FormatNotValidError as error:
					print(error)
			else:
				return None, None
			
		# Si ambas direcciones van al mismo nodo, en vez de imprimir direcciones vacías, se dice al usuario que las introduzca de nuevo
		if ox.distance.nearest_nodes(G, lon1, lat1) == ox.distance.nearest_nodes(G, lon2, lat2):
			print('\nLas direcciones que ha introducido están demasiado cerca y no es posible hallar un camino entre ellas.')
			print('Introduzca las direcciones de nuevo.')
			same_place = True
		else:
			same_place = False

	return (lat1, lon1), (lat2, lon2)
	
def elegir_modo_calculo() -> str:

	print('\n-- MÉTODO DE CÁLCULO DE RUTA --')
	modos_posibles = ['MC', 'MR', 'MRO']
	modo_elegido = input('Seleccione el modo de cálculo de ruta entre: ' \
		'\n - Ruta más corta (MC) \n - Ruta más rápida (MR) \n - Ruta más rápida optimizada con semáforos (MRO)' \
		'\n Opción: ').strip().upper()
	while modo_elegido not in modos_posibles:
		print('Debe elegir un modo válido.')
		modo_elegido = input('Seleccione el modo de cálculo de ruta entre: ' \
		'\n - Ruta más corta (MC) \n - Ruta más rápida (MR) \n - Ruta más rápida optimizada con semáforos (MRO)' \
		'\nOpción: ').strip().upper()
	return modo_elegido

def calculo_ruta(G: nx.DiGraph, lon1: float, lat1: float, lon2: float, lat2: float, modo_calculo: str) -> list[object]:

	u = ox.distance.nearest_nodes(G, lon1, lat1)   # nodo origen
	v = ox.distance.nearest_nodes(G, lon2, lat2)   # nodo destino

	if modo_calculo == 'MC':
		path = g.camino_minimo(G, p.length_weight, u, v)
	elif modo_calculo =='MR':
		path = g.camino_minimo(G, p.time_weight, u, v)
	else:
		path = g.camino_minimo(G, p.stoplights_weight, u, v)

	return path

def construir_camino(G: nx.DiGraph, path: list[object]):
	print('\nDIRECCIONES:')
	count = 0
	n = len(path)
	for i in range(n-1):
		u = path[i]
		v = path[i+1]
		nombre1 = hallar_nombre_via(G, u, v)
		length = G[u][v]['length']
		count += length
		giro = None

		if i != n-2:
			w = path[i+2]
			nombre2 = hallar_nombre_via(G, v, w)
			if nombre1 != nombre2:
				giro = tipo_giro(G, u, v, w)
		else:
			nombre2 = None

		if i == n-2 or nombre1 != nombre2:
			if nombre1 == 'NO-NAME':
				# Calle sin nombre
				# Nos gustaría poder poner el nombre de la carretera, pero estas aristas no tienen atirbuto 'name' ni 'ref', ni 
				# siquiera en el multidigrafo original
				if nombre2 is None:
					print(f'Avance {count:.2f} m hasta llegar a su destino.')
				else:
					if giro == 'izquierda' or giro == 'derecha':
						print(f'Avance {count:.2f} m y gire a la {giro} hacia {nombre2}.')
					else:
						print(f'Siga recto {count:.2f} m hasta {nombre2}.')
			else:
				if giro is None:
					print(f'Avance {count:.2f} m por {nombre1} hasta llegar a su destino.')
				else:
					if giro == 'izquierda' or giro == 'derecha':
						print(f'Avance {count:.2f} m por {nombre1}.')
						if nombre2 != 'NO-NAME':
							print(f'Gire a la {giro} hacia {nombre2}.')
						else:
							print(f'Gire a la {giro}.')
					else:
						print(f'Avance {count:.2f} m por {nombre1}.')
						if nombre2 != 'NO-NAME':
							print(f'Siga recto hacia {nombre2}.')

			count = 0

def hallar_nombre_via(G: nx.DiGraph, u: object, v: object) -> str:
	try:
		nombre = G[u][v]['name']
		if type(nombre) is list:
			nombre_str = ''
			while len(nombre) >= 2:
				if nombre_str:
					nombre_str += ', '
				calle = nombre[0]
				nombre = nombre[1:]
				nombre_str += calle
			nombre_str += f' y {nombre[0]}'
			return nombre_str
		return nombre
	except KeyError:
		try:
			nombre = G[u][v]['ref']
		except:
			nombre = 'NO-NAME'
	return nombre

def tipo_giro(G: nx.DiGraph, u: object, v: object, w: object):
	# Coordenadas de los nodos
	xu, yu = G.nodes[u]['x'], G.nodes[u]['y']
	xv, yv = G.nodes[v]['x'], G.nodes[v]['y']
	xw, yw = G.nodes[w]['x'], G.nodes[w]['y']

	# Vectores de las aristas a = (u, v), b = (v, w)
	ax, ay = xv - xu, yv - yu
	bx, by = xw - xv, yw - yv

	escalar = ax*bx + ay*by
	mod_a = math.sqrt(ax**2 + ay**2)
	mod_b = math.sqrt(bx**2 + by**2)
	# Se limita el coseno a [-1, 1] porque el redondeo puede dar valores como 1.0000000002 (math domain error)
	theta = math.acos(max(-1.0, min(1.0, escalar/(mod_a*mod_b))))
	
	# El producto escalar no te da el signo, el signo viene dado por el producto cruzado
	cruzado = ax*by - ay*bx

	if abs(theta) < math.radians(30):
		return 'recto'
	elif cruzado > 0:
		return 'izquierda'
	else:
		return 'derecha'
	
def dibujar_camino(G: nx.DiGraph, path: list[object]):
	print('\nDibujando camino...')

	# Almacenar las posiciones en un diccionario
	pos = {}
	for n in G.nodes:
		pos[n] = (G.nodes[n]['x'], G.nodes[n]['y'])
	edges_path = []

	for i in range(len(path)-1):
		edges_path.append((path[i], path[i+1]))

	# Ajustar ejes para que se imprima solo la zona relevante
	xmin, xmax, ymin, ymax = float('inf'), -float('inf'), float('inf'), -float('inf')
	for n in path:
		x = G.nodes[n]['x']
		y = G.nodes[n]['y']
		if x < xmin:
			xmin = x
		if x > xmax:
			xmax = x
		if y < ymin:
			ymin = y
		if y > ymax:
			ymax = y

	origen = path[0]
	destino = path[-1]

	cx = (xmin + xmax) / 2
	cy = (ymin + ymax) / 2
	lado = max(xmax - xmin, ymax - ymin) * 1.1

	xmin = cx - lado/2
	xmax = cx + lado/2
	ymin = cy - lado/2
	ymax = cy + lado/2

	# Dibujar
	plt.figure(figsize=(8, 8))

	nx.draw(G, pos=pos, node_size=0, edge_color='lightgray', width=0.5, arrows=False)
	nx.draw_networkx_edges(G, pos=pos, edgelist=edges_path, edge_color='blue', width=2.0, arrows=False)
	nx.draw_networkx_nodes(G, pos=pos, nodelist=[origen], node_color='red', node_size=20)
	nx.draw_networkx_nodes(G, pos=pos, nodelist=[destino], node_color='green', node_size=30)

	plt.xlim(xmin, xmax)
	plt.ylim(ymin, ymax)
	plt.gca().set_aspect('equal', adjustable='box')   # Mantiene la relación de aspecto 1:1
	plt.show()

if __name__ == '__main__':
	imprimir_intro()
	
	#parte 1: lectura del fichero 
	direcciones_fichero = c.carga_callejero()
	grafo_mapa = cargar_procesar_grafo()

	#parte 2: seleccionar direcciones
	done = False
	while not done:
		coord_origen, coord_destino = pedir_coordenadas(grafo_mapa, direcciones_fichero)
		if coord_origen is not None:
			lat1, lon1 = coord_origen
			lat2, lon2 = coord_destino

			#parte 3: elegir modo de cálculo de ruta
			modo_calculo = elegir_modo_calculo()

			#parte 4: calcular ruta
			ruta_calculada = calculo_ruta(grafo_mapa, lon1, lat1, lon2, lat2, modo_calculo)

			if ruta_calculada is None:
				print('\nNo existe una ruta en coche desde el origen hasta el destino.')
			else:
				#parte 5: construir direcciones de navegación
				construir_camino(grafo_mapa, ruta_calculada)

				#parte 6: mostrar ruta resaltada sobre el grafo
				dibujar_camino(grafo_mapa, ruta_calculada)

			#part7: volver a ruta
			print('\nPuede hacer otra búsqueda.')
		else:
			done = True

	print('\nHasta pronto...')
