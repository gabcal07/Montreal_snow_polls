import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
from networkx.algorithms.flow import min_cost_flow

from folium import plugins
import folium
import sys
import resource
import pickle
import json
from drone import start_drone
from SPRP import launch_snow_plows
from colorama import Fore, Back, Style

from datetime import datetime, timedelta
import osmnx as ox
import folium

sys.setrecursionlimit(2000)
resource.setrlimit(resource.RLIMIT_STACK, (2**29, -1))

# default value
DRONE_ACTIVE = False

# region datas
# speed
drone_speed = 70
speed = 10
speed_second = speed / 3.6
drone_speed_second = drone_speed / 3.6
# endregion

# Get the value of DRONE_ACTIVE from the user
DRONE_ACTIVE = input("Voulez-vous simuler le parcours du drone(0) ou bien des deneigeuses(1) ? (0/1): ")

# Convert the user input to a boolean value
if DRONE_ACTIVE.lower() == "0":
    print("Simulation du parcours du drone")
    DRONE_ACTIVE = True
else:
    print("Simulation du parcours des deneigeuses")
    DRONE_ACTIVE = False

# region utils

# # METHOD: FIND GRAPH FROM NAME
# city_name = "Verdun, Montreal, Quebec, Canada"
# # # # Télécharger le graphe des routes pour la ville spécifiée
# G = ox.graph_from_place(city_name, network_type='drive')

# # METHOD:  Sauvegarder le graphe dans un fichier
# file_path = "Verdun/verdun.pkl"
# nx.write_gpickle(G, file_path)
# endregion

current_date = datetime.now()
date_format = "%Y-%m-%dT%H:%M:%S"
date_str = current_date.strftime(date_format)


def addition_date(date, seconds):
    date = datetime.strptime(date, date_format)
    new_date = date + timedelta(seconds=seconds)
    return new_date.strftime(date_format)

def space_between_dates(date1, date2):
    date1 = datetime.strptime(date1, date_format)
    date2 = datetime.strptime(date2, date_format)
    return timedelta(seconds=(date2 - date1).total_seconds())


# region scenario

# here city_selector is gonna indicate the number of snowplows we are going to use for the simulation
# it has the same index as the corresponding city in the list possible_cities
# scenario_selector is gonna indicate the proportion of snowplows from type1 and type2 we are gonna use (type1, type2)

#### VALEURS PAR DEFAUT ####
city_selector = 0 # selects the city and the number of snowplows that we estimated to be the best
scenario_selector = 2 # selects the scenario we want to run
### FIN VALEURS PAR DEFAUT ###

# Demander à l'utilisateur de sélectionner une ville
# region input from user
city_selector = int(input("Sélectionnez une ville (0: Rivière-des-prairies-pointe-aux-trembles, 1: Anjou, 2: Verdun, 3: Outremont, 4: Le-Plateau-Mont-Royal): "))

# Valider l'entrée de l'utilisateur
while city_selector < 0 or city_selector > 4:
    print("Sélection de ville invalide. Veuillez réessayer.")
    city_selector = int(input("Sélectionnez une ville (0: Rivière-des-prairies-pointe-aux-trembles, 1: Anjou, 2: Verdun, 3: Outremont, 4: Le-Plateau-Mont-Royal): "))

# Demander à l'utilisateur de sélectionner un scénario
scenario_selector = int(input("Sélectionnez un scénario (0: 100% type 1, 1: 100% type 2, 2: 50% type 1 et 50% type 2): "))

# Valider l'entrée de l'utilisateur
while scenario_selector < 0 or scenario_selector > 2:
    print("Sélection de scénario invalide. Veuillez réessayer.")
    scenario_selector = int(input("Sélectionnez un scénario (0: 100% type 1, 1: 100% type 2, 2: 50% type 1 et 50% type 2): "))
# endregion

snowplows_numbers_0 = [(20, 0), (10, 0), (10, 0), (6, 0), (10, 0)] # 100 0
snowplows_numbers_1 = [(x[1], x[0]) for x in snowplows_numbers_0] # 0 100
snowplows_numbers_2 = [(x[0] // 2, x[0] // 2) for x in snowplows_numbers_0] # 50 50

# Print the selected scenario description
scenario_descriptions = ["100% de deneigeuses de type 1", "100% de deneigeuse de type 2",  "50% de deneigeuse de type 1 et 50% de deneigeuse de type 2"]
print(f"Scenario: {scenario_descriptions[scenario_selector]}")

scenario_array = [snowplows_numbers_0, snowplows_numbers_1, snowplows_numbers_2]
snowplows_number = scenario_array[scenario_selector][city_selector] # selects the number of snowplows we are gonna use for the simulation according to the scenario and the city
possible_cities = ["Rivière-des-prairies-pointe-aux-trembles", "Anjou", "Verdun", "Outremont", "Le-Plateau-Mont-Royal"]
# endregion

# # Load the graph from the file
city = "../" + possible_cities[city_selector]
print(Fore.GREEN + "Lancement de la simulation pour " + city.split("/")[1] + " avec " + str(snowplows_number[0]) + " deneigeuses de type 1 et " + str(snowplows_number[1]) + " deneigeuses de type 2" + Style.RESET_ALL)
file_dir = city + "/"
file_path = city + "/graph.pkl"
# Load the graph from the file
with open(file_path, 'rb') as f:
    G = pickle.load(f)
# file_path = "limeil.pkl"
# G = nx.read_gpickle(file_path)
G_undirected = G.to_undirected()
G = G.to_directed()
dist = 0
for edge in G_undirected.edges:
    dist+=G_undirected[edge[0]][edge[1]][0]['length']
print(f"Distance totale du graph non orienté: {dist}")


def create_map_with_edges(G, city):
    # Créer une carte basée sur Leaflet avec folium
    center = (ox.geocode(city)[0], ox.geocode(city)[1])
    m = folium.Map(location=center, zoom_start=14)
    folium.TileLayer('openstreetmap').add_to(m)

    # Fonction pour ajouter les arêtes une par une sur la carte
    def add_edges_to_map(m, edges, G):
        for u, v in edges:
            folium.PolyLine(
                locations=[(G.nodes[u]['y'], G.nodes[u]['x']), (G.nodes[v]['y'], G.nodes[v]['x'])],
                color='blue', weight=2
            ).add_to(m)

    # Ajouter les arêtes au graphe folium
    for u, v in G.edges():
        folium.PolyLine(locations=[(G.nodes[u]['y'], G.nodes[u]['x']), (G.nodes[v]['y'], G.nodes[v]['x'])],
                        color='red', weight=2).add_to(m)

    return m

if (city == "../Verdun" or city == "../Anjou"):
    m = create_map_with_edges(G, city+",Montréal,QA,Canada")
else:
    m = create_map_with_edges(G, city)


# m.save(file_dir+'map.html')
# exit()

start_node = list(G_undirected.nodes)[0]
# print("Start node", start_node)
total_distance_drone = 0

if DRONE_ACTIVE:
    visited_edges, graph, total_distance_drone = start_drone(G_undirected)
else: paths = launch_snow_plows(G_undirected, G, snowplows_number[0] + snowplows_number[1])




# Create a list of GeoJSON features for each step
lines = []
total_end = date_str
total_distance_d = 0
total_distance_d_2 = 0

# for i in range (0, len(visited_edges)):

def create_lines_from_visited_edges_drone(G, visited_edges, speed, color):
    lines = []
    date_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    total_end = date_str
    j = 0
    global total_distance_drone
    for edge in visited_edges:
        u, v, length = edge
        coordinates = [
            [G.nodes[u]['x'], G.nodes[u]['y']],
            [G.nodes[v]['x'], G.nodes[v]['y']]
        ]
        total_distance_drone += length
        start = addition_date(date_str, j)
        end = addition_date(start, length / speed)
        total_end = max(total_end, end)
        line = {
            'coordinates': coordinates,
            "dates": [start, end],
            "color": color,
        }
        lines.append(line)
        j += length / speed
    return lines, total_end

def create_lines_from_visited_edges(G, visited_edges, speed, color, type_2 = False):
    lines = []
    date_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    total_end = date_str
    j = 0
    global total_distance_d
    global total_distance_d_2
    for edge in visited_edges:
        u, v, length,dic = edge
        coordinates = [
            [G.nodes[u]['x'], G.nodes[u]['y']],
            [G.nodes[v]['x'], G.nodes[v]['y']]
        ]
        if type_2:
            total_distance_d_2 += dic['length']
        else:
            total_distance_d += dic['length']
        start = addition_date(date_str, j)
        end = addition_date(start, dic['length'] / speed)
        total_end = max(total_end, end)
        line = {
            'coordinates': coordinates,
            "dates": [start, end],
            "color": color,
        }
        lines.append(line)
        j += dic['length'] / speed
    return lines, total_end

def create_features_drone(G_undirected, visited_edges, speed, color):
    features = []
    lines, total_end = create_lines_from_visited_edges_drone(G_undirected, visited_edges, speed, color)
    features = [
        {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": line["coordinates"],
            },
            "properties": {
                "times": line["dates"],
                "style": {
                    "color": line["color"],
                    "weight": line["weight"] if "weight" in line else 3,
                },
            },
        }
        for line in lines
    ]
    return features, total_end

def create_features_desnowing(G, paths, speed, colors):
    features = []
    lines_ = []
    nb_type_2 = snowplows_number[1]
    for i in range(len(paths)):
        type_2 = True if nb_type_2 > 0 else False
        lines, total_end = create_lines_from_visited_edges(G, paths[i], speed, colors[i % len(colors)], type_2)
        lines_ += lines
        features.extend([
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": line["coordinates"],
                },
                "properties": {
                    "times": line["dates"],
                    "style": {
                        "color": line["color"],
                        "weight": line["weight"] if "weight" in line else 3,
                    },
                },
            }
            for line in lines_
        ])
        nb_type_2 -= 1
        lines_.clear()
    return features, total_end

colors = colors = [
    "green", "black", "yellow", "blue", "grey", "purple", "pink", "brown", "cyan", "orange",
    "red", "magenta", "lime", "maroon", "navy", "olive", "teal", "silver", "gold", "beige",
    "lavender", "coral", "turquoise", "indigo", "violet", "salmon", "chocolate", "tan", "khaki", "crimson"
]
features, total_end_new = create_features_drone(G_undirected, visited_edges, drone_speed_second, 'blue') if DRONE_ACTIVE else  create_features_desnowing(G, paths, speed_second, colors)
total_end = total_end_new

# Create the TimestampedGeoJson plugin
folium.plugins.TimestampedGeoJson(
    {
        "type": "FeatureCollection",
        "features": features,
    },
    period = "PT30S",
    add_last_point = False,
    loop  = False,
).add_to(m)

total_distance_d /= 1000
total_distance_drone /= 1000
total_distance_d_2 /= 1000

# Distance snow removal
print(f"Distance totale parcourue par le drone en km: {total_distance_drone}")
print(f"Distance totale parcourue par les deneigeuses de type 1 en km: {total_distance_d}")
print(f"Distance totale parcourue par les deneigeuses de type 2 en km: {total_distance_d_2}")
print(f"Distance totale parcourue par les deneigeuses en km: {total_distance_d + total_distance_d_2}")

if(not DRONE_ACTIVE):
    if city[3:] == "Rivière-des-prairies-pointe-aux-trembles":
        file_name = f"/RPPT-animation.html"
    elif city[3:] == "Le-Plateau-Mont-Royal":
        file_name = f"/LPMR-animation.html"
    else:
        file_name = f"/{city[3:]}-animation.html"
else:
    file_name = f"/animation.html"
# Save the map to an HTML file
if DRONE_ACTIVE:
    m.save("../ERO1/public" + file_name)
    m.save(file_dir + file_name)
else:
    m.save(file_dir + file_name)
    m.save("../ERO1/public"+file_name)

device = "drone" if DRONE_ACTIVE else "deneigeuses"
print("date_str -> " + date_str)
print("total end = " + total_end)
# print("Temps pour déneiger:", space_between_dates(date_str, total_end))
print("Temps de parcours du " + device + ": ", space_between_dates(date_str, total_end))
print("Temps de parcours du " + device + " en secondes: ", space_between_dates(date_str, total_end).total_seconds())

# give the distance for desnowing
# give distance for the drone
# give the number of type 1 and type 2 snowplows
# give the time in millisecond
# give the name for scenario

# region data prep for front end
# Time for each city in seconds
TIME_DRONE_OUTREMONT, DISTANCE_DRONE_OUTREMONT = 2930, 114
TIME_DRONE_VERDUN, DISTANCE_DRONE_VERDUN = 4288, 166
TIME_DRONE_ANJOU, DISTANCE_DRONE_ANJOU = 10914, 417
TIME_DRONE_LE_PLATEAU, DISTANCE_DRONE_LE_PLATEAU = 7997, 307
TIME_DRONE_LA_RIVIERE = 8 * 3600 + 32 * 60, 1085

def generate_simulation_json(snowplows1, snowplows2, snowplows3,distance_deneigeuse1, distance_deneigeuse2, distance_drone, duration, duration_drone, filepath):
    """
    @brief:
        Generate a JSON object for the current simulation with the specified parameters and save it to a file.

    @param:
        snowplows1: Number of type 1 snowplows.
        snowplows2: Number of type 2 snowplows.
        distance_deneigeuse1: Distance covered by type 1 snowplows.
        distance_deneigeuse2: Distance covered by type 2 snowplows.
        distance_drone: Distance covered by the drone.
        duration: Duration of the snowplow operation.
        duration_drone: Duration of the drone operation.
        filepath: Path where the JSON file will be saved.

    @return:
        None. The JSON object is saved to the specified file.
    """
    duration_seconds = int(duration.total_seconds())
    duration_drone_seconds = int(duration_drone.total_seconds())
    simulation_data = {
        "pricingPlans": [
            {
                "name": "TYPE I",
                "snowplows1": snowplows1[0],
                "snowplows2": snowplows1[1],
                "distance_deneigeuse1": distance_deneigeuse1,
                "distance_deneigeuse2": distance_deneigeuse2,
                "distance_drone": distance_drone,
                "duration": duration_seconds,
                "duration_drone": duration_drone_seconds
            },
            {
                "name": "TYPE II",
                "snowplows1": snowplows2[0],
                "snowplows2": snowplows2[1],
                "distance_deneigeuse1": distance_deneigeuse1,
                "distance_deneigeuse2": distance_deneigeuse2,
                "distance_drone": distance_drone,
                "duration": duration_seconds // 2,
                "duration_drone": duration_drone_seconds
            },
            {
                "name": "TYPE I et II",
                "snowplows1": snowplows3[0],
                "snowplows2": snowplows3[1],
                "distance_deneigeuse1": distance_deneigeuse1,
                "distance_deneigeuse2": distance_deneigeuse2,
                "distance_drone": distance_drone,
                "duration": duration_seconds // 2,
                "duration_drone": duration_drone_seconds
            }
        ]
    }

    with open(filepath, 'w') as json_file:
        json.dump(simulation_data, json_file, indent=2)

scenario1 = scenario_array[0][city_selector]
scenario2 = scenario_array[1][city_selector]
scenario3 = scenario_array[2][city_selector]

snowplows1 = scenario1
snowplows2 = scenario2
snowplows3 = scenario3

distance_deneigeuse1 = total_distance_d
distance_deneigeuse2 = total_distance_d_2

distance_drone = total_distance_drone
duration = space_between_dates(date_str, total_end)
duration_drone = space_between_dates(date_str, total_end)

file_path = "../ERO1/public/"+city[3:]+".json"
generate_simulation_json(snowplows1,snowplows2,snowplows3,distance_deneigeuse1,distance_deneigeuse2,distance_drone,duration,duration_drone,file_path)
print(Fore.GREEN + f"JSON file saved to {file_path}")
# end region