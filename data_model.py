import numpy as np
import pandas as pd

from airbnb_model import make_prediction


usecols = ['price', 'neighbourhood_cleansed',
           'latitude', 'longitude', 
           'property_type', 'room_type','minimum_nights',
           'accommodates', 'guests_included','cancellation_policy',
           'cleaning_fee', 
           'beds','bedrooms','bathrooms'
           ]

data = pd.read_csv('train.csv', usecols=usecols)
#data.to_csv('train_usecols.csv', index=False)

def weighted_median(y1):
    y1 = np.array(y1)
    y = np.sort(y1[y1 > 0])
    w = 1.0 / y
    return y[w.cumsum() >= 0.5 * w.sum()][0]

bour_group = data.groupby('neighbourhood_cleansed')
bour_price = bour_group['price'].apply(weighted_median)

#def get_sample_data(n=100):
#    df = data.sample(n)
#    price = df['price']
#    price_model = df['neighbourhood_cleansed'].map(bour_price)
#    return df, price, price_model


def get_sample_data(reg, room, cancel, prop,  lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee, \
                    reg_check, room_check, cancel_check, prop_check,  acc_check, beds_check, bath_check, bedrooms_check, night_check, guests_check, fee_check):
    
    
     #data[['accommodates', 'bedrooms',  'bathrooms', 'beds', 'cleaning_fee' , 'guests_included',  'minimum_nights']]
    # ['property_type',  'room_type', 'cancellation_policy', 'neighbourhood_cleansed']]#,
    df = data
    if reg_check:
        df = df[(df['neighbourhood_cleansed'] == reg)]
    if room_check:
        df = df[df['room_type'] == room]
    if cancel_check:
        df = df[df['cancellation_policy'] == cancel]
    if prop_check:
       df = df[df['property_type'] == prop]
    if acc_check:  
       df = df[df['accommodates'] == accomodates]
    if beds_check:   
       df = df[df['beds'] == beds]
    if bath_check:   
       df = df[df['bathrooms'] ==  bath]
    if bedrooms_check:   
       df = df[df['bedrooms'] == bedrooms]
    if night_check:
       df =  df[df['minimum_nights'] == night]
    if guests_check:
       df = df[df['guests_included'] == guests]
    if fee_check:
       df = df[df['cleaning_fee'] ==  fee]
       
       
    df = df.sample(min(100, df.shape[0]))    
    print(df.head())    
    price = df['price']
    if (df.shape[0] != 0):
        price_model = make_prediction(df)#df['neighbourhood_cleansed'].map(bour_price)
    else:
        price_model = []    
    return df, price, price_model
