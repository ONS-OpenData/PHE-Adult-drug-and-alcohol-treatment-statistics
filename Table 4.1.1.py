# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.1.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# Table 4.1.1: Substance breakdown of all clients in treatment

# +
from gssutils import *

if is_interactive():
    scraper = Scraper('https://www.gov.uk/government/collections/alcohol-and-drug-misuse-and-treatment-statistics')
    scraper.select_dataset(title=lambda x: x.startswith('Substance misuse treatment for adults'), latest=True)
    tabs = {tab.name: tab for tab in scraper.distribution(title=lambda x: x.startswith('Data tables')).as_databaker()}
# -

tab = tabs['Table 4.1.1']

# https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/752515/AdultSubstanceMisuseNDTMSDataTables2017-18.xlsx

cell = tab.filter('Substance')
cell.assert_one()
observations = tab.filter('n').fill(DOWN).is_not_blank().is_not_whitespace()
Substance = cell.expand(DOWN).is_not_blank().is_not_whitespace()
Clients = cell.expand(RIGHT).is_not_blank().is_not_whitespace()
Dimensions = [
            HDim(Substance,'Treatment group',DIRECTLY,LEFT),
            HDim(Clients,'Clients in treatment',CLOSEST,LEFT),
            HDimConst('Measure Type','count-of-clients-in-treatment'),
            HDimConst('Unit','clients-in-treatment'),
            HDimConst('Period', 'gregorian-interval/2017-04-01T00:00:00/P1Y')
            ]

c1 = ConversionSegment(observations, Dimensions, processTIMEUNIT=True)
if is_interactive():
    savepreviewhtml(c1)

new_table = c1.topandas()

import numpy as np
new_table['OBS'].replace('', np.nan, inplace=True)
new_table.dropna(subset=['OBS'], inplace=True)
new_table.rename(columns={'OBS': 'Value'}, inplace=True)
new_table['Value'] = new_table['Value'].astype(int)
new_table['Value'] = new_table['Value'].map(lambda x:''
                                  if (x == '-')
                                  else int(x))

new_table['Treatment group'] = new_table['Treatment group'].str.rstrip('* ')

new_table['Treatment group'].unique()

new_table['Basis of treatment'] = new_table['Treatment group'].map(
    lambda x: {
        'Opiate (not crack cocaine)' : 'substance/opiate-not-crack-cocaine', 
        'Both opiate and crack cocaine\xa0' : 'substance/both-opiate-and-crack-cocaine',
       'Crack cocaine (not opiate)' : 'substance/crack-cocaine-not-opiate', 
        'Cannabis': 'substance/cannabis', 
        'Cocaine' :'substance/cocaine',
       'Benzodiazepine' :'substance/benzodiazepine', 
        'Amphetamine (other than ecstasy)' : 'substance/amphetamine-other-than-ecstasy', 
        'Other drug' : 'substance/other-drug',
       'Hallucinogen' : 'substance/hallucinogen', 
        'Other prescription drug' :'substance/other-prescription-drug', 
        'Anti-depressant' : 'substance/anti-depressant',
       'Solvent' : 'substance/solvent', 'Major tranquiliser' :'substance/major-tranquiliser', 
        'Barbiturate' : 'substance/barbiturate', 
        'Alcohol' : 'substance/alcohol',
       'Total number of individuals' : 'substance/total-number-of-individuals'
                
        }.get(x, x))

import urllib.request as request
import csv
import io
import requests
vrl="https://raw.githubusercontent.com/ONS-OpenData/ref_alcohol/master/codelists/substance-type.csv"
t=requests.get(vrl).content
g=pd.read_csv(io.StringIO(t.decode('utf-8')))
new_table = pd.merge(new_table, g, how = 'left', left_on = 'Clients in treatment', right_on = 'Label')
new_table.columns = ['Substance type' if x=='Notation' else x for x in new_table.columns]
new_table = new_table[['Period','Basis of treatment','Substance type','Measure Type','Value','Unit']]

new_table


