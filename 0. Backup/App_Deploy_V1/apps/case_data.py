from dash import dash_table
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
import plotly.express as px
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

#Preparing Data and Initial DF settings
conn = sqlite3.connect(DATA_PATH.joinpath('CovidIndia.sqlite'))
Data=pd.read_sql_query("SELECT *  FROM Data",conn)

State=pd.read_sql_query("SELECT *  FROM State",conn)

State_Data=pd.read_sql_query("SELECT *  FROM State_Data",conn)

Joined_DF=pysqldf("Select state_code, Date, Confirmed,Recovered,Deceased,Tested,Vaccinated1,Vaccinated2,State_Name,State_Area,State_Population from Data left join State on Data.state_id=State.id left join State_Data on Data.state_id=State_Data.state_id")
Joined_DF["Date"]=pd.DatetimeIndex(Joined_DF['Date'])

#changing names to make it compatible for geojson
Joined_DF["State_Name"].replace({"Andaman and Nicobar Islands":"Andaman & Nicobar Island","Arunachal Pradesh":"Arunanchal Pradesh",
                               "Daman and Diu":"Daman & Diu","Delhi":"NCT of Delhi","Jammu and Kashmir":"Jammu & Kashmir",
                               "Pondicherry":"Puducherry",None:"Jammu & Kashmir"},inplace=True)

Summary_Table=pysqldf("Select State_Name,sum(Confirmed) as 'Total cases', sum(Deceased) as 'Total Deaths', sum(Vaccinated1) as 'Partially_Vax', sum(Vaccinated2) as 'Fully_Vax'"
           "from Joined_DF group by State_Name order by sum(confirmed) DESC")

#building geojson file
india_states = json.load(open(DATA_PATH.joinpath("states_india.geojson"), "r"))
state_id_map = {}
for feature in india_states["features"]:
    feature["id"] = feature["properties"]["state_code"]
    state_id_map[feature["properties"]["st_nm"]] = feature["id"]


#Initializing Dash
list_of_states = sorted(Joined_DF["State_Name"].unique())  # input is an array
list_of_states.append("India")

# https://www.bootstrapcdn.com/bootswatch/
# dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"


# Layout section: Bootstrap (https://hackerthemes.com/bootstrap-cheatsheet/)

layout = dbc.Container([

    dbc.Row([
        dbc.Col(html.H1("Covid Cases - India",
                        className="text-center bg-transparent mb-5 border display-5"),  # put space to apply multiple classNames
                width={'size': 8, 'offset': 2, 'order': 1})  # width of the column
    ]),

    # 2nd row - Dropdown - states_dpdwn
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(id="states_dpdwn", multi=False, value="India",
                         options=[{'label': x, 'value': x} for x in list_of_states],
                         style={'width':"100%"},
                         className="dbc mb-2")
        ],className=' text-white',width={'size': 6, 'offset': 3, 'order': 1})
    ],align="center"
    ),

    # 3rd row - Graphs - line_graph_conf & line_graph_death
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='line_graph_conf',
                figure={}
            )
        ],className="border",width={'size':12, 'offset': 0, 'order': 1}),

        dbc.Col([
            dcc.Graph(
                id='line_graph_death',
                figure={}
            )
        ], className="border",width={'size':12, 'offset': 0, 'order': 2}),

        dbc.Col([
            dcc.Graph(
                id='line_graph_cum_conf',
                figure={}
            )
        ], className="border", width={'size':12, 'offset': 0, 'order': 3}),

        dbc.Col([
            dcc.Graph(
                id='line_graph_cum_death',
                figure={}
            )
        ],className="border", width={'size':12, 'offset': 0, 'order': 4})

    ], className="border border-dark mb-5",align="center"),
    # not sure what it does. Might not be relevent due to the offset and size matching the total col size of 12


    # 4th row - Date Slider

    dbc.Row([
        html.Div(children="Highlights in a date range(use the below date picker)",
                className="text-center text-white mb-2 display-10")
    ]),

    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id="Date_slider",
                min_date_allowed=Joined_DF["Date"].min(),
                max_date_allowed=Joined_DF["Date"].max(),
                initial_visible_month=Joined_DF["Date"].min(),
                start_date=Joined_DF["Date"].min(),
                end_date=Joined_DF["Date"].max()
            )
        ], className=' text-white',width={'size': 6, 'offset': 3, 'order': 1})
    ], className="mb-2",justify='center'),

    # 5th row Bubblechart, IndiaMap
    dbc.Row([
        dbc.Col([
            dcc.Tabs(id="Case_Tabs", value="Tree Map", children=[
                dcc.Tab(label="Tree Map", value="Tree Map"),
                dcc.Tab(label="India Map", value="India Map")])
        ],className="border text-white"),

        dbc.Col([
            dcc.Graph(
                id='Map',
                figure={})
        ],width={'size': 10, 'offset': 1, 'order': 1},className="border")
    ],className="mb-4"),

    # 6th row - Summary Table   https://dash.plotly.com/datatable - need to stylize
    dbc.Row([
        dbc.Col([
            html.Div(id="table_interactive")
        ])

    ],className="border mb-4"),

    # dcc.Store inside the user's current browser session
    dcc.Store(id='Joined_DF_filtered', data=[], storage_type='session'),  # 'local' or 'session'
    dcc.Store(id='Joined_DF', data=[], storage_type='session')

],className="dbc")


# Callback section: connecting the components
@app.callback(
    Output('Joined_DF_filtered','data'),
    Input('states_dpdwn', 'value')
)

def store_data_filtered(state):
    if state == 'India':
        dff = Joined_DF.groupby("Date").sum().reset_index()
        dff.insert(3, "Cum_Conf", dff["Confirmed"].cumsum(), True)
        dff.insert(5, "Cum_Deaths", dff["Deceased"].cumsum(), True)

    else:
        dff = Joined_DF[Joined_DF["State_Name"] == state]
        dff.insert(3, "Cum_Conf", dff["Confirmed"].cumsum(), True)
        dff.insert(5, "Cum_Deaths", dff["Deceased"].cumsum(), True)

    return dff.to_dict('records')

@app.callback(
    Output('Joined_DF','data'),
    Input('Date_slider', 'start_date'),
    Input('Date_slider', 'end_date')
)

def store_data(start_date,end_date):
    dff = Joined_DF
    mask = (dff["Date"] > start_date) & (dff["Date"] < end_date)
    dff = dff.loc[mask]

    return dff.to_dict('records')

# callback for first four graphs
@app.callback(
    [Output('line_graph_conf', 'figure'),
     Output('line_graph_death', 'figure'),
     Output('line_graph_cum_conf', 'figure'),
     Output('line_graph_cum_death', 'figure')
     ],
    Input('Joined_DF_filtered', 'data')
)
def update_graph(data):

    dff=pd.DataFrame(data)
    fig1 = px.line(dff,
                   x='Date',
                   y='Confirmed',
                   markers=False,
                   template="plotly_dark",
                   # hover_name="Date",
                   hover_data={"Date":True,
                               "Confirmed":':,',
                               "Tested":':,',
                               "Deceased":':,'}
                   )

    fig1.update_layout(yaxis={'title': 'Daily Confirmed'},
                       title={'text': "Confirmed Cases", 'font': {'size': 20}, 'x': 0.5, 'xanchor': 'center'}
                       )

    fig2 = px.line(dff, x='Date',
                        y='Deceased',
                        markers=False,
                        template="plotly_dark",
                        hover_data={"Date": True,
                               "Deceased": ':,',
                               "Confirmed": ':,'}
                   )

    fig2.update_layout(yaxis={'title': 'Daily Deaths'},
                       title={'text': "Deaths", 'font': {'size': 20}, 'x': 0.5, 'xanchor': 'center'}
                       )

    fig3 = px.line(dff,
                   x='Date',
                   y='Cum_Conf',
                   markers=False,
                   template="plotly_dark",
                   hover_data={"Date": True,
                               "Cum_Conf":':,',
                               "Cum_Deaths":':,',
                               "Confirmed": ':,',
                               "Deceased": ':,'}
                   )
    fig3.update_layout(yaxis={'title': 'Cum Confirmed cases'},
                       title={'text': "Cumulative Confirmed Cases", 'font': {'size': 20}, 'x': 0.5,
                              'xanchor': 'center'}
                       )

    fig4 = px.line(dff,
                   x='Date',
                   y='Cum_Deaths',
                   markers=False,
                   template="plotly_dark",
                   hover_data={"Date": True,
                               "Cum_Conf":':,',
                               "Cum_Deaths":':,',
                               "Confirmed": ':,',
                               "Deceased": ':,'}
                   )
    fig4.update_layout(yaxis={'title': 'Cum Deaths'},
                       title={'text': "Cumulative Deaths", 'font': {'size': 20}, 'x': 0.5, 'xanchor': 'center'}
                       )

    return fig1, fig2, fig3, fig4


# callback for next two graphs
@app.callback(
    [Output('Map', 'figure'),
     Output('table_interactive', 'children')
     ],
    Input('Joined_DF', 'data'),
    Input('Case_Tabs', 'value')
)

def update_graph2(data,tab):
    dff = pd.DataFrame(data)
    # mask = (dff["Date"] > start_date) & (dff["Date"] < end_date)
    # dff = dff.loc[mask]
    dff2 = dff.groupby("State_Name").sum().reset_index()
    dff2["id"] = dff2["State_Name"].apply(lambda x: state_id_map[x])

    if tab=='Tree Map':
        map1 = px.treemap(dff,
                          path=["State_Name"],
                          values="Deceased",
                          template="plotly_dark",
                          hover_name="State_Name",
                          hover_data={"State_Name": False,
                                      "Deceased": ':,'}
                          )
        map1.update_traces(hovertemplate='State_Name %{label}<br>Deceased %{value}<extra></extra>')

        map1.update_layout(title={'text': "Total Deaths by State", 'font': {'size': 20}, 'x': 0.5, 'xanchor': 'center'})


    elif tab=='India Map':
        map1 = px.choropleth(
            dff2,
            locations="id",
            geojson=india_states,
            color="Deceased",
            template="plotly_dark",
            hover_name="State_Name",
            hover_data={"State_Name": False,
                        "Deceased": ':,',
                        "Confirmed": ':,'},
            color_continuous_scale=px.colors.diverging.Portland,  # https://plotly.com/python/builtin-colorscales/
            color_continuous_midpoint=0)

        map1.update_geos(fitbounds="locations", visible=False)

        map1.update_layout(title={'text': "Total Deaths by State", 'font': {'size': 20}, 'x': 0.5, 'xanchor': 'center'})

    dff3 = dff2.drop(columns=["State_Area", "State_Population", "id"])
    data1 = dff3.to_dict('rows')
    # columns = [{"name": i, "id": i} for i in dff3.columns]
    columns = []

    for i in dff3.columns:
        if i == "State_Name":
            columns.append({'name': i, 'id': i})

        else:
            columns.append({'name': i, 'id': i,'type':'numeric','format':{'specifier':",.2r"}})
            # columns.append({'name': i, 'id': i, 'type': 'numeric', format:Format.Format().group(True)})

    Table = dash_table.DataTable(
        data=data1,
        columns=columns,
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
        style_cell={'textAlign': 'left'},
        style_header={'fontWeight': 'bold'}
        )

    return [map1, Table]


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
