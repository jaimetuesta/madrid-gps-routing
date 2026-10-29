# Madrid GPS: Route Planning on the City Street Graph

**Authors:** Jaime Tuesta de Simón and Ignacio Mascarell Agúndez (joint work, group GP11B)
**Context:** Practical assignment 3 of *Matemática Discreta* (Discrete Mathematics), 2nd year, Universidad Pontificia Comillas (ICAI), November 2025.
**Language:** code comments, console messages and report are in Spanish; this README is in English.

## Overview

A command-line GPS for driving in Madrid. The user types an origin and a destination address and chooses how to optimise the route. The program then:

1. finds both addresses in the official Madrid street directory and gets their coordinates,
2. snaps each point to the nearest node of the OpenStreetMap drivable street graph,
3. computes the optimal route with the authors' own implementation of **Dijkstra's algorithm** (binary heap),
4. prints turn-by-turn instructions ("Avance 170.00 m por ...", "Gire a la derecha hacia ..."),
5. draws the street graph with the route highlighted.

Three routing modes are available:

| Mode | Edge weight |
|---|---|
| `MC` shortest route | edge length (m) |
| `MR` fastest route | length / speed limit. The speed limit comes from the OSM `maxspeed` tag; if it is missing, a default per road type is used (e.g. residential 30 km/h, primary 50 km/h), and 30 km/h if the road type is unknown |
| `MRO` fastest route with traffic lights | `MR` time plus an expected wait of 0.8 × 30 s = 24 s when entering a node whose number of incoming plus outgoing edges is greater than two (treated as an intersection), as defined in the assignment. Actual traffic-light locations are not used |

### Address input

Addresses can be typed in full (`Calle de Alberto Aguilera, 23`) or without the road type (`Alberto Aguilera, 23`); they are parsed with regular expressions. If an address is not found, a fuzzy search based on a normalised Levenshtein distance proposes up to five similar addresses. An empty address exits the program.

## Repository structure

```
├── gps.py              # main program: user interaction, route, instructions, map
├── callejero.py        # street directory loading, address search (regex + fuzzy), graph loading
├── grafo_pesado.py     # weighted-graph library: Dijkstra, shortest path, Prim, Kruskal
├── pesos.py            # weight functions: length, time, time with traffic lights
├── direcciones.csv     # Madrid street directory (see Data)
├── madrid.graphml      # Madrid drivable street graph from OpenStreetMap (see Data)
├── report/
│   ├── Memoria_GPS_Madrid.pdf
│   ├── memoria.tex     # LaTeX source of the report
│   └── figs/           # route maps and console screenshots used in the report
├── requirements.txt
├── .gitignore
└── README.md
```

`grafo_pesado.py` also contains Prim's and Kruskal's minimum spanning tree algorithms, written for the course; the GPS itself only uses Dijkstra.

## Data

- **`direcciones.csv`**: *Callejero oficial del Ayuntamiento de Madrid – Relación de direcciones vigentes, con coordenadas*, Madrid City Council Open Data Portal ([datos.madrid.es](https://datos.madrid.es/en/dataset/213605-0-callejero-oficial-madrid/resource/213605-4-callejero-oficial-madrid-csv)), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The copy in this repository was downloaded in November 2025; the portal publishes updated versions.
- **`madrid.graphml`**: drivable street network of Madrid downloaded from OpenStreetMap with OSMnx (`graph_from_place("Madrid, Spain", network_type="drive")`) in November 2025. Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), available under the [ODbL](https://opendatacommons.org/licenses/odbl/).

Both files are included so that the program runs with the same data used in the project. If `madrid.graphml` is deleted, `callejero.py` downloads the current graph from OpenStreetMap and saves it again; routes may then differ slightly.

## How to run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python gps.py
```

Run it **from the repository root**: the data files are opened with relative paths. For each route the whole city graph is drawn first and the view is then zoomed in on the route.

## Limitations

- Travel times use speed limits only (no traffic data), and the traffic-light model is the simplified one from the assignment.
- Dijkstra computes the shortest-path tree of the whole reachable graph for every query instead of stopping at the destination; Kruskal uses insertion into a sorted list and relabels components in a loop (quadratic). Both are kept as implemented in the course.
- The fuzzy address search compares the input with every row of the address file, so it can take a while on the full file.
- Turn directions are computed with longitude/latitude used as plane coordinates, which is adequate for distinguishing left, right and straight at city scale.

## Changes made for publication

The algorithms and program logic are those of the original submission. For this repository, the following changes were made:

- `camino_minimo` returns `None` when the destination cannot be reached from the origin, and `gps.py` tells the user instead of printing an empty route.
- `time_weight` falls back to a default speed (30 km/h) when an edge has no readable `maxspeed` and an unknown road type, so that a freshly downloaded graph cannot stop the program.
- `tipo_giro` clamps the cosine to [-1, 1] before `acos` to avoid rounding errors on aligned nodes.
- Student ID numbers were removed from the file headers, `requirements.txt` was completed, and the report was rewritten and expanded (explicit weight formulas, navigation-instruction logic, and figures from real runs of the program).
