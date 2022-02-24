from cmath import pi
from math import atan2,sin,cos,sqrt
import math
from pickle import NONE
import sqlite3
from flask import Flask, render_template,request

app = Flask(__name__)

def DbConnection():
    con = NONE
    try:
        con=sqlite3.connect("DataBase.db")
    except sqlite3.Error as e:
        print(e)
    return con


def GreatCirlceDistance(Lat1,Lat2,Long1,Long2):             #Also called haversine formula, used to calculate shortest distance
    Radius = 6371       #Radius of earth in km               between two points on surface of a rounded sphere
    Phi1 = Lat1 * pi/180
    Phi2 = Lat2 * pi/180
    DeltaPhi = (Lat2-Lat1) * pi/180
    DeltaLamda = (Long2-Long1) * pi/180
    a= sin(DeltaPhi/2)**2 + cos(Phi1)*cos(Phi2) * sin(DeltaLamda/2)**2
    c=2* atan2(sqrt(a),sqrt(1-a))
    return round(Radius * c,2)


def AllTablesInfo(cursor):
    TableNameWithColumnInfo=[]
    AllTablesNames=[]
    cursor= cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for TableInfo in cursor.fetchall():
        for EachTable in TableInfo:
            AllTablesNames.append(EachTable)
            cursor=cursor.execute(f"PRAGMA table_info({EachTable})")
            ColumnNameWithDataType=[]
            for ColumnInfo in cursor.fetchall(): 
                ColumnNameWithDataType.append([ColumnInfo[1],ColumnInfo[2]])
            TableNameWithColumnInfo.append([EachTable,ColumnNameWithDataType])
    return TableNameWithColumnInfo,AllTablesNames
    #TableNameWithColumnInfo structure is
    # [['Table1Name', [['Table1Column1Name', 'Table1Column1DataType'], ['Table1Column2Name', 'Table1Column2DataType']], 
    # ['Table2Name', [['Table2Column1Name', 'Table2Column1DataType'], ['Table2Column2Name', 'Table2Column2DataType']]]]


@app.route("/",methods=['GET','POST'])
def Index():

    con = DbConnection()
    cursor = con.execute("SELECT * FROM locations")
    
    Governorates =  list(Col[0] for Col in cursor.fetchall())
    Governorates.sort()
    cursor = con.execute("SELECT * FROM fuel")
    FuelList = list(Col[0] for Col in cursor.fetchall())
    Distance="0.0"
    Liters =0
    TotalPrice=0
    FromGov = ""
    ToGov = ""
    GasolineType =""
    Time = ""
    Speed = 120.0

    if request.method == 'POST':
        FromGov=str(request.form.get('Gov'))
        ToGov =str(request.form.get('ToGov'))
        GasolineType =str(request.form.get('Fuel'))
        Speed =float(request.form.get('Speed'))

        FromLat = list(Col[0]   #Latitude
        for Col in con.execute(f"SELECT latitude from locations WHERE Governorate = '{FromGov}'").fetchall()
        )
        FromLong = list(Col[0]  #Longitude
        for Col in con.execute(f"SELECT longitude from locations WHERE Governorate = '{FromGov}'").fetchall()
        )
        ToLat = list(Col[0]     #Latitude
        for Col in con.execute(f"SELECT latitude from locations WHERE Governorate = '{ToGov}'").fetchall()
        )
        ToLong = list(Col[0]    #Longtiude
        for Col in con.execute(f"SELECT longitude from locations WHERE Governorate = '{ToGov}'").fetchall()
        )
        FuelPrice = list(Col[0] 
        for Col in con.execute(f"SELECT Price from fuel WHERE FuelType = '{GasolineType}'").fetchall()
         )


        
        Distance=GreatCirlceDistance(FromLat[0],ToLat[0],FromLong[0],ToLong[0])
        Liters =round((Distance / 12.5),1)       # one liter of fuel moves the car about 12.5 km
        if FuelPrice:
          TotalPrice = int(Liters * int(FuelPrice[0]))
        if Speed <1.0 or Speed > 1000.0:
            Speed = 120.0
        Hours = Distance / float(Speed)
        min = float(math.modf(Hours)[0])* 60
        Time = str(int(Hours)) + ' Hours and '+str(int(min)) +' min '
        
    return render_template('Index.html',Governorates=Governorates,Distance=str(Distance),Liters = Liters,
    Price=TotalPrice,FromGov = FromGov,ToGov =ToGov,GasolineType = GasolineType,Time=Time,Speed=str(Speed),
    FuelList=FuelList
    )


#-----------------------------------------------------------------------------

@app.route("/DatabaseManagement",methods=['GET','POST'])
def UpdateData():
    con = DbConnection()
    cursor = sqlite3.Cursor(con)
    TableData=[]   #holds a list of dictionaries of each column name with corresponding data 
    TablesInfo,AllTablesName = AllTablesInfo(cursor)
    SelectedTable = AllTablesName[0]
    SelectedTableColumnsWithDataType=[]
    SelectedTableColumnsNames=[]
    SelectedTableCoulmnsDataType=[]
    SelectedQuery = "Select"
    UpdatedDeletedFromColumn=""
    NewVal=""
    ComparsionColumn=""
    ComparsionVal=""
    
    Msg =""
    error=False
    if request.method =='POST':   
            SelectedQuery = str(request.form.get('QueryType'))
            SelectedTable = str(request.form.get('TableName'))

            for names in TablesInfo:
                    if names[0] == SelectedTable:
                        for ColumnInfo in names[1]:
                            SelectedTableColumnsWithDataType.append(ColumnInfo)
                            SelectedTableColumnsNames.append(ColumnInfo[0])
                            SelectedTableCoulmnsDataType.append(ColumnInfo[1])

            if SelectedQuery =="Update" or SelectedQuery =="Delete":
                UpdatedDeletedFromColumn = str(request.form.get('UpdatedDeletedFromColumn'))
                if SelectedTableColumnsNames.count(UpdatedDeletedFromColumn)==0:
                    UpdatedDeletedFromColumn = SelectedTableColumnsNames[0]
                ComparsionColumn = str(request.form.get('ComparsionColumn'))
                if SelectedTableColumnsNames.count(ComparsionColumn)==0:
                    ComparsionColumn = SelectedTableColumnsNames[0]

                NewVal= str(request.form.get('NewVal'))
                ComparsionVal=str(request.form.get('ComparsionVal'))

            if request.form.get('ExecuteQuery') == "Execute Query":
                #Switch-Case is only supported in python 3.10 so we need to use multiple ifs
                if SelectedQuery == "Select":
                    #filling TableData with dictionaries filled with columnname-value for each column and row in the table
                    for names in TablesInfo:
                        if names[0] == SelectedTable:                     
                                cursor = con.execute(f"SELECT * FROM {SelectedTable}")
                                for Col in cursor.fetchall():  
                                    TemporaryDictionary={}
                                    for ColumnIndex in range(0,len(names[1])):
                                        TemporaryDictionary[names[1][ColumnIndex][0]]=Col[ColumnIndex]
                                    TableData.append(TemporaryDictionary)
                    if not TableData:
                        Msg = "Table is empty"
                        error = True
                    
                elif SelectedQuery =="Insert":
                    InsertedData=[]
                    DatatypeDoesNotMatch=False
                    for EachColumn in SelectedTableColumnsNames:
                        Data=str(request.form.get(f'{EachColumn}'))       
                        if Data and Data.strip() and Data[0]!=" ":
                            DataTy=SelectedTableCoulmnsDataType[SelectedTableColumnsNames.index(EachColumn)]
                            if not((DataTy=="INT" or DataTy=="INTEGER" or DataTy=="UNSIGNED BIG INT") and ("." in Data)):
                                InsertedData.append(str(Data))
                            else:
                                DatatypeDoesNotMatch=True
                                break
                        else:
                            break
                    if not(len(InsertedData)< len(SelectedTableColumnsNames)) and not DatatypeDoesNotMatch:
                        try:
                            cursor = con.execute(f"INSERT INTO {SelectedTable}{tuple(SelectedTableColumnsNames)} VALUES {tuple(InsertedData)}")
                            con.commit()
                        except Exception as e:
                            if("UNIQUE constraint failed" in str(e)):
                                Msg="Cannot have duplicate of the same data"
                            else:
                                Msg=e
                            error=True
                    
                        else:
                            Msg="Values Inserted Successfully"
                            error=False
                    else:
                        if DatatypeDoesNotMatch:
                            Msg="One or more fields' datatype does not match"
                        else:
                            Msg="There are empty fields or one of the values starting with blank space"
                        error=True
                    
                elif SelectedQuery =="Update":
                        
                        NewValue = str(request.form.get('NewVal'))
                        DatatypeDoesNotMatch=False
                        if NewValue and NewValue.strip and NewValue[0]!=" ":
                            for EachColumn in SelectedTableColumnsNames:
                                if UpdatedDeletedFromColumn == EachColumn:
                                    DataTy = SelectedTableCoulmnsDataType[SelectedTableColumnsNames.index(EachColumn)]
                                    if not((DataTy=="INT" or DataTy=="INTEGER" or DataTy=="UNSIGNED BIG INT") and ("." in NewValue)):
                                        try:
                                            cursor = con.execute(f"UPDATE {str(request.form.get('TableName'))} SET {str(request.form.get('UpdatedDeletedFromColumn'))} = '{NewValue}' WHERE {str(request.form.get('ComparsionColumn'))} =  '{str(request.form.get('ComparsionVal'))}'") 
                                            con.commit()
                                        except Exception as e:
                                            Msg=e
                                            error=True
                                        else:
                                            Msg="Values Updated Successfully"
                                            error=False
                                    else:
                                        Msg="One or more fields' datatype does not match"
                                        error=True
                                        DatatypeDoesNotMatch=True
                        else:                  
                            
                            Msg="New value cannot be empty or starting with blank space"
                            error=True
                elif SelectedQuery =="Delete":
                    try:
                        cursor = con.execute(f"DELETE FROM {str(request.form.get('TableName'))} WHERE {str(request.form.get('UpdatedDeletedFromColumn'))} = '{str(request.form.get('NewVal'))}'") 
                        con.commit()
                    except Exception as e:
                        Msg=e
                        error=True
                    else:
                        Msg="Row Deleted Sucessfully"
                        error=False
                            
    return render_template('DatabaseManagement.html',TableData=TableData,SelectedQuery=SelectedQuery,
    SelectedTable=SelectedTable,UpdatedDeletedFromColumn=UpdatedDeletedFromColumn,ComparsionColumn=ComparsionColumn,NewVal=NewVal,
    ComparsionVal=ComparsionVal,SelectedTableColumnsWithDataType=SelectedTableColumnsWithDataType,AllTablesName=AllTablesName,
    Msg=Msg,error=error
    )





@app.route("/About",methods=['GET','POST'])
def About():
    return render_template('About.html')



@app.route("/Contact",methods=['GET','POST'])
def Contact():
    con = DbConnection()
    cursor = con.execute("SELECT * FROM Contacts")
    Contacts = cursor.fetchall()
    return render_template('Contact.html',Contacts = Contacts)
