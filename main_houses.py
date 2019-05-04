#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  3 17:37:30 2019

@author: sean

This is the main file for my project draft



"""


import bs4 as bs
import pickle
import requests
import pandas as pd
import csv
reader=pd.read_csv


#first of all get all the counties and their respective median incomes from wiki
def save_county_data():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_United_States_counties_by_per_capita_income#cite_note-1')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    data = []
    counties=[]
    for row in table.findAll('tr')[1:]:
        
        county = row.findAll('td')[1].text[:-1]
        state=row.findAll('td')[2].text[:-1]
        if county!='':
            income= row.findAll('td')[4].text[1:-1].replace(',', '')
            
            income=int(income)
            data.append([county+', '+state,income])
            counties.append(county)
    #alphabetize by county
    data.sort(key=lambda x: x[0])
    counties.sort(key=lambda x: x[0])
    with open("prices.pickle", "wb") as f:
        pickle.dump(data, f)
        pickle.dump(counties, f)
    
    return data,counties


data_income, counts=save_county_data()
# we now have the requisite data in the workspace.
#%%
#now we need to get the housing prices

data_prices=reader('house_data.csv')


prices_temp=data_prices['Median Home\rPrice Q2 2017'].values
counties_price=data_prices['County Name'].values
L=len(counties_price)

data_prices=[]
for k in range(0,L):
    data_prices.append([counties_price[k].replace(' County', ''),int(prices_temp[k].replace(',', '').replace('$', '').replace(' ', ''))])
    
#again alphabetize all
data_prices.sort(key=lambda x: x[0])

print(data_prices[:10]) 

#%%
#Now we need to take the data that we have and merge them into one data set. 
#one issue with this is that the two lists don't exactly line up because  some 
#counties are in one data set and not the other.

data_tot=[]
LP=len(data_prices)
LI=len(data_income)

for i in range(0,LI):
    for p in range(0,LP):
        
        
        temp_i=data_income[i]
        temp_p=data_prices[p]
        
        name_i=temp_i[0].split(', ')
        name_p=temp_p[0].split(', ')
        
        state_i=name_i[1]
        state_p=name_p[1]
        
        count_i=name_i[0].split(' ')[0]
        count_p=name_p[0].split(' ')[0]
        
        
        
        if count_i==count_p and state_i.replace(' ', '')==state_p.replace(' ', ''):
            
            #name, state income prices, rat
            data_tot.append([data_income[i][0],data_income[i][1],data_prices[p][1],data_income[i][1]/data_prices[p][1]])
            


data_tot.sort(key=lambda x: x[3])
#We now have the ratios that we are after. It looks like King county texas
# is one of the more relaxed places to live


#%%
#Now,we have our ratios and counties we need to make a heatmap. TO do 
#this we need to get the corresponding county codes. We can scrape this directly
#from wikipedia as well

def save_code_data():
    resp = requests.get('https://en.wikipedia.org/wiki/List_of_United_States_FIPS_codes_by_county')
    soup = bs.BeautifulSoup(resp.text, 'lxml')
    table = soup.find('table', {'class': 'wikitable sortable'})
    data = []
    for row in table.findAll('tr')[1:]:
        
        code = 'c'+row.findAll('td')[0].text[:-1]
        county_state=row.a['title'].replace(' County','')
        

        data.append([code,county_state])
        
    #alphabetize by county
    data.sort(key=lambda x: x[1])

    with open("prices.pickle", "wb") as f:
        pickle.dump(data, f)

    
    return data

data_codes=save_code_data()

#%%
# we need to make an array that has the appropriate codes. This is the last
#step before our first graphic

LT=len(data_tot)
LC=len(data_codes)

data_full=[]

for t in range(0,LT):
    for c in range(0,LC):
        
        temp_t=data_tot[t]
        temp_c=data_codes[c]
        
        name_t=temp_t[0].split(', ')
        name_c=temp_c[1].split(', ')
        if len(name_c)==2:
            state_t=name_t[1]
            state_c=name_c[1]
        
        count_t=name_t[0].split(' ')[0]
        count_c=name_c[0].split(' ')[0]
        
        
        
        if count_c==count_t and state_t.replace(' ', '')==state_c.replace(' ', ''):
            
            #code,rat,income,house,(county, state)
            data_full.append([data_codes[c][0],data_tot[t][-1],data_tot[t][1],\
                             data_tot[t][2],data_tot[t][0]])

data_full[:10]
        
#%%
#We now have our data in pristine form! We can make our image


svg = open('county_map.svg', 'r').read()

print(type(svg))

soup = bs.BeautifulSoup(svg, selfClosingTags=['defs','sodipodi:namedview'], features='lxml')
paths = soup.findAll('path')
colors = ["#00441b", "#006d2c","#238b45", "#41ae76", "#66c2a4", "#99d8c9", "#ccece6","#e5f5f9","#f7fcfd"]
colors.reverse()


# County style
path_style = 'font-size:12px;fill-rule:nonzero;stroke:#FFFFFF;stroke-opacity:1;stroke-width:0.1;stroke-miterlimit:4;stroke-dasharray:none;stroke-linecap:butt;marker-start:none;stroke-linejoin:bevel;fill:'


# Color the counties based on unemployment rate
for p in paths:

    try:
        pcode=p['class'][0]
    except:
        continue
    
    con=False
    for l in data_full:
        if l[0]==pcode:
            rate=l[1]
            con=True
    if con==False:
        continue
        

    if rate > 0.9:
        color_class = 8
    elif rate > 0.8:
        color_class = 7
    elif rate > 0.7:
        color_class = 6     
    elif rate > 0.6:
        color_class = 5
    elif rate > 0.5:
        color_class = 4
    elif rate > 0.4:
        color_class = 3
    elif rate > 0.3:
        color_class = 2
    elif rate > 0.1:
        color_class = 1
    else:
        color_class = 0
    color = colors[color_class]
    p['style'] = path_style + color
    
            
                




    
# Output map
coords=soup.prettify()

outter = open("target.svg", "w")
outter.write(coords)
outter.close()



















