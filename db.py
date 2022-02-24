import sqlite3

con = sqlite3.connect("DataBase.db")
cursor = con.cursor()
#sql_query = """CREATE TABLE locations(
 #   Governorate text NOT NULL UNIQUE,
  #  latitude FLOAT NOT NULL,
   # longitude FLOAT NOT NULL)
    #"""

#sql2 = """INSERT INTO locations('Governorate','latitude','longitude') VALUES ('Sogag','26.549999','31.700001'),('Cairo','30.033333','31.233334')"""


# sql4 = """CREATE TABLE fuel(
#         FuelType text NOT NULL UNIQUE,
#         Price FLOAT NOT NULL)
#     """

#sql5 = """INSERT INTO fuel('FuelType','Price') VALUES ('Gasoline 80','7.00'),('Gasoline 92','8.25'),('Gasoline 95','9.25')"""

#sql6 = """DELETE FROM locations"""

#sql_query = """CREATE TABLE hi(
 #   yo text NOT NULL UNIQUE,
  #   k FLOAT NOT NULL,
   #   s FLOAT NOT NULL,
    #o FLOAT NOT NULL)
    #"""

#query = """UPDATE Contacts SET 'Email' = 'yasershaban03@hotmail.com' WHERE 'Email' =  '123az.az.Az.yaser@gmail.com' """
#query = """UPDATE Contacts SET Email = '123az.az.Az.yaser@gmail.com' WHERE Email =  'yasershaban03@hotmail.com' """


# cursor.execute(query)
# con.commit()