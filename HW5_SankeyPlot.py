# Load packages
import requests as rq
import bs4
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

## load in the hierarchy information
url = "https://raw.githubusercontent.com/bcaffo/MRIcloudT1volumetrics/master/inst/extdata/multilevel_lookup_table.txt"
multilevel_lookup = pd.read_csv(url, sep = "\t").drop(['Level5'], axis = 1)
multilevel_lookup = multilevel_lookup.rename(columns = {
    "modify"   : "roi",
    "modify.1" : "level4",
    "modify.2" : "level3",
    "modify.3" : "level2",
    "modify.4" : "level1"})
multilevel_lookup = multilevel_lookup[['roi', 'level4', 'level3', 'level2', 'level1']]

## Now load in the subject data
id = 127
subjectData = pd.read_csv("https://raw.githubusercontent.com/smart-stats/ds4bio_book/main/book/assetts/kirby21AllLevels.csv")
subjectData = subjectData.loc[(subjectData.type == 1) & (subjectData.level == 5) & (subjectData.id == id)]
subjectData = subjectData[['roi', 'volume']]

## Merge the subject data with the multilevel data
subjectData = pd.merge(subjectData, multilevel_lookup, on = "roi")
subjectData = subjectData.assign(icv = "ICV")
subjectData = subjectData.assign(comp = subjectData.volume / np.sum(subjectData.volume))

# Make the first hierarchy: Level 2 to level 1
df1 = subjectData.drop(['roi','comp','level4','level3','icv','volume'], axis =1)
df1 = df1.assign(volumn = subjectData.volume)
df1.columns = ['target','source','value']

# Make the second hierarchy: Level 2 to ICV
df2 = subjectData.drop(['roi','volume','comp','level4','level3','level2'], axis =1)
df2 = df2.assign(volume = subjectData.volume)
df2 = df2.groupby(['level1','icv']).volume.sum().reset_index()
df2.columns = ['target','source','value']

#link them tgt by concatinating
links = pd.concat([df1, df2], axis=0)

#find all the unique values in source and target
unique_source_target = list(pd.unique(links[['source','target']].values.ravel('k')))
#mapping
mapping_dictionary = {k: v for v, k in enumerate(unique_source_target)}

links['source'] = links['source'].map(mapping_dictionary)
links['target'] = links['target'].map(mapping_dictionary)
# convert this dataframe into a dictionary
links_dict = links.to_dict(orient='list')


#Sankey diagram

fig2 = go.Figure(data=[go.Sankey(
    node = dict(
        pad = 15,
        thickness=20,
        line=dict(color='black', width=0.5),
        label = unique_source_target,
        color = "paleturquoise"
    ),
    link = dict(
        source= links_dict['source'],
        target = links_dict['target'],
        value = links_dict['value'],
        color = "lightpink"
    )
)
])

#save as html
fig2.show()