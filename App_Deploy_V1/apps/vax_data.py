from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
from pandasql import sqldf
pysqldf=lambda q :sqldf(q,globals())
import json
import pathlib
from app import app

PATH=pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("../datasets").resolve()

#Data Preparation
conn = sqlite3.connect(DATA_PATH.joinpath('CovidIndia.sqlite'))
Data=pd.read_sql_query("SELECT *  FROM Data",conn)
State=pd.read_sql_query("SELECT *  FROM State",conn)
State_Data=pd.read_sql_query("SELECT *  FROM State_Data",conn)

Joined_DF=pysqldf("Select state_code, Date,Tested,Vaccinated1 as First_Dose,Vaccinated2 as Second_Dose,State_Name,State_Area,State_Population from Data left join State on Data.state_id=State.id left join State_Data on Data.state_id=State_Data.state_id")
Joined_DF["Date"]=pd.DatetimeIndex(Joined_DF['Date'])

#changing names to make it compatible for geojson
Joined_DF["State_Name"].replace({"Andaman and Nicobar Islands":"Andaman & Nicobar Island","Arunachal Pradesh":"Arunanchal Pradesh",
                               "Daman and Diu":"Daman & Diu","Delhi":"NCT of Delhi","Jammu and Kashmir":"Jammu & Kashmir",
                               "Pondicherry":"Puducherry",None:"Jammu & Kashmir"},inplace=True)

Summary_Table=pysqldf("Select State_Name,sum(First_Dose) as 'Partially_Vax', sum(Second_Dose) as 'Fully_Vax'"
           "from Joined_DF group by State_Name")

#building geojson file
india_states = json.load(open(DATA_PATH.joinpath("states_india.geojson"), "r"))
state_id_map = {}
for feature in india_states["features"]:
    feature["id"] = feature["properties"]["state_code"]
    state_id_map[feature["properties"]["st_nm"]] = feature["id"]

#Initializing Dash
list_of_states=sorted(Joined_DF["State_Name"].unique()) #input is an array
list_of_states.append("India")

list_of_states2=list_of_states.copy()
list_of_states2.remove("India")

#app layout
layout = dbc.Container([

    dbc.Row([
        dbc.Col(html.H1("Vaccination Coverage",
                        className="text-center bg-transparent mb-5 border display-5"),  # put space to apply multiple classNames
                width={'size': 8, 'offset': 2, 'order': 1})
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id="states_dpdwn", multi=False, value="India",
                         options=[{'label': x, 'value': x} for x in list_of_states],
                         style={'width': "100%"},
                         className="dbc mb-2"
                         )
        ],width={'size': 6, 'offset': 3, 'order': 1})
    ],align="center"),

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='line_graph_day',
                figure={})
        ], className="border",width={'size':12, 'offset': 0, 'order': 1}),

        dbc.Col([
            dcc.Graph(
                id='line_graph_cum',
                figure={})
        ], className="border",width={'size':12, 'offset': 0, 'order': 2})
    ],className="border-dark mb-5",align="center"),

    dbc.Row([
        html.Div(children="Compare Vaccination",
                 className="text-center  text-white mb-2 display-8")
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id="states_dpdwn2", multi=True, value=["Andaman & Nicobar Island"],
                         options=[{'label': x, 'value': x} for x in list_of_states2],
                         clearable=False,
                         searchable=True)
        ], width={'size': 12, 'offset': 0, 'order': 1})
    ], className="mb-2",align='center'),

    dbc.Row([
        dbc.Col([
            dcc.Tabs(id="tabs", value="First_Dose", children=[
                dcc.Tab(label="First_Dose", value="First_Dose"),
                dcc.Tab(label="Second_Dose", value="Second_Dose")])
        ],className=' text-white'),

        dbc.Col([
            dcc.Graph(
                id='line_graph_cum_com',
                figure={})
        ], width={'size': 10, 'offset': 1, 'order': 1})
    ],className="border mb-4"),

    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id="Date_slider",
                min_date_allowed='2021-01-16 00:00:00',
                max_date_allowed=Joined_DF["Date"].max(),
                initial_visible_month='2021-01-16 00:00:00',
                start_date='2021-01-16 00:00:00',
                end_date=Joined_DF["Date"].max()
            )

        ],className=' text-white', width={'size': 6, 'offset': 3, 'order': 1})
    ],  className="mb-2",justify='center'),

    dbc.Row([
        dbc.Col([
            dcc.Tabs(id="Map_Tabs", value="First_Dose", children=[
                dcc.Tab(label="First_Dose", value="First_Dose"),
                dcc.Tab(label="Second_Dose", value="Second_Dose")])
        ],className=' text-white'),
        dbc.Col([
                dcc.Graph(
                    id='India_Map1',
                    figure={})
            ],width={'size': 10, 'offset': 1, 'order': 1})
    ],className="border mb-4"),

    # dcc.Store inside the user's current browser session
    dcc.Store(id='Joined_DF_filtered1', data=[], storage_type='session'),
    dcc.Store(id='Joined_DF_filtered2', data=[], storage_type='session'),
    dcc.Store(id='Joined_DF_filtered3', data=[], storage_type='session')

],className='dbc')

# Callback section: connecting the components

@app.callback(
    Output('Joined_DF_filtered1','data'),
    Input('states_dpdwn', 'value')
)

def store_data_filtered(state):
    if state == "India":
        dff = Joined_DF.groupby("Date").sum().reset_index()
        dff.insert(3, "Cum_Vax1", dff["First_Dose"].cumsum(), "True")
        dff.insert(5, "Cum_Vax2", dff["Second_Dose"].cumsum(), "True")

    else:
        dff = Joined_DF[Joined_DF["State_Name"] == state]
        dff.insert(3, "Cum_Vax1", dff["First_Dose"].cumsum(), "True")
        dff.insert(5, "Cum_Vax2", dff["Second_Dose"].cumsum(), "True")

    return dff.to_dict('records')

@app.callback(
    Output('Joined_DF_filtered2','data'),
    Input('states_dpdwn2', 'value')
)

def store_data_filtered2(state):
    if state==[]:
        dff=Joined_DF[Joined_DF["State_Name"]=='Andaman & Nicobar Island']
    else:
        dff = Joined_DF[Joined_DF["State_Name"].isin(state)]

    dff.insert(3, "Cum_Vax1", dff.groupby(["State_Name"])["First_Dose"].cumsum(), True)
    dff.insert(5, "Cum_Vax2", dff.groupby(["State_Name"])["Second_Dose"].cumsum(), True)
    dff.insert(4, "First_Dose(%)", (dff["Cum_Vax1"] / dff["State_Population"])*100, True)
    dff.insert(6, "Second_Dose(%)", (dff["Cum_Vax2"] / dff["State_Population"])*100, True)

    return dff.to_dict('records')

@app.callback(
    Output("Joined_DF_filtered3", "data"),
    Input('Date_slider', 'start_date'),
    Input('Date_slider', 'end_date')
)
def store_data_filtered3(start_date, end_date):
    dff1 = Joined_DF.drop(columns=["State_Area", "State_Population", "Tested"])
    dff2 = State_Data.drop(columns=["state_id", "state_code", "State_Area"])

    mask = (dff1["Date"] > start_date) & (dff1["Date"] < end_date)
    dff1 = dff1.loc[mask]

    dff1 = dff1.groupby("State_Name").sum().reset_index()

    dff3 = pd.merge(dff1,
                    dff2,
                    on="State_Name",
                    how="left")

    dff3["id"] = dff3["State_Name"].apply(lambda x: state_id_map[x])

    dff3.insert(3, "First_Dose(%)", (dff3["First_Dose"] / dff3["State_Population"])*100, True)
    dff3.insert(5, "Second_Dose(%)", (dff3["Second_Dose"] / dff3["State_Population"])*100, True)

    return dff3.to_dict('records')

# callback for first two graphs
@app.callback(
    [Output('line_graph_day', 'figure'),
     Output('line_graph_cum', 'figure')],
    Input('Joined_DF_filtered1', 'data')
)
def update_graph1(data):

    dff=pd.DataFrame(data)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=dff["Date"],
        y=dff["First_Dose"],
        mode='lines',
        name="First Dose",
        hovertemplate="%{y:,.0f}<br>"
    ))

    fig1.add_trace(go.Scatter(
        x=dff["Date"],
        y=dff["Second_Dose"],
        mode='lines',
        name="Second Dose",
        hovertemplate="%{y:,.0f}<br>"
    ))

    fig1.update_layout(hovermode="x unified",
                       template="plotly_dark")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=dff["Date"],
        y=dff["Cum_Vax1"],
        mode='lines',
        name="First Dose",
        hovertemplate="%{y:,.0f}<br>"
    ))

    fig2.add_trace(go.Scatter(
        x=dff["Date"],
        y=dff["Cum_Vax2"],
        mode='lines',
        name="Second Dose",
        hovertemplate="%{y:,.0f}<br>",
    ))

    fig2.update_layout(hovermode="x unified",
                       template="plotly_dark")

    return fig1, fig2


# callback for 3rd graph(comparing percentage coverage by day)
@app.callback(
    Output('line_graph_cum_com', 'figure'),
    Input('Joined_DF_filtered2', 'data'),
    Input('tabs', 'value')
)

def update_graph2(data, tab):
    dff=pd.DataFrame(data)

    if tab == "First_Dose":
        fig = px.line(
            dff,
            x="Date",
            y="First_Dose(%)",
            color="State_Name",
            markers=False,
            hover_data={'Date': True,
                        'State_Name': True,
                        'First_Dose(%)': ':.2f'}
            )

    elif tab == "Second_Dose":
        fig = px.line(
            dff,
            x="Date",
            y="Second_Dose(%)",
            color="State_Name",
            markers=False,
            hover_data={'Date': True,
                        'State_Name': True,
                        'Second_Dose(%)': ':.2f'}
        )

    fig.update_layout(template="plotly_dark",
                      hovermode="x unified")

    return fig


# callback for last 2 maps
@app.callback(
    Output("India_Map1", 'figure'),
    Input("Joined_DF_filtered3", "data"),
    Input('Map_Tabs', 'value')
)
def update_graph3(data, tab):
    dff3=pd.DataFrame(data)

    if tab == "First_Dose":
        map1 = px.choropleth(
            dff3,
            locations="id",
            geojson=india_states,
            color="First_Dose(%)",
            template="plotly_dark",
            hover_name="State_Name",
            hover_data={"State_Name":False,
                        'First_Dose':':,',
                        'First_Dose(%)': ':.2f'},
            color_continuous_scale=px.colors.diverging.RdYlGn,  # https://plotly.com/python/builtin-colorscales/
            range_color=[0, 100]
        )

        map1.update_geos(fitbounds="locations", visible=False)

    elif tab == "Second_Dose":
        map1 = px.choropleth(
            dff3,
            locations="id",
            geojson=india_states,
            color="Second_Dose(%)",
            template="plotly_dark",
            hover_name="State_Name",
            hover_data={"State_Name":False,
                        'Second_Dose':':,',
                        'Second_Dose(%)': ':.2f'},
            color_continuous_scale=px.colors.diverging.RdYlGn,  # https://plotly.com/python/builtin-colorscales/
            range_color=[0, 100]
        )

        map1.update_geos(fitbounds="locations", visible=False)

    return map1

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
