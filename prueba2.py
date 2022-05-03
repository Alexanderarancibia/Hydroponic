import json
from datetime import datetime,date, time, timedelta
# Opening JSON file
f = open('parametros.json')
data = json.load(f)
print((data["Parametros_EC"][0])["Semana6_EC"][1])
