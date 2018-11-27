''' 
initial loading of government demographics and source
'''
import io
import os
import subprocess
import pandas as pd
import sqlalchemy as sql
import us
import datetime 
from census import Census
from pkg_resources import resource_string
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from housing_affordability import __name__
from housing_affordability.models import Government, Gov_Demographic, Gov_Demographics_Source


class Command(BaseCommand):
    help = 'Scrapes Government data from Census'
    def handle(self, *args, **options):
        # database connection
        user = os.environ.get('DB_USER')
        password = os.environ.get('DB_PASSWORD')
        database_name = os.environ.get('DB_NAME')
        host = os.environ.get('DB_HOST')
        port = os.environ.get('DB_PORT')
        
        database_url = 'postgresql://{user}:{password}@{host}:{port}/{database_name}'.format(
            user=user,
            password=password,
            host=host,
            port=port,
            database_name=database_name,
        )
        engine = sql.create_engine(database_url, echo=False)
        
        ## load data from census
        
        # census variables we want
        fields_data = resource_string(__name__, 'data/census_vars.csv')
        fields_df = pd.read_csv(io.BytesIO(fields_data))
        # fields_df = pd.read_csv('./housing_affordability/data/census_vars.csv')
        fields_df.columns = ['var_name', 'source_variable', 'description']

        # convert to dictionary
        fields = fields_df.set_index('var_name').to_dict()
        
        # reverse the dictionary for linking census name to colloquial name
        rev_fields = {i[1]:i[0] for i in fields['source_variable'].items()}

        acs5_years = [2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009]
        acs5_df = pd.DataFrame()
        varlist = list(rev_fields.keys())
        ckey = os.getenv('CENSUS_KEY')

        places = pd.DataFrame(list(Government.objects.all().values('name','state_fip','place_fip')))
        
        for y in acs5_years:
            print('Gettings Census Demographics for {}'.format(y))
            c = Census(ckey, year=y)
            place_data = pd.DataFrame(c.acs5.state_place(varlist, '*', '*'))
    
            # rename appropriately
            place_data.rename(columns={'state':'state_fip', 'place':'place_fip'}, inplace=True)
            place_data.rename(columns=rev_fields, inplace=True)
            place_data['state_abbr'] = [us.states.lookup(i).abbr for i in place_data['state_fip']]

            place_data['year'] = y
            place_data['source'] = 'acs5'
            acs5_df = acs5_df.append(place_data)

        acs5_df.reset_index(inplace=True, drop=True)
        cities = acs5_df['name'].str.split(',')
        acs5_df['name'] = [i[0] for i in cities]

        # merge to keep only places were interested in
        acs5_df = acs5_df.merge(places, how='inner', on=['state_fip', 'place_fip'])

        ## set up models

        # government demographics source model
        fields['source_variable'].pop('name') # remove name variable from dict
        demos = list(fields['source_variable'].keys())

        govt_dem_source = pd.melt(acs5_df,
                                  id_vars=['year', 'source'],
                                  value_vars=demos,
                                  var_name='var_name').drop('value', axis=1).drop_duplicates()

        govt_dem_source['source_variable'] = [fields['source_variable'][i] for i in govt_dem_source['var_name']]
        govt_dem_source['description'] = [fields['description'][i] for i in govt_dem_source['var_name']]

        # add created_date and updated_date
        govt_dem_source['created_date'] = datetime.datetime.now()
        govt_dem_source['updated_date'] = govt_dem_source['created_date']

        # keep only the new records
        # get old records
        old = pd.DataFrame(list(Gov_Demographics_Source.objects.all().values('year', 'var_name')))

        if len(old) > 0:
            # keep only new records
            new = govt_dem_source[['year', 'var_name']]
            match = new.merge(old, on=['year','var_name'], how='left', indicator=True)
            govt_dem_source_new = match[match['_merge'] == 'left_only'][['year', 'var_name']]
            govt_dem_source_new = govt_dem_source_new.merge(govt_dem_source, on=['year','var_name'])
        else:
            govt_dem_source_new = govt_dem_source
            
        
        govt_dem_source_new.to_sql(Gov_Demographics_Source._meta.db_table,
                        index = False,
                        con=engine,
                        if_exists='append')

        # government demographics model

        # map fips to id
        idmap = list(Government.objects.all().values('id','state_fip', 'place_fip'))
        idmap = {i['state_fip'] + '_' + i['place_fip']: i['id'] for i in idmap}
        
        # map var name to id
        varidmap = list(Gov_Demographics_Source.objects.all().values('id','var_name','year'))
        varidmap = {i['var_name'] + str(i['year']): i['id'] for i in varidmap}

        
        acs5_df['state_place'] = acs5_df['state_fip'] + '_' + acs5_df['place_fip']
        acs5_df['gov_id'] = [idmap[i] for i in acs5_df['state_place']]
        
        govt_dem = pd.melt(acs5_df,
                           id_vars=['gov_id','year'],
                           value_vars=demos,
                           var_name='var_name')

        govt_dem['name_year'] = govt_dem['var_name'] + govt_dem['year'].astype(str)
        govt_dem['var_id'] = [varidmap[i] for i in govt_dem['name_year']]

        # add created_date and updated_date
        govt_dem['created_date'] = datetime.datetime.now()
        govt_dem['updated_date'] = govt_dem['created_date']

        govt_dem = govt_dem[['gov_id', 'var_id', 'value', 'created_date', 'updated_date']]

        # keep only the new records
        # get old records
        old = pd.DataFrame(list(Gov_Demographic.objects.all().values('gov', 'var')))

        if len(old) > 0:
            # keep only new records
            new = govt_dem[['gov_id', 'var_id']]
            match = new.merge(old,
                              left_on=['gov_id','var_id'],
                              right_on=['gov', 'var'],
                              how='left', indicator=True)
            govt_dem_new = match[match['_merge'] == 'left_only'][['gov_id', 'var_id']]
            govt_dem_new = govt_dem_new.merge(govt_dem, on=['gov_id','var_id'])
        else:
            govt_dem_new = govt_dem

        print('Writing Census Demographics to SQL')
        govt_dem_new.to_sql(Gov_Demographic._meta.db_table,
                        index = False,
                        con=engine,
                        if_exists='append')
