import datetime
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import dash
import pandas as pd

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Demo dashboard"
server = app.server




if __name__ == "__main__":
    app.run_server(debug=True)