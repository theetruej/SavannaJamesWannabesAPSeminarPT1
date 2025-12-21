import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import math
#Load API Key
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
#Load Json Data from EIA API
response = requests.get(f"https://api.eia.gov/v2/international/data/?api_key={pullAPIKEY()}&frequency=annual&data[0]=value&facets[countryRegionId][]=USA&facets[unit][]=MMTCD&facets[productId][]=4008&facets[activityId][]=8&start=1949&end=2025&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000")
JSONdata = response.json()

data = JSONdata['response']['data']
df = pd.DataFrame(columns=["Year", "US CO2 Emissions"])
i = 0
while i < len(data):
    
    year = float(data[i]['period'])
    us_emissions = float(data[i]['value'])
    df = pd.concat([df, pd.DataFrame([[year,us_emissions]],columns=df.columns)],ignore_index= True)
    i += 1

#Graphing US CO2 Emissions
mpl.rcParams["font.size"] = 5

yticks = np.arange(math.floor(df["US CO2 Emissions"].min()), math.ceil(df["US CO2 Emissions"].max()), 500)
plt.plot(df["Year"], df["US CO2 Emissions"])
plt.xlabel("Year")
plt.ylabel("US CO2 Emissions (MMTCD)")
plt.title("US CO2 Emissions Over Time")
plt.xticks(df["Year"][::3])
plt.legend()
plt.show()