#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import sqlite3
import json


# In[2]:


urljson="https://api.covid19india.org/v4/min/timeseries.min.json"
df=pd.read_json(urljson)
count=0
df.head()


# for loop through the states, for loop through the dates, for loop through the delta
# first column state, second column date, then confirmed, recovered, deceased, tested, other, vaccinated
# output in a csv file and then in a SQL file


# In[3]:


"""
state_list=[]
date_list=[]
confirmed_list=[]
recovered_list=[]
death_list=[]
vaccinated_list=[]
tested_list=[]

for state in df:
    #print(state)
    for date in df[state]["dates"]:
        try:
            #print(date)
            #print (df[state]["dates"][date]["delta"])
            state_list.append(state)
            date_list.append(date)
            try:
                confirmed_list.append(df[state]["dates"][date]["delta"]["confirmed"])
            except:
                confirmed_list.append(0)
                
            try:
                recovered_list.append(df[state]["dates"][date]["delta"]["recovered"])
            except:
                recovered_list.append(0)
            
            try:
                death_list.append(df[state]["dates"][date]["delta"]["deceased"])
            except:
                death_list.append(0)
                
            try:
                vaccinated_list.append(df[state]["dates"][date]["delta"]["vaccinated"])
            except:
                vaccinated_list.append(0)
                
            try:
                tested_list.append(df[state]["dates"][date]["delta"]["tested"])
            except:
                tested_list.append(0)
                       
        #except:
        #    pass

#print(len(state_list))
#print(len(date_list))
#print(len(confirmed_list))
#print(len(recovered_list))
#print(len(death_list))
#print(len(vaccinated_list))
#print(len(tested_list))

#print(state_list)
#print(date_list)
#print(confirmed_list)
#print(recovered_list)
#print(death_list)
#print(vaccinated_list)
#print(tested_list)

"""




# In[4]:


conn=sqlite3.connect('CovidIndia.sqlite')
cur=conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS State;
DROP TABLE IF EXISTS Data;
DROP TABLE IF EXISTS State_Data;

CREATE TABLE State(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, name TEXT UNIQUE);
CREATE TABLE Data(
    state_id INTEGER, Date DATE, Confirmed INTEGER, Recovered INTEGER, Deceased INTEGER, Tested INTEGER, Vaccinated INTEGER);
CREATE TABLE State_Data(
    state_id INTEGER, State_Name TEXT, State_Area INTEGER, State_Popuation INTEGER)'''
                 )
for state in df:
    if not (state=="TT" or state=="UN"):
        for date in df[state]["dates"]:
            cur.execute('''INSERT OR IGNORE INTO State(name) VALUES(?)''',(state,))
            cur.execute('''SELECT id FROM State WHERE name=?''',(state,))
            state_id=cur.fetchone()[0]

            try:
                confirmed=df[state]["dates"][date]["delta"]["confirmed"]
            except:
                confirmed=0
                
            try:
                recovered=df[state]["dates"][date]["delta"]["recovered"]
            except:
                recovered=0
        
            try:
                death=df[state]["dates"][date]["delta"]["deceased"]
            except:
                death=0
                
            try:
                vaccinated=df[state]["dates"][date]["delta"]["vaccinated"]
            except:
                vaccinated=0
                
            try:
                tested=df[state]["dates"][date]["delta"]["tested"]
            except:
                tested=0            
            
            cur.execute('''INSERT OR IGNORE INTO Data(state_id, Date, Confirmed, Recovered, Deceased, Tested, Vaccinated) VALUES(?,?,?,?,?,?,?)''',
                        (state_id,date,confirmed,recovered,death,tested,vaccinated))

        conn.commit()



# In[5]:


df1=pd.read_excel('State_Population_Data.xlsx')
cur.executescript('''
DROP TABLE IF EXISTS State_Data;

CREATE TABLE State_Data(
    state_id INTEGER, state_code TEXT, State_Name TEXT, State_Area INTEGER, State_Popuation INTEGER)''')

for index,row in df1.iterrows():
    cur.execute('''SELECT id FROM State WHERE name=?''',(row['State_Code'],))
    state_id=cur.fetchone()[0]
    cur.execute('''INSERT OR IGNORE INTO State_Data(state_id, state_code,State_Name, State_Area, State_Popuation) VALUES(?,?,?,?,?)''',
                        (state_id,row['State_Code'],row['State_Name'],row['Area'],row['Population']))
conn.commit()


# In[6]:


"""js=df["AN"]["dates"]
print(js)
print(js["2020-01-30"])
print(js["2020-02-02"])
for entry in js:
    try:
        print(js[entry]['delta'])
    except:
        pass
"""


# In[ ]:




