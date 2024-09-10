# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 10:05:56 2024

@author: luise
"""

from dash import Dash, dcc, html, dash_table, Input, Output, State, callback

import base64
#import datetime
import io

import pandas as pd

#import plotly.graph_objects as go
#from plotly.subplots import make_subplots
#from plotly.colors import qualitative

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Dash(__name__, external_stylesheets=external_stylesheets)





# Parte referente ao título da página
titulo = html.Div([
    html.H2('Interative Dashboard for Extreme Events Auditing', 
            style={'textAlign': 'center'}),
    html.H2('IDEEA',
            style={'textAlign': 'center'})
    ])





# Parte referente a importação do arquivo
selector = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ], style={'textAlign': 'center'}),
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
        multiple=False
    ),
    html.Div(id='output-data-upload', style={'textAlign': 'center'}),
])


app.layout = html.Div([titulo, selector])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return html.Div([
                'Arquivo inválido, selecione um arquivo .csv ou .xls'
            ])
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    else:
        return html.Div([
            html.H5(filename),
            
            # O dataframe com os dados é df, use ele para acessar a tabela.
            dash_table.DataTable(
                df.to_dict('records'),
                [{'name': i, 'id': i} for i in df.columns]
            ),
        ])

@callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))


def update_output(list_of_contents, list_of_names, list_of_dates):
    print(list_of_names)
    
    if list_of_contents is not None:
        children = [
            parse_contents(list_of_contents, list_of_names, list_of_dates)]
        return children

if __name__ == '__main__':
    app.run(debug=True)