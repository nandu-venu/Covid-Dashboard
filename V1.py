#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import sqlite3
import datetime as dt
import altair as alt
from pandasql import sqldf
pysqldf=lambda q :sqldf(q,globals())

import plotly as py
import plotly.express as px
import plotly.io as pio
pio.renderers.default='browser'


# In[2]:


conn=sqlite3.connect('CovidIndia.sqlite')
Data=pd.read_sql_query("SELECT *  FROM Data",conn)
State=pd.read_sql_query("SELECT *  FROM State",conn)
State_Data=pd.read_sql_query("SELECT *  FROM State_Data",conn)
#df=pd.read_sql_query("SELECT Date,Confirmed, Recovered, Deceased, Tested,Vaccinated, State_Name, State_Area,State_Population  FROM Data LEFT JOIN State_Data ON Data.state_id=State_Data.state_id",conn)
#df.to_excel("Test.xlsx")
#Date,Confirmed, Recovered, Deceased, Tested,Vaccinated ,State_Population 
#df=pd.read_sql_table(conn,conn)

State_Data.head()


# In[3]:


#x=lambda a,b:a+b
#x(1,2)


# In[4]:


Joined_DF=pysqldf("Select state_code, Date, Confirmed,Recovered,Deceased,Tested,Vaccinated1,Vaccinated2,State_Name,State_Area,State_Population from Data left join State on Data.state_id=State.id left join State_Data on Data.state_id=State_Data.state_id")
Joined_DF.head()


# In[5]:


Joined_DF["Date"]=pd.DatetimeIndex(Joined_DF['Date'])
Joined_DF.dtypes


# In[6]:


alt.data_transformers.enable('json') #To avoid MaxRowsError

select_timeline=alt.selection_interval(encodings=["x"])  # as slider
bar_slider=alt.Chart(Joined_DF).mark_bar().encode(
    y="sum(Confirmed):Q",
    x="Date:T"
    ).add_selection(select_timeline
                   ).properties(title="Bar Slider",height=50)  #now bar slider will act like a slider

Conf_line=alt.Chart(Joined_DF).mark_line().encode(
    x="Date:T",
    y="sum(Confirmed):Q",
    tooltip="sum(Confirmed):Q",
    color=alt.condition(select_timeline,alt.value("black"),alt.value("lightgray"))
).properties(title="Detailed - Confirmed")   #defining basic chart for confirmed cases

Death_line=alt.Chart(Joined_DF).mark_line().encode(
    x="Date:T",
    y="sum(Deceased):Q",
    tooltip="sum(Deceased):Q",
    color=alt.condition(select_timeline,alt.value("black"),alt.value("lightgray"))
) .properties(title="Detailed - Deaths")     #defining basic chart for death cases

States=pysqldf("select distinct(State_Name) from Joined_DF")["State_Name"].values.tolist() #making a list of distinct states
states_dropdown=alt.binding_select(options=States) 
states_select=alt.selection_single(fields=["State_Name"],bind=states_dropdown,name="Select")  #dropdown for states

filter_conf=Conf_line.add_selection(
    states_select
).transform_filter(
    states_select
).transform_filter(
    select_timeline)  #applying necessary transform_filter

filter_death=Death_line.add_selection(
    states_select
).transform_filter(
    states_select
).transform_filter(
    select_timeline
)


# In[7]:


#Defining cumulative charts for the country overall
Conf_cum=alt.Chart(Joined_DF).mark_line().encode(
    x="Date:T",
    y="sum(Confirmed):Q",
    tooltip="sum(Confirmed):Q"
).properties(title="National Count Confirmed").interactive()   #defining basic chart for confirmed cases

Death_cum=alt.Chart(Joined_DF).mark_line().encode(
    x="Date:T",
    y="sum(Deceased):Q",
    tooltip="sum(Deceased):Q"
).properties(title="National count Deaths").interactive()    #defining basic chart for death cases

Conf_cum | Death_cum


# In[8]:


filter_conf | filter_death & bar_slider 


# In[9]:


Table_Bubble=alt.Chart(Joined_DF).mark_circle().encode(
    y="state_code:N",
    x="Date:T",
    size="sum(Confirmed)").transform_filter(
    select_timeline)

Table_Bubble & bar_slider 


# In[10]:


Summary_Table=pysqldf("Select State_Name,sum(Confirmed) as 'Total cases', sum(Deceased) as 'Total Deaths', sum(Vaccinated1) as 'Partially_Vax', sum(Vaccinated2) as 'Fully_Vax'"
           "from Joined_DF group by state_code order by sum(confirmed) DESC")
Summary_Table

#https://pandas.pydata.org/pandas-docs/stable/user_guide/style.html - use this to stylize the data


# In[11]:


Joined_DF["State_Name"].replace({"Andaman and Nicobar Islands":"Andaman & Nicobar Island","Arunachal Pradesh":"Arunanchal Pradesh",
                               "Daman and Diu":"Daman & Diu","Delhi":"NCT of Delhi","Jammu and Kashmir":"Jammu & Kashmir",
                               "Pondicherry":"Puducherry"},inplace=True)
Joined_DF


# In[12]:


# list1=[]
# i=0
# while i<=35:
#     list1.append(geojson_data["features"][i]["properties"]["st_nm"])
#     i=i+1
    
# tempdf=pysqldf("Select distinct State_Name from Joined_DF")
# tempdf["check"]=sorted(list1)


# In[13]:


#Map of India with data
geojson_data=pd.read_json("states_india.geojson")
#geojson_data["features"][1]["properties"] format of geojson

state_id_dict={}
for feature in geojson_data["features"]:
    state_id_dict[feature["properties"]["st_nm"]]=feature["properties"]["state_code"]
state_id_dict["Ladakh"]=99 #since Ladakh is not in our geojson file

Joined_DF['id']=Joined_DF["State_Name"].apply(lambda x:state_id_dict[x])


# In[14]:


Summary_Table["State_Name"].replace({"Andaman and Nicobar Islands":"Andaman & Nicobar Island","Arunachal Pradesh":"Arunanchal Pradesh",
                               "Daman and Diu":"Daman & Diu","Delhi":"NCT of Delhi","Jammu and Kashmir":"Jammu & Kashmir",
                               "Pondicherry":"Puducherry"},inplace=True)
Summary_Table['id']=Summary_Table["State_Name"].apply(lambda x:state_id_dict[x])
Summary_Table1=Summary_Table.to_json()
Joined_DF1=Joined_DF.to_json()
Summary_Table.drop(index=32,inplace=True)


# In[15]:


Summary_Table=Summary_Table.astype({"id":int})
Summary_Table.dtypes


# In[16]:


fig=px.choropleth(Summary_Table,
             locations='id',
              geojson=geojson_data.to_json(),
              color="Total Deaths"
             )
fig.show()


# In[ ]:





# In[ ]:





# In[17]:


#Exploratory on top 10 contributors, multi colored bar chart, tree map etc.


# In[18]:


#Visuals stating total vaccination doses, vax 1 as % of population, vax 2 as % of population, testing per 100 people


# In[ ]:





# In[ ]:




