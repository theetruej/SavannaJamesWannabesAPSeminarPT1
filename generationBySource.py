#
#Load API Key
import ast
import requests
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
API_dir = './.env.txt'


def pullAPIKEY():
    try:
        with open(API_dir, 'r') as file:
            Key = file.read().strip()
            return Key
    except FileNotFoundError:
        print(f"FileNotFoundError{API_dir}")
    except PermissionError:
        print(f"PermissionError{API_dir}")
#Load Json Data from EIA API into a DataFrame
emissionResponse = requests.get(f"https://api.eia.gov/v2/international/data/?api_key={pullAPIKEY()}&frequency=annual&data[0]=value&facets[countryRegionId][]=USA&facets[productId][]=116&facets[productId][]=30&facets[productId][]=31&facets[productId][]=33&facets[productId][]=35&facets[productId][]=37&facets[productId][]=54&facets[productId][]=4413&facets[productId][]=27&facets[activityId][]=12&facets[unit][]=BKWH&start=2005&end=2023&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000")
raw_content = emissionResponse.json()
while isinstance(raw_content,str):
    try:
        raw_content = ast.literal_eval(raw_content)
    except (ValueError, SyntaxError):
        print("Decoding JSON has failed")
        break
generationData = raw_content['response']['data']


cache_dict = {
    116: {
        "name": "Solar",
        "array": []
    },
    30: {
        "name": "Coal",
         "array": []
    },
    31: {
        "name": "Natural Gas",
         "array": []
    },
    33: {
        "name": "Hydroelectricity",
         "array": []
    },
    35: {
        "name": "Geothermal",
         "array": []
    },
    37: {
        "name": "Wind",
         "array": []
    },
    31: {
        "name": "Natural Gas",
         "array": []
    },
    27: {
        "name": "Nuclear",
         "array": []
    },

}

for entry in generationData:
    Id = int(entry["productId"])
    Period = int(entry["period"])
    if Id in cache_dict:
        cache_dict[Id]["array"].append(round(float(entry["value"]),2))
    



x_points = np.array(range(2006, 2024))
fig, ax = plt.subplots(figsize=(10, 6), layout='constrained') 


for value in cache_dict.values():
    ax.plot(x_points, value["array"], label=value["name"], linewidth=2) 


ax.set_title("U.S. Generation of Electricity by Source", fontsize=14, fontweight='bold') #
ax.set_xlabel("Year", fontsize=12)
ax.set_ylabel("Billion Kilowatthours (BKWH)", fontsize=12)


ax.legend(loc='upper left', bbox_to_anchor=(1, 1), frameon=False) 

ax.grid(True, linestyle='--', alpha=0.6) #


ax.spines[['top', 'right']].set_visible(False) #


ax.set_xticks(np.arange(2006, 2025, 2)) 

plt.show()

