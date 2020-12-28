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
                                    f"What does it mean  >",
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
                                    f"What kind of data we have  >",
                                    id=f"group-dwh-toggle",
                                    size="lg",
                                    color="secondary",
                                ), className="card-title",
                                style={'margin-bottom': '0'},
                            )
                        ),
                    ], md=8
                ),
            ],  # no_gutters=True,
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
                                html.P("Apply filters and find apartments similar to yours",
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

        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.CardHeader(
                            html.H3(
                                dbc.Button(
                                    f"Efficiency  >",
                                    id=f"group-f-toggle",
                                    size="lg",
                                    color="secondary",
                                ), style={'margin-bottom': '0'},
                            )
                        ),
                    ], md=4),
                dbc.Col(
                    [
                        dbc.CardHeader(
                            html.H3(
                                dbc.Button(
                                    f"What next  >",
                                    id=f"group-wn-toggle",
                                    size="lg",
                                    color="secondary",
                                ), style={'margin-bottom': '0'},
                            )
                        ),
                    ], md=8),
            ]
        ),
        dbc.Collapse(
            dbc.CardBody(
                [
                    html.P("Optimizing the cost of rental commission",
                           className="card-text", ),
                    html.P(
                        [
                            html.B("E = c * p * n, where:")
                        ],
                        className="card-text", ),
                    html.Ul(
                        [
                            html.Li("c - site commission when renting a house"),
                            html.Li("p - the cost of renting an apartment per day"),
                            html.Li("n - the number of rental days for a certain period"),
                        ]
                    ),
                    html.P("We get an estimate of the effectiveness of the service impact:",
                           className="card-text",
                           ),
                    html.P(
                        [
                            html.B("∆ E = c * (nNew * pNew - nOld * pOld), where:")
                        ],
                        className="card-text",
                    ),
                    html.Ul(
                        [
                            html.Li("pOld, oNew - current and recommended housing price"),
                            html.Li("nNew, nOld - the number of rental days with the current "
                                    "and recommended price for the period"),
                        ]
                    ),
                ]
            ),
            id=f"collapse-f",
        ),
        dbc.Collapse(
            dbc.CardBody(
                [
                    html.P("Recommendations to raise prices will artificially increase prices over "
                           "time, which can have negative consequences in the long term for users "
                           "and the company. It would be wiser to refine the system in order to make "
                           "recommendations based not only on ad data, but also on market fluctuations "
                           "- when demand increases, you can recommend raising prices (and lowering "
                           "prices when demand decreases) in order to maximize profits. The model can "
                           "also be improved if there is data on the effect of price changes on changes "
                           "in demand.",
                           className="card-text", ),
                ]
            ),
            id=f"collapse-wn",
        ),

    ],
)

app.layout = dbc.Container(
    [
        dbc.Card(
            [
                dbc.CardImg(src="data:image/jpeg;base64,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", top=True),
            ],
            # style={"width": "18rem"},
        ),
        html.Hr(),
        html.H1("Better price for landlord - better profit for Airbnb"),
        html.Hr(),

        # description
        dbc.Row(
            [
                dbc.Col(description, md=12),
            ]
        ),

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
        html.Hr()
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


# Toggles
@app.callback(
    Output(f"collapse-wdtm", "is_open"),
    Output(f"collapse-dwh", "is_open"),
    [Input(f"group-wdtm-toggle", "n_clicks")],
    [Input(f"group-dwh-toggle", "n_clicks")],
    [State(f"collapse-wdtm", "is_open")],
    [State(f"collapse-dwh", "is_open")],
)
def toggle_accordion(n1, n2, is_open1, is_open2):
    ctx = dash.callback_context

    if not ctx.triggered:
        return False, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "group-wdtm-toggle" and n1:
        return not is_open1, False
    elif button_id == "group-dwh-toggle" and n2:
        return False, not is_open2
    return False, False


@app.callback(
    Output(f"collapse-f", "is_open"),
    Output(f"collapse-wn", "is_open"),
    [Input(f"group-f-toggle", "n_clicks")],
    [Input(f"group-wn-toggle", "n_clicks")],
    [State(f"collapse-f", "is_open")],
    [State(f"collapse-wn", "is_open")],
)
def toggle_accordion2(n1, n2, is_open1, is_open2):
    ctx = dash.callback_context

    if not ctx.triggered:
        return False, False
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id == "group-f-toggle" and n1:
        return not is_open1, False
    elif button_id == "group-wn-toggle" and n2:
        return False, not is_open2
    return False, False


if __name__ == '__main__':
    # app.run_server(host = '138.68.99.110', debug=True)
    app.run_server(debug=True)
