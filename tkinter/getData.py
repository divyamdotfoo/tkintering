import requests
import math
import numpy as np
import json
url = "https://alpha-vantage.p.rapidapi.com/query"
apiKeyNumber=0
apiKeys=['373ab60297msh8fba4a196229134p1481acjsn2e8a1390dfc1','befd1e42c5mshd6c5752dff71197p19e9f7jsn3a15dd034632','f2acfd7a7amsh5cbd4417d278c86p178c46jsn9599c82d225a','a5dec7ce03mshe0e5c71fd67a71ep1c46ebjsn777ac00b939a','542881abdfmsh79a37ac7ef81656p1409ecjsn98f487ce5b5e']
def headers():
    global apiKeyNumber
    header= {
	"X-RapidAPI-Key": apiKeys[apiKeyNumber],
	"X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"
}
    apiKeyNumber=math.floor((apiKeyNumber+1)%5)
    return header
db=[]
stockListings = [
  { "name": 'Adobe Inc.', "symbol": 'ADBE' },
  { "name": 'Nike Inc.', "symbol": 'NKE' },
  { "name": 'McDonald Corporation', "symbol": 'MCD' },
  { "name": 'International Business Machines Corporation', "symbol": 'IBM' },
  { "name": 'Uber Technologies Inc.', "symbol": 'UBER' },
  { "name": 'Apple Inc.', "symbol": 'AAPL' },
  { "name": 'Meta Platforms, Inc.', "symbol": 'META' },
  { "name": 'Netflix, Inc.', "symbol": 'NFLX' },
  { "name": 'Verizon Communications Inc.', "symbol": 'VZ' },
  { "name": 'NVIDIA Corporation', "symbol": 'NVDA' },
  { "name": 'Caterpillar Inc.', "symbol": 'CAT' },
  { "name": 'PayPal Holdings, Inc.', "symbol": 'PYPL' },
  { "name": 'United Parcel Service, Inc.', "symbol": 'UPS' },
  { "name": 'Alibaba Group Holding Limited', "symbol": 'BABA' },
  { "name": 'Tesla, Inc.', "symbol": 'TSLA' },
  { "name": 'Walgreens Boots Alliance, Inc.', "symbol": 'WBA' },
  { "name": 'Bank of America Corporation', "symbol": 'BAC' },
  { "name": 'Pfizer Inc.', "symbol": 'PFE' },
  { "name": 'Thermo Fisher Scientific Inc.', "symbol": 'TMO' },
  { "name": 'Chevron Corporation', "symbol": 'CVX' },
  { "name": 'Intuit Inc.', "symbol": 'INTU' },
  { "name": 'Vertex Pharmaceuticals Incorporated', "symbol": 'VRTX' },
  { "name": 'Advanced Micro Devices, Inc.', "symbol": 'AMD' },
  { "name": 'Zoom Video Communications, Inc.', "symbol": 'ZM' },
  { "name": 'Micron Technology, Inc.', "symbol": 'MU' },
  { "name": 'Goldman Sachs Group, Inc.', "symbol": 'GS' },
  { "name": 'Microsoft Corporation', "symbol": 'MSFT' },
  { "name": 'Cisco Systems, Inc.', "symbol": 'CSCO' },
  { "name": 'Automatic Data Processing, Inc.', "symbol": 'ADP' },
  { "name": 'Twitter, Inc.', "symbol": 'TWTR' },
]
for stock in stockListings:
    params={"function":"TIME_SERIES_DAILY","symbol":stock["symbol"],"outputsize":"","datatype":"json"}
    res=requests.get(url,headers=headers(),params=params)
    if(not res.ok):
        continue
    data=res.json()
    try:
        allData=list(dict(data).values())[1]
        prices=list(dict(allData).values())
        dates=list(dict(allData).keys())    
        db.append({
                    "name":stock["name"],
                    "sym":stock["symbol"],
                    "prices":prices,
                    "dates":dates
                })
    except(IndexError,KeyError):
        continue
    
f=open("template.json","w")
json.dump(db,f)
f.close()