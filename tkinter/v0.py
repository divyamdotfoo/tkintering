import json
import customtkinter
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("./theme.json")

app=customtkinter.CTk()
app.columnconfigure(0,weight=1)
app.title("V0")
appGlobals={
    "pageWidgets":[],
    "lastIndex":7,
    "db":[],
    "currentWidgets":[],
    "comparisons":[]
}



customtkinter.CTkLabel(text="V0.dev/",master=app,width=100,font=customtkinter.CTkFont(size=32,underline=True,weight="bold")).grid(row=0,column=0,pady=10,sticky="w",padx=30)
notification=customtkinter.CTkLabel(text="",master=app)
notification.grid(row=0,column=0,padx=50,pady=10)
def notify(txt):
    notification.configure(text=txt)
    app.after(7500,lambda:notification.configure(text=""))

def changePage():
    if len(appGlobals["pageWidgets"]):
        for z in appGlobals["pageWidgets"]:
            z.destroy()

def addToCompare(data):
    isIn=False
    for z in appGlobals["comparisons"]:
        if data["sym"]==z["sym"]:
            isIn=True
    if len(appGlobals["comparisons"])>4:
        appGlobals["comparisons"]=appGlobals["comparisons"][0:3]
        appGlobals["comparisons"].append(data)
        notify(f"Item added: {data["name"]} added to the comparison tab.")
        return
    if isIn:
        notify(f"Item exist: {data["name"]} is already there!")
    appGlobals["comparisons"].append(data)
    notify(f"Notification : {data["name"]} added to the comparison tab.")




def StockInfo(stockInfoFrame):
    headers=["Open","High","Low","Close","Options"]
    headerFont=customtkinter.CTkFont(size=22,weight="bold")
    sno=customtkinter.CTkLabel(text="Sno",font=headerFont,master=stockInfoFrame,fg_color="#6d28d9")
    sno.grid(row=0,column=0,ipady=5,ipadx=30)
    name=customtkinter.CTkLabel(text="Name",font=headerFont,master=stockInfoFrame,fg_color="#6d28d9")
    name.grid(row=0,column=1,ipady=5,sticky="ew")
    for i,header in enumerate(headers):
        txt=customtkinter.CTkLabel(text=header,font=headerFont,master=stockInfoFrame,fg_color="#6d28d9")
        txt.grid(row=0,column=i+2,ipady=5,ipadx=50)
    Listings(appGlobals["lastIndex"]-7,stockInfoFrame)

    
def Listings(startIndex,frame):
    for row,item in enumerate(appGlobals["db"][startIndex:min(startIndex+8,len(appGlobals["db"]))]):
        row+=1
        sno=customtkinter.CTkLabel(text=startIndex+row,master=frame,font=customtkinter.CTkFont(size=14,weight="bold"),text_color="#6d28d9")
        sno.grid(row=row,column=0,pady=15)
        name=customtkinter.CTkLabel(master=frame,text=item["name"][0:30],font=customtkinter.CTkFont(size=16,weight="bold"))
        name.grid(row=row,column=1,pady=15,sticky="w")
        today=item["prices"][0]
        for col,value in enumerate(list(today.values())[0:4]):
            label=customtkinter.CTkLabel(master=frame,text="$"+" "+str(round(float(value),2)),font=customtkinter.CTkFont(size=16))
            appGlobals["currentWidgets"].append(label)
            label.grid(row=row,column=col+2,pady=15)
        btnFrame=customtkinter.CTkFrame(fg_color=None,master=frame)
        btnFrame.grid(row=row,column=6)
        viewBtn=customtkinter.CTkButton(master=btnFrame,width=20,text="view",command=lambda prices=item["prices"], dates=item["dates"],name=item["name"]: ViewPage(prices, dates,name))
        viewBtn.grid(row=0,column=0,padx=5)
        addBtn=customtkinter.CTkButton(master=btnFrame,width=20,text="Add",command=lambda data=item:addToCompare(data))
        addBtn.grid(row=0,column=1,padx=5)
        appGlobals["currentWidgets"].extend([sno,name,viewBtn,addBtn])
        



def HomePage():
    changePage()
    appGlobals["comparisons"].clear()
    comparisonPageBtn=customtkinter.CTkButton(master=app,text="Comparison view",command=ComparisonPage)
    comparisonPageBtn.grid(row=0,column=1,pady=10,sticky="ew",padx=30)
    appGlobals["pageWidgets"].append(comparisonPageBtn)
    stockInfoFrame=customtkinter.CTkFrame(master=app)
    stockInfoFrame.grid(row=1,column=0,padx=60,pady=15,columnspan=3)
    appGlobals["pageWidgets"].append(stockInfoFrame)
    StockInfo(stockInfoFrame)
    Navigation(stockInfoFrame)



def ViewPage(prices,dates,name):
    changePage()
    homePageBtn=customtkinter.CTkButton(master=app,text="Home",command=HomePage)
    homePageBtn.grid(row=0,column=1,pady=10,sticky="ew",padx=30)
    appGlobals["pageWidgets"].append(homePageBtn)
    renderGraphs(prices,dates,name)


def ComparisonPage():
    changePage()
    homePageBtn=customtkinter.CTkButton(master=app,text="Home",command=HomePage)
    homePageBtn.grid(row=0,column=1,pady=10,sticky="ew",padx=30)
    appGlobals["pageWidgets"].append(homePageBtn)
    renderComparisons()
    

def getData():
    f=open("template.json","r")
    data=json.load(f)
    appGlobals["db"].extend(data)
    f.close()

def getOverTime(prices,dates):
    x = np.asarray(dates, dtype='datetime64[s]')
    y=np.array([round(float(z["4. close"]),2) for z in prices])
    return [x,y]


def calculateVolatility(prices, window_size=10):
    daily_returns = (np.diff(prices) / prices[:-1]) * 100
    rolling_volatility = np.full_like(prices, np.nan)

    for i in range(window_size, len(prices)):
        window_returns = daily_returns[i - window_size + 1 : i + 1]
        window_volatility = np.std(window_returns)
        rolling_volatility[i] = window_volatility

    return rolling_volatility


def calculateEma(npPrices):
    ema = [npPrices[0]]
    for i in range(1, npPrices.shape[0]):
        ema_value = 0.2 * npPrices[i] + (1 - 0.2) * ema[i-1]
        ema.append(ema_value)
    return np.array(ema)


def renderGraphs(prices,dates,name):
    title=customtkinter.CTkLabel(master=app,text="Performance of "+name,font=customtkinter.CTkFont(size=18,weight="bold"))
    title.grid(row=0,column=0,padx=50,pady=10)
    appGlobals["pageWidgets"].append(title)
    graphFrame=customtkinter.CTkFrame(master=app)
    graphFrame.grid(row=1,column=0,pady=30,columnspan=3)
    appGlobals["pageWidgets"].append(graphFrame)
    fig,ax=plt.subplots(ncols=2,nrows=2,figsize=(15,7))
    plt.subplots_adjust(hspace=0.6)
    plt.subplots_adjust(wspace=0.2)
    npDates,npPrices=getOverTime(prices,dates)
    ax[0,0].plot(npDates,npPrices,"#6d28d9")
    ax[0,0].tick_params(axis='x', labelrotation=45)
    ax[0,0].set_title("Last 100 days")
    ax[0,0].set_ylabel("In dollars")
    volatility=calculateVolatility(npPrices)
    ax[1,0].plot(npDates,volatility,"#6d28d9")
    ax[1,0].tick_params(axis='x', labelrotation=45)
    ax[1,0].set_title("Volatility analysis")
    volume=np.array([round(float(z["5. volume"])/1000000) for z in prices])
    ax[0,1].plot(npDates,volume,"#6d28d9")
    ax[0,1].tick_params(axis='x', labelrotation=45)
    ax[0,1].set_title("Volume analysis")
    ax[0,1].set_ylabel("In Millions")
    ax[1,1].plot(npDates,calculateEma(npPrices),"#6d28d9")
    ax[1,1].tick_params(axis='x', labelrotation=45)
    ax[1,1].set_title("Exponential moving average analysis")
    canvas = FigureCanvasTkAgg(fig, master=graphFrame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()


def renderComparisons():
    data=appGlobals["comparisons"]
    if not len(data):
        label=customtkinter.CTkLabel(master=app,text="Add some stocks in the comparison view to compare.",font=customtkinter.CTkFont(size=22,weight="bold"))
        label.grid(row=1,column=0,columnspan=3,pady=50)
        appGlobals["pageWidgets"].append(label)
        return
    npDates=np.asarray(data[0]["dates"],dtype='datetime64[s]')
    names=[z["name"] for z in data]
    prices=[]
    volumes=[]
    volatility=[]
    ema=[]
    for item in data:
        prices.append(np.array([round(float(z["4. close"]),2) for z in item["prices"]]))
        volumes.append(np.array([round(float(z["5. volume"])/1000000) for z in item["prices"]]))
        volatility.append(calculateVolatility(np.array([round(float(z["4. close"]),2) for z in item["prices"]])))
        ema.append(calculateEma(np.array([round(float(z["4. close"]),2) for z in item["prices"]])))
    

    graphFrame=customtkinter.CTkFrame(master=app)
    graphFrame.grid(row=1,column=0,pady=30,columnspan=3)
    appGlobals["pageWidgets"].append(graphFrame)
    fig,ax=plt.subplots(ncols=2,nrows=2,figsize=(15,7))
    plt.subplots_adjust(hspace=0.6)
    plt.subplots_adjust(wspace=0.2)

    for price,name in zip(prices,names):
        ax[0,0].plot(npDates,price,label=f"{name}")
    ax[0,0].set_ylabel("In dollars")
    ax[0,0].set_title("Last 100 days")
    ax[0,0].tick_params(axis='x', labelrotation=45)
    for volume,name in zip(volumes,names):
        ax[0,1].plot(npDates,volume)
    ax[0,1].tick_params(axis='x', labelrotation=45)
    ax[0,1].set_title("Volume analysis")
    ax[0,1].set_ylabel("In Millions")
    for v,name in zip(volatility,names):
        ax[1,0].plot(npDates,v)
    ax[1,0].tick_params(axis='x', labelrotation=45)
    ax[1,0].set_title("Volatility analysis")
    for e,name in zip(ema,names):
        ax[1,1].plot(npDates,e)
    ax[1,1].tick_params(axis='x', labelrotation=45)
    ax[1,1].set_title("Exponential moving average analysis")
    fig.legend()
    canvas = FigureCanvasTkAgg(fig, master=graphFrame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()
    

def Navigation(stockInfoFrame):
    def nPage():
        print("before",appGlobals["lastIndex"])
        if(appGlobals["lastIndex"]>=len(appGlobals["db"])-1):
            return
        for z in appGlobals["currentWidgets"]:
            z.destroy()
        appGlobals["lastIndex"]=min(appGlobals["lastIndex"]+7,len(appGlobals["db"])-1)
        Listings(appGlobals["lastIndex"]-7,stockInfoFrame)
        print("after",appGlobals["lastIndex"])

        return
    
    def pPage():
        print("before",appGlobals["lastIndex"])
        if(appGlobals["lastIndex"]<=7):
            return
        for z in appGlobals["currentWidgets"]:
            z.destroy()
        appGlobals["lastIndex"]=max(7,appGlobals["lastIndex"]-7)
        Listings(appGlobals["lastIndex"]-7,stockInfoFrame)
        print("after",appGlobals["lastIndex"])

        return
        
           
    f=customtkinter.CTkFrame(master=app,fg_color=None)
    prev=customtkinter.CTkButton(text="<",master=f,font=customtkinter.CTkFont(size=20,weight="bold"),width=20,command=pPage)
    prev.grid(row=0,column=1,padx=5)
    next=customtkinter.CTkButton(text=">",master=f,font=customtkinter.CTkFont(size=20,weight="bold"),width=20,command=nPage)
    next.grid(row=0,column=2,padx=5)
    f.grid(row=2,column=0,pady=(0,20),columnspan=3)
    appGlobals["pageWidgets"].append(f)

def main():
    getData()
    print(len(appGlobals["db"]))
    HomePage()
    app.mainloop()

main()
