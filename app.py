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
#from airbnb_model import combine_data
import pickle
from sklearn.feature_extraction import DictVectorizer as DV
import math
import numpy as np



def get_options(cat_list):
    options = []
    for el  in cat_list:
        options_el = {}
        options_el['label'] = el;
        options_el['value'] = el;
        options.append(options_el)
    return options


def combine_data(ndata, cdata):

    X = np.hstack((ndata, cdata))

    for j in range(X.shape[1]):
        mean = calc_mean(X[:, j])
    
        for i in range(X.shape[0]):
      
        #if ((X_train[i, j] > 100) | (X_train[i, j] < 0)):
        #    X_train[i, j] = 0
        
            if math.isinf(X[i, j]) or math.isnan(X[i, j]):
                X[i, j] = mean

    Xd = pd.DataFrame(X)
        #Xd = Xd[[0, 1, 2,3, 4, 5,6,7,8,9,10, 56,57,84,97,99,152, 66, 94, 107, 109, 13, 15, 47, 59, 62, 69, 83, 108, 114 ,96 , 98 ]]
        #print(Xd)
   
    return(Xd)     
    



def make_prediction(reg, room, cancel, prop, accomodates, beds, bath, bedrooms, night, guests, fee):
        test_web = pd.DataFrame(columns = ['id', 'name', 'summary', 'space', 'description', 'experiences_offered',
                                           'neighborhood_overview', 'notes', 'transit', 'access', 'interaction',
                                           'house_rules', 'host_id', 'host_since', 'host_about',
                                           'host_response_time', 'host_response_rate', 'host_is_superhost',
                                           'host_has_profile_pic', 'host_identity_verified',
                                           'neighbourhood_cleansed', 'zipcode', 'latitude', 'longitude',
                                           'is_location_exact', 'property_type', 'room_type', 'accommodates',
                                           'bathrooms', 'bedrooms', 'beds', 'bed_type', 'amenities', 'square_feet',
                                           'security_deposit', 'cleaning_fee', 'guests_included', 'extra_people',
                                           'minimum_nights', 'cancellation_policy',
                                           'require_guest_profile_picture', 'require_guest_phone_verification'])
                                           
        test_web.loc[0] = [1, "", "", "", "", "", "", "", "", "", "", "", 1, 0, "", "", "", 0,0,0, reg, "", 0.54, 0.54,  0,  prop, room, accomodates, bath, \
                           bedrooms, beds, "", "", 0, 0, fee, guests, 0, night, cancel, 0, 0]
        print(test_web.shape)    
            
        ndata = test_web[['accommodates', 'bedrooms',  'bathrooms', 'beds', 'cleaning_fee' , 'guests_included',  'minimum_nights']]
        cdata = test_web[['property_type',  'room_type', 'cancellation_policy', 'neighbourhood_cleansed']]#,'responce_time']]
        print(cdata)

        
        #train = pd.read_csv( "train.csv")#, parse_dates=['host_since'],  converters= dict_convert)
        #test = pd.read_csv( "test.csv")#, parse_dates=['host_since'],  converters= dict_convert)
        
        ##train1 = train[['property_type',  'room_type', 'cancellation_policy', 'neighbourhood_cleansed']]#,'responce_time']]
        #test1 = test[['property_type',  'room_type', 'cancellation_policy', 'neighbourhood_cleansed']]#, 'responce_time']]#, 'host_response_time']]

        
        #categorial_data =  pd.DataFrame(np.vstack((train1, test1)))
        #encoder = DV(sparse = False)
        #encoded_data = encoder.fit_transform(categorial_data.T.to_dict().values())
        #encoded_test = encoder.transform(cdata)
        #temp = encoder.fit_transform(categorial_data.T.to_dict().values())
        #print(temp.shape)
        
        
        filename = 'encoder.sav'
        encoder = pickle.load(open(filename, 'rb'))
        cdata1 =  encoder.transform(cdata.T.to_dict().values())
        print(cdata1.shape)
        print(ndata.shape)
        data = np.hstack((ndata, cdata1))
        filename = 'last_model.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        result = loaded_model.predict(data)    
        func = (lambda x : math.e ** x)
        result = func(result)
        print(result[0])
        return result[0]
        
            




external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


#model_obj = Model()

#try:
 #   model = model_obj.make_model_work()
  #  #data_to_predict = model_obj.make_data_to_predict()
  #  neighbourhood_cleansed_options = get_options(model_obj.neighbourhood_list)
  #  room_type_options = get_options(model_obj.room_type_list)
  #  cancel_options = get_options(model_obj.cancel_list)
  #  property_options = get_options(model_obj.property_list)
    
#except:
 #   neighbourhood_cleansed_options = [{'label': 'Westminster ', 'value': 'Westminster'}]#get_options(model_obj.neighbourhood_list)
  #  room_type_options =  [{'label': 'Westminster ', 'value': 'Westminster'}]
            
            #get_options(model_obj.room_type_list)
  #  cancel_options = [{'label': 'Westminster ', 'value': 'Westminster'}]#get_options(model_obj.cancel_list)
  #  property_options = [{'label': 'Westminster ', 'value': 'Westminster'}]#get_options(model_obj.property_list)
    #responce_options = get_options(model_obj..responce_list)

# some time later...

# load the model from disk
#loaded_model = pickle.load(open(filename, 'rb'))
#result = loaded_model.score(X_test, Y_test)
#print(result)


property_list = ['Earth house', 'Hut', 'Treehouse', 'Townhouse', 'Tipi', 'Yurt', 'Apartment', 'Hostel', 'Parking Space', 'Cottage', 'Farm stay', 'Aparthotel', 'Nature lodge', 'Bed and breakfast', 'Guesthouse', 'Tiny house', 'Villa', 'Cabin', 'Boutique hotel', 'Lighthouse', 'Ryokan (Japan)', 'Tent', 'Other', 'Casa particular (Cuba)', 'Houseboat', 'Guest suite', 'Bus', 'Boat', 'Hotel', "Shepherd's hut (U.K., France)", 'Loft', 'Bungalow', 'Camper/RV', 'Chalet', 'Igloo', 'Dome house', 'House', 'Resort', 'Barn', 'Island', 'Serviced apartment', 'Condominium']
room_type_list = ['Entire home/apt', 'Private room', 'Shared room']
cancel_list = ['moderate', 'flexible', 'strict', 'super_strict_30', 'super_strict_60', 'strict_14_with_grace_period']
neighbourhood_list = ['Greenwich', 'Islington', 'Enfield', 'Westminster', 'Brent', 'Bexley', 'Hounslow', 'Camden', 'Haringey', 'Harrow', 'Redbridge', 'Croydon', 'Southwark', 'Tower Hamlets', 'Newham', 'Lewisham', 'Kensington and Chelsea', 'Hillingdon', 'Hackney', 'Sutton', 'Richmond upon Thames', 'Barking and Dagenham', 'Bromley', 'Barnet', 'Havering', 'City of London', 'Merton', 'Ealing', 'Waltham Forest', 'Wandsworth', 'Kingston upon Thames', 'Lambeth', 'Hammersmith and Fulham']

neighbourhood_cleansed_options = get_options(neighbourhood_list)
room_type_options = get_options(room_type_list)
cancel_options = get_options(cancel_list)
property_options = get_options(property_list)

print()

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
            html.Label('Region'), dcc.Dropdown(id = 'reg',
            options = neighbourhood_cleansed_options,
            #options = [{'label': 'Westminster ', 'value': 'Westminster'},
            #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
            #value=neighbourhood_cleansed_options[0]['value'], style = {"width" : "30%"}),
            value='Greenwich', style = {"width" : "50%"}),
            
            html.Br(),
            
            html.Label('Room type'), dcc.Dropdown( id = 'room_type',
            options = room_type_options,
            #options = [{'label': 'Westminster ', 'value': 'Westminster'},
            #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
            #value=room_type_options[0]['value'], style = {"width" : "30%"}) ,
            value='Entire home/apt', style = {"width" : "50%"}) ,
            
            
            html.Br(),
            
            html.Label('cancellation policy'), dcc.Dropdown( id = 'cancel',
            options = cancel_options,
            #options = [{'label': 'Westminster ', 'value': 'Westminster'},
            #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
            #value=cancel_options[0]['value'], style = {"width" : "30%"}) ,
            value='moderate', style = {"width" : "50%"}) ,
            
            
            html.Br(),
            
            html.Label('property type'), dcc.Dropdown( id = 'property',
            options = property_options,
            #options = [{'label': 'Westminster ', 'value': 'Westminster'},
            #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
            #value=property_options[0]['value'], style = {"width" : "30%"}),
            value='Apartment', style = {"width" : "50%"}),
            
            
            html.Br(),
            
            #html.Label('responce rate'), dcc.Dropdown(
            #options = responce_options,
            #options = [{'label': 'Westminster ', 'value': 'Westminster'},
            #/{'label': u'Tower Hamlets', 'value': 'Tower Hamlets'}],
            #value=options[0]['value']),
            
            html.Label('Accomodates'),
            dcc.Input(id = 'accomodates', value='1', type='number', style = {"width" : "10%"}),
            
            html.Br(),
            
            html.Label('Beds'),
            dcc.Input(id = 'beds', value='1', type='number', style = {"width" : "10%"}),
            
            html.Br(),
            
            html.Label('bathrooms'),
            dcc.Input(id = 'bath', value='1', type='number', style = {"width" : "10%"}),
            
            html.Br(),
            
            html.Label('bedrooms'),
            dcc.Input(id = 'bedrooms', value='1', type='number', style = {"width" : "10%"}),
            
            html.Br(),
            
            html.Label('minimum_nights'        ),
            dcc.Input(id = 'nights', value='1', type='number', style = {"width" : "10%"}), 
            
            html.Br(),
            
            html.Label('guests_included'),
            dcc.Input(id = 'guests', value='1', type='number', style = {"width" : "10%"}),
            
            html.Br(),
            
            html.Label('cleaning_fee'),
            dcc.Input(id = 'fee', value='1', type='number', style = {"width" : "10%"}),
            
            
            
            html.Div(id='price')
                        
 ])



@app.callback(
    Output(component_id='price', component_property='children'),
    Input(component_id='reg', component_property='value'),
    Input(component_id='room_type', component_property='value'),
    Input(component_id='cancel', component_property='value'),
    Input(component_id='property', component_property='value'),
    Input(component_id='accomodates', component_property='value'),
    Input(component_id='beds', component_property='value'),
    Input(component_id='bath', component_property='value'),
    Input(component_id='bedrooms', component_property='value'),
    Input(component_id='nights', component_property='value'),
    Input(component_id='guests', component_property='value'),
    Input(component_id='fee', component_property='value')
)
def update_output_div(reg, room, cancel, prop, accomodates, beds, bath, bedrooms, night, guests, fee):
    price = make_prediction(reg, room, cancel, prop, accomodates, beds, bath, bedrooms, night, guests, fee)
    return 'Output: {}'.format(price)




    # html.Div(children=[
    # html.H1(children='Hello Dash'),

    # html.Div(children='''
    #     Dash: A web application framework for Python.
    # '''),

    # dcc.Graph(
    #     id='example-graph',
    #     figure=fig
    # )


if __name__ == '__main__':
    app.run_server(host = '138.68.99.110', debug=True)
    
    
    
    
    

    
    