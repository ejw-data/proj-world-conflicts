#!/usr/bin/env python
# coding: utf-8

# # Notebook Contents
# * Transforming the excel data into a pandas dataframe
# * Performing a t test that compares the mean deaths in afghanistan of 1989-1993 to 2013-2018
# * Generating google maps screenshots of conflicts in afghanistan

# In[1]:


import pandas as pd
import gmaps
import numpy as np
import requests
import time
from ipywidgets.embed import embed_minimal_html
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy.stats import norm
import seaborn as sns
import math


# In[2]:


url = 'http://ucdpapi.pcr.uu.se/api/gedevents/19.1?pagesize=1&page=1'

filepath = 'Data_Files/ged191.xlsx'

data = pd.read_excel(filepath)


# In[3]:


data_df = pd.DataFrame(data)
data_df.head()


# In[4]:


df_year=[]
df_month=[]
df_day=[]
df_date = data_df['date_start'].astype(str).str.split('-')
df_date = df_date.reset_index()
for i in range(len(df_date)):
   df_year.append(df_date.loc[i][1][0])
   df_month.append(df_date.loc[i][1][1])
   df_day.append(df_date.loc[i][1][2][:2])
data_df['year2']=df_year
data_df['month']=df_month
data_df['day']=df_day
data_df


# In[5]:


# CREATE CLEANED DATAFRAME WITH ALL COUNTRIES
heatmap_df = data_df[['year','country','latitude', 'longitude', 'best']]
heatmap_df


# In[6]:


# Store 'Lat' and 'Lng' into  locations 
locations = heatmap_df[['latitude', 'longitude']].astype(float)

# Convert best death guess to float and store
deaths = heatmap_df['best'].astype(float)

years = heatmap_df['year'].astype(int).unique()

years.astype(int)
years.sort()
years


# In[8]:


fig = gmaps.figure()

heat_layer = gmaps.heatmap_layer(locations, weights=deaths, 
                                 dissipating=False, max_intensity=100,
                                 point_radius = .5)

fig.add_layer(heat_layer)
fig


# In[9]:


afg_df = heatmap_df.loc[heatmap_df['country'] == 'Afghanistan']
mean_lat = afg_df['latitude'].mean()
mean_long = afg_df['longitude'].mean()
mean_location = [mean_lat, mean_long]

year = 2018

year_df = heatmap_df.loc[heatmap_df['year'] == year]
year_locations = year_df[['latitude', 'longitude']]
year_deaths = year_df['best']

fig = gmaps.figure(zoom_level = 5.5, center = mean_location, layout={
        'width': '500px',
        'height': '600px',
        'padding': '3px',
        'border': '1px solid black'
})

heat_layer = gmaps.heatmap_layer(year_locations, weights=year_deaths, 
                             dissipating=False, max_intensity=100,
                             point_radius = .05)

fig.add_layer(heat_layer)
fig


# In[11]:


afg_grp = afg_df[['best', 'country', 'year']].groupby('year').sum().reset_index()
afg_grp.head()


# In[13]:


plt.plot(afg_grp['year'], afg_grp['best'], marker = 'o')
plt.title('Number of Deaths in Afghanistan, 1989-2018', weight = 'bold')
plt.xlabel('Year')
plt.ylabel('Number of deaths')
plt.grid()


# ## Perform t Test
# * Group 1 = Number of deaths per month from 1989 - 1994
# * Group 2 = Number of deaths per month from 2013 - 2018
# 
# * $H_{0}$ : mean(Group 1) = mean(Group 2)
# 

# In[14]:


# CREATE T TEST DATAFRAME (USES MONTH/DAY)
month_df = data_df[['country', 'year2', 'month', 'day', 'best']]
afg_df = month_df.loc[month_df['country'] == 'Afghanistan']

new_names = ['Country', 'Year', 'Month', 'Day', 'Best Estimate of Deaths']
afg_df.columns = new_names

afg_df.head()


# In[15]:


month_grp = afg_df.groupby(['Year', 'Month']).sum()

# [['Year', 'Month', 'Best Estimate of Deaths']]
months_grp = pd.DataFrame(month_grp).reset_index()
months_grp

grp_1 = ['1989', '1990', '1991', '1992', '1993', '1994']
grp_2 = ['2013', '2014', '2015', '2016', '2017', '2018']    


# In[16]:


# Create groups with monthly deaths from 1989 - 1994

months1 = months_grp.loc[months_grp['Year'] == '1989']
months2 = months_grp.loc[months_grp['Year'] == '1990']
months3 = months_grp.loc[months_grp['Year'] == '1991']
months4 = months_grp.loc[months_grp['Year'] == '1992']
months5 = months_grp.loc[months_grp['Year'] == '1993']
months6 = months_grp.loc[months_grp['Year'] == '1994']


# In[17]:


# Create dataframe containing all of those values
months_df = months1.append(months2)
months_df = months_df.append(months3)
months_df = months_df.append(months4)
months_df = months_df.append(months5)
months_df = months_df.append(months6)

# Get number of deaths for each month
grp1_deaths = list(months_df['Best Estimate of Deaths'])


# In[40]:


log1 = []
for i in grp1_deaths:
    log1.append(math.log10(i))


# SHOW LOG DISTRIBUTION    
sns.distplot(log1, hist = True, bins = 10, fit = norm,              color = 'blue', axlabel = "Log of Number of Deaths") 
plt.title("Logarithmic Distribution of Number of Monthly Deaths (1989-1994)")
plt.grid()
plt.savefig('images/Early_Deaths_Distribution')


# In[41]:


# Create group with monthly deaths from 2013 - 2018
months1a = months_grp.loc[months_grp['Year'] == '2013']
months2a = months_grp.loc[months_grp['Year'] == '2014']
months3a = months_grp.loc[months_grp['Year'] == '2015']
months4a = months_grp.loc[months_grp['Year'] == '2016']
months5a = months_grp.loc[months_grp['Year'] == '2017']
months6a = months_grp.loc[months_grp['Year'] == '2018']

# Create dataframe containing all of those values
months_dfa = months1a.append(months2a)
months_dfa = months_dfa.append(months3a)
months_dfa = months_dfa.append(months4a)
months_dfa = months_dfa.append(months5a)
months_dfa = months_dfa.append(months6a)

# Get number of deaths for each month
grp2_deaths = months_dfa['Best Estimate of Deaths']


# In[43]:


log2 = []
for i in grp2_deaths:
    log2.append(math.log10(i))

# SHOW LOG DISTRIBUTION    
sns.distplot(log2, hist = True, bins = 10, fit = norm,              color = 'blue', axlabel = "Log of Number of Deaths") 
plt.title("Logarithmic Distribution of Number of Monthly Deaths (2013-2018)")
plt.grid()
plt.savefig('images/Late_Deaths_Distribution')


# In[36]:


sns.distplot(log1, hist = True, bins = 10, fit = norm,              color = 'blue', axlabel = "Log of Number of Deaths") 
sns.distplot(log2, hist = True, bins = 10, fit = norm,              color = 'blue', axlabel = "Log of Number of Deaths") 
plt.grid()


# In[21]:


stats.ttest_ind(log1, log2, equal_var = False)

