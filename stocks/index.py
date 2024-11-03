import numpy as np
import customtkinter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json

customtkinter.set_appearance_mode("System") 
customtkinter.set_default_color_theme("blue")
tableHeaders=["Name","Symbol","Open","High","Low","Close"]
lastIndex=0
db=[]
currentWidgets=[]
graphWidgets=[]
comparisonData=[]

app = customtkinter.CTk()
app.title("Stocks and stuff")
tableFrame=customtkinter.CTkFrame(master=app)
paginationFrame=customtkinter.CTkFrame(master=app)

def renderParents():
    tableFrame.grid(row=0,column=0,pady=10,padx=(5,20))
    paginationFrame.grid(row=1,column=0)
    return


def renderLables():
    def createLabel(row,col,headerText):
        label=customtkinter.CTkLabel(master=tableFrame,text=headerText,fg_color="#3A7EBF",width=64,corner_radius=6)
        label.grid(row=row,column=col,pady=10,padx=5)

    for i,header in enumerate(tableHeaders):
        createLabel(0,i,header)
       
def viewGraph(prices,dates,name):
    for widget in graphWidgets:
        widget.destroy()
    y=[]
    y.extend([round(float(z["1. open"]),2) for z in prices])
    x = np.asarray(dates, dtype='datetime64[s]')
    tempFrame=customtkinter.CTkFrame(master=app) 
    tempFrame.grid(row=0,column=1,padx=10,pady=30)
    graphWidgets.append(tempFrame)
    fig,ax=plt.subplots(ncols=1,nrows=2,figsize=(6,7))
    plt.subplots_adjust(hspace=0.5)
    ax[0].plot(x,np.array(y))
    ax[0].tick_params(axis='x', labelrotation=45)
    ax[0].set_title("Last 100 days for "+name)
    ax[0].set_ylabel("In dollars")
    ax[1].bar(x[0:6],np.array(y)[0:6])
    ax[1].tick_params(axis='x', labelrotation=45)
    ax[1].set_title("Last 7 days for "+name)
    ax[1].set_ylabel("In dollars")
    canvas = FigureCanvasTkAgg(fig, master=tempFrame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack() 

def getData():
    f=open("template.json","r")
    data=json.load(f)
    db.extend(data)
    f.close()


def addToCompare(data):
    if(len(comparisonData)>4):
        return
    comparisonData.append(data)


def compareGraph():
    global comparisonData
    if(len(comparisonData)<=0):
        return
    for widget in graphWidgets:
        widget.destroy()
    compareFrame=customtkinter.CTkFrame(master=app)
    compareFrame.grid(row=0,column=1,padx=10,pady=30)
    graphWidgets.append(compareFrame)
    x = np.asarray(comparisonData[0]["dates"], dtype='datetime64[s]')
    names=[z["name"] for z in comparisonData]
    print(x[0:3])
    prices=[]
    fig,ax=plt.subplots(figsize=(7,7))
    ax.set_ylabel("In dollars")
    ax.set_xlabel("Last 100 days")
    for data in comparisonData:
        y=[round(float(z["1. open"]),2) for z in data["prices"]]
        prices.append(y)
        print(y[0:2])

    for price,name in zip(prices,names):
        ax.plot(x, price, label=f"{name}")
    ax.legend()
    canvas = FigureCanvasTkAgg(fig, master=compareFrame)
    canvas_widget = canvas.get_tk_widget()
    canvas_widget.pack()
    comparisonData.clear()

# name,sym,prices,dates

def renderData(startIndex):
    global lastIndex
    lastIndex=min(startIndex+10,len(db)-1) 
    row=startIndex+1
    for i,item in enumerate(db):
        if(i>=startIndex and i<startIndex+11 and item):
            name=customtkinter.CTkLabel(master=tableFrame,text=item["name"][0:30])
            currentWidgets.append(name)
            name.grid(row=row,column=0,padx=5,pady=10)
            symbol=customtkinter.CTkLabel(master=tableFrame,text=item["sym"])
            currentWidgets.append(symbol)
            symbol.grid(row=row,column=1,padx=5,pady=10)
            today=item["prices"][0]
            col=2
            for value in today.values():
                if(col<6):
                    label=customtkinter.CTkLabel(master=tableFrame,text="$"+" "+str(round(float(value),2)))
                    currentWidgets.append(label)
                    label.grid(row=row,column=col,padx=5,pady=10)
                col+=1
            graphViewBtn=customtkinter.CTkButton(master=tableFrame,text="view",command=lambda prices=item["prices"], dates=item["dates"],name=item["name"]: viewGraph(prices, dates,name),width=56)
            currentWidgets.append(graphViewBtn)
            graphViewBtn.grid(row=row,column=col,padx=10,pady=10)
            compareBtn=customtkinter.CTkButton(master=tableFrame,text="select",width=56,command=lambda data=item:addToCompare(data))
            compareBtn.grid(row=row,column=col+1,padx=10,pady=10)
            currentWidgets.append(compareBtn)
            row+=1  


        

def destroyWidgets():
    if len(currentWidgets)>0:
        for i in currentWidgets:
            i.destroy()
        currentWidgets.clear()
    if len(graphWidgets)>0:
        for w in graphWidgets:
            w.destroy()
        graphWidgets.clear()


def nextPage():
    global lastIndex
    if(lastIndex<len(db)-1):
        destroyWidgets()
        renderData(lastIndex+1)


def prevPage():
    global lastIndex
    destroyWidgets()
    renderData(max(0,lastIndex-10))

def renderPagination():
        prev=customtkinter.CTkButton(master=paginationFrame,text="previous",command=prevPage,width=56)
        prev.grid(row=0,column=5,padx=20,pady=10)
        next=customtkinter.CTkButton(master=paginationFrame,text="next",command=nextPage,width=56)
        next.grid(row=0,column=6,padx=20,pady=10)
        compare=customtkinter.CTkButton(master=paginationFrame,text="compare",command=compareGraph)
        compare.grid(row=0,column=7,padx=20,pady=10)


def main():
    getData()
    renderParents()
    renderLables()
    renderData(0)
    renderPagination()
    app.mainloop()


main()