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
emissionResponse = requests.get(f"https://api.eia.gov/v2/international/data/?api_key={pullAPIKEY()}&frequency=annual&data[0]=value&facets[countryRegionId][]=USA&facets[productId][]=4411&facets[productId][]=4413&facets[productId][]=4415&facets[productId][]=4417&facets[productId][]=4418&facets[activityId][]=2&start=1949&end=2025&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000")
raw_content = emissionResponse.json()
while isinstance(raw_content,str):
    try:
        raw_content = ast.literal_eval(raw_content)
    except (ValueError, SyntaxError):
        print("Decoding JSON has failed")
        break
consumptionData = raw_content['response']['data']
cache_dict = {
    4413: [0,0,"Natural Gas"],
    4411: [0,0, "Coal"],
    4415: [0,0, "Petroleum and other liquids"],
    4417: [0,0, "Nuclear"],
    4418: [0,0, "Renewables / Miscellaneous"],
}
for entry in consumptionData:
    product_id = entry['productId']
    if int(entry['period']) >= 2003:
        if int(product_id) in cache_dict:
            cache_dict[int(product_id)][1] += float(entry['value'])
            cache_dict[int(product_id)][0] += 1
        else:
            print(f"Unexpected productId: {product_id}")
    


averages = [round((cache_dict[4413][1]/cache_dict[4413][0]), 2), round((cache_dict[4411][1]/cache_dict[4411][0]), 2), round((cache_dict[4415][1]/cache_dict[4415][0]), 2), round((cache_dict[4417][1]/cache_dict[4417][0]), 2), round((cache_dict[4418][1]/cache_dict[4418][0]), 2  )]
print(averages)

plt.pie(averages, labels=[cache_dict[4413][2], cache_dict[4411][2], cache_dict[4415][2], cache_dict[4417][2], cache_dict[4418][2]], autopct='%1.1f%%', startangle=140)
plt.title("Average U.S. Energy Consumption by Source (2003-2023)", pad=20)
plt.axis('equal')
mpl.rcParams['font.size'] = 12
plt.show()