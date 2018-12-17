import pandas as pd
import os
import datetime
import numpy as np
from django.shortcuts import render
from django.db.models import Max, Count, Sum, Case, When, IntegerField, CharField, Q
from housing_affordability.models import *
import plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as ff
from plotly import tools
from scipy.interpolate import interp1d



def govs_all(request):
    '''display all governments'''
    max_year = Gov_Demographics_Source.objects.all().aggregate(Max('year'))['year__max']

    # get the governments sorted by population 
    govs = Government.objects.all()
    for gov in govs:
        gov.population = gov.gov_demographic_set.filter(var__var_name='population_total')[0].value


    context = {
        'govs': govs
        }

    return render(
        request,
        'housing_affordability/govs_all.html',
        context
        )


def affordability(request):
    '''project profile page'''


    map_div = "Here goes a map"

    context = {
        'map_div':map_div
    }


    return render(
        request,
        'housing_affordability/affordability.html',
        context
        )

def affordability_select(request):
    '''project profile page'''
    
    landcolor = '#d9d9d9'
    #rgba(0,0,0,0)
    
    # Filter and select data
    
    govs = Government.objects.prefetch_related('gov_demographic_set')\
                             .filter(Q(gov_demographic__var__var_name='population_total') &\
                                     Q(gov_demographic__value__gt=30000) &\
                                     Q(gov_demographic__var__year=2016))

    long = [i['longitude'] for i in govs.values('longitude')]
    lat = [i['latitude'] for i in govs.values('latitude')]
    txt = [i['name'] for i in govs.values('name')]
    link = ['<a target="_top" href="/analysis/housing/overview/{}" style="color:rgba(0,0,0,0);">.</a>'.format(i['id']) for i in govs.values('id')]
    pops = Gov_Demographic.objects.filter(gov__in=govs,
                                          var__year=2016,
                                          var__var_name='population_total')
    pop = [i.value for i in pops]
    mrks = [4 + 5*np.log2(i/50000) if 4 + 5*np.log2(i/50000)>4 else 4 for i in pop]
    
    # Map Data
    map_data = [dict(
                     type = 'scattergeo',
                     locationmode = 'USA-states',
                     lon = long,
                     lat = lat,
                     mode = 'markers+text',
                     hoverinfo = 'text',
                     hovertext = txt,
                     text = link,
                     marker = dict(size = mrks,
                                   color = np.log(pop),
                                   colorscale='Viridis',
                                   cmax = np.log(2000000),
                                   cmin = np.log(30000),
                                   line = dict(width=0)),
                     textfont=dict(size=mrks),
                     opacity = 0.6)]

    # Map Layout
    map_lay = go.Layout(autosize=True,
                        hovermode='closest',
                        geo = dict(scope='usa',
                                   projection=dict(type='albers usa'),
                                   showland = True,
                                   landcolor = landcolor,
                                   subunitwidth=1,
                                   countrywidth=1,
                                   subunitcolor='white',
                                   countrycolor='white',
                                   showlakes=True,
                                   lakecolor='white',
                                   resolution=50),
                        showlegend = False,
                        width = 900,
                        height = 500,
                        margin = go.layout.Margin(l=10, r=10, b=10, t=30, pad=0),
                        )

    # Create figure
    map_div = py.offline.plot({'data':map_data,
                              'layout':map_lay},
                              include_plotlyjs = False,
                              output_type = 'div',
                              config = dict(showLink = False,
                                            modeBarButtonsToRemove = ['sendDataToCloud',
                                                                      'lasso2d',
                                                                      'select2d',
                                                                      'pan2d'],
                                            #modeBarButtonsToAdd = ['zoomInGeo'],
                                            displaylogo = False,
                                            scrollZoom = True,
                                            #displayModeBar = False,
                                            responsive = True)
                              )

    context = {
        'map_div':map_div
    }
    
    
    return render(
                  request,
                  'housing_affordability/affordability_select.html',
                  context
                  )


def affordability_wwc(request):
    '''project profile page'''
    
    #t1 = datetime.datetime.now()
    #t2 = datetime.datetime.now()
    #t3 = datetime.datetime.now()
    #print(t2-t1)
    #print(t3-t2)
 
    #General plot settings
    colorA = 'orange'
    colorB = 'darkcyan'
    colorC = 'lightgrey'
    colorD = 'purple'
    fontsize = 10
    single_width = 410
    double_width = 780
    total_height = 205
    
    # Cities list
    wwc_city_list = ['Albuquerque', 'Anchorage', 'Arlington', 'Athens',
                     'Augusta', 'Baltimore', 'Baton Rouge', 'Bellevue',
                     'Birmingham', 'Boise', 'Boston', 'Boulder', 'Buffalo',
                     'Cambridge', 'Cape Coral', 'Cary', 'Charleston',
                     'Charlotte', 'Chattanooga', 'Chula Vista',
                     'Colorado Springs', 'Columbia', 'Corona', 'Denton',
                     'Denver', 'Des Moines', 'Downey', 'Durham', 'Fargo',
                     'Fayetteville', 'Fort Collins', 'Fort Lauderdale',
                     'Fort Worth', 'Gainesville', 'Gilbert', 'Glendale',
                     'Grand Rapids', 'Greensboro', 'Gresham', 'Hartford',
                     'Hayward', 'Honolulu', 'Independence', 'Indianapolis',
                     'Irving', 'Jackson', 'Kansas City', 'Kansas City',
                     'Knoxville', 'Laredo', 'Las Vegas', 'Lewisville',
                     'Lexington', 'Lincoln', 'Little Rock', 'Long Beach',
                     'Louisville', 'Madison', 'Memphis', 'Mesa', 'Miami',
                     'Milwaukee', 'Minneapolis', 'Modesto', 'Naperville',
                     'Nashville', 'New Haven', 'New Orleans', 'Norfolk',
                     'Oklahoma City', 'Olathe', 'Orlando', 'Palmdale',
                     'Portland', 'Providence', 'Raleigh', 'Rancho Cucamonga',
                     'Riverside', 'Saint Paul', 'Salinas', 'Salt Lake City',
                     'San Francisco', 'San Jose', 'Scottsdale', 'Seattle',
                     'Sioux Falls', 'South Bend', 'Syracuse', 'Tacoma',
                     'Tempe', 'Topeka', 'Tulsa', 'Tyler', 'Victorville',
                     'Virginia Beach', 'Waco', 'Washington', 'West Palm Beach',
                     'Wichita', 'Winston-Salem']
        
    wwc_stat_list = ['NM', 'AK', 'TX', 'GA', 'GA', 'MD', 'LA', 'WA', 'AL',
                     'ID', 'MA', 'CO', 'NY', 'MA', 'FL', 'NC', 'SC', 'NC',
                     'TN', 'CA', 'CO', 'SC', 'CA', 'TX', 'CO', 'IA', 'CA',
                     'NC', 'ND', 'NC', 'CO', 'FL', 'TX', 'FL', 'AZ', 'AZ',
                     'MI', 'NC', 'OR', 'CT', 'CA', 'HI', 'MO', 'IN', 'TX',
                     'MS', 'KS', 'MO', 'TN', 'TX', 'NV', 'TX', 'KY', 'NE',
                     'AR', 'CA', 'KY', 'WI', 'TN', 'AZ', 'FL', 'WI', 'MN',
                     'CA', 'IL', 'TN', 'CT', 'LA', 'VA', 'OK', 'KS', 'FL',
                     'CA', 'OR', 'RI', 'NC', 'CA', 'CA', 'MN', 'CA', 'UT',
                     'CA', 'CA', 'AZ', 'WA', 'SD', 'IN', 'NY', 'WA', 'AZ',
                     'KS', 'OK', 'TX', 'CA', 'VA', 'TX', 'DC', 'FL', 'KS',
                     'NC']
        
    # Cities IDs & names
    gov_all = Government.objects.all()
    gov_all = pd.DataFrame.from_records((gov_all.values('name','id',
                                                        'state_abbr')))
    wwc = []
    for i in np.arange(len(wwc_city_list)):
        row = gov_all[gov_all.name.str.contains(wwc_city_list[i]+' ') &
                      gov_all.state_abbr.str.contains(wwc_stat_list[i])]
        if wwc_city_list[i]=='Honolulu':
            wwc.append([gov_all[gov_all.name.str.contains('Urban Honolulu'
                        )].id.values[0], wwc_city_list[i]+', '+wwc_stat_list[i]])
        elif len(row)>1: #Select city name with shortest name
            wwc.append([row[row.name.str.len() ==
                           row.name.str.len().min()].id.values[0],
                       wwc_city_list[i]+', '+wwc_stat_list[i]])
        elif len(row)==1:
            wwc.append([row.id.values[0], wwc_city_list[i]+', '+wwc_stat_list[i]])
    wwc = pd.DataFrame(wwc, columns=['gov_id', 'gov_name'])

    # Cities all data
    data_all_list = []
    for city in wwc.gov_id:
        df = pd.DataFrame.from_records(Gov_Demographic.objects.filter(
             gov_id = city).values('gov_id','var_id', 'value'))
        data_all_list.append(df)
    data_all = pd.concat(data_all_list, ignore_index=True)

    # Variables IDs
    vars_id = pd.DataFrame.from_records(
              Gov_Demographics_Source.objects.all().values(
              'var_name','id','year'))
    
    #Real State Tax
    source_mortg = vars_id[vars_id.var_name ==
                           'real_state_tax_mortg_median'][['year','id']]
    source_hval = vars_id[vars_id.var_name ==
                          'house_median_value'][['year','id']]
    source_inc = vars_id[vars_id.var_name ==
                         'household_income_own_median'][['year','id']]
    source_pop = vars_id[vars_id.var_name ==
                         'population_total'][['year','id']]
                           
    data_tax_all = data_all.merge(source_mortg, left_on = 'var_id',
                                  right_on = 'id')[['year', 'value', 'gov_id']]
    data_inc_all = data_all.merge(source_inc, left_on = 'var_id',
                                  right_on = 'id')[['year', 'value', 'gov_id']]
    data_hval_all = data_all.merge(source_hval, left_on = 'var_id',
                                   right_on = 'id')[['year', 'value']]
    data_per_all = data_tax_all.value.values/data_inc_all.value.values
    min_per = np.min(data_per_all)
    max_per = np.max(data_per_all)
                           
    years_list = source_mortg.year.unique()
    tax_data = []
    tax_frames = []
    tax_slider_steps = []
    for yr in years_list:

        data_tax = data_tax_all[data_tax_all.year==yr].value
        data_inc = data_inc_all[data_inc_all.year==yr].value
        data_hval = data_hval_all[data_hval_all.year==yr].value
        data_nam = data_tax_all[data_tax_all.year==yr].merge(wwc,
                   on = 'gov_id').gov_name
        data_per = data_tax/data_inc
                                                                                        
        tax_yr = go.Scatter(x=data_hval,
                            y=data_inc,
                            mode='markers',
                            hoverinfo = 'text',
                            hovertext = [x+'<br>'+'${:.0f}<br>{:.1f}% HH inc'
                                         .format(y,z) for x,y,z in
                                         zip(data_nam, data_tax, data_per*100)],
                            marker=dict(color = data_per,
                                        opacity=0.5,
                                        size=2+data_tax.values/200.,
                                        showscale = True,
                                        colorscale='YlOrRd',
                                        cmin = min_per,
                                        cmax = max_per,
                                        reversescale=True,
                                        colorbar=dict(tickformat = '.0%',
                                                      thickness=10,
                                                      y=0.5,
                                                      x=1.0,
                                                      ypad=0,
                                                      title = 'Property tax as a percentage of HH income',
                                                      titleside='right',
                                                      outlinewidth=1,
                                                      outlinecolor='white')
                                        )
                            )
        if (yr == years_list.min()):
            tax_data.append(tax_yr)
                                                                                                                    
        slider_step = dict(args = [[yr], dict(frame = dict(duration = 500,
                                                           redraw = False),
                                              mode = 'immediate',
                                              transition = dict(duration= 150))],
                           label= '{:.0f}'.format(yr),
                           method = 'animate')
                                                                                                                        
        tax_frames.append(dict(data=[tax_yr], name='{:.0f}'.format(yr)))
        tax_slider_steps.append(slider_step)

    tax_lay = go.Layout(xaxis = dict(range=[0.8*data_hval_all.value.min(),
                                            1.1*data_hval_all.value.max()],
                                     showgrid = False,
                                     zeroline = False,
                                     showline = True,
                                     automargin=True,
                                     title='Median house value'),
                        yaxis = dict(range=[0.8*data_inc_all.value.min(),
                                            1.1*data_inc_all.value.max()],
                                     showgrid = False,
                                     zeroline = False,
                                     showline = True,
                                     automargin=True,
                                     title='Median household income'),
                        font = dict(size=fontsize),
                        width = 1.3*single_width,
                        height = 2*total_height,
                        margin = go.layout.Margin(l=50, r=10, b=10, t=30, pad=0),
                        hovermode='closest',
                        updatemenus = [dict(type = 'buttons',
                                            buttons = [dict(label= 'Play',
                                                            method = 'animate',
                                                            args = [None])],
                                            bgcolor = 'white',
                                            bordercolor = colorC,
                                            showactive = False,
                                            x = 0.1,
                                            y = -0.27)],
                        sliders = [dict(active = 0,
                                        currentvalue = dict(prefix = 'Year: ',
                                                            visible = True,
                                                            xanchor = 'right',
                                                            offset = 4),
                                        transition = dict(duration = 150,
                                                          easing = 'cubic-in-out'),
                                        visible = True,
                                        bgcolor = 'white',
                                        activebgcolor = colorC,
                                        bordercolor = colorC,
                                        ticklen = 5,
                                        tickcolor = colorC,
                                        x = 0.15,
                                        y = -0.2,
                                        len = 0.80,
                                        pad = dict(t=0),
                                        steps = tax_slider_steps)]
                        )
    
    tax_config= dict(showLink = False,
                     modeBarButtonsToRemove = ['sendDataToCloud'
                                               'lasso2d',
                                               'select2d',
                                               'pan2d'],
                     displaylogo = False,
                     responsive = True)
        
    tax_div = py.offline.plot({'data':tax_data,
                              'frames':tax_frames,
                              'layout':tax_lay},
                              include_plotlyjs = False,
                              output_type = 'div',
                              config = tax_config)
                     
    # Affordability
    source_tot_own_mortg = vars_id.loc[vars_id.var_name.isin(
                           ['owner_costs_pctincome_mortg_tot'])]
    source_tot_own_nomortg = vars_id.loc[vars_id.var_name.isin(
                             ['owner_costs_pctincome_nomortg_tot'])]
    source_tot_rent = vars_id.loc[vars_id.var_name.isin(
                      ['rent_pctincome_tot'])]
    source_own_mortg = vars_id.loc[vars_id.var_name.str.contains(
                       '^owner_costs_pctincome_mortg_[0-9]')]
    source_own_nomortg = vars_id.loc[vars_id.var_name.str.contains(
                        '^owner_costs_pctincome_nomortg_[0-9]')]
    source_rent = vars_id.loc[vars_id.var_name.str.contains(
                  '^rent_pctincome_[0-9]')]
                     
    data_tot_own_mortg_all = data_all.merge(source_tot_own_mortg, left_on =
        'var_id', right_on = 'id')[['year', 'value', 'gov_id']]
    data_tot_own_nomortg_all = data_all.merge(source_tot_own_nomortg, left_on =
        'var_id', right_on = 'id')[['year', 'value', 'gov_id']]
    data_tot_rent_all = data_all.merge(source_tot_rent, left_on =
        'var_id', right_on = 'id')[['year', 'value', 'gov_id']]
    data_own_mortg_all = data_all.merge(source_own_mortg, left_on =
        'var_id', right_on = 'id')[['year', 'value', 'gov_id']]
    data_own_nomortg_all = data_all.merge(source_own_nomortg, left_on =
        'var_id', right_on = 'id')[['year', 'value', 'gov_id']]
    data_rent_all = data_all.merge(source_rent, left_on =
        'var_id', right_on = 'id')[['year', 'value', 'gov_id']]
                     
    aff_frames = []
    aff_slider_steps = []
    max_range = 0
    for yr in years_list:
                         
        r_own_mortg = (data_own_mortg_all[data_own_mortg_all.year == yr]
                       .groupby('gov_id').value.sum()
                       / data_tot_own_mortg_all[data_tot_own_mortg_all.year ==yr]
                       .set_index('gov_id').value)
        r_own_nomortg = (data_own_nomortg_all[data_own_nomortg_all.year == yr]
                         .groupby('gov_id').value.sum()
                        / data_tot_own_nomortg_all[data_tot_own_nomortg_all.year
                        == yr].set_index('gov_id').value)
        r_rent = (data_rent_all[data_rent_all.year ==yr]
                  .groupby('gov_id').value.sum()
                  /data_tot_rent_all[data_tot_rent_all.year == yr]
                  .set_index('gov_id').value)
        data_nam = (data_tot_rent_all[data_tot_rent_all.year == yr]
                   .merge(wwc, on = 'gov_id').gov_name)
        max_yr = (r_own_mortg + r_own_nomortg + r_rent).max()
        if max_yr > max_range:
            max_range = max_yr
                                                                                   
        aff_yr_0 = go.Barpolar(r = np.ones(len(r_own_mortg))*0.1,
                               hoverinfo = 'skip',
                               marker = dict(color='rgba(0,0,0,0)'),
                               showlegend = False)
        aff_yr_a = go.Barpolar(r = r_own_mortg,
                               hoverinfo = 'text',
                               text = [x+'<br>{:.0f}%'.format(y*100) for x,y in
                                       zip(data_nam, r_own_mortg)],
                               name = 'Owned w/ mortgage',
                               marker = dict(color=colorA),
                               opacity = 0.6)
        aff_yr_b = go.Barpolar(r = r_own_nomortg,
                               hoverinfo = 'text',
                               text = [x+'<br>{:.0f}%'.format(y*100) for x,y in
                                       zip(data_nam, r_own_nomortg)],
                               name = 'Owned w/o mortgage',
                               marker = dict(color=colorC),
                               opacity = 0.5)
        aff_yr_c = go.Barpolar(r = r_rent,
                               hoverinfo = 'text',
                               text = [x+'<br>{:.0f}%'.format(y*100) for x,y in
                                       zip(data_nam, r_rent)],
                               name = 'Rented',
                               marker = dict(color=colorB),
                               opacity = 0.5)

        if (yr == years_list.min()):
            aff_data = [aff_yr_0, aff_yr_c, aff_yr_a, aff_yr_b]
                                                                                                                                                 
        slider_step = dict(args = [[yr], dict(frame = dict(duration = 500,
                                                           redraw = False),
                                              mode = 'immediate',
                                              transition = dict(duration= 150))],
                           label= '{:.0f}'.format(yr),
                           method = 'animate')
        aff_frames.append(dict(data=[aff_yr_0, aff_yr_c, aff_yr_a, aff_yr_b],
                                name='{:.0f}'.format(yr)))
        aff_slider_steps.append(slider_step)

    aff_lay = go.Layout(polar = dict(radialaxis = dict(showticklabels=False,
                                                       showline = False,
                                                       gridcolor = '#E6E6E6',
                                                       gridwidth = 0.5,
                                                       ticks = '',
                                                       tickvals = np.array([0.3,
                                                            0.5,0.7])*max_range,
                                                       range = [0,max_range+0.1]),
                                     angularaxis = dict(visible=False)),
                        font = dict(size=fontsize),
                        width = 1.3*single_width,
                        height = 2.3*total_height,
                        margin = go.layout.Margin(l=0, r=0, b=30, t=40, pad=0),
                        hovermode='y',
                        legend = dict(x=0.13,
                                      y=1.05,
                                      orientation='h',
                                      bgcolor='rgba(0,0,0,0)'),
                        updatemenus = [dict(type = 'buttons',
                                        buttons = [dict(label= 'Play',
                                                        method = 'animate',
                                                        args = [None])],
                                        bgcolor = 'white',
                                        bordercolor = colorC,
                                        showactive = False,
                                        x = 0.18,
                                        y = 0.07)],
                    sliders = [dict(active = 0,
                                    currentvalue = dict(prefix = 'Year: ',
                                                        visible = True,
                                                        xanchor = 'right',
                                                        offset = 4),
                                    transition = dict(duration = 150,
                                                      easing = 'cubic-in-out'),
                                    visible = True,
                                    bgcolor = 'white',
                                    activebgcolor = colorC,
                                    bordercolor = colorC,
                                    ticklen = 5,
                                    tickcolor = colorC,
                                    x = 0.22,
                                    y = 0.12,
                                    len = 0.61,
                                    pad = dict(t=0),
                                    steps = tax_slider_steps)]
                    )
    
    aff_config= dict(showLink = False,
                     modeBarButtonsToRemove = ['sendDataToCloud'
                                               'lasso2d',
                                               'select2d',
                                               'pan2d'],
                     displaylogo = False,
                     responsive = True)
        
    aff_div = py.offline.plot({'data':aff_data,
                              'frames':aff_frames,
                              'layout':aff_lay},
                              include_plotlyjs = False,
                              output_type = 'div',
                              config = tax_config)
                     
    # Rent/Buy price change
    source_tot_pop = vars_id.loc[vars_id.var_name.isin(['population_total'])]
    source_med_rent = vars_id.loc[vars_id.var_name.isin(['rent_contract_median'])]
    source_med_inc = vars_id.loc[vars_id.var_name
                     .isin(['household_income_median'])]
    source_tot_price = vars_id.loc[vars_id.var_name
                       .isin(['house_price_tot'])]
    source_dist_price = vars_id.loc[vars_id.var_name
                        .str.contains('^house_price_[0-9]+')]
                     
    data_tot_pop_all = data_all.merge(source_tot_pop, left_on = 'var_id',
                       right_on = 'id')[['year', 'value', 'gov_id']]
    data_med_rent_all = data_all.merge(source_med_rent, left_on = 'var_id',
                        right_on = 'id')[['year', 'value', 'gov_id']]
    data_med_inc_all = data_all.merge(source_med_inc, left_on = 'var_id',
                       right_on = 'id')[['year', 'value', 'gov_id']]
    data_tot_price_all = data_all.merge(source_tot_price, left_on = 'var_id',
                         right_on = 'id')[['year', 'value', 'gov_id']]
    data_dist_price_all = data_all.merge(source_dist_price, left_on = 'var_id',
                          right_on = 'id')[['year', 'value', 'gov_id']]
                     
    # Note that 2 extra bins are added in 2015,
    # but we do not need them to calculate the median
    dist_price_minbins = np.array([0, 10, 15, 20, 25, 30, 35, 40, 50, 60, 70,
                                   80, 90, 100, 125, 150, 175, 200, 250, 300,
                                   400, 500, 750, 1000])*1000
    data_med_price_all = []
    for gov in wwc.gov_id:
        for yr in data_tot_pop_all.year.unique():
            freq = (data_dist_price_all[(data_dist_price_all.gov_id == gov) &
                    (data_dist_price_all.year == yr)].value.values)
            totunits = (data_tot_price_all[(data_tot_price_all.gov_id == gov) &
                        (data_tot_price_all.year == yr)].value.values)
            if totunits:
                med = median_from_hist(dist_price_minbins, freq, tot=totunits[0])
            else:
                med = np.nan
            data_med_price_all.append([yr, gov, med])

    data_med_price_all = pd.DataFrame(data_med_price_all,
                                      columns=['year', 'gov_id', 'value'])
    data_med_inc_all['pctchange'] = (data_med_inc_all.groupby(['gov_id'])
                                     .value.pct_change())
    data_med_inc_all['csum'] = (data_med_inc_all.groupby(['gov_id'])
                                .pctchange.cumsum())
    data_med_price_all['pctchange'] = (data_med_price_all.groupby(['gov_id'])
                                       .value.pct_change())
    data_med_price_all['csum'] = (data_med_price_all.groupby(['gov_id'])
                                  .pctchange.cumsum())
    data_med_rent_all['pctchange'] = (data_med_rent_all.groupby(['gov_id'])
                                      .value.pct_change())
    data_med_rent_all['csum'] = (data_med_rent_all.groupby(['gov_id'])
                                 .pctchange.cumsum())
    data_tot_pop_all['pctchange'] = (data_tot_pop_all.groupby(['gov_id'])
                                     .value.pct_change())
    data_tot_pop_all['csum'] = (data_tot_pop_all.groupby(['gov_id'])
                                .pctchange.cumsum())

    years = data_med_rent_all.year.unique()
    x_inc = data_med_inc_all[data_med_inc_all.year==years[-1]].csum.iloc[::-1]
    x_prc = data_med_price_all[data_med_price_all.year==years[-1]].csum.iloc[::-1]
    x_rnt = data_med_rent_all[data_med_rent_all.year==years[-1]].csum.iloc[::-1]
    x_pop = data_tot_pop_all[data_tot_pop_all.year==years[-1]].csum.iloc[::-1]
    y_nam = data_med_rent_all[data_med_rent_all.year==years[-1]
                              ].merge(wwc, on='gov_id').gov_name.iloc[::-1]

    price_data = [go.Bar(x = x_inc,
                         y = y_nam,
                         marker = dict(color = colorD,
                                       line=dict(width=1, color='white')),
                         opacity = 0.5,
                         orientation='h',
                         hoverinfo = 'text',
                         hovertext = [n+'<br>{:.1f}%'.format(x*100) for n,x in
                                      zip(y_nam, x_inc)],
                         showlegend = False,
                         xaxis='x',
                         yaxis='y'),
                  go.Bar(x = x_prc,
                         y = y_nam,
                         marker = dict(color = colorA,
                                       line=dict(width=1, color='white')),
                         opacity = 0.6,
                         orientation='h',
                         hoverinfo = 'text',
                         hovertext = [n+'<br>{:.1f}%'.format(x*100) for n,x in
                                      zip(y_nam, x_prc)],
                         showlegend = False,
                         xaxis='x2',
                         yaxis='y'),
                  go.Bar(x = x_rnt,
                         y = y_nam,
                         marker = dict(color = colorB,
                                       line=dict(width=1, color='white')),
                         opacity = 0.6,
                         orientation='h',
                         hoverinfo = 'text',
                         hovertext = [n+'<br>{:.1f}%'.format(x*100) for n,x in
                                      zip(y_nam, x_rnt)],
                         showlegend = False,
                         xaxis='x3',
                         yaxis='y'),
                  go.Bar(x = x_pop,
                         y = y_nam,
                         marker = dict(color = colorC,
                                       line=dict(width=1, color='white')),
                         opacity = 0.8,
                         orientation='h',
                         hoverinfo = 'text',
                         hovertext = [n+'<br>{:.1f}%'.format(x*100) for n,x in
                                      zip(y_nam, x_pop)],
                         showlegend = False,
                         xaxis='x4',
                         yaxis='y'),
                  ]
    
    price_lay = go.Layout(xaxis = dict(domain = [0.02, 0.25],
                                       showgrid = True,
                                       showline = True,
                                       automargin=True,
                                       tickformat = '.0%',
                                       title = 'HH income',
                                       tickangle = 315,
                                       side = 'top'),
                          yaxis = dict(showgrid = True,
                                       zeroline = False,
                                       showline = False,
                                       automargin = True),
                          xaxis2 = dict(domain = [0.27, 0.5],
                                        showgrid = True,
                                        showline = True,
                                        automargin = True,
                                        anchor = 'y',
                                        tickformat = '.0%',
                                        title = 'House Price',
                                        tickangle = 315,
                                        side = 'top'),
                          xaxis3 = dict(domain = [0.52, 0.75],
                                        showgrid = True,
                                        showline = True,
                                        automargin = True,
                                        anchor = 'y',
                                        tickformat = '.0%',
                                        title = 'Monthly rent amount',
                                        tickangle = 315,
                                        side = 'top'),
                          xaxis4 = dict(domain = [0.77, 1.],
                                        showgrid = True,
                                        showline = True,
                                        automargin = True,
                                        anchor = 'y',
                                        tickformat = '.0%',
                                        title = 'Population',
                                        tickangle = 315,
                                        side = 'top'),
                          font = dict(size=fontsize),
                          width = 1.6*single_width,
                          height = 5*total_height,
                          margin = go.layout.Margin(l = 0,
                                                    r = 0,
                                                    b = 10,
                                                    t = 80,
                                                    pad = 0),
                          )
        
    price_config= dict(showLink = False,
                       modeBarButtonsToRemove = ['sendDataToCloud',
                                                 'lasso2d',
                                                 'select2d',
                                                 'pan2d'],
                       displaylogo = False,
                       responsive = True)
                          
    price_div = py.offline.plot({'data': price_data[::-1],
                                'layout': price_lay},
                                include_plotlyjs = False,
                                output_type = 'div',
                                config = price_config)
                          
    context = {
        'tax_div': tax_div,
        'aff_div': aff_div,
        'price_div': price_div,
        'lastyeardata': years[-1]
    }


    return render(
                  request,
                  'housing_affordability/affordability_wwc.html',
                  context
                  )
    
    
    


def affordability_overview(request, gov_id):
    '''project profile page'''

    #General plot settings
    colorA = 'orange'
    colorB = 'darkcyan'
    colorC = 'lightgrey'
    fontsize = 10
    margin_aff=go.layout.Margin(l=45, r=20, b=50, t=50, pad=0)
    single_width = 410
    double_width = 830
    total_height = 205
    
    #Data request
    gov = Government.objects.get(id=gov_id)
    demos = Gov_Demographic.objects.filter(gov_id=gov_id)
    demos = pd.DataFrame(list(demos.values()))
    demos.dropna(inplace=True)
    demos_source = Gov_Demographics_Source.objects.all()
    demos_source = pd.DataFrame(list(demos_source.values()))
    demos['value'] = [(i > 0) * i for i in demos['value']]
    df = demos.merge(demos_source, left_on = 'var_id', right_on = 'id')[['var_name','description','year','value']]
    
    #City name
    cityname_div = gov.name+', '+gov.state_abbr
    
    #Rented vs. owned units
    renttot = df.loc[df['var_name'].isin(['house_renter_occupied'])]
    owntot  = df.loc[df['var_name'].isin(['house_owner_occupied'])]
    vactot  = df.loc[df['var_name'].isin(['house_vacant'])]
    unittot = df.loc[df['var_name'].isin(['house_units'])]
    rentper = [float(renttot[renttot['year']==y].value) /
               float(unittot[unittot['year']==y].value)*100 for y in unittot.year]
    ownper  = [float(owntot[owntot['year']==y].value) /
               float(unittot[unittot['year']==y].value)*100 for y in unittot.year]
    vacper  = [float(vactot[vactot['year']==y].value) /
               float(unittot[unittot['year']==y].value)*100 for y in unittot.year]

    ownrent_rent = go.Scatter(x = renttot['year'],
                              y = rentper,
                              name = 'Rented',
                              mode = 'lines',
                              marker = dict(color = colorB),
                              hoverinfo = 'text',
                              text = ['{:.0f}%'.format(i) for i in rentper],
                              fill = 'tonexty')
    ownrent_own = go.Scatter(x = owntot['year'],
                             y = ownper,
                             name = 'Owned',
                             mode = 'lines',
                             marker = dict(color = colorA),
                             hoverinfo = 'text',
                             text = ['{:.0f}%'.format(i) for i in ownper],
                             fill ='tonexty')
    ownrent_vac = go.Scatter(x = vactot['year'],
                             y = vacper,
                             name = 'Vacant',
                             mode = 'lines',
                             marker = dict(color = colorC),
                             hoverinfo = 'text',
                             text = ['{:.0f}%'.format(i) for i in vacper],
                             fill = 'tozeroy')
    ownrent_data = [ownrent_vac, ownrent_rent, ownrent_own]
    
    ownrent_lay = go.Layout(xaxis = dict(showgrid = False,
                                         zeroline = False,
                                         showline = True,
                                         automargin=True),
                            yaxis = dict(showgrid = True,
                                         zeroline = False,
                                         showline = True,
                                         title = 'Tenure type (%)',
                                         automargin=True),
                            font = dict(size=fontsize),
                            showlegend = True,
                            legend = dict(x=0.3,
                                          y=1.3,
                                          orientation='h',
                                          bgcolor='rgba(0,0,0,0)'),
                            autosize = False,
                            width = single_width,
                            height = total_height,
                            margin = margin_aff,)
    ownrent_config= dict(showLink = False,
                         modeBarButtonsToRemove = ['sendDataToCloud'],
                         displaylogo = False,
                         responsive = True)
    ownrent_div = py.offline.plot({'data':ownrent_data,
                                  'layout':ownrent_lay},
                                  include_plotlyjs = False,
                                  output_type = 'div',
                                  config = ownrent_config)

    #Renters vs. owners population
    rentpop = df.loc[df['var_name'].isin(['pop_rented'])]
    ownpop  = df.loc[df['var_name'].isin(['pop_owned'])]
    
    rentpopper = [float(rentpop[rentpop['year']==y].value) /
                  (float(ownpop[ownpop['year']==y].value) +
                  float(rentpop[rentpop['year']==y].value))*100 for y in rentpop.year]
    ownpopper  = [float(ownpop[ownpop['year']==y].value) /
                  (float(ownpop[ownpop['year']==y].value) +
                   float(rentpop[rentpop['year']==y].value))*100 for y in ownpop.year]
    
    ownrentpop_rent = go.Scatter(x=rentpop['year'],
                                 y=rentpopper,
                                 name='Renters',
                                 mode='lines',
                                 marker=dict(color = colorB),
                                 hoverinfo='text',
                                 text=['{:.0f}%'.format(i) for i in rentpopper],
                                 fill='tozeroy')
    ownrentpop_own = go.Scatter(x=ownpop['year'],
                                y=ownpopper,
                                name='Owners',
                                mode='lines',
                                marker=dict(color = colorA),
                                hoverinfo = 'text',
                                text=['{:.0f}%'.format(i) for i in ownpopper],
                                fill='tonexty')
    ownrentpop_data = [ownrentpop_rent, ownrentpop_own]
                              
    ownrentpop_lay = go.Layout(xaxis=dict(showgrid=False,
                                          zeroline=False,
                                          showline=True,
                                          automargin=True),
                               yaxis=dict(showgrid=True,
                                          zeroline=False,
                                          showline=True,
                                          title='Population (%)',
                                          automargin=True),
                               font=dict(size=fontsize),
                               showlegend=True,
                               legend=dict(x=0.52,
                                           y=1.3,
                                           orientation='h',
                                           bgcolor='rgba(0,0,0,0)'),
                               autosize=False,
                               width=single_width,
                               height=total_height,
                               margin=margin_aff)
    ownrentpop_config= dict(showLink = False,
                            modeBarButtonsToRemove = ['sendDataToCloud'],
                            displaylogo = False,
                            responsive = True)
    ownrentpop_div = py.offline.plot({'data':ownrentpop_data, 'layout':ownrentpop_lay},
                                     include_plotlyjs=False,
                                     output_type='div',
                                     config=ownrentpop_config)

    #Average household income
    hhincmed_city = df.loc[df['var_name'].isin(['household_income_median'])]
    hhincmed_us   = [51425, 51914, 52762, 53046, 53046, 53482, 53889, 55322]
    hhincmed_st   = [69475, 70647, 72419, 72999, 73538, 74149, 74551, 76067]
    
    hhincmed_city_pct = hhincmed_city.value.pct_change()
    hhincmed_st_pct = pd.Series(hhincmed_st).pct_change()
    hhincmed_us_pct = pd.Series(hhincmed_us).pct_change()
    hhinc_city_hovertxt = [str(hhincmed_city.year.iloc[i])+
                           '<br>{0:+.2f}%'.format(hhincmed_city_pct.iloc[i]*100)
                           for i in np.arange(len(hhincmed_city['year']))]
    hhinc_st_hovertxt = [str(hhincmed_city.year.iloc[i])+
                         '<br>{0:+.2f}%'.format(hhincmed_st_pct.iloc[i]*100)
                         for i in np.arange(len(hhincmed_city['year']))]
    hhinc_us_hovertxt = [str(hhincmed_city.year.iloc[i])+
                         '<br>{0:+.2f}%'.format(hhincmed_us_pct.iloc[i]*100)
                         for i in np.arange(len(hhincmed_city['year']))]
    hhinc_city_hovertxt[0] = str(hhincmed_city.year.iloc[0])
    hhinc_st_hovertxt[0] = str(hhincmed_city.year.iloc[0])
    hhinc_us_hovertxt[0] = str(hhincmed_city.year.iloc[0])
    
    hhinc_city = go.Scatter(x=hhincmed_city['value'],
                            y=np.ones(len(hhincmed_city['value']))*3,
                            mode = 'markers',
                            marker = dict(color = hhincmed_city['year'],
                                          colorscale='Viridis',
                                          cmin=min(hhincmed_city['year']),
                                          cmax=max(hhincmed_city['year']),
                                          size=20,
                                          opacity=0.5,
                                          showscale=True,
                                          line=dict(width=1, color='white'),
                                          reversescale=True,
                                          colorbar=dict(thickness=10,
                                                        y=0.5,
                                                        x=1.0,
                                                        ypad=0,
                                                        title='Year',
                                                        titleside='right',
                                                        outlinewidth=1,
                                                        outlinecolor='white')),
                            hoverinfo = 'text+x',
                            text=hhinc_city_hovertxt)
    hhinc_st = go.Scatter(x=hhincmed_st,
                          y=np.ones(len(hhincmed_city['value']))*2,
                          mode = 'markers',
                          marker = dict(color = hhincmed_city['year'],
                                        colorscale='Viridis',
                                        cmin=min(hhincmed_city['year']),
                                        cmax=max(hhincmed_city['year']),
                                        size=20,
                                        opacity=0.5,
                                        line=dict(width=1, color='white'),
                                        reversescale=True),
                          hoverinfo = 'text+x',
                          text=hhinc_st_hovertxt)
    hhinc_us = go.Scatter(x=hhincmed_us,
                          y=np.ones(len(hhincmed_city['value']))*1,
                          mode = 'markers',
                          marker = dict(color = hhincmed_city['year'],
                                        colorscale='Viridis',
                                        cmin=min(hhincmed_city['year']),
                                        cmax=max(hhincmed_city['year']),
                                        size=20,
                                        opacity=0.5,
                                        line=dict(width=1, color='white'),
                                        reversescale=True),
                          hoverinfo = 'text+x',
                          text=hhinc_us_hovertxt)
    hhinc_data = [hhinc_city, hhinc_st, hhinc_us]
    
    hhinc_lay = go.Layout(xaxis=dict(showgrid=True,
                                     zeroline=False,
                                     nticks=round(max(hhincmed_city['value'])/5000),
                                     showline=True,
                                     title='Median household income',
                                     automargin=True),
                          yaxis=dict(showgrid=True,
                                     zeroline=False,
                                     showline=True,
                                     tickvals=[1,2,3],
                                     ticktext=[gov.country_abbr, gov.state_abbr, gov.name.title(),],
                                     automargin=True),
                          font=dict(size=fontsize),
                          showlegend=False,
                          autosize=False,
                          width=double_width,
                          height=total_height,
                          margin=margin_aff,)
    hhinc_config={'showLink': False, 'displaylogo': False, 'responsive': True}
    hhinc_div = py.offline.plot({'data':hhinc_data, 'layout':hhinc_lay},
                                include_plotlyjs=False,
                                output_type='div',
                                config=hhinc_config)

    # Distribution of prices asked
    priceasked_city = df.loc[df.var_name.str.contains('^house_price_[0-9]+')]
    
    listyears = priceasked_city['year'].unique()
    max_range = 1.5*priceasked_city['value'].max()/(priceasked_city['value'].mean()*24)
    houseprice_data = []
    for y, yr in enumerate(listyears):
        
        houseprice_city_bins = []
        houseprice_stat_bins = []
        houseprice_city_bins.append(priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_01')].value.values[0] +
                                    priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_02')].value.values[0] +
                                    priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_03')].value.values[0] +
                                    priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_04')].value.values[0])
        houseprice_city_bins.append(priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_05')].value.values[0] +
                                    priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_06')].value.values[0] +
                                    priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_07')].value.values[0] +
                                    priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_08')].value.values[0])
        houseprice_city_bins.append(priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_09')].value.values[0] +
                                    priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_10')].value.values[0] +
                                    priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_11')].value.values[0]/2)
        houseprice_city_bins.append(priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_11')].value.values[0]/2 +
                                    priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_12')].value.values[0] +
                                    priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_13')].value.values[0])
                                        
        for n in [14, 15, 16, 17, 18, 19, 20, 21]:
            houseprice_city_bins.append( priceasked_city[(priceasked_city['year']==yr) &
                                                         (priceasked_city['var_name']=='house_price_'+'{:02.0f}'.format(n))].value.values[0] )
        
        houseprice_city_bins.append(priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_22')].value.values[0] +
                                    priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_23')].value.values[0] +
                                    priceasked_city[(priceasked_city['year']==yr) &
                                                    (priceasked_city['var_name']=='house_price_24')].value.values[0])

        tot = sum([float(i) for i in houseprice_city_bins])
        norm = [-1*float(i)/tot for i in houseprice_city_bins]
        ylab = ['{:.0f}%'.format(-1*float(i)*100)  for i in norm]
        houseprice_city = go.Bar(y=np.arange(len(norm)),
                                 x=norm,
                                 base=y*max_range*2,
                                 orientation='h',
                                 name=gov.name,
                                 hoverinfo='text',
                                 text=ylab,
                                 hoverlabel=dict(bgcolor=colorA, bordercolor='white'),
                                 marker=dict(color=colorA, opacity=0.5))
        if y!=0: houseprice_city.update(dict(showlegend= False))
        houseprice_data.append(houseprice_city)

        norm_c = [float(i)/tot for i in houseprice_city_bins]
        ylab_c = [str(round(float(i)*100))+'%' for i in norm]
        houseprice_state = go.Bar(y=np.arange(len(norm_c)),
                                  x=norm_c,
                                  base=y*max_range*2,
                                  orientation='h',
                                  name=gov.state_abbr,
                                  hoverinfo='text',
                                  text=ylab,
                                  hoverlabel=dict(bgcolor=colorB, bordercolor='white'),
                                  marker=dict(color=colorB, opacity=0.5))
        if y!=0: houseprice_state.update(dict(showlegend= False))
        houseprice_data.append(houseprice_state)

    
        
    
    housevalmed_city = df.loc[df['var_name'].isin(['house_median_value'])]
    yval = [12500, 37500, 62500, 87500, 112500, 137500, 162500, 187500, 225000, 275000, 350000, 450000, 750000]
    f = interp1d(yval, np.arange(len(yval)), kind='cubic', bounds_error=False, fill_value=len(yval))
    avg_city_val = f(housevalmed_city.value.values)
    avg_city = go.Scatter(x=np.arange(len(housevalmed_city.year))*max_range*2,
                          y=avg_city_val,
                          mode = 'lines',
                          line=dict(width=1.0),
                          marker = dict(color = colorA),
                          hoverinfo = 'none',
                          showlegend = False)
    houseprice_data.append(avg_city)
    avg_stat = go.Scatter(x=np.arange(len(housevalmed_city.year))*max_range*2,
                          y=avg_city_val+0.5,
                          mode = 'lines',
                          line=dict(width=1.0),
                          marker = dict(color = colorB),
                          hoverinfo = 'none',
                          showlegend = False)
    houseprice_data.append(avg_stat)
    


    ylab = [' ', '50', ' ', '100', ' ', '150', ' ', '200',
            ' ', '300', ' ', '500']
    houseprice_lay = go.Layout(yaxis=dict(title='Price (k$)',
                                          tickvals=np.arange(len(ylab))+0.5,
                                          ticktext=ylab,
                                          showgrid=True,
                                          zeroline=False,
                                          showline=True,
                                          automargin=True),
                               xaxis=dict(range=[-max_range, 2*max_range*len(listyears)-max_range],
                                          ticktext=listyears,
                                          tickvals=np.arange(len(listyears))*max_range*2,
                                          showgrid=False,
                                          zeroline=False,
                                          showline=True,
                                          automargin=True),
                               autosize=False,
                               width=double_width,
                               height=total_height,
                               barmode='overlay',
                               bargap=0.,
                               hovermode='y',
                               hoverdistance=10,
                               legend=dict(x=0.75,
                                           y=1.3,
                                           orientation='h',
                                           bgcolor='rgba(0,0,0,0)'),
                               font=dict(size=10),
                               margin=margin_aff)
    
    houseprice_config={'showLink': False, 'displaylogo': False, 'responsive': True}
    houseprice_div = py.offline.plot({"data":houseprice_data,
                                     "layout":houseprice_lay},
                                     include_plotlyjs=False,
                                     output_type='div',
                                     config=ownrentpop_config)

    #Average househould size owners vs. renters
    ppsize_own = df.loc[df['var_name'].isin(['household_average_size_own'])]
    ppsize_rent = df.loc[df['var_name'].isin(['household_average_size_rent'])]
    
    bdsize_own_distr = df.loc[df.var_name.str.contains('house_own_.beds')]
    bdsize_own = []
    for yr in ppsize_own.year:
        sumbd = 0
        for bd in [1, 2, 3, 4, 5]:
            sumbd += bd * bdsize_own_distr[(bdsize_own_distr.year==yr) & (bdsize_own_distr.var_name=='house_own_'+str(bd)+'beds')].value.values[0]
        totbd = np.sum(bdsize_own_distr[bdsize_own_distr.year==yr].value)
        bdsize_own.append(sumbd/totbd)
    bdsize_rent_distr = df.loc[df.var_name.str.contains('house_rent_.beds')]
    bdsize_rent = []
    for yr in ppsize_own.year:
        sumbd = 0
        for bd in [1, 2, 3, 4, 5]:
            sumbd += bd * bdsize_rent_distr[(bdsize_rent_distr.year==yr) & (bdsize_rent_distr.var_name=='house_rent_'+str(bd)+'beds')].value.values[0]
        totbd = np.sum(bdsize_rent_distr[bdsize_rent_distr.year==yr].value)
        bdsize_rent.append(sumbd/totbd)

    hhsize_own = go.Bar(x = ppsize_own.year,
                        y = ppsize_own.value.values/bdsize_own,
                        name = 'Owned',
                        marker = dict(color = colorA),
                        opacity=0.6,
                        hoverinfo = 'y',)
    hhsize_rent = go.Bar(x = ppsize_rent.year,
                         y = ppsize_rent.value.values/bdsize_rent,
                         name = 'Rented',
                         marker = dict(color = colorB),
                         opacity=0.5,
                         hoverinfo = 'y')
    hhsize_data = [hhsize_own, hhsize_rent]

    min_hhsize = min(min(ppsize_own.value.values/bdsize_own), min(ppsize_rent.value.values/bdsize_rent))
    max_hhsize = max(max(ppsize_own.value.values/bdsize_own), max(ppsize_rent.value.values/bdsize_rent))
    hhsize_lay = go.Layout(barmode = 'group',
                           font = dict(size=fontsize),
                            yaxis = dict(hoverformat = '.2f',
                                         showline=True,
                                         title='Occupancy',
                                         automargin=True,
                                         range=[0.6*min_hhsize,1.1*max_hhsize]),
                           xaxis = dict(showline=True),
                           legend=dict(x=0.53,
                                       y=1.3,
                                       orientation='h',
                                       bgcolor='rgba(0,0,0,0)'),
                           hovermode='closest',
                           width = single_width,
                           height = total_height,
                           margin = margin_aff)
    hhsize_config = dict(showLink = False,
                         modeBarButtonsToRemove = ['sendDataToCloud'],
                         displaylogo = False,
                         responsive = True)
    hhsize_div = py.offline.plot({"data":hhsize_data,
                                 "layout":hhsize_lay},
                                 include_plotlyjs=False,
                                 output_type='div',
                                 config=hhsize_config)

    # Monthly housing expenses and income
    incmed_own = df.loc[df['var_name'].isin(['household_income_own_median'])]
    incmed_rent = df.loc[df['var_name'].isin(['household_income_rent_median'])]
    rent_median = df.loc[df['var_name'].isin(['rent_gross_median'])]
    owncost_median  = df.loc[df['var_name'].isin(['own_costs_med_mortg'])]

    monthexp_inc_own = go.Bar(x = incmed_own.year,
                              y = incmed_own.value.values/12,
                              name = 'Owners income',
                              opacity = 0.5,
                              hoverinfo='text',
                              text = ['Net income:<br>${:.0f}'.format(x) for x in
                                      incmed_own.value.values/12 - owncost_median.value],
                              marker = dict(color = colorA))
    monthexp_inc_rent = go.Bar(x = incmed_rent.year,
                               y = incmed_rent.value.values/12,
                               name = 'Renters income',
                               opacity=0.5,
                               hoverinfo='text',
                               text = ['Net income:<br>${:.0f}'.format(x) for x in
                                       incmed_rent.value.values/12 - rent_median.value],
                               marker = dict(color = colorB))
    monthexp_rent = go.Scatter(x = rent_median.year,
                               y = rent_median.value,
                               name = 'Renters expenses',
                               mode = 'lines',
                               hoverinfo='none',
                               line = dict(color = colorB,
                                           width = 1))
    monthexp_own = go.Scatter(x = owncost_median.year,
                               y = owncost_median.value,
                               name = 'Owners expenses',
                               mode = 'lines',
                               hoverinfo='none',
                               line = dict(color = colorA,
                                           width = 1))
    monthexp_data = [monthexp_inc_own, monthexp_inc_rent, monthexp_own, monthexp_rent]

    range_max_plot = max(incmed_own.value.values/12)
    monthexp_lay = go.Layout(xaxis = dict(showgrid = False,
                                          zeroline = False,
                                          showline = True,
                                          automargin=True),
                             yaxis = dict(showgrid = True,
                                          zeroline = False,
                                          showline = True,
                                          title='$',
                                          hoverformat = '.0f',
                                          automargin=True,
                                          range=[0, 1.15*range_max_plot]),
                             font = dict(size=fontsize),
                             showlegend = True,
                             legend = dict(x=0.4,
                                           y=1.5,
                                           orientation='h',
                                           bgcolor='rgba(0,0,0,0)'),
                             autosize = False,
                             width = single_width,
                             height = total_height,
                             margin = margin_aff)
    monthexp_config= dict(showLink = False,
                          modeBarButtonsToRemove = ['sendDataToCloud'],
                          displaylogo = False,
                          responsive = True)
    monthexp_div = py.offline.plot({'data':monthexp_data,
                                   'layout':monthexp_lay},
                                   include_plotlyjs = False,
                                   output_type = 'div',
                                   config = ownrent_config)

    # Rent by number of bedrooms
    numbeds = [0, 1, 2, 3]
    colors_beds = ['purple', colorA, colorC, colorB]
    minbins_2009 = [0, 200, 300, 500, 750, 1000]
    minbins_2015 = [0, 300, 500, 750, 1000, 1500]
    
    beds_data = []
    for bd in numbeds:
        med_arr = []
        for yr in incmed_own.year:
            rent_beds_distr = df.loc[df.var_name.str.contains('^rent_gross_'+str(bd)+'beds_')]
            freq = rent_beds_distr[rent_beds_distr.year==yr].value.values
            if yr < 2015:
                med = median_from_hist(minbins_2009, freq)
            else:
                med = median_from_hist(minbins_2015, freq)
            med_arr.append(med)
        beds_data.append(go.Scatter(x=incmed_own.year,
                                    y = med_arr,
                                    name = str(bd)+' bdr',
                                    mode = 'lines+markers',
                                    hoverinfo='y',
                                    line = dict(color = colors_beds[bd],
                                                width = 2)))

    beds_lay = go.Layout(xaxis = dict(showgrid = False,
                                      zeroline = False,
                                      showline = True,
                                      automargin=True),
                         yaxis = dict(showgrid = True,
                                      zeroline = False,
                                      showline = True,
                                      title='Median gross rent',
                                      hoverformat = '$.0f',
                                      automargin=True),
                         font = dict(size=fontsize),
                         showlegend = True,
                         legend = dict(x=0.15,
                                       y=1.3,
                                       orientation='h',
                                       bgcolor='rgba(0,0,0,0)'),
                         autosize = False,
                         width = single_width,
                         height = total_height,
                         margin = margin_aff)
    beds_config= dict(showLink = False,
                      modeBarButtonsToRemove = ['sendDataToCloud'],
                      displaylogo = False,
                      responsive = True)
    beds_div = py.offline.plot({'data':beds_data,
                               'layout':beds_lay},
                               include_plotlyjs = False,
                               output_type = 'div',
                               config = ownrent_config)



    context = {
        'govid':gov.id,
        'cityname_div':cityname_div,
        'ownrent_div':ownrent_div,
        'ownrentpop_div':ownrentpop_div,
        'hhsize_div':hhsize_div,
        'hhinc_div':hhinc_div,
        'houseprice_div':houseprice_div,
        'monthexp_div':monthexp_div,
        'beds_div':beds_div
    }


    return render(
        request,
        'housing_affordability/affordability_overview.html',
        context
        )

def median_from_hist(minbins, freq, tot=0):
    '''find the median of a distribution for which we know the histogram
        inputs: minbins: minimum value of each bin/group
        freq: frequencies of the histogram
        tot: total number of events
        '''
    # Cumulative distribution
    distr_cum = np.array(freq).cumsum()

    # Total number of observations
    if tot==0:
        tot = distr_cum[-1]
    
    # Locate bin containing median
    idx = (np.abs(distr_cum - tot/2)).argmin()
    
    # Assume homogeneous distribution inside the bin to find median
    med = minbins[idx] + ((tot/2 - distr_cum[idx-1]) / freq[idx]) * (minbins[idx+1] - minbins[idx])

    return med


def affordability_index(request, gov_id):
    '''project profile page'''
    
    #General plot settings
    colorA = 'orange'
    colorB = 'darkcyan'
    colorC = 'lightgrey'
    fontsize = 10
    margin_aff=go.layout.Margin(l=45, r=20, b=50, t=50, pad=0)
    single_width = 410
    double_width = 780
    total_height = 205
    
    plot_config= dict(showLink = False,
                      modeBarButtonsToRemove = ['sendDataToCloud',
                                                'lasso2d',
                                                'select2d',
                                                'pan2d',
                                                'autoScale2d',
                                                'toggleHover',
                                                #'zoomIn2d',
                                                #'zoomIn2d'
                                                ],
                      displaylogo = False,
                      responsive = True,
                      scrollZoom = True)
    
    #Data request
    gov = Government.objects.get(id=gov_id)
    demos = Gov_Demographic.objects.filter(gov_id=gov_id)
    demos = pd.DataFrame(list(demos.values()))
    demos.dropna(inplace=True)
    demos_source = Gov_Demographics_Source.objects.all()
    demos_source = pd.DataFrame(list(demos_source.values()))
    demos['value'] = [(i > 0) * i for i in demos['value']]
    df = demos.merge(demos_source, left_on = 'var_id', right_on = 'id')[['var_name','description','year','value']]
    
    #City name
    cityname_div = gov.name+', '+gov.state_abbr
    
    #Housing/Renting prices
    hhinc_med = df.loc[df['var_name'].isin(['household_income_median'])]
    houseval_med = df.loc[df['var_name'].isin(['house_median_value'])]
    rent_med = df.loc[df['var_name'].isin(['rent_contract_median'])]
    
    hhinc_y = hhinc_med.value.pct_change().fillna(0).cumsum()*100
    hhinc = go.Bar(x=hhinc_med.year,
                   y= hhinc_y,
                   name='HH income',
                   marker = dict(color = colorC),
                   opacity = 0.7,
                   hoverinfo = 'text',
                   text= ['{:.1f}%'.format(i) for i in hhinc_y])
    houseval_y = houseval_med.value.pct_change().fillna(0).cumsum()*100
    houseval = go.Scatter(x=houseval_med.year,
                          y= houseval_y,
                          name='House value',
                          mode = 'lines+markers',
                          marker = dict(color = colorA),
                          hoverinfo = 'text',
                          text = ['{:.1f}%'.format(i) for i in houseval_y])
    rent_y = rent_med.value.pct_change().fillna(0).cumsum()*100
    rent = go.Scatter(x=rent_med.year,
                      y=rent_y,
                      name='Monthly rent',
                      mode = 'lines+markers',
                      marker = dict(color = colorB),
                      hoverinfo = 'text',
                      text = ['{:.1f}%'.format(i) for i in rent_y])
    pricechange_data = [houseval, rent, hhinc]
    
    pricechange_lay = go.Layout(xaxis=dict(showgrid=False,
                                           zeroline=False,
                                           showline=True,
                                           automargin=True),
                                yaxis=dict(showgrid=True,
                                           zeroline=False,
                                           showline=True,
                                           title='% change',
                                           automargin=True),
                                showlegend=True,
                                legend=dict(x=0.1,
                                            y=1.3,
                                            orientation='h'),
                                font = dict(size=fontsize),
                                autosize=False,
                                width = single_width,
                                height = total_height,
                                margin = margin_aff)
    
    pricechange_div = py.offline.plot({'data':pricechange_data,
                                      'layout':pricechange_lay},
                                      include_plotlyjs = False,
                                      output_type = 'div',
                                      config = plot_config)
                
    
    #Affordability
    own_costs_mortg = df.loc[df['var_name'].isin(['owner_costs_pctincome_mortg_median'])]
    own_costs_nomortg = df.loc[df['var_name'].isin(['owner_costs_pctincome_nomortg_median'])]
    rent_costs = df.loc[df['var_name'].isin(['rent_gros_pctincome_median'])]
    
    aff_own_nomortg = go.Bar(x=own_costs_nomortg.year,
                             y=own_costs_nomortg.value,
                             name='Owners w/o mortgage',
                             marker = dict(color = colorC),
                             opacity = 0.6,
                             hoverinfo = 'text',
                             text = ['{:.1f}%'.format(i) for i in own_costs_nomortg.value])
    aff_own_mortg = go.Bar(x=own_costs_mortg.year,
                           y=own_costs_mortg.value,
                           name='Owners w/ mortgage',
                           marker = dict(color = colorA),
                           opacity = 0.6,
                           hoverinfo = 'text',
                           text = ['{:.1f}%'.format(i) for i in own_costs_mortg.value])
    aff_rent = go.Bar(x=rent_costs.year,
                      y=rent_costs.value,
                      name='Renters',
                      marker = dict(color = colorB),
                      opacity = 0.6,
                      hoverinfo = 'text',
                      text = ['{:.1f}%'.format(i) for i in rent_costs.value])
    aff_percent = go.Scatter(x=rent_costs.year,
                             y=np.ones(len(rent_costs.year))*30,
                             name='Affordability threshold',
                             mode = 'lines',
                             marker = dict(color = 'Red'),
                             line=dict(width=1),
                             hoverinfo='none')
    aff_data = [aff_percent, aff_rent, aff_own_mortg, aff_own_nomortg]
    
    aff_lay = go.Layout(xaxis=dict(showgrid=False,
                                   zeroline=False,
                                   showline=True,
                                   automargin=True),
                        yaxis=dict(showgrid=True,
                                   zeroline=False,
                                   showline=True,
                                   title='% hh income',
                                   automargin=True),
                        showlegend=True,
                        legend=dict(x=0.5,
                                    y=1.6,
                                    orientation='h',
                                    bgcolor='rgba(0,0,0,0)'),
                        font = dict(size=fontsize),
                        autosize=False,
                        width = single_width,
                        height = total_height,
                        margin = margin_aff)
    
    aff_div = py.offline.plot({'data':aff_data,
                              'layout':aff_lay},
                              include_plotlyjs = False,
                              output_type = 'div',
                              config = plot_config)
    
    #Low income affordability
    # Note that variables for this plot have changed in the Census since 2009 to add
    # more bins to the distribution of gross rents. However, we probably do not need
    # them to calculate ELI, and therefore are not added to the list of vars.
    med_inc = df.loc[df['var_name'].isin(['income_median'])]
    rent_costs_distr = df.loc[df.var_name.str.contains('^rent_gross_distr_')]
    own_costs_distr = df.loc[df.var_name.str.contains('^own_costs_distr_')]
    rent_tot = df.loc[df['var_name'].isin(['rent_gross_cashtot'])]
    own_tot = df.loc[df['var_name'].isin(['house_owner_occupied'])]
    
    # Inferior range limit of the bin
    rent_ranges = np.array([0, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550,
                            600, 650, 700, 750, 800, 900, 1000, 1250, 1500, 2000])
    own_ranges = np.array([0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500])
    rent_midbin = (rent_ranges[1:] - rent_ranges[:-1])/2 + rent_ranges[:-1]
    own_midbin = (own_ranges[1:] - own_ranges[:-1])/2 + own_ranges[:-1]
    
    def eli_get_data(yr):

        #Total units
        rent_units = rent_tot[rent_tot.year==yr].value.values[0]
        own_units = own_tot[own_tot.year==yr].value.values[0]
    
        #ELI: Extremely low income below 30% of the median income
        eli_budget = med_inc[med_inc.year==yr].value/12*0.3*0.3
    
        #Cumulative distributions
        rent_distr_cum = rent_costs_distr[rent_costs_distr.year==yr].value.cumsum()
        own_distr_cum = own_costs_distr[own_costs_distr.year==yr].value.cumsum()
    
        #Fit cumulative distribution
        fint_rent = interp1d(rent_midbin, rent_distr_cum[:len(rent_midbin)], kind='cubic')
        fint_own = interp1d(own_midbin, own_distr_cum[:len(own_midbin)], kind='cubic')
        
        #ELI available units
        avail_rent = fint_rent(eli_budget)
        avail_own = fint_own(eli_budget)
        
        data = [[avail_rent[0], rent_units-avail_rent[0]],
                [avail_own[0], own_units-avail_own[0]]]
        
        return data
    
    dt_init = eli_get_data(med_inc.year.iloc[0])
    eli_rent = go.Pie(values = dt_init[0],
                      labels = ['ELI affordable', 'ELI not affordable'])
    eli_own = go.Pie(values = dt_init[1],
                     labels = ['ELI affordable', 'ELI not affordable'])
    eli_data = [eli_own, eli_rent]

    eli_frames = []
    eli_slider_steps = []
    for yr in rent_tot.year:
        dt_yr = eli_get_data(yr)
        eli_rent_yr = go.Pie(values = dt_yr[0],
                             labels = ['ELI affordable', 'ELI not affordable'],
                             hoverinfo = 'text',
                             hovertext = ['ELI affordable:<br>{:,.0f} units'.format(dt_yr[0][0]),
                                          'ELI not affordable:<br>{:,.0f} units'.format(dt_yr[0][1])],
                             text = ['{:.1f}%'.format(dt_yr[0][0]/(dt_yr[0][0]+dt_yr[0][1])*100), ' '],
                             textinfo = 'text',
                             textposition = 'outside',
                             marker = dict(colors=[colorA, colorC],
                                           line=dict(color='#ffffff', width=2)),
                             hole = 0,
                             domain = dict(x = [0, .48]),
                             showlegend = False)
        eli_own_yr = go.Pie(values = dt_yr[1],
                            labels = ['ELI affordable', 'ELI not affordable'],
                            hoverinfo = 'text',
                            hovertext = ['ELI affordable:<br>{:,.0f} units'.format(dt_yr[1][0]),
                                    'ELI not affordable:<br>{:,.0f} units'.format(dt_yr[1][1])],
                            text = ['{:.1f}%'.format(dt_yr[1][0]/(dt_yr[1][0]+dt_yr[1][1])*100), ' '],
                            textinfo = 'text',
                            textposition = 'outside',
                            marker = dict(colors=[colorB, colorC],
                                          line=dict(color='#ffffff', width=2)),
                            hole = 0,
                            domain = dict(x = [.52, 1]),
                            showlegend = False)
                            
        slider_step = dict(args = [[yr], dict(
                                              frame = dict(duration = 500,
                                                           redraw = False),
                                              mode = 'immediate',
                                              transition = dict(duration= 150))],
                           label= yr,
                           method = 'animate')
    
        eli_frames.append(dict(data=[eli_rent_yr, eli_own_yr], name='{:.0f}'.format(yr)))
        eli_slider_steps.append(slider_step)
    
    eli_lay = go.Layout(annotations = [dict(font = dict(size = fontsize),
                                            showarrow = False,
                                            text = 'Own',
                                            x = 0.2,
                                            y = 0.35),
                                       dict(font = dict(size = fontsize),
                                            showarrow = False,
                                            text = 'Rent',
                                            x = 0.8,
                                            y = 0.35)],
                        font = dict(size=fontsize),
                        width = single_width,
                        height = total_height,
                        margin = margin_aff,
                        updatemenus = [dict(type = 'buttons',
                                            buttons = [dict(label= 'Play',
                                                            method = 'animate',
                                                            args = [None])],
                                            
                                            bgcolor = 'white',
                                            bordercolor = colorC,
                                            showactive = False,
                                            x = 0.2,
                                            y = -0.27)],
                        sliders = [dict(active = 0,
                                        currentvalue = dict(prefix = 'Year: ',
                                                            visible = True,
                                                            xanchor = 'right',
                                                            offset = 4),
                                        transition = dict(duration = 150,
                                                          easing = 'cubic-in-out'),
                                        visible = True,
                                        bgcolor = 'white',
                                        activebgcolor = colorC,
                                        bordercolor = colorC,
                                        ticklen = 5,
                                        tickcolor = colorC,
                                        x = 0.25,
                                        y = 0,
                                        len = 0.75,
                                        pad = dict(t=0),
                                        steps = eli_slider_steps)]
                        )
    
    eli_div = py.offline.plot({'data':eli_data,
                              'frames':eli_frames,
                              'layout':eli_lay},
                              include_plotlyjs = False,
                              output_type = 'div',
                              config = plot_config)

    #Renters affordability by age
    rent_aff_age_distr = df.loc[df.var_name.str.contains('^renter_costs_pctincome_age_')]
    rent_age_distr = df.loc[df.var_name.str.contains('^renthh_age_distrib_')]

    colors_aff_age = [colorA, colorB, colorC, '#57114c']
    labels_aff_age = ['15-24yr', '25-34yr', '35-64yr', '65+yr']
    
    fig_affage_rent = tools.make_subplots(rows=2,
                                          cols=1,
                                          specs=[[{}], [{}]],
                                          shared_xaxes=True,
                                          shared_yaxes=True,
                                          vertical_spacing=0.1)
                                         
    aff_age_x = rent_aff_age_distr[rent_aff_age_distr.var_name=='renter_costs_pctincome_age_1'].year
    for i in np.arange(4)[::-1]:
        y = rent_aff_age_distr[rent_aff_age_distr.var_name=='renter_costs_pctincome_age_'+str(i*2+1)].value.values + \
            rent_aff_age_distr[rent_aff_age_distr.var_name=='renter_costs_pctincome_age_'+str(i*2+2)].value.values
        t = rent_age_distr[rent_age_distr.var_name=='renthh_age_distrib_'+str(i+1)].value.values
        fig_affage_rent.append_trace(go.Bar(x = aff_age_x,
                                            y = y,
                                            hoverinfo = 'y',
                                            name = labels_aff_age[i],
                                            marker = dict(color = colors_aff_age[i]),
                                            opacity = 0.6), 1, 1)
        fig_affage_rent.append_trace(go.Scatter(x = aff_age_x,
                                                y = 100*y/t,
                                                mode = 'lines+markers',
                                                hoverinfo = 'text',
                                                hovertext = ['{:.0f}%'.format(100*x) for x in y/t],
                                                marker = dict(color = colors_aff_age[i]),
                                                line=dict(width=2),
                                                showlegend= False), 2, 1)

    affage_lay_rent = dict(xaxis=dict(showgrid=False,
                                      zeroline=False,
                                      showline=True,
                                      automargin=True),
                           yaxis1=dict(showgrid=True,
                                       zeroline=False,
                                       showline=True,
                                       title='no. of homes',
                                       hoverformat = '{:.0f}',
                                       automargin=True),
                           yaxis2=dict(title='% householders',
                                       hoverformat = '{:.0f}',
                                       showline=True,
                                       automargin=True),
                           barmode='stack',
                           showlegend=True,
                           legend=dict(x=0.,
                                       y=1.15,
                                       orientation='h',
                                       bgcolor='rgba(0,0,0,0)'),
                           font = dict(size=fontsize),
                           autosize=False,
                           width = 1.05*single_width,
                           height = 1.5*total_height,
                           margin = margin_aff)
    fig_affage_rent['layout'].update(affage_lay_rent)

    affage_rent_div = py.offline.plot(fig_affage_rent,
                                      include_plotlyjs = False,
                                      output_type = 'div',
                                      config = plot_config)

    #Owners affordability by age
    own_aff_age_distr = df.loc[df.var_name.str.contains('^owner_costs_pctincome_age_')]
    own_age_distr = df.loc[df.var_name.str.contains('^ownhh_age_distrib_')]


    fig_affage_own = tools.make_subplots(rows=2,
                                         cols=1,
                                         specs=[[{}], [{}]],
                                         shared_xaxes=True,
                                         shared_yaxes=True,
                                         vertical_spacing=0.1)

    aff_age_x = own_aff_age_distr[own_aff_age_distr.var_name=='owner_costs_pctincome_age_1'].year
    for i in np.arange(4)[::-1]:
        y = own_aff_age_distr[own_aff_age_distr.var_name=='owner_costs_pctincome_age_'+str(i*2+1)].value.values + \
            own_aff_age_distr[own_aff_age_distr.var_name=='owner_costs_pctincome_age_'+str(i*2+2)].value.values
        t = own_age_distr[own_age_distr.var_name=='ownhh_age_distrib_'+str(i+1)].value.values
        fig_affage_own.append_trace(go.Bar(x = aff_age_x,
                                           y = y,
                                           hoverinfo = 'y',
                                           name = labels_aff_age[i],
                                           marker = dict(color = colors_aff_age[i]),
                                           opacity = 0.6), 1, 1)
        fig_affage_own.append_trace(go.Scatter(x = aff_age_x,
                                               y = 100*y/t,
                                               mode = 'lines+markers',
                                               hoverinfo = 'text',
                                               hovertext = ['{:.0f}%'.format(100*x) for x in y/t],
                                               marker = dict(color = colors_aff_age[i]),
                                               line=dict(width=2),
                                               showlegend= False), 2, 1)

    fig_affage_own['layout'].update(affage_lay_rent)

    affage_own_div = py.offline.plot(fig_affage_own,
                                      include_plotlyjs = False,
                                      output_type = 'div',
                                      config = plot_config)

    context = {
        'govid':gov.id,
        'cityname_div':cityname_div,
        'pricechange_div':pricechange_div,
        'aff_div':aff_div,
        'eli_div':eli_div,
        'affagerent_div':affage_rent_div,
        'affageown_div':affage_own_div,
    }
    
    
    return render(
                  request,
                  'housing_affordability/affordability_index.html',
                  context
                  )

