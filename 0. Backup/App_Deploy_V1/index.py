import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Connect to main app.py file
from app import app
from app import server

# Connect to your app pages
from apps import case_data,vax_data

app.layout=dbc.Container([
    dcc.Location(id='url', refresh=False),
    html.Div([
        dcc.Link('Covid Cases |', href='/apps/case_data'),
        dcc.Link(' Vaccination', href='/apps/vax_data')
    ]),

    html.Div(
                id='page-content',children=[]
            )
        ])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/apps/case_data':
        return case_data.layout
    if pathname == '/apps/vax_data':
        return vax_data.layout
    else:
        return "404 Page Error! Please choose a link"

if __name__ == '__main__':
    app.run_server(debug=False, use_reloader=False)
