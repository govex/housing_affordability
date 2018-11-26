''' 
initial loading of governments
'''
import os
import pandas as pd
import datetime
import us
import pytz
from census import Census
from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from housing_affordability.models import Government
from django.conf import settings


class Command(BaseCommand):
    help = 'Loads governments with 30k+ population'
    def handle(self, *args, **options):
        ## load cities from census
        fields = {'NAME':'name', 'B01003_001E':'population_total'}
        acs5_years = [2016]
        acs5_years.sort() # for robustness (city naming requires this)
        acs5_df = pd.DataFrame()
        
        # load data using census variables
        varlist = list(fields.keys())

        for y in acs5_years:
            # create census object
            ckey = os.getenv('CENSUS_KEY')
            c = Census(ckey, year=y)

            place_data = pd.DataFrame(c.acs5.state_place(varlist, '*', '*'))
            
            # rename appropriately
            place_data.rename(columns={'state':'state_fip', 'place':'place_fip'}, inplace=True)
            place_data.rename(columns=fields, inplace=True)
    
            # filter for pop > 30k
            place_data = place_data.loc[place_data['population_total'] > 30000]

            # add state abbreviation
            place_data['state_abbr'] = [us.states.lookup(i).abbr for i in place_data['state_fip']]

            # add year
            place_data['year'] = y
            
            acs5_df = acs5_df.append(place_data)

            # continue
            acs5_df.reset_index(inplace=True, drop=True)
            cities = acs5_df['name'].str.split(',')
            acs5_df['name'] = [i[0] for i in cities]

            # get locations
            lonlats = pd.read_csv('housing_affordability/data/2016_Gaz_place_national.txt',
                                  sep='\t',
                                  encoding='latin1')
            lonlats.columns=['state_abbr','geoid','ANSICODE','name','LSAD','FUNCSTAT',
                             'ALAND','AWATER','ALAND_SQMI','AWATER_SQMI','latitude','longitude']
            lonlats = lonlats[['state_abbr', 'name', 'geoid', 'latitude', 'longitude']]
            
            ## set up government models
            govt = acs5_df[['name', 'state_abbr', 'state_fip', 'place_fip']].drop_duplicates()
            govt = govt.merge(lonlats, how='left', on=['name','state_abbr'])
            govt = govt[['name', 'state_abbr', 'state_fip', 'place_fip', 'latitude', 'longitude']]
            
            # add created_date and updated_date
            govt['created_date'] = datetime.datetime.now(pytz.utc)
            govt['updated_date'] = govt['created_date']
            
            # add country_abbr
            govt['country_abbr'] = 'USA'

            # to sql
            govt = govt.to_dict('index')
            for gov in govt.keys():
                g = Government.objects.update_or_create(place_fip=govt[gov].get('place_fip'),
                                                        state_fip=govt[gov].get('state_fip'),
                                                        defaults=govt[gov])
