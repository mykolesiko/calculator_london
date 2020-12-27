import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_leaflet as dl

import numpy as np
import pandas as pd

import branca.colormap as cm

from data_model import get_sample_data
from airbnb_model import get_price
from airbnb_model import get_options, make_prediction
import plotly.express as px
import plotly



property_list = ['Earth house', 'Hut', 'Treehouse', 'Townhouse', 'Tipi', 'Yurt', 'Apartment', 'Hostel', 'Parking Space', 'Cottage', 'Farm stay', 'Aparthotel', 'Nature lodge', 'Bed and breakfast', 'Guesthouse', 'Tiny house', 'Villa', 'Cabin', 'Boutique hotel', 'Lighthouse', 'Ryokan (Japan)', 'Tent', 'Other', 'Casa particular (Cuba)', 'Houseboat', 'Guest suite', 'Bus', 'Boat', 'Hotel', "Shepherd's hut (U.K., France)", 'Loft', 'Bungalow', 'Camper/RV', 'Chalet', 'Igloo', 'Dome house', 'House', 'Resort', 'Barn', 'Island', 'Serviced apartment', 'Condominium']
room_type_list = ['Entire home/apt', 'Private room', 'Shared room']
cancel_list = ['moderate', 'flexible', 'strict', 'super_strict_30', 'super_strict_60', 'strict_14_with_grace_period']
neighbourhood_list = ['Greenwich', 'Islington', 'Enfield', 'Westminster', 'Brent', 'Bexley', 'Hounslow', 'Camden', 'Haringey', 'Harrow', 'Redbridge', 'Croydon', 'Southwark', 'Tower Hamlets', 'Newham', 'Lewisham', 'Kensington and Chelsea', 'Hillingdon', 'Hackney', 'Sutton', 'Richmond upon Thames', 'Barking and Dagenham', 'Bromley', 'Barnet', 'Havering', 'City of London', 'Merton', 'Ealing', 'Waltham Forest', 'Wandsworth', 'Kingston upon Thames', 'Lambeth', 'Hammersmith and Fulham']

neighbourhood_cleansed_options = get_options(neighbourhood_list)
room_type_options = get_options(room_type_list)
cancel_options = get_options(cancel_list)
property_options = get_options(property_list)



carto_urls = {
    'carto_dark' : 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
    'carto_light': 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
    'carto_color': 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
}
carto_attribution = '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attributions">CARTO</a>'
carto_subdomatins='abcd'
carto_tile_layers = [
    dl.BaseLayer(
        dl.TileLayer(url=carto_urls[key], attribution=carto_attribution, subdomains=carto_subdomatins, maxZoom=20),
        name=key, 
        checked=(key == "carto_dark"),
    ) 
    for key in carto_urls
] 

def reversed_colormap(existing):
    return cm.LinearColormap(
        colors=list(reversed(existing.colors)),
        vmin=existing.vmin, 
        vmax=existing.vmax
    )

def price_markers(df_lat_lon, price, price_model, colmap=reversed_colormap(cm.linear.RdYlGn_09)):
    markers=[]
    vmax = price.median() * 2
    colormap = colmap.scale(0, vmax)
    df = df_lat_lon[['latitude', 'longitude']]
    df.loc[:,'price'] = price
    df.loc[:,'price_model'] = price_model
    for row in df.itertuples():
        text_price = str(int(row.price))
        text_color = 'black' if row.price < row.price_model else 'blue'
        marker = dl.DivMarker(
                    position=[row.latitude, row.longitude],
                    title='Estimate price = {} $'.format(row.price_model),
                    iconOptions={
                        'iconSize' : (22,20),
                        'icon_anchor' : (11,10),
                        'html' : '<div style="font-size: 10pt; background-color: %s; '
                            'color: %s; text-align: center">%s</div>' % 
                            (colormap(row.price), text_color, text_price),
                        }
                     )
        markers.append(marker)
    return markers

app = dash.Dash()
app.layout = html.Div(
    [
     html.Table([
        html.Tr([
          html.Td(children=[
            html.Div([
    
            #html.Br(),
            #html.Label('District', style = {"width" : "100", "color" : "blue", "font-size": "20px"}), 
            #html.Br(),
           
            #dcc.Dropdown(id = 'reg',
            #options = neighbourhood_cleansed_options,
            #options = [{'label': 'Westminster ', 'value': 'Westminster'},
            #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
            #value=neighbourhood_cleansed_options[0]['value'], style = {"width" : "30%"}),
            #value='Greenwich', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue", "display": "inline-block", "font-size": "16px"}),
            html.Table([
                    html.Tr([
                        html.Th(html.Label('Evaluate the price of your FLAT!', style = {"color" : "blue", "font-size": "20px", "width" : "100%"}), style = {"width" : "80%"}),
                        html.Th(html.Label('Filtered by feature ON MAP ', style = {"color" : "blue", "font-size": "20px", "width" : "100%"}), style = {"width" : "20%"})  
                    ])
            ], style = {"width" : "100%"}),
            
            
            html.Table([
                    html.Tr([
                        html.Td(children = [html.Label('District', style = {"color" : "blue", "font-size": "20px", "width" : "100%"}), 
                        dcc.Dropdown(id = 'reg',
                                      options = neighbourhood_cleansed_options,
                                      #options = [{'label': 'Westminster ', 'value': 'Westminster'},
                                      #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
                                      #value=neighbourhood_cleansed_options[0]['value'], style = {"width" : "30%"}),
                                      value='Greenwich', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue", "display": "inline-block", "font-size": "16px"}, multi=False)     
                    ], style = {"width" : "80%"}),
                    html.Td(dcc.Checklist(id = "reg_check", options=[{'label': '', 'value': ''}],style = {"width" : "100%", 'zoom' : '3.0'}),  style = {"width" : "20%"})], style = {"width" : "100%"}
                ),  
                
            ], style = {"width" : "100%"}),
            
            
            
            html.Br(),
      
            
            #html.Label('Room type', style = {"color" : "blue", "font-size": "20px"}), 
            #html.Br(),
            #dcc.Dropdown( id = 'room_type',
            #options = room_type_options,
            #value='Entire home/apt', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue", "display": "inline-block", "font-size": "16px"}),
            
            html.Table([
                    html.Tr([
                        html.Td(children = [html.Label('Room type', style = {"color" : "blue", "font-size": "20px", "width" : "100%"}), 
                        dcc.Dropdown(id = 'room_type',
                                      options = room_type_options,
                                      #options = [{'label': 'Westminster ', 'value': 'Westminster'},
                                      #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
                                      #value=neighbourhood_cleansed_options[0]['value'], style = {"width" : "30%"}),
                                      value='Entire home/apt', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue", "display": "inline-block", "font-size": "16px"})     
                    ], style = {"width" : "80%"}),
                    html.Td(dcc.Checklist(id = "room_check", options=[{'label': '', 'value': ''}],style = {"width" : "100%", 'zoom' : '3.0'}),  style = {"width" : "20%"})], style = {"width" : "100%"}
                ),  
                
            ], style = {"width" : "100%"}),
            
            
            html.Br(),
            
            #html.Label('Cancellation policy', style = {"color" : "blue", "font-size": "20px"}), 
            #html.Br(),
            #dcc.Dropdown( id = 'cancel',
            #options = cancel_options,
           
            #value='moderate', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue", "display": "inline-block", "font-size": "16px"}),
            
            html.Table([
                    html.Tr([
                        html.Td(children = [html.Label('Cancellation policy', style = {"color" : "blue", "font-size": "20px", "width" : "100%"}), 
                        dcc.Dropdown(id = 'cancel',
                                      options = cancel_options,
                                      #options = [{'label': 'Westminster ', 'value': 'Westminster'},
                                      #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
                                      #value=neighbourhood_cleansed_options[0]['value'], style = {"width" : "30%"}),
                                      value='moderate', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue", "display": "inline-block", "font-size": "16px"})     
                    ], style = {"width" : "80%"}),
                    html.Td(dcc.Checklist(id = "cancel_check", options=[{'label': '', 'value': ''}],style = {"width" : "5%"}),  style = {"width" : "20%"})], style = {"width" : "100%"}
                ),  
                
            ], style = {"width" : "100%"}),
            
            
            html.Br(),
            
            #html.Label('Property type', style = {"color" : "blue", "font-size": "20px"}), 
            #html.Br(),
            #dcc.Dropdown( id = 'property',
            #options = property_options,
            #value='Apartment', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue", "display": "inline-block", "font-size": "16px"}),
            
            
            html.Table([
                    html.Tr([
                        html.Td(children = [html.Label('Property type', style = {"color" : "blue", "font-size": "20px", "width" : "100%"}), 
                        dcc.Dropdown(id = 'property',
                                      options = property_options,
                                      #options = [{'label': 'Westminster ', 'value': 'Westminster'},
                                      #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
                                      #value=neighbourhood_cleansed_options[0]['value'], style = {"width" : "30%"}),
                                      value='Apartment', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue", "display": "inline-block", "font-size": "16px"})     
                    ], style = {"width" : "80%"}),
                    html.Td(dcc.Checklist(id = "prop_check", options=[{'label': '', 'value': ''}],style = {"width" : "5%"}),  style = {"width" : "20%"})], style = {"width" : "100%"}
                ),  
                
            ], style = {"width" : "100%"}),
            
            
            
            html.Br(),
            
            #html.Label('responce rate'), dcc.Dropdown(
            #options = responce_options,
            #options = [{'label': 'Westminster ', 'value': 'Westminster'},
            #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
            #value=options[0]['value']),
            
            #html.Label('Latitude', style = {"color" : "blue", "font-size": "20px"}), 
            #dcc.Input(id = 'latitude', value='1', type='number', style = {"width" : "10%", "color" : "blue", "background-color" : "lightblue"}),
            
           # html.Br(),
            
           # html.Label('Longitude', style = {"color" : "blue", "font-size": "20px"}), 
           # dcc.Input(id = 'longitude', value='1', type='number', style = {"width" : "10%", "color" : "blue", "background-color" : "lightblue"}),
            
           # html.Br(),
            
            html.Table([
                    html.Tr([
            
                        html.Td([html.Label('Latitude', style = {"color" : "blue", "font-size": "20px"}), 
                                 html.Br(),
                                 dcc.Input(id = 'latitude',  value='51.50853', readOnly = True, type='number', style = {"height": "30px", "width" : "100%", "color" : "blue", "background-color" : "lightblue"})], style = {"width" : "35%"}), 
                        
            
              ]),  
            ], style = {"width" : "50%"}),
            
            html.Br(),
            
            html.Table([
                    html.Tr([
            
                        html.Td([html.Label('Longitude', style = {"color" : "blue", "font-size": "20px"}), 
                                 html.Br(),
                                 dcc.Input(id = 'longitude', value='-0.12574', type='number', readOnly = True, style = {"height": "30px", "width" : "100%", "color" : "blue", "background-color" : "lightblue"})], style = {"width" : "35%"}), 
                        
            
              ]),  
            ], style = {"width" : "50%"}),
            
            
            html.Br(),
            
            html.Table([
                    html.Tr([
            
                        html.Td([html.Label('Accomodates', style = {"color" : "blue", "font-size": "20px"}), 
                                 html.Br(),
                                 dcc.Input(id = 'accomodates', min = '0', value='0', type='number', style = {"height": "30px", "width" : "100%", "color" : "blue", "background-color" : "lightblue"})], style = {"width" : "75%"}), 
                        html.Td([dcc.Checklist(id = "acc_check", options=[{'label': '', 'value': ''}],style = {"width" : "10%"})], style = {"width" : "20%"})
            
              ]),  
            ], style = {"width" : "100%"}),
            
            html.Br(),
            
            #html.Label('Beds', style = {"color" : "blue", "font-size": "20px"}), 
            ##html.Br(),
            #dcc.Input(id = 'beds', value='1', type='number', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue"}),
            
            html.Table([
                    html.Tr([
            
                        html.Td([html.Label('Beds', style = {"color" : "blue", "font-size": "20px"}), 
                                 html.Br(),
                                 dcc.Input(id = 'beds', min = '0', value='0', type='number', style = {"height": "30px", "width" : "100%", "color" : "blue", "background-color" : "lightblue"})], style = {"width" : "75%"}), 
                        html.Td([dcc.Checklist(id = "beds_check", options=[{'label': '', 'value': ''}],style = {"width" : "10%"})], style = {"width" : "20%"})
            
              ]),  
            ], style = {"width" : "100%"}),
            
            html.Br(),
            
            #html.Label('Bathrooms', style = {"color" : "blue", "font-size": "20px"}), 
            #html.Br(),
            #dcc.Input(id = 'bath', value='1', type='number', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue"}),
            
              html.Table([
                    html.Tr([
            
                        html.Td([html.Label('Bathrooms', style = {"color" : "blue", "font-size": "20px"}), 
                                 html.Br(),
                                 dcc.Input(id = 'bath', min = '0', value='0', type='number', style = {"height": "30px", "width" : "100%", "color" : "blue", "background-color" : "lightblue"})], style = {"width" : "75%"}), 
                        html.Td([dcc.Checklist(id = "bath_check", options=[{'label': '', 'value': ''}],style = {"width" : "10%"})], style = {"width" : "20%"})
            
              ]),  
            ], style = {"width" : "100%"}),
            
            
            html.Br(),
            
            #html.Label('Bedrooms', style = {"color" : "blue", "font-size": "20px"}), 
            #html.Br(),
            #dcc.Input(id = 'bedrooms', value='1', type='number', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue"}),
            
             html.Table([
                    html.Tr([
            
                        html.Td([html.Label('Bedrooms', style = {"color" : "blue", "font-size": "20px"}), 
                                 html.Br(),
                                 dcc.Input(id = 'bedrooms', min = '0', value='0', type='number', style = {"height": "30px", "width" : "100%", "color" : "blue", "background-color" : "lightblue"})], style = {"width" : "75%"}), 
                        html.Td([dcc.Checklist(id = "bedrooms_check", options=[{'label': '', 'value': ''}],style = {"width" : "10%"})], style = {"width" : "20%"})
            
              ]),  
            ], style = {"width" : "100%"}),
            
            
            html.Br(),
            
            #html.Label('Minimum_nights' , style = {"color" : "blue", "font-size": "20px"}), 
            #html.Br(),
            #dcc.Input(id = 'nights', value='1', type='number', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue"}), 
            
            html.Table([
                    html.Tr([
            
                        html.Td([html.Label('Minimum nights', style = {"color" : "blue", "font-size": "20px"}), 
                                 html.Br(),
                                 dcc.Input(id = 'nights', min = '0', value='0', type='number', style = {"height": "30px", "width" : "100%", "color" : "blue", "background-color" : "lightblue"})], style = {"width" : "75%"}), 
                        html.Td([dcc.Checklist(id = "night_check", options=[{'label': '', 'value': ''}],style = {"width" : "10%"})], style = {"width" : "20%"})
            
              ]),  
            ], style = {"width" : "100%"}),
            
            
            html.Br(),
            
            #html.Label('Guests_included', style = {"color" : "blue", "font-size": "20px"}), 
            #html.Br(),
            #dcc.Input(id = 'guests', value='1', type='number', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue"}),
            
            
            html.Table([
                    html.Tr([
            
                        html.Td([html.Label('Guests included', style = {"color" : "blue", "font-size": "20px"}), 
                                 html.Br(),
                                 dcc.Input(id = 'guests', min = '0', value='0', type='number', style = {"height": "30px", "width" : "100%", "color" : "blue", "background-color" : "lightblue"})], style = {"width" : "75%"}), 
                        html.Td([dcc.Checklist(id = "guests_check", options=[{'label': '', 'value': ''}],style = {"width" : "10%"})], style = {"width" : "20%"})
            
              ]),  
            ], style = {"width" : "100%"}),
            
            
            html.Br(),
            
            #html.Label('Cleaning_fee', style = {"color" : "blue", "font-size": "20px"}), 
            #html.Br(),
            #dcc.Input(id = 'fee', value='1', type='number', style = {"width" : "100%", "color" : "blue", "background-color" : "lightblue"}),
            html.Table([
                    html.Tr([
            
                        html.Td([html.Label('Cleaning fee', style = {"color" : "blue", "font-size": "20px"}), 
                                 html.Br(),
                                 dcc.Input(id = 'fee', min = '0', value='0', type='number', style = {"height": "30px", "width" : "100%", "color" : "blue", "background-color" : "lightblue"})], style = {"width" : "75%"}), 
                        html.Td([dcc.Checklist(id = "fee_check", options=[{'label': '', 'value': ''}],style = {"width" : "10%"})], style = {"width" : "20%"})
            
              ]),  
            ], style = {"width" : "100%"}),
            
            
            
            html.Br(),
            html.Br(),
            
            html.Div(id='price', style = {"width" : "100%","color" : "red", "background-color" : "white", "font-size": "20px"}),                        
            ])
        ], style = {"width" : "30%"} ),
        html.Td(children = [
           #dcc.Input(
           # id='num-multi',
           # type='number',
           # value=100
           # ),
           #html.Button(id='update-button-state', n_clicks=0, children='Update'),
           #html.Div(id='debug-info',children='Debug info...'),

           html.Div(   
            dl.Map(id='map',
                children=[   
                    dl.LayersControl(
                        carto_tile_layers + 
                        [dl.Overlay(
                            dl.LayerGroup(
                                id='marker_layer',
                                #children = price_markers(*get_sample_data(100)),
                                ),
                            name="price_markers",
                            checked=True)]
                        ),
                    dl.LayerGroup(id="click_marker", children=[]),
                ],
                zoom=11, 
                center=[51.50853, -0.12574],
                ),
            style={
                    #'width' : '-moz-calc(100% - 150px)',
                    #'width' : '-webkit-calc(100% - 150px)',
                    #'width' : '100%'
                    
                    'width' : 'calc(100% - 50px)',
                    'height': 'calc(90vh - 410px)',
                    
                    
                    #'width' : 'calc(100% - 350px)',
                    #'height': 'calc(90vh - 50px)',
                    'margin': "130px 0 0 10px",
                    
                    #"display": "block",
                    #"position": "relative"
                    },
            ),  
           
           dcc.Graph(
            id='graph',
            #figure=fig
           )
        ], style = {"width" : "70%"})
       ], style = {"width" : "80%"})
     ], style = {"width" : "100%"})   
    ])
    
@app.callback(#Output('debug-info', 'children'),
              Output('marker_layer', 'children'),
              Input(component_id='reg', component_property='value'),
              Input(component_id='room_type', component_property='value'),
              Input(component_id='cancel', component_property='value'),
              Input(component_id='property', component_property='value'),
              Input(component_id='latitude', component_property='value'),
              Input(component_id='longitude', component_property='value'),
              Input(component_id='accomodates', component_property='value'),
              Input(component_id='beds', component_property='value'),
              Input(component_id='bath', component_property='value'),
              Input(component_id='bedrooms', component_property='value'),
              Input(component_id='nights', component_property='value'),
              Input(component_id='guests', component_property='value'),
              Input(component_id='fee', component_property='value'),
              Input(component_id='reg_check', component_property='value'),
              Input(component_id='room_check', component_property='value'),
              Input(component_id='cancel_check', component_property='value'),
              Input(component_id='prop_check', component_property='value'),
              Input(component_id='acc_check', component_property='value'),
              Input(component_id='beds_check', component_property='value'),
              Input(component_id='bath_check', component_property='value'),
              Input(component_id='bedrooms_check', component_property='value'),
              Input(component_id='night_check', component_property='value'),
              Input(component_id='guests_check', component_property='value'),
              Input(component_id='fee_check', component_property='value'),
              
              #Input('update-button-state', 'n_clicks'),
              #State('num-multi', 'value'),
              )
#def update_output(n_clicks, n_markers):
def update_output(reg, room, cancel, prop,  lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee,
                  reg_check, room_check, cancel_check, prop_check,  acc_check, beds_check, bath_check, bedrooms_check, night_check, guests_check, fee_check):

    #debug_text = u'''
    #    The Button has been pressed {} times
    #'''.format(n_clicks)
    #return debug_text, price_markers(*get_sample_data(n_markers))
    return price_markers(*get_sample_data(reg, room, cancel, prop, lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee, \
                                          reg_check, room_check, cancel_check, prop_check,  acc_check, beds_check, bath_check, bedrooms_check, night_check, guests_check, fee_check))


@app.callback(
    Output(component_id='price', component_property='children'),
    Input(component_id='reg', component_property='value'),
    Input(component_id='room_type', component_property='value'),
    Input(component_id='cancel', component_property='value'),
    Input(component_id='property', component_property='value'),
    Input(component_id='latitude', component_property='value'),
    Input(component_id='longitude', component_property='value'),
    Input(component_id='accomodates', component_property='value'),
    Input(component_id='beds', component_property='value'),
    Input(component_id='bath', component_property='value'),
    Input(component_id='bedrooms', component_property='value'),
    Input(component_id='nights', component_property='value'),
    Input(component_id='guests', component_property='value'),
    Input(component_id='fee', component_property='value')
)
def update_output_div(reg, room, cancel, prop,  lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee):
    price = get_price(reg, room, cancel, prop,  lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee)
    return 'Price: {:f}'.format(price)



@app.callback(#Output('debug-info', 'children'),
              Output(component_id='graph',component_property= 'figure'),
              Input(component_id='reg', component_property='value'),
              Input(component_id='room_type', component_property='value'),
              Input(component_id='cancel', component_property='value'),
              Input(component_id='property', component_property='value'),
              Input(component_id='latitude', component_property='value'),
              Input(component_id='longitude', component_property='value'),
              Input(component_id='accomodates', component_property='value'),
              Input(component_id='beds', component_property='value'),
              Input(component_id='bath', component_property='value'),
              Input(component_id='bedrooms', component_property='value'),
              Input(component_id='nights', component_property='value'),
              Input(component_id='guests', component_property='value'),
              Input(component_id='fee', component_property='value'),
              Input(component_id='reg_check', component_property='value'),
              Input(component_id='room_check', component_property='value'),
              Input(component_id='cancel_check', component_property='value'),
              Input(component_id='prop_check', component_property='value'),
              #Input(component_id='latitude', component_property='value'),
              #Input(component_id='longitude', component_property='value'),
              Input(component_id='acc_check', component_property='value'),
              Input(component_id='beds_check', component_property='value'),
              Input(component_id='bath_check', component_property='value'),
              Input(component_id='bedrooms_check', component_property='value'),
              Input(component_id='night_check', component_property='value'),
              Input(component_id='guests_check', component_property='value'),
              Input(component_id='fee_check', component_property='value'),
              
              #Input('update-button-state', 'n_clicks'),
              #State('num-multi', 'value'),
              )
#def update_output(n_clicks, n_markers):
def update_output(reg, room, cancel, prop,  lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee,
                  reg_check, room_check, cancel_check, prop_check,  acc_check, beds_check, bath_check, bedrooms_check, night_check, guests_check, fee_check):

    #debug_text = u'''
    #    The Button has been pressed {} times
    #'''.format(n_clicks)
    #return debug_text, price_markers(*get_sample_data(n_markers))
    (df_lat_lon, price, price_model) = get_sample_data(reg, room, cancel, prop,  lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee, \
                       reg_check, room_check, cancel_check, prop_check,  acc_check, beds_check, bath_check, bedrooms_check, night_check, guests_check, fee_check)
    if price.shape[0] == 0:
        return (plotly.graph_objects.Figure())
    fig = px.histogram(price, nbins = 100)
    return fig


@app.callback(Output('latitude', 'value'),
              Output('longitude', 'value'),
              Output('click_marker', 'children'),
              Input("map", "click_lat_lng"),
              State("click_marker", "children")
              )
def click_output(click_lat_lng, children):
    lat_str, lng_str = '', ''
    if click_lat_lng is not None:
        lat_lng = [round(val, 4) for val in click_lat_lng]
        lat_str, lng_str = (str(val) for val in lat_lng)
        children = [dl.Marker(children=[dl.Tooltip("Your location"), dl.Popup(str(lat_lng))], position=lat_lng)]
                    
    return lat_str, lng_str, children





if __name__ == '__main__':
    #app.run_server(host = '138.68.99.110', debug=True)
    app.run_server(debug=True)



