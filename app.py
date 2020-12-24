# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 14:20:08 2020

@author: Asus
"""
# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
from airbnb_model import get_options, make_prediction
import pickle
from sklearn.feature_extraction import DictVectorizer as DV
import math
import numpy as np
from airbnb_model import get_price


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

property_list = ['Earth house', 'Hut', 'Treehouse', 'Townhouse', 'Tipi', 'Yurt', 'Apartment', 'Hostel', 'Parking Space', 'Cottage', 'Farm stay', 'Aparthotel', 'Nature lodge', 'Bed and breakfast', 'Guesthouse', 'Tiny house', 'Villa', 'Cabin', 'Boutique hotel', 'Lighthouse', 'Ryokan (Japan)', 'Tent', 'Other', 'Casa particular (Cuba)', 'Houseboat', 'Guest suite', 'Bus', 'Boat', 'Hotel', "Shepherd's hut (U.K., France)", 'Loft', 'Bungalow', 'Camper/RV', 'Chalet', 'Igloo', 'Dome house', 'House', 'Resort', 'Barn', 'Island', 'Serviced apartment', 'Condominium']
room_type_list = ['Entire home/apt', 'Private room', 'Shared room']
cancel_list = ['moderate', 'flexible', 'strict', 'super_strict_30', 'super_strict_60', 'strict_14_with_grace_period']
neighbourhood_list = ['Greenwich', 'Islington', 'Enfield', 'Westminster', 'Brent', 'Bexley', 'Hounslow', 'Camden', 'Haringey', 'Harrow', 'Redbridge', 'Croydon', 'Southwark', 'Tower Hamlets', 'Newham', 'Lewisham', 'Kensington and Chelsea', 'Hillingdon', 'Hackney', 'Sutton', 'Richmond upon Thames', 'Barking and Dagenham', 'Bromley', 'Barnet', 'Havering', 'City of London', 'Merton', 'Ealing', 'Waltham Forest', 'Wandsworth', 'Kingston upon Thames', 'Lambeth', 'Hammersmith and Fulham']

neighbourhood_cleansed_options = get_options(neighbourhood_list)
room_type_options = get_options(room_type_list)
cancel_options = get_options(cancel_list)
property_options = get_options(property_list)



app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
#df = pd.DataFrame({
#    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#    "Amount": [4, 1, 2, 2, 4, 5],
#    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
#})

#fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")



app.layout = html.Div([
    
            html.Br(),
            html.Label('District', style = {"color" : "blue", "font-size": "20px"}), 
           
            dcc.Dropdown(id = 'reg',
            options = neighbourhood_cleansed_options,
            #options = [{'label': 'Westminster ', 'value': 'Westminster'},
            #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
            #value=neighbourhood_cleansed_options[0]['value'], style = {"width" : "30%"}),
            value='Greenwich', style = {"min-width" : "20%", "color" : "blue", "background-color" : "lightblue", "display": "inline-block", "font-size": "16px"}),
            
            html.Br(),
      
            
            html.Label('Room type', style = {"color" : "blue", "font-size": "20px"}), 
            dcc.Dropdown( id = 'room_type',
            options = room_type_options,
            #options = [{'label': 'Westminster ', 'value': 'Westminster'},
            #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
            #value=room_type_options[0]['value'], style = {"width" : "30%"}) ,
            value='Entire home/apt', style = {"min-width" : "20%", "color" : "blue", "background-color" : "lightblue", "display": "inline-block", "font-size": "16px"}),
            
            
            html.Br(),
            
            html.Label('Cancellation policy', style = {"color" : "blue", "font-size": "20px"}), 
            dcc.Dropdown( id = 'cancel',
            options = cancel_options,
            #options = [{'label': 'Westminster ', 'value': 'Westminster'},
            #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
            #value=cancel_options[0]['value'], style = {"width" : "30%"}) ,
            value='moderate', style = {"min-width" : "20%", "color" : "blue", "background-color" : "lightblue", "display": "inline-block", "font-size": "16px"}),
            
            
            html.Br(),
            
            html.Label('Property type', style = {"color" : "blue", "font-size": "20px"}), 
            dcc.Dropdown( id = 'property',
            options = property_options,
            #options = [{'label': 'Westminster ', 'value': 'Westminster'},
            #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
            #value=property_options[0]['value'], style = {"width" : "30%"}),
            value='Apartment', style = {"min-width" : "20%", "color" : "blue", "background-color" : "lightblue", "display": "inline-block", "font-size": "16px"}),
            
            
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
            
            
            html.Label('Accomodates', style = {"color" : "blue", "font-size": "20px"}), 
            dcc.Input(id = 'accomodates', value='1', type='number', style = {"width" : "10%", "color" : "blue", "background-color" : "lightblue"}),
            
            html.Br(),
            
            html.Label('Beds', style = {"color" : "blue", "font-size": "20px"}), 
            dcc.Input(id = 'beds', value='1', type='number', style = {"width" : "10%", "color" : "blue", "background-color" : "lightblue"}),
            
            html.Br(),
            
            html.Label('Bathrooms', style = {"color" : "blue", "font-size": "20px"}), 
            dcc.Input(id = 'bath', value='1', type='number', style = {"width" : "10%", "color" : "blue", "background-color" : "lightblue"}),
            
            html.Br(),
            
            html.Label('Bedrooms', style = {"color" : "blue", "font-size": "20px"}), 
            dcc.Input(id = 'bedrooms', value='1', type='number', style = {"width" : "10%", "color" : "blue", "background-color" : "lightblue"}),
            
            html.Br(),
            
            html.Label('Minimum_nights' , style = {"color" : "blue", "font-size": "20px"}), 
            dcc.Input(id = 'nights', value='1', type='number', style = {"width" : "10%", "color" : "blue", "background-color" : "lightblue"}), 
            
            html.Br(),
            
            html.Label('Guests_included', style = {"color" : "blue", "font-size": "20px"}), 
            dcc.Input(id = 'guests', value='1', type='number', style = {"width" : "10%", "color" : "blue", "background-color" : "lightblue"}),
            
            html.Br(),
            
            html.Label('Cleaning_fee', style = {"color" : "blue", "font-size": "20px"}), 
            dcc.Input(id = 'fee', value='1', type='number', style = {"width" : "10%", "color" : "blue", "background-color" : "lightblue"}),
            
            html.Br(),
            html.Br(),
            
            html.Div(id='price', style = {"width" : "20%","color" : "red", "background-color" : "white", "font-size": "20px"}),                        
 ])



@app.callback(
    Output(component_id='price', component_property='children'),
    Input(component_id='reg', component_property='value'),
    Input(component_id='room_type', component_property='value'),
    Input(component_id='cancel', component_property='value'),
    Input(component_id='property', component_property='value'),
    #Input(component_id='latitude', component_property='value'),
    #Input(component_id='longitude', component_property='value'),
    Input(component_id='accomodates', component_property='value'),
    Input(component_id='beds', component_property='value'),
    Input(component_id='bath', component_property='value'),
    Input(component_id='bedrooms', component_property='value'),
    Input(component_id='nights', component_property='value'),
    Input(component_id='guests', component_property='value'),
    Input(component_id='fee', component_property='value')
)
def update_output_div(reg, room, cancel, prop,  accomodates, beds, bath, bedrooms, night, guests, fee):
    price = get_price(reg, room, cancel, prop,  accomodates, beds, bath, bedrooms, night, guests, fee)
    return 'Price: {:f}'.format(price)



if __name__ == '__main__':
    app.run_server(host = '138.68.99.110', debug=True)
    #app.run_server(debug=True)
    
    
    
    

    
    