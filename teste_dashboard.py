# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 19:53:36 2024

@author: luise
"""

import pandas as pd
import dash
from dash.dependencies import Input, Output, State
#from dash_table import DataTable
from dash import dash_table
#import dash_core_components as dcc
from dash import dcc
#import dash_html_components as html
from dash import html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import qualitative
import pandas as pd
#from dash import Dash, html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#app = Dash(__name__, external_stylesheets=external_stylesheets)
app = dash.Dash(external_stylesheets=external_stylesheets)

titulo = html.Div([
    html.H2('Interative Dashboard for Extreme Events Auditing', 
            style={'textAlign': 'center'}),
    html.H2('IDEEA',
            style={'textAlign': 'center'})
    ])

selector = html.Div([
    dcc.Upload(
        id='upload-image',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '30%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'margin-left':'35%'
        },
        # Allow multiple files to be uploaded
        multiple=True)
        ])










app.layout = html.Div([titulo, selector])


app.callback( Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))




if __name__ == '__main__':
    
    #layout = html.Div([title, table_tabs])

    
    
    
    
    app.run(debug=True)