import customtkinter
import openmeteo_requests
import requests_cache
from retry_requests import retry
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import tkintermapview
import matplotlib.dates as mdates


customtkinter.set_default_color_theme("green")
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
app=customtkinter.CTk(fg_color="gray14")
app.geometry("1100x550")
app.title("Ask Pam")
searchFrame=customtkinter.CTkFrame(master=app)
input=customtkinter.CTkEntry(master=searchFrame,width=300,corner_radius=12)
input.grid(row=0,column=0,padx=10,pady=20)

mapView=tkintermapview.TkinterMapView(app,width=600,height=480,corner_radius=12)
mapView.grid(row=1,column=0)

def getLatLang(value:str):
    if(not value):
        return
    url="https://geocoding-api.open-meteo.com/v1/search"
    params={
        "name":value
    }
    res=requests.get(url=url,params=params)
    if(not res):
        print("something went wrong")
        return
    data=res.json()["results"][0]
    return [data["latitude"],data["longitude"],data["country"]]


def getWeather(lat,long):
    url = "https://api.open-meteo.com/v1/forecast"
    params={
        "latitude":lat,
        "longitude":long,
        "hourly":["temperature_2m"],
        "current":["temperature_2m","relative_humidity_2m","is_day","precipitation","wind_speed_10m"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "sunrise", "sunset"],
        "timezone":"auto"
    }
    data=openmeteo.weather_api(url=url,params=params)[0]
    weather={
        "current":{},
        "daily":{},
        "hourly":{}
    }
    for i,x in enumerate(params["current"]):
       weather["current"][x]=data.Current().Variables(i).Value()
    for i,x in enumerate(params["daily"]):
        weather["daily"][x]=data.Daily().Variables(i).ValuesAsNumpy()
    for i,x in enumerate(params["hourly"]):
        weather["hourly"]["temp"]=data.Hourly().Variables(i).ValuesAsNumpy()
        tStart=np.datetime64(data.Hourly().Time(),"s")
        tEnd=np.datetime64(data.Hourly().TimeEnd(),"s")
        interval=np.timedelta64(data.Hourly().Interval())
        weather["hourly"]["date"]=np.arange(tStart,tEnd,interval)
    return weather

def getAir(lat,long):
    url = "https://air-quality-api.open-meteo.com/v1/air-quality"
    params = {
        "latitude": lat,
        "longitude": long,
        "hourly": ["pm10", "pm2_5", "carbon_monoxide","uv_index"],
        "current": ["european_aqi", "pm10", "pm2_5", "carbon_monoxide"],
        "forecast_days": 3
    }
    data=openmeteo.weather_api(url=url,params=params)[0]
    air={
        "current":{},
        "hourly":{}
    }
    for i,x in enumerate(params["current"]):
        air["current"][x]=data.Current().Variables(i).Value()
    for i,x in enumerate(params["hourly"]):
        air["hourly"][x]=data.Hourly().Variables(i).ValuesAsNumpy()
    tStart=np.datetime64(data.Hourly().Time(),"s")
    tEnd=np.datetime64(data.Hourly().TimeEnd(),"s")
    interval=np.timedelta64(data.Hourly().Interval())
    air["hourly"]["date"]=np.arange(tStart,tEnd,interval)
    return air


def getData(text="Paris"):
    value=input.get()
    if not value:
        value=text
    searchBtn.configure(text="Loading...")
    app.update_idletasks()
    lat,long,country=getLatLang(value)
    if(not lat or not long):
        return
    weather=getWeather(lat,long)
    air=getAir(lat,long)
    info={
        "name":value or "Paris",
        "country":country,
        "lat":lat,
        "long":long,
        "weather":weather,
        "air":air,
    }
    input.delete(0,len(value))
    searchBtn.configure(text="Search 🔎")
    app.update_idletasks()
    return info

def showGraph(info):
    tempFrame=customtkinter.CTkFrame(master=app) 
    tempFrame.grid(row=0,column=1,padx=10,pady=30,rowspan=2,columnspan=2)
    fig,ax=plt.subplots(ncols=2,nrows=2,figsize=(11,9))
    plt.subplots_adjust(hspace=0.4)
    temp=info["weather"]["hourly"]["temp"]
    dates=info["weather"]["hourly"]["date"]
    pm2=info["air"]["hourly"]["pm2_5"]
    pm10=info["air"]["hourly"]["pm10"]
    co=info["air"]["hourly"]["carbon_monoxide"]
    uv=info["air"]["hourly"]["uv_index"]
    date2=info["air"]["hourly"]["date"]
    locator=mdates.AutoDateLocator()
    formatter=mdates.ConciseDateFormatter(locator)
    ax[0,0].plot(dates,temp,"r")
    ax[0,0].set_ylabel("In celsius")
    ax[0,0].set_title("Temperature projections")
    ax[0,0].xaxis.set_major_formatter(formatter)
    ax[1,0].plot(date2,pm2,"r",label="PM2.5")
    ax[1,0].plot(date2,pm10,"b",label="PM10")
    ax[1,0].set_ylabel("In milligrams/meter cube")
    ax[1,0].set_title("PM2.5 & PM10 projections")
    ax[1,0].legend()
    ax[1,0].xaxis.set_major_formatter(formatter)
    ax[0,1].plot(date2,co,"b",label="Carbon monoxide")
    ax[0,1].set_ylabel("In milligrams/meter cube")
    ax[0,1].set_title("Carbon monoxide projections")
    ax[0,1].legend()
    ax[0,1].xaxis.set_major_formatter(formatter)
    ax[1,1].plot(date2,uv,"b",label="UV")
    ax[1,1].set_title("UV index projections")
    ax[1,1].legend()
    ax[1,1].xaxis.set_major_formatter(formatter)


    
   
    canvas = FigureCanvasTkAgg(fig, master=tempFrame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack() 

# loads of shit
currentWidgets=[]
def renderData():
    info=getData()
    if not info:
        return
    showGraph(info)
    global mapView
    mapView.set_position(info["lat"],info["long"])
    mapView.set_marker(info["lat"],info["long"],info["name"])
    mapView.set_zoom(13)
    normal=("Roboto",18,"normal")
    bold=("Roboto",20,"bold")
    for z in currentWidgets:
        if(z):
            z.destroy()
    infoFrame=customtkinter.CTkFrame(master=searchFrame,fg_color="gray17")
    infoFrame.grid_rowconfigure(0,weight=1)
    location=customtkinter.CTkLabel(master=infoFrame,text="Location :",font=bold)
    location.grid(row=0,column=0,pady=5)
    currentWidgets.append(location)
    name=customtkinter.CTkLabel(text=info["name"].capitalize(),master=infoFrame,font=normal)
    name.grid(row=0,column=1,padx=(0,30),pady=5)
    currentWidgets.append(name)
    country=customtkinter.CTkLabel(text="Country : ",master=infoFrame,font=bold)
    country.grid(row=0,column=2,pady=5)
    currentWidgets.append(country)
    countryName=customtkinter.CTkLabel(text=info["country"],master=infoFrame,font=normal)
    countryName.grid(row=0,column=3,pady=5)
    currentWidgets.append(countryName)
    temp=customtkinter.CTkLabel(text="Temp :",master=infoFrame,font=bold)
    temp.grid(row=1,column=0,pady=5)
    currentWidgets.append(temp)
    tempValue=customtkinter.CTkLabel(master=infoFrame,text=f"{round(info["weather"]["current"]["temperature_2m"],1)}C",font=normal)
    tempValue.grid(row=1,column=1,padx=(0,30),pady=5)
    currentWidgets.append(tempValue)
    humidity=customtkinter.CTkLabel(text="Humidity :",master=infoFrame,font=bold)
    humidity.grid(row=1,column=2,pady=5)
    currentWidgets.append(humidity)
    humidityNumber=customtkinter.CTkLabel(master=infoFrame,text=f"{round(info["weather"]["current"]["relative_humidity_2m"],1)}%",font=normal)
    humidityNumber.grid(row=1,column=3,pady=5)
    currentWidgets.append(humidityNumber)
    windSpeed=customtkinter.CTkLabel(text="Wind :",master=infoFrame,font=bold)
    windSpeed.grid(row=2,column=0,pady=5)
    currentWidgets.append(windSpeed)
    windNumber=customtkinter.CTkLabel(master=infoFrame,text=f"{round(info["weather"]["current"]["wind_speed_10m"],1)}km/hr",font=normal)
    windNumber.grid(row=2,column=1,pady=5)
    currentWidgets.append(windNumber)
    aqi=customtkinter.CTkLabel(text="AQI :",master=infoFrame,font=bold)
    aqi.grid(row=2,column=2,pady=5)
    currentWidgets.append(aqi)
    aqiNumber=customtkinter.CTkLabel(master=infoFrame,text=f"{round(info["air"]["current"]["european_aqi"],1)}",font=normal)
    aqiNumber.grid(row=2,column=3,pady=5)
    currentWidgets.append(aqiNumber)
    pm2=customtkinter.CTkLabel(text="PM 2.5 :",master=infoFrame,font=bold)
    pm2.grid(row=3,column=0,pady=5)
    currentWidgets.append(pm2)
    pm2Number=customtkinter.CTkLabel(master=infoFrame,text=f"{round(info["air"]["current"]["pm2_5"],1)}",font=normal)
    pm2Number.grid(row=3,column=1,pady=5)
    currentWidgets.append(pm2Number)
    pm10=customtkinter.CTkLabel(text="PM 10 :",master=infoFrame,font=bold)
    pm10.grid(row=3,column=2,pady=5)
    currentWidgets.append(pm10)
    pm10Number=customtkinter.CTkLabel(master=infoFrame,text=f"{round(info["air"]["current"]["pm10"],1)}",font=normal)
    pm10Number.grid(row=3,column=3,pady=5)
    currentWidgets.append(pm10Number)
    infoFrame.grid(row=1,column=0,padx=10,pady=10,columnspan=2)    



searchBtn=customtkinter.CTkButton(master=searchFrame,corner_radius=12,text="Search",command=renderData,width=56)
searchBtn.grid(row=0,column=1,pady=20,padx=10)
searchFrame.grid(row=0,column=0,padx=30,pady=(20,0))
def main():
    renderData()
    app.mainloop()

main()
