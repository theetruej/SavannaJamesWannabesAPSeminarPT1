#Load API Key
import ast
import requests
import matplotlib.pyplot as plt
import matplotlib as mpl

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
emissionResponse = requests.get(f"https://api.eia.gov/v2/seds/data/?api_key={pullAPIKEY()}&frequency=annual&data[0]=value&facets[seriesId][]=FFACE&facets[seriesId][]=FFCCE&facets[seriesId][]=FFEIE&facets[seriesId][]=FFICE&facets[seriesId][]=FFRCE&start=2003&end=2023&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000")
raw_content = emissionResponse.json()
while isinstance(raw_content,str):
    try:
        raw_content = ast.literal_eval(raw_content)
    except (ValueError, SyntaxError):
        print("Decoding JSON has failed")
        break
emissionData = raw_content["response"]["data"]
print(emissionData)
cache_dict = {
    "FFACE": [0,0,"Transportation Sector"],
    "FFCCE": [0,0, "Commercial Sector"],
    "FFEIE": [0,0, "Electric Power"],
    "FFICE": [0,0, "Industrial Sector"],
    "FFRCE": [0,0, "Residential Sector"],
}
for entry in emissionData:
    sector = entry['seriesId']
    if sector in cache_dict:
        cache_dict[sector][1] += float(entry['value'])
        cache_dict[sector][0] += 1
    else:
        print(f"Unexpected productId: {sector}")
    


averages = [round((cache_dict["FFACE"][1]/cache_dict["FFACE"][0]), 2), round((cache_dict["FFCCE"][1]/cache_dict["FFCCE"][0]), 2), round((cache_dict["FFEIE"][1]/cache_dict["FFEIE"][0]), 2), round((cache_dict["FFICE"][1]/cache_dict["FFICE"][0]), 2), round((cache_dict["FFRCE"][1]/cache_dict["FFRCE"][0]), 2  )]
print(averages)

plt.pie(averages, labels=[cache_dict["FFACE"][2], cache_dict["FFCCE"][2], cache_dict["FFEIE"][2], cache_dict["FFICE"][2], cache_dict["FFRCE"][2]], autopct='%1.1f%%', startangle=140)
plt.title("Average U.S. CO2 Emission of Fossil Fuels by Sector (2003-2023)", pad=20)
plt.axis('equal')
mpl.rcParams['font.size'] = 12
plt.show()