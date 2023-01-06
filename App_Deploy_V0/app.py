import dash

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG],
                suppress_callback_exceptions=True,
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                # meta_tags is to make the app mobile compatible
                )

server=app.server
