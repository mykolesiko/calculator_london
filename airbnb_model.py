# -*- coding: utf-8 -*-
"""
Created on Sat Dec 19 17:36:19 2020

@author: Asus
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib
from matplotlib import pyplot as plt
from sklearn.feature_extraction import DictVectorizer as DV
import re

import math

from sklearn.model_selection import ShuffleSplit

    
from  sklearn import model_selection
from sklearn.preprocessing import StandardScaler
import lightgbm
from lightgbm import LGBMRegressor
import pickle
import logging
from logging import config
import yaml


DEFAULT_LOGGING_CONFIG_FILEPATH = 'logging.conf.yml'
APPLICATION_NAME = 'stackoverflow'
logger = logging.getLogger(APPLICATION_NAME)

def setup_logging():
    """ description """

    with open(DEFAULT_LOGGING_CONFIG_FILEPATH) as file:
        logging.config.dictConfig(yaml.safe_load(file))


def get_options(cat_list):
    options = []
    for el  in cat_list:
        options_el = {}
        options_el['label'] = el;
        options_el['value'] = el;
        options.append(options_el)
    return options


def calc_mean(numeric):
        sum = 0
        s = 0
        for i in range(len(numeric)):
            if ((~math.isinf(numeric[i])) & (~math.isnan(numeric[i])) & (math.isfinite(numeric[i]))):
                sum = sum + numeric[i]
                s = s + 1
        if s == 0:
            sum = 0           
        else:   
            sum = sum  / s
        return sum


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



def get_numeric_data(data):    
        #logger.info("get numeric data")
        
        #numeric_data = data[['polarity', 'accommodates', 'bedrooms',  'bathrooms', 'beds', 'num',  'responce_rate', 'latitude','longitude', 'responce_rate', 'security_deposit', 'cleaning_fee' , 'guests_included',  'host_is_superhost', 'host_identity_verified', 'vigoda', 'extra_people', 'minimum_nights']]#,  'host_identity_verified', 'host_has_profile_pic', 'latitude','longitude','extra_people', 'minimum_nights',  'security_deposit', 'cleaning_fee' ]]       
    numeric_data = data[['latitude', 'longitude', 'accommodates', 'bedrooms',  'bathrooms', 'beds', 'cleaning_fee' , 'guests_included',  'minimum_nights']]
    numeric_data = numeric_data.apply(pd.to_numeric)
    print(numeric_data.info())
    for i in range(numeric_data.shape[0]):
            #print(numeric_data.iloc[i, 0])
        if math.isnan(numeric_data.iloc[i, 0]):
            numeric_data.iloc[i, 0] = -1        
    return numeric_data        




def get_data_from_web(reg, room, cancel, prop,lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee):
    print(f"region = {reg} room = {room} cancel = {cancel} property = {prop} ")
    print(f"accomodates = {accomodates} beds = {beds} bath = {bath} bedrooms = {bedrooms} night = {night} guests = {guests} fee = {fee}")
        
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
                                           
    test_web.loc[0] = [1, "", "", "", "", "", "", "", "", "", "", "", 1, 0, "", "", "", 0,0,0, reg, "", lat, lon,  0,  prop, room, accomodates, bath, \
                           bedrooms, beds, "", "", 0, 0, fee, guests, 0, night, cancel, 0, 0]
    return test_web    
    

def make_prediction(test_web):
        ndata = get_numeric_data(test_web)#test_web[['accommodates', 'bedrooms',  'bathrooms', 'latitude','longitude', 'beds', 'cleaning_fee' , 'guests_included',  'minimum_nights']]
        cdata = test_web[['property_type',  'room_type', 'cancellation_policy', 'neighbourhood_cleansed']]#,'responce_time']]
        print(cdata)

               
        
        filename = 'encoder3.sav'
        encoder = pickle.load(open(filename, 'rb'))
        cdata1 =  encoder.transform(cdata.T.to_dict().values())
        print(cdata1.shape)
        print(ndata.shape)
        data = combine_data(ndata, cdata1)
        
        #filename = 'scaler2.sav'
        #scaler = pickle.load(open(filename, 'rb'))
        #data = scaler.transform(data)
        filename = 'last_model3.sav'
        loaded_model = pickle.load(open(filename, 'rb'))
        result = loaded_model.predict(data)    
        func = (lambda x : math.e ** x)
        result = func(result)
        print(result[0])
        return result 
    
def get_price(reg, room, cancel, prop, lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee):    
    test_web = get_data_from_web(reg, room, cancel, prop, lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee)
    result = make_prediction(test_web)
    return result[0] 

    
def get_predict():    
    train = pd.read_csv( "train.csv")#, parse_dates=['host_since'],  converters= dict_convert)
    target = train['price'].to_list()
    train = train.drop(['price'], 1)
    pred = make_prediction(train)
    return target, pred





def vec_amenities(pole: str):
        pole = pole.strip("{}")
        #print(pole)
        pole = pole.strip("\'")
        values = re.split('\'{+\'}+,+"+', pole)
        values_list = list(values[0].split(','))
        return(values_list)



def find_anomalies(locations, koeff, data_to_find):

    count = 0
    anomalies = []
    for location in locations:
        data_location = data_to_find[data_to_find["neighbourhood_cleansed"] == location]
        data_std = data_location[['price']].std()
        data_mean = data_location[['price']].mean()
        anomaly_cut_off = data_std * koeff
    
        lower_limit  = data_mean - anomaly_cut_off 
        upper_limit = data_mean + anomaly_cut_off
        data_location_bad = data_location.loc[(data_location['price'] > int(upper_limit)) | (data_location['price'] <= 0)]
        data_location_good = data_location[(data_location['price'] < int(upper_limit)) & (data_location['price'] > 0)]
        
        anomalies = anomalies + list(data_location_bad['id'])
        
    return anomalies
    
    
def MAPE(y_pred, y_actual):
    sum = 0
    n = len(y_pred)
    print(n)
    for i in range(n):
        if (y_actual[i] < 0.1):
           continue
        sum = sum + abs((y_pred[i] - y_actual[i])/y_actual[i])
        #print(sum)
    return (sum/n) * 100
    
   

def get_category_values(data, name):
    print(data)
    return (list(set(data[name].to_list())))
    


def str_to_int(s:str)->int:
    if s == "t":
        return 1
    return 0


def scale_data(Xd, target):
    scaler_train = StandardScaler()
    scaler_train.fit(Xd, target)
    Xd = scaler_train.transform(Xd)
    filename = 'scaler3.sav'
    pickle.dump(scaler_train, open(filename, 'wb'))

    return scaler_train, Xd



class Model:
    
    def __init__(self):
       pass
       setup_logging()
       # self.train_clean = pd.DataFrame()
       # self.review = pd.DataFrame()
       # self.train_vigoda = pd.DataFrame()
       # self.polarity = pd.DataFrame()
        

    def make_data_to_predict(self):
        data_from_frame = pd.DataFrame()
    #data_from_frame.set_columns


    



   


    def read_data(self,folder):
        logger.info("begin read_data")
        dict_convert = {"host_is_superhost":str_to_int, 'host_has_profile_pic':str_to_int, 'host_identity_verified':str_to_int,  'is_location_exact':str_to_int, 'require_guest_profile_picture': str_to_int, 'require_guest_phone_verification' : str_to_int}
        self.train = pd.read_csv( folder + "train.csv", parse_dates=['host_since'],  converters= dict_convert)
        self.polarity = pd.read_csv(folder + "rating.csv", header = None)
        self.train_vigoda = pd.read_csv(folder + "vigoda.csv", header = None)
        self.review = pd.read_csv(folder + "reviews.csv", parse_dates=['date'])
        self.test= pd.read_csv(folder + "test.csv", parse_dates=['host_since'],  converters= dict_convert)
        self.test_vigoda = pd.read_csv(folder + "vigoda_test.csv", header = None)
        logger.info("end read_data")
    
    
    def process_review(self):   
        logger.info("begin process_review")
        review = self.review
        review['time'] = review.date.apply(lambda x : x.month/12.0 + x.year)
        review['polarity'] = self.polarity[1].to_list()
        mean_reviews = self.review[["polarity","listing_id"]].groupby(by = "listing_id").mean()
        #print(self.review)
        #data_min = review.groupby(by = ["listing_id"]).time.min()#.sort_values(by=['time'])
        data_min = review.loc[review.groupby(by = "listing_id")['time'].idxmin()]
        data_min1 = pd.DataFrame()
        data_min1['listing_id'] = data_min.index
        data_min1['time_min'] = data_min['time'].to_list()
        print(data_min1.head())
        
        data_max = review.loc[review.groupby(by = "listing_id")['time'].idxmax()]#review.groupby(by = "listing_id").time.max()#.sort_values(by=['time'])
        data_max1 = pd.DataFrame()
        data_max1['listing_id'] = data_max.index
        data_max1['time_max'] = data_max['time'].to_list()
        print(data_max1.head())
    
        kol_reviews = review.groupby("listing_id").count()
        result_review = pd.DataFrame()
        result_review['listing_id'] = kol_reviews.index
        print(result_review)
        num = (kol_reviews["id"].tolist())
        result_review['num'] = num
        result_review['polarity'] = mean_reviews['polarity'].to_list()

        result_review = result_review.merge(data_min1, how = 'left', left_on = 'listing_id', right_on = 'listing_id')
        result_review = result_review.merge(data_max1, how = 'left', left_on = 'listing_id', right_on = 'listing_id')
        self.result_review = result_review
        logger.info("end process_review")
        return result_review
  
    def add_vigoda(self, data, data_vigoda):
        logger.info("add_vigoda")
        data['vigoda'] = data_vigoda.iloc[:, 1].to_list()
    

#def added_vigoda_to_test():
 #   test['vigoda'] = test_vigoda.iloc[:, 1].to_list()
 
 
    def add_reviews_info(self, data):
        logger.info("reviews info")
        print(data.info())
        data = data.merge(self.result_review, how = 'left', left_on = 'id', right_on = 'listing_id')
        print(data.info())
        return(data)
    
#def added_reviews_info_to_test():
#    test = test.merge(kol_reviews1, how = 'left', left_on = 'id', right_on = 'listing_id')
    #test = train.drop(['listing_id_x', 'num_x' , 'polarity_x'], 1)
    #print(test)
    
    def add_host_since(self, data):
        logger.info("host since")
        data['host_since'] = data.host_since.apply(lambda x : x.year + x.month/12)


    def add_responce_rate(self, data):
        logger.info("responce rate")
        rate = []
        #print((data.iloc[1:100, 16]))
        for i  in range(data.shape[0]):
            if (type(data.iloc[i, 16]) != str):
                if math.isnan(data.iloc[i, 16]):
                    rate.append(0) 
            else:
                temp = data.iloc[i, 16]
                #print(type(temp))
                templist = temp.split('%')
                rate.append(int(templist[0]))
        data['responce_rate'] = rate   


#def added_responce_rate_to_test():
#    rate = []
 
 ##      if (type(self.test.iloc[i, 16]) != str):
   #         if math.isnan(self.test.iloc[i, 16]):
    #            rate.append(0) 
     #   else:
     #       temp = self.test.iloc[i, 16]
     #       #print(type(temp))
     #       templist = temp.split('%')
     #       rate.append(int(templist[0]))    
    #self.test['responce_time'] = rate 




    def process_target(self):
        logger.info("process target")
        locations = list(set(self.train["neighbourhood_cleansed"]))
        anomalies = find_anomalies(locations, 3.0, self.train)
        self.train_clean = self.train[~self.train['id'].isin(anomalies)]
    

    def get_target(self):
        logger.info("get target")
        data_train = self.train_clean
        self.target = data_train['price'].apply(math.log)
        return self.target

    
    

    

    def get_categorial_data(self, train_clean, test):
            logger.info("get cat data")
            #train1 = train_clean[['property_type',  'room_type', 'cancellation_policy', 'neighbourhood_cleansed']]#,'responce_time']]
            train1 = self.train[['property_type',  'room_type', 'cancellation_policy', 'neighbourhood_cleansed']]#,'responce_time']]
            test1 = test[['property_type',  'room_type', 'cancellation_policy', 'neighbourhood_cleansed']]#, 'responce_time']]#, 'host_response_time']]

            categorial_data =  pd.concat([train1, test1], axis = 0)#pd.DataFrame(np.vstack((train1, test1)))
            #self.cat_data = data_all
            
            #categorial_data = pd.DataFrame(data_all)
            #print(categorial_data)
            #self.cat_data = data_all
            
            #self.property_list = get_category_values(categorial_data, 'property_type')
            #self.room_type_list = get_category_values(categorial_data, 'room_type')
            #self.cancel_list = get_category_values(categorial_data, 'cancellation_policy')
            #self.neighbourhood_list = get_category_values(categorial_data, 'neighbourhood_cleansed')
            #print(self.property_list)
            #print(self.room_type_list)
            #print(self.cancel_list)
            #print(self.neighbourhood_list)
            #self.responce_list = get_categorial_data(data_all, 'responce_time')
    
    
    
    #property_list = get_categorial_data(data_all, 'property_type')
#room_type_list = get_categorial_data(data_all, 'room_type')
#cancel_list = get_categorial_data(data_all, 'cancellation_policy')
#neighbourhood_list = get_categorial_data(data_all, 'neighbourhood_cleansed')
#responce_list = get_categorial_data(data_all, 'responce_time')
    
    
            encoder = DV(sparse = False)
            encoded_data = encoder.fit_transform(categorial_data.T.to_dict().values())
            filename = 'encoder3.sav'
            pickle.dump(encoder, open(filename, 'wb'))

            encoded_data_train = encoded_data[0:train_clean.shape[0], : ]
            encoded_data_test = encoded_data[train_clean.shape[0]:, : ]

            print(encoded_data.shape) 
            #print(encoded_data_train.shape)
            #print(encoded_data_test.shape)
    
    
            #train1 = train_clean[['amenities']]
            #test1 = test[['amenities']]
            #data_all = train1.append(test1) 

            #amenities_list = data_all.amenities.apply(lambda x:  vec_amenities(x))# Converting it into dataframe and working on it seperately
            #df = pd.DataFrame({"amenities":amenities_list})

            #print(df.shape)
    
            #from sklearn.preprocessing import MultiLabelBinarizer# instantiating MultiLabelBinarizer
            #mlb = MultiLabelBinarizer()
            #encoded1 = pd.DataFrame(mlb.fit_transform(df["amenities"]),columns=mlb.classes_)
            #print(encoded1.head())
            #encoded1 = encoded1.drop('"translation missing: en.hosting_amenity_49"', 1)
            #encoded1 = encoded1.drop('', 1)
            #encoded2 = encoded1
            #amen_train = encoded2.loc[0:(train_clean.shape[0] - 1), : ]
            #amen_test = encoded2.loc[train_clean.shape[0]:, : ]
            #encoded_data_train1 = pd.concat([pd.DataFrame(encoded_data_train), amen_train], axis = 1)
            #encoded_data_test = pd.DataFrame(encoded_data_test).set_index(amen_test.index)
            #encoded_data_test1 = pd.concat([pd.DataFrame(encoded_data_test), amen_test], axis = 1)
            #return (encoded_data_train1, encoded_data_test1)
            return (encoded_data_train, encoded_data_test)


    def get_model(self, X_train, y_train):    
        logger.info("begin get model")
        model = LGBMRegressor(boosting_type='dart', class_weight=None, colsample_bytree=1.0,
                              importance_type='split', learning_rate=0.1, max_depth=36,
                              min_child_samples=20, min_child_weight=0.001, min_split_gain=0,
                              n_estimators=1500, n_jobs=-1, num_leaves=90, objective=None,   
                              random_state=None, reg_alpha=0.0, reg_lambda=0.0, silent=True,
                              subsample=1.0, subsample_for_bin=200000, subsample_freq=0)

        model.fit(X_train, y_train) # обучение
        logger.info("end get model")
        return model


    def make_model_work(self):
        self.read_data("")
        #result_review = self.process_review()
        #self.add_vigoda(self.train, self.train_vigoda) 
        #print(self.result_review)
        #self.train = self.add_reviews_info(self.train)
        #print(self.train.info())
        #self.add_host_since(self.train)
        #self.add_responce_rate(self.train)
        #print(self.train.info())
        self.process_target()
        self.target =  self.get_target()
        ntrain = get_numeric_data(self.train_clean)
        (cat_train, cat_test) = self.get_categorial_data(self.train_clean, self.test)
        logger.info("begin combine data")
        self.data = combine_data(ntrain, cat_train)
        logger.info("end combine data")
        self.data_scaled, scaler = scale_data(self.data, self.target)
    
        (X_train, X_test, y_train, y_test) = model_selection.train_test_split(self.data, self.target,  test_size = 0.3, shuffle = True)

        self.model = self.get_model( X_train, y_train)
        
        filename = 'last_model3.sav'
        pickle.dump(self.model, open(filename, 'wb'))
        
        a_test = np.array(y_test)
        a = self.model.predict(X_test) 
        func = (lambda x : math.e ** x)
        a_test1 = func(a_test)
        a1 = func(a)
        print(a1[1:50])
        print(a_test1[1:50])
        print ("MAPE = ", MAPE(a1, a_test1))

        return self.model
    
    
    
    
    
    
        
#a = model.predict(X_test) # предсказание


if __name__ == '__main__':
    model_obj = Model()
    model = model_obj.make_model_work()
    data_to_predict = model_obj.make_data_to_predict()


#def split_data(Xd):
#    ids = Xd.iloc[:, 0]
#    Xd.drop(0, 1)



#Xd1 = pd.DataFrame(Xd1)
#Xd1['id'] = ids.to_list()


#(X_train, 
# X_test, 
# y_train, y_test) = model_selection.train_test_split(Xd1, target,  test_size = 0.3, shuffle = True)




#X_train = pd.DataFrame(X_train)
#X_train['target'] = y_train.to_list()

#ids1 = diff_bad1['id'].to_list()
#ids2 = diff_bad2['id'].to_list()
#print(ids1)

#X_train_clean = X_train[~X_train['id'].isin(ids1)]
#X_train_clean = X_train_clean[~X_train_clean['id'].isin(ids2)]

#y_train = X_train_clean['target']
#X_train = X_train_clean.drop('target', 1)


#X_test = pd.DataFrame(X_test)


#print(X_train)

#ids_train = X_train['id']
#ids_test = X_test['id']
 
#X_train = X_train.drop('id', 1)
#X_test = X_test.drop('id', 1)

#print(X_train.shape)