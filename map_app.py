import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_leaflet as dl

import numpy as np
import pandas as pd

import branca.colormap as cm

from data_model import get_sample_data
from airbnb_model import get_price
from airbnb_model import get_options, make_prediction
import plotly.express as px
import plotly

app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])
server = app.server

property_list = ['Earth house', 'Hut', 'Treehouse', 'Townhouse', 'Tipi', 'Yurt', 'Apartment', 'Hostel', 'Parking Space',
                 'Cottage', 'Farm stay', 'Aparthotel', 'Nature lodge', 'Bed and breakfast', 'Guesthouse', 'Tiny house',
                 'Villa', 'Cabin', 'Boutique hotel', 'Lighthouse', 'Ryokan (Japan)', 'Tent', 'Other',
                 'Casa particular (Cuba)', 'Houseboat', 'Guest suite', 'Bus', 'Boat', 'Hotel',
                 "Shepherd's hut (U.K., France)", 'Loft', 'Bungalow', 'Camper/RV', 'Chalet', 'Igloo', 'Dome house',
                 'House', 'Resort', 'Barn', 'Island', 'Serviced apartment', 'Condominium']
room_type_list = ['Entire home/apt', 'Private room', 'Shared room']
cancel_list = ['moderate', 'flexible', 'strict', 'super_strict_30', 'super_strict_60', 'strict_14_with_grace_period']
neighbourhood_list = ['Greenwich', 'Islington', 'Enfield', 'Westminster', 'Brent', 'Bexley', 'Hounslow', 'Camden',
                      'Haringey', 'Harrow', 'Redbridge', 'Croydon', 'Southwark', 'Tower Hamlets', 'Newham', 'Lewisham',
                      'Kensington and Chelsea', 'Hillingdon', 'Hackney', 'Sutton', 'Richmond upon Thames',
                      'Barking and Dagenham', 'Bromley', 'Barnet', 'Havering', 'City of London', 'Merton', 'Ealing',
                      'Waltham Forest', 'Wandsworth', 'Kingston upon Thames', 'Lambeth', 'Hammersmith and Fulham']

neighbourhood_cleansed_options = get_options(neighbourhood_list)
room_type_options = get_options(room_type_list)
cancel_options = get_options(cancel_list)
property_options = get_options(property_list)

carto_urls = {
    'carto_dark': 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
    'carto_light': 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
    'carto_color': 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png',
}
carto_attribution = '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; <a href="https://carto.com/attributions">CARTO</a>'
carto_subdomatins = 'abcd'
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
    markers = []
    vmax = price.median() * 2
    colormap = colmap.scale(0, vmax)
    df = df_lat_lon[['latitude', 'longitude']]
    df.loc[:, 'price'] = price
    df.loc[:, 'price_model'] = price_model
    for row in df.itertuples():
        text_price = str(int(row.price))
        text_color = 'black' if row.price < row.price_model else 'blue'
        marker = dl.DivMarker(
            position=[row.latitude, row.longitude],
            title='Estimate price = {} $'.format(int(row.price_model)),
            iconOptions={
                'iconSize': (38, 20),
                'icon_anchor': (11, 10),
                'html': '<div style="font-size: 10pt; background-color: %s; '
                        'color: %s; text-align: center">%s</div>' %
                        (colormap(row.price), text_color, text_price + '$'),
            }
        )
        markers.append(marker)
    return markers


'''
START OF TEMPLATE PART
'''
# Switches for Map filtering
switches = dbc.FormGroup(
    [
        dbc.CardBody(
            [
                dbc.Checklist(
                    options=[
                        {"label": "District", "value": ''},
                    ],
                    id="reg_check",
                    switch=True,
                    inline=True,
                    className="custom-control-inline"
                ),
                dbc.Checklist(
                    options=[
                        {"label": "Room type", "value": ''},
                    ],
                    id="room_check",
                    switch=True,
                    inline=True,
                    className="custom-control-inline"
                ),
                dbc.Checklist(
                    options=[
                        {"label": "Cancellation policy", "value": ''},
                    ],
                    id="cancel_check",
                    switch=True,
                    inline=True,
                    className="custom-control-inline"
                ),
                dbc.Checklist(
                    options=[
                        {"label": "Property type", "value": ''},
                    ],
                    id="prop_check",
                    switch=True,
                    inline=True,
                    className="custom-control-inline"
                ),
                dbc.Checklist(
                    options=[
                        {"label": "Accommodates", "value": ''},
                    ],
                    id="acc_check",
                    switch=True,
                    inline=True,
                    className="custom-control-inline"
                ),
                dbc.Checklist(
                    options=[
                        {"label": "Beds", "value": ''},
                    ],
                    id="beds_check",
                    switch=True,
                    inline=True,
                    className="custom-control-inline"
                ),
                dbc.Checklist(
                    options=[
                        {"label": "Bathrooms", "value": ''},
                    ],
                    id="bath_check",
                    switch=True,
                    inline=True,
                    className="custom-control-inline"
                ),
                dbc.Checklist(
                    options=[
                        {"label": "Bedrooms", "value": ''},
                    ],
                    id="bedrooms_check",
                    switch=True,
                    inline=True,
                    className="custom-control-inline"
                ),
                dbc.Checklist(
                    options=[
                        {"label": "Minimum nights", "value": ''},
                    ],
                    id="night_check",
                    switch=True,
                    inline=True,
                    className="custom-control-inline"
                ),
                dbc.Checklist(
                    options=[
                        {"label": "Guests included", "value": ''},
                    ],
                    id="guests_check",
                    switch=True,
                    inline=True,
                    className="custom-control-inline"
                ),
                dbc.Checklist(
                    options=[
                        {"label": "Cleaning fee", "value": ''},
                    ],
                    id="fee_check",
                    switch=True,
                    inline=True,
                    className="custom-control-inline"
                ),
            ], id="switches-inline-input"
        ),
    ]
)

# Form controls for Model review
form_controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("District"),
                dbc.Select(
                    id="reg",
                    options=neighbourhood_cleansed_options,
                    value="Greenwich",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Room type"),
                dbc.Select(
                    id="room_type",
                    options=room_type_options,
                    value="Entire home/apt",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Cancellation policy"),
                dbc.Select(
                    id="cancel",
                    options=cancel_options,
                    value='moderate',
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Property type"),
                dbc.Select(
                    id="property",
                    options=property_options,
                    value='Apartment',
                ),
            ]
        ),
        dbc.Row(
            [
                html.Label("Choose your location on map"),
                dbc.Col(
                    [
                        dbc.FormGroup(
                            [
                                # dbc.Label("Latitude"),
                                dbc.Input(
                                    id="latitude",
                                    value='51.50853',
                                    disabled=True,
                                    type='number',
                                    placeholder="Latitude"
                                ),
                            ]
                        ),
                    ], md=6,
                ),
                dbc.Col(
                    [
                        dbc.FormGroup(
                            [
                                # dbc.Label("Longitude"),
                                dbc.Input(
                                    id="longitude",
                                    value='-0.12574',
                                    disabled=True,
                                    type='number',
                                    placeholder="Longitude"
                                )
                            ],
                        ),
                    ], md=6,
                ),
            ], no_gutters=True,
        ),
        dbc.FormGroup(
            [
                dbc.Label("Accommodates"),
                dbc.Input(
                    id="accomodates",
                    min='1',
                    value='1',
                    type='number',
                ),
            ],
        ),
        dbc.FormGroup(
            [
                dbc.Label("Beds"),
                dbc.Input(
                    id="beds",
                    min='0',
                    value='1',
                    type='number',
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Bathrooms"),
                dbc.Input(
                    id="bath",
                    min='0',
                    value='0',
                    type='number',
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Bedrooms"),
                dbc.Input(
                    id="bedrooms",
                    min='0',
                    value='0',
                    type='number',
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Minimum nights"),
                dbc.Input(
                    id="nights",
                    min='1',
                    value='1',
                    type='number',
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Guests included"),
                dbc.Input(
                    id="guests",
                    min='1',
                    value='1',
                    type='number',
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Cleaning fee"),
                dbc.Input(
                    id="fee",
                    min='0',
                    value='0',
                    type='number',
                ),
            ]
        ),
    ],
    body=True,
)

# MAP
map_div = html.Div(
    dl.Map(
        id="map",
        children=
        [
            dl.LayersControl(
                carto_tile_layers +
                [
                    dl.Overlay(
                        dl.LayerGroup(
                            id='marker_layer',
                        ),
                        name="price_makers",
                        checked=True
                    )
                ]
            ),
            dl.LayerGroup(
                id="click_marker",
                children=[],
            )
        ],
        zoom=11,
        center=[51.50853, -0.12574],
    ),
    style=
    {
        'width': '100%',
        'height': '500px',
        # 'margin': '10px 0 0 10px',
    }
)

# Histogram
hist = dcc.Graph(id='graph', )

# Description of project
description = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.CardHeader(
                            html.H2(
                                dbc.Button(
                                    f"What does it mean >",
                                    id=f"group-wdtm-toggle",
                                    size="lg",
                                    color="secondary",
                                ), className="card-title",
                                style={'margin-bottom': '0'},
                            )
                        ),
                    ], md=4
                ),
                dbc.Col(
                    [
                        dbc.CardHeader(
                            html.H2(
                                dbc.Button(
                                    f"What kind of data we have >",
                                    id=f"group-dwh-toggle",
                                    size="lg",
                                    color="secondary",
                                ), className="card-title",
                                style={'margin-bottom': '0'},
                            )
                        ),
                    ], md=8
                ),
            ], #no_gutters=True,
        ),
        dbc.Collapse(
            dbc.CardBody(
                [
                    html.P("Users are not always able to define the value of their apartments, "
                           "because many factors must be taken into account.",
                           className="card-text", ),
                    html.P("We can make this task easier for users, increase rental income and "
                           "our own profit through a higher commission:",
                           className="card-text", ),
                    html.Ol(
                        [
                            html.Li("If the landlord puts a price, and the model has determined "
                                    "a higher price, then it is worth offering to raise the price "
                                    "of the apartment."),
                            html.Li("The landlord can independently “play” with the settings, find "
                                    "his own points of growth (for example, put an extra bed)."),
                            html.Li("The opportunity to see the distribution of prices for "
                                    "apartments with similar basic properties, to understand how "
                                    "much the rental price can be increased, for example, by "
                                    "making repairs, improving the photo of the apartment, etc."),
                        ]
                    ),
                    html.P("An additional plus is increased loyalty to the company by providing a "
                           "convenient service for price research.",
                           className="card-text", ),
                ]
            ),
            id=f"collapse-wdtm",
        ),
        dbc.Collapse(
            dbc.CardBody(
                [
                    html.P("In our research the data with parameters of London's apartments "
                           "scraped from Airbnb are used, also we use datasets with reviews "
                           "of travelers and information on the availability of the apartments "
                           "during the year.",
                           className="card-text", ),
                ]
            ),
            id=f"collapse-dwh",
        ),
    ],
)

# Data review
# data_review = dbc.Card(
#     [
#         dbc.CardBody(
#             [
#                 html.H2("What kind of data we have",
#                         className="card-title", ),
#                 html.P("Some words about data ...",
#                        className="card-text", ),
#             ],
#         ),
#     ],
# )

# Model review
model_review = dbc.Row(
    [
        dbc.Col(
            [
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H3("Get the best price",
                                        className="card-title", ),
                                html.P("Fill-in the form below",
                                       className="card-text", ),
                            ],
                        ),
                    ],
                ),
                form_controls,
                dbc.Alert(
                    [
                        html.H4(id="price", style={'margin-bottom': '0'})
                    ],
                    color="success"),
            ], md=4,
        ),
        dbc.Col(
            [
                dbc.Card(
                    [
                        dbc.CardBody(
                            [
                                html.H3("Make a research on map",
                                        className="card-title", ),
                                html.P("Apply filters to the map",
                                       className="card-text", ),
                            ],
                        ),
                    ],
                ),
                dbc.Card(
                    [
                        switches,
                        map_div,
                        hist,
                    ]
                )
            ], md=8,
        ),
    ],
)

# Conclusion
conclusion = dbc.Card(
    [
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3("Efficiency",
                                        className="card-title", ),
                                html.P("To assess the effectiveness, we can derive the formula:",
                                       className="card-text", ),
                                html.P(
                                    [
                                        html.B("E = c * n * (dP - dk * OldP), where:")
                                    ],
                                    className="card-text", ),
                                html.Ul(
                                    [
                                        html.Li("c - site commission when renting a house"),
                                        html.Li("n - number of leases for the period"),
                                        html.Li("dP - the difference between the recommended and current price"),
                                        html.Li("dk - reduction factor for the number of leases (% of outstanding "
                                                "leases due to high prices)"),
                                        html.Li("OldP - current housing price"),
                                    ]
                                ),
                            ], md=6),
                        dbc.Col(
                            [
                                html.H3("What next?",
                                        className="card-title", ),
                                html.P("Recommendations to raise prices will artificially increase prices over "
                                       "time, which can have negative consequences in the long term for users "
                                       "and the company. It would be wiser to refine the system in order to make "
                                       "recommendations based not only on ad data, but also on market fluctuations "
                                       "- when demand increases, you can recommend raising prices (and lowering "
                                       "prices when demand decreases) in order to maximize profits. The model can "
                                       "also be improved if there is data on the effect of price changes on changes "
                                       "in demand.",
                                       className="card-text", ),
                            ], md=6),
                    ]
                ),

            ],
        ),
    ],
)

app.layout = dbc.Container(
    [
        html.Hr(),
        html.H1("Better price for landlord - better profit for Airbnb"),
        html.Hr(),
        # description
        dbc.Row(
            [
                dbc.Col(description, md=12),
            ]
        ),

        # data review
        # dbc.Row(
        #     [
        #         dbc.Col(data_review, md=12),
        #     ]
        # ),

        # model review
        html.Hr(),
        html.H2("Let's try it!", ),
        html.P(
            [
                "The model will find better price for the user's apartment "
                "based on the description, including key features and data "
                "from other ads on Airbnb.",
                html.Br(),
                "Example is given for London, UK.",
            ]
        ),
        model_review,

        # conclusion
        html.Hr(),
        html.H2("Conclusion", ),
        dbc.Row(
            [
                dbc.Col(conclusion, md=12),
            ],
        ),
    ]
)

'''
END OF TEMPLATE PART
'''



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
def update_output_div(reg, room, cancel, prop, lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee):
    price = get_price(reg, room, cancel, prop, lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee)
    return 'Price: {}$'.format(int(price))


@app.callback(  # Output('debug-info', 'children'),
    Output('marker_layer', 'children'),
    Output(component_id='graph', component_property='figure'),
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
    # Input(component_id='latitude', component_property='value'),
    # Input(component_id='longitude', component_property='value'),
    Input(component_id='acc_check', component_property='value'),
    Input(component_id='beds_check', component_property='value'),
    Input(component_id='bath_check', component_property='value'),
    Input(component_id='bedrooms_check', component_property='value'),
    Input(component_id='night_check', component_property='value'),
    Input(component_id='guests_check', component_property='value'),
    Input(component_id='fee_check', component_property='value'),

    # Input('update-button-state', 'n_clicks'),
    # State('num-multi', 'value'),
)
def update_output(reg, room, cancel, prop, lat, lon, accomodates, beds, bath, bedrooms, night, guests, fee,
                  reg_check, room_check, cancel_check, prop_check, acc_check, beds_check, bath_check, bedrooms_check,
                  night_check, guests_check, fee_check):
    (df_lat_lon, price, price_model) = get_sample_data(reg, room, cancel, prop, lat, lon, accomodates, beds, bath,
                                                       bedrooms, night, guests, fee, \
                                                       reg_check, room_check, cancel_check, prop_check, acc_check,
                                                       beds_check, bath_check, bedrooms_check, night_check,
                                                       guests_check, fee_check)
    if price.shape[0] == 0:
        return (plotly.graph_objects.Figure())
    fig = px.histogram(price, nbins=100)
    return price_markers(df_lat_lon, price, price_model), fig


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


# Toogles

# Description toogle
@app.callback(
    Output("collapse-wdtm", "is_open"),
    [Input("group-wdtm-toggle", "n_clicks")],
    [State("collapse-wdtm", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("collapse-dwh", "is_open"),
    [Input("group-dwh-toggle", "n_clicks")],
    [State("collapse-dwh", "is_open")],
)
def toggle_collapse2(n, is_open):
    if n:
        return not is_open
    return is_open


if __name__ == '__main__':
    # app.run_server(host = '138.68.99.110', debug=True)
    app.run_server(debug=True)
