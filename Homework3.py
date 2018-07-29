# Python Homework 3
# Name - Aman Shrivastava
# Computing ID - as3ek


# Initial imports
import pandas as pd 
from pandas import DataFrame, Series


import requests
from bs4 import BeautifulSoup

# The url of the first page to be scraped
base_url = "https://www.superherodb.com/characters/"
# Data to be scraped from the first page
list_chars_cols = ['Name', 'Url']

# Using the beautifulsoup package to parse the html page
url = base_url 
source_code = requests.get(url)
plain_text = source_code.text
soup = BeautifulSoup(plain_text, "html.parser")

# Extracting all the list elements from the page
list_of_supers = soup.findAll('li', {'class': 'char-li'})

# Creating a master dataframe to write all data to
data = DataFrame(columns=list_chars_cols)

# Looping through the list items to extract relevant data
for l in list_of_supers:
    temp = DataFrame([[l.text, l.find('a').get('href')]])
    temp.columns = list_chars_cols
    # Writing extracted data to the master dataframe
    data = data.append(temp, ignore_index=1)

# Base url of the character info page to extract personal data of all the characters
char_base_url = 'https://www.superherodb.com'

# Stats we want to extract
stats_list = ['Url', 'Intelligence', 'Strength', 'Speed', 'Durability', 'Power', 
              'Combat', 'Full name', 'Alter Egos', 'Aliases', 'Place of birth', 
              'First appearance', 'Creator', 'Alignment', 'Gender', 'Race', 'Height', 
              'Weight', 'Eye color', 'Hair color', 'Occupation', 'Base', 'Team Affiliation', 
              'Relatives']

# Creating a master dataframe for the collected stats
stat_data = DataFrame(columns=stats_list)
# Looping through the previously collected data to go the each url 
for index, row in data.iterrows():
    # Creating a map for all stats and values
    stat_map = {'Url': str(row['Url'])}
    # Generating character page url by appending to the base url
    char_url = char_base_url + str(row['Url'])
    source_code = requests.get(char_url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, "html.parser")
    # Extracting all the relavant divs from the soup object
    attrs = soup.findAll('div', {'class': 'gridbarholder'})
    personal = soup.findAll('table', {'class': 'table'})
    # Extracting all values and putting them in the map
    for a in attrs[:6]:
        stat_name = a.find('div', {'class': 'gridbarlabel'}).text
        stat_value = a.find('div', {'class': 'gridbarvalue'}).text
        stat_map[str(stat_name)] = stat_value
    for p in personal[:3]:
        trs = p.findAll('tr')
        for tr in trs:
            stat_map[str(tr.find('td').text.strip())] = str(tr.findAll('td')[1].text.strip())
    stat_map[str(personal[3].findAll('td')[0].text.strip())] = str(personal[3].findAll('td')[1].text.strip())
    stat_map[str(personal[3].findAll('td')[2].text.strip())] = str(personal[3].findAll('td')[3].text.strip())
    # Using the map to append new data to the master stat_data dataframe
    for key in stat_map.keys():
        stat_data.loc[index,key] = stat_map[key]
        
# Merging data and stat_data dataframe to consolidate all extracted info
full_data = pd.merge(data, stat_data, left_index=True, right_index=True)
# Removing duplicate columns
full_data.drop('Url_x', 1,  inplace=True)
f = full_data.rename(index=str, columns={"Url_y": "Url"})

# Writing data to a csv file
f.to_csv('SuperheroDataset.csv', encoding='utf-8')

#============================================================================================================
## Analysis of the collected data

# Reading from the csv file
data = pd.read_csv('SuperheroDataset.csv', encoding='utf-8', index_col=False)

# Converting numeric data to type float
data[['Intelligence', 'Strength', 
   'Speed', 'Durability', 
   'Power', 'Combat']] = data[['Intelligence', 'Strength', 'Speed', 'Durability', 'Power', 'Combat']].astype(float)

# Creating a new column for total power
data['Total Power'] = data['Intelligence'] +  data['Strength'] + data['Speed'] + data['Durability'] + data['Power'] + data['Combat']

# Filling out missing values for total power with 0
data['Total Power'].fillna(0, inplace=True)

data.to_csv('SuperheroDataset.csv', encoding='utf-8')

# Finding out the top 10 most poerful superheros
sorted_d = data.sort_values('Total Power', ascending=False)
top_10_names = sorted_d['Name'][:10].tolist()
top_10_power = sorted_d['Total Power'][:10].tolist()
top_10_creators = sorted_d['Creator'][:10].tolist()

print("Top 10 most powerful superheroes across all universes are: ")
for i in range(10):
    print(str(i+1) + " : " + str(top_10_names[i]) + " | Overall Rating: " + str(top_10_power[i]) + " | By: " + str(top_10_creators[i]))

# Defining function to get all character details for user input character
def get_char_data(char_name, dataset):
    d = data.loc[data['Name'] == 'na']
    if not data.loc[data['Name'] == char_name.title()].empty:
        d = data.loc[data['Name'] == char_name.title()]
    if d.empty:
        char_name = '-'.join(char_name.split())
        d = data.loc[data['Name'] == char_name.title()]
    return d

# Getting character as user input
char_name = str(input("Enter the name of a character to get his/her details: "))
d = get_char_data(char_name, data)

# Print all details of the character if character exists in the database
if d.empty == True:
    print('Character ' + str(char_name) + ' not found!')
else:
    for column in d.columns:
        print (str(column) + ": " + str(d.iloc[0][column]) + '\n')

# Program to battle two character and predict winner.        
print("Let's battle two supperheroes!".upper())

# Taking user inputs for character names
char_name1 = str(input("Enter the name of 1st character for battle: "))
while (get_char_data(char_name1, data).empty == True):
    char_name1 = str(input("Not found! Enter the name of 1st character for battle: "))

char_name2 = str(input("Enter the name of 2nd character for battle: "))
while (get_char_data(char_name2, data).empty == True):
    char_name1 = str(input("Not found! Enter the name of 2nd character for battle: "))

# Extracting character data from the dataset
battle1 = get_char_data(char_name1, data)
battle2 = get_char_data(char_name2, data)

# Comparing heroes across all fighting statistics
battle_cols = ['Intelligence', 'Strength', 'Speed', 'Durability', 'Power', 'Combat']
for bat in battle_cols:
    winner = battle1.iloc[0]['Name']
    if battle1.iloc[0][bat] < battle2.iloc[0][bat]:
        winner = battle2.iloc[0]['Name']
    print('In terms of ' + str(bat) + ', ' + str(winner) + ' wins! \n')

winner = battle1.iloc[0]['Name']
if battle1.iloc[0]['Total Power'] < battle2.iloc[0]['Total Power']:
    winner = battle2.iloc[0]['Name']
print('Overall Verdict: ' + str(winner) + ' wins! \n')

## NOTE : Further analysis is done in a Jupyter notebook(.ipynb)due to the ease of generating visualisations, 
#         request ypu to consider that for grading as well