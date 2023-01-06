import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output

app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                # meta_tags is to make the app mobile compatible
                )

app.layout=html.Div([
    dcc.Location(id='url', refresh=False),

    html.Div([
        dcc.Link('Case Data |', href='/apps/covidviz'),
        dcc.Link('Vaccination Data',href='/apps/Vaccination_Viz')
    ]),

    html.Div(id='page-content', children=[])
])

if __name__ == '__main__':
    app.run_server(debug=True,use_reloader=False)