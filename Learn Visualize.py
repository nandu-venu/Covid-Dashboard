#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt


# In[2]:


dataset_url="https://raw.githubusercontent.com/datasets/covid-19/master/data/countries-aggregated.csv"
df=pd.read_csv(dataset_url)
print(df)


# In[3]:


#checking the shape of df
df.head()
df.tail()
df.shape


# In[4]:


#preprocessing
df=df[df.Confirmed>0]
df.head()


# In[5]:


df[df.Country=="Italy"]


# In[6]:


#first plot of global spread
fig=px.choropleth(df,locations="Country",locationmode='country names',color='Confirmed'
                 ,animation_frame='Date')
fig.update_layout(title_text='Global Spread of Covid 19') # to add the title
#fig.show()


# In[7]:


#first plot of global death
fig2=px.choropleth(df,locations="Country",locationmode='country names',color='Deaths'
                 ,animation_frame='Date')
fig2.update_layout(title_text='Global Death Count of Covid 19') # to add the title
#fig2.show()


# In[8]:


#How intensive Covid Transmission has been in each of the country
df_China=df[df.Country=="China"]
df_China.head()


# In[9]:


df_China=df_China[['Date','Confirmed']]
df_China.head()


# In[10]:


#calculating the first derivation of confirmed column
df_China['Infection Rate']=df_China['Confirmed'].diff() #Difference between last line and today
df_China.head()
print(df_China)


# In[11]:


px.line(df_China, x="Date", y=["Confirmed","Infection Rate"])


# In[12]:


df_China['Infection Rate'].max() #calculating the max value of Infection Rate


# In[13]:


countries=list(df['Country'].unique()) 
max_infection_rates=[]
for c in countries:
    MIR=df[df.Country==c].Confirmed.diff().max()
    max_infection_rates.append(MIR)

df_MIR=pd.DataFrame()
df_MIR['Country']=countries
df_MIR['Max Infection Rates']=max_infection_rates
df_MIR[df_MIR.Country=="India"]


# In[14]:


px.bar(df_MIR,x="Country", y="Max Infection Rates",color="Country", title='Global Max Infection Rates',log_y=True)


# In[15]:


#Effect of Lockdown in Italy
italy_lockdown_start_date='2020-03-09'
italy_lockdown_a_month_later='2020-04-09'
df.head()


# In[16]:


df_Italy=df[df.Country=="Italy"]
df_Italy["Infection_Rate"]=df_Italy.Confirmed.diff()
df_Italy


# In[17]:


fig3=px.line(df_Italy,x="Date",y="Infection_Rate",title="Impact of Lockdown in Italy")
fig3.add_shape(
    dict(
        type="line",
        x0=italy_lockdown_start_date,
        y0=0,
        x1=italy_lockdown_start_date,
        y1=df_Italy["Infection_Rate"].max()*1.25,
        line=dict(color="red",width=2)
    )
)

fig3.add_annotation(
    dict(
    x=italy_lockdown_start_date,
    y=df_Italy["Infection_Rate"].max(),
    text="Start of the lockdown"
    )
)

fig3.add_shape(
    dict(
        type="line",
        x0=italy_lockdown_a_month_later,
        y0=0,
        x1=italy_lockdown_a_month_later,
        y1=df_Italy["Infection_Rate"].max()*1.25,
        line=dict(color="green",width=2)
    )
)
fig3.show()
#px.line(df_China, x="Date", y=["Confirmed","Infection Rate"])


# In[18]:


df_Italy['Death_Rate']=df_Italy.Deaths.diff()
#normalizing the values
df_Italy['Infection_Rate']=df_Italy['Infection_Rate']/df_Italy['Infection_Rate'].max()
df_Italy['Death_Rate']=df_Italy['Death_Rate']/df_Italy['Death_Rate'].max()
fig4=px.line(df_Italy,x="Date",y=["Infection_Rate","Death_Rate"])

fig4.add_shape(
    dict(
        type="line",
        x0=italy_lockdown_start_date,
        y0=0,
        x1=italy_lockdown_start_date,
        y1=1,
        line=dict(color="red",width=2)
    )
)

fig4.add_annotation(
    dict(
    x=italy_lockdown_start_date,
    y=1,
    text="Start of the lockdown"
    )
)

fig4.add_shape(
    dict(
        type="line",
        x0=italy_lockdown_a_month_later,
        y0=0,
        x1=italy_lockdown_a_month_later,
        y1=1,
        line=dict(color="green",width=2)
    )
)
fig4.add_annotation(
    dict(
    x=italy_lockdown_a_month_later,
    y=0.8,
    text="One month of the lockdown"
    )
)
fig4.show()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




