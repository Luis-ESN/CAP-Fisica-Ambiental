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

# Layout do aplicativo
quest_um = html.Div([
    html.H3("Questionário sobre Eventos",style={'margin-top':'1cm'}),
    
    # Pergunta A
    html.Label("Possui algum rio no local do evento?", style={'margin-top':'1cm'}),
    dcc.Dropdown(
        id='pergunta_a',
        options=[
            {'label': 'Sim', 'value': 'Sim'},
            {'label': 'Não', 'value': 'Não'}
        ],
        value=None,
        placeholder='Selecione uma resposta',
        style={'width':'7cm'}
    ),
    
    # Pergunta B
    html.Label("Em caso positivo, houve um transbordamento do rio?", style={'margin-top':'1cm'}),
    dcc.Dropdown(
        id='pergunta_b',
        options=[
            {'label': 'Sim', 'value': 'Sim'},
            {'label': 'Não', 'value': 'Não'}
        ],
        value=None,
        placeholder='Selecione uma resposta',
        style={'width':'7cm'}
    ),
    
    # Pergunta C
    html.Label("Houve escoamento de água superficial com alta energia de transporte?", style={'margin-top':'1cm'}),
    dcc.Dropdown(
        id='pergunta_c',
        options=[
            {'label': 'Sim', 'value': 'Sim'},
            {'label': 'Não', 'value': 'Não'}
        ],
        value=None,
        placeholder='Selecione uma resposta',
        style={'width':'7cm'}
    ),
    
    html.Button('Enviar', id='Enviar', n_clicks=0, style={'margin-top':'1cm'}),
    html.Div(id='resposta_quest_um') #espaco onde sera exibido o retorno
])

@app.callback(
    Output('resposta_quest_um', 'children'),
    Input('Enviar', 'n_clicks'),  
    State('pergunta_a', 'value'),
    State('pergunta_b', 'value'),
    State('pergunta_c', 'value')
)
def class_evento(n_clicks, resposta_a, resposta_b, resposta_c):
    if n_clicks > 0: 
        if resposta_a == 'Não' and resposta_b == 'Não' and resposta_c == 'Não':
            evento = 'ALAGAMENTO'
            descricao = 'É um acúmulo momentâneo de águas em determinados locais por deficiência no sistema de drenagem.'
        elif resposta_a == 'Não' and resposta_b == 'Não' and resposta_c == 'Sim':
            evento = 'ENXURRADA'
            descricao = 'É um escoamento superficial concentrado e com alta energia de transporte, que pode ou não estar associado aos rios. As enxurradas são capazes de carregar pessoas, carros, caçambas e outros objetos. Geralmente ocorrem em áreas com deficiência no sistema de drenagem, em locais com maior declividade, entre outras.'
        elif resposta_a == 'Sim' and resposta_b == 'Não' and resposta_c == 'Não':
            evento = 'ENCHENTE'
            descricao = 'É definida pela elevação do nível d’água no canal de drenagem devido ao aumento da vazão, atingindo a cota máxima do canal de drenagem, porém, sem extravasar (sem o rio transbordar).'
        elif resposta_a == 'Sim' and resposta_b == 'Sim' and resposta_c == 'Não':
            evento = 'INUNDAÇÃO'
            descricao = 'Representa o transbordamento de um curso d’água, atingindo a planície de inundação ou área de várzea.'
        elif resposta_a == 'Sim' and resposta_b == 'Sim' and resposta_c == 'Sim':
            evento = 'INUNDAÇÃO COM ENXURRADA'
            descricao = 'Transbordamento de um curso d’água, atingindo a planície de inundação ou área de várzea e com escoamento superficial concentrado e com alta energia de transporte.'
        else:
            evento = 'INVÁLIDO'
            descricao = 'Por favor, verifique suas respostas.'
        
        return html.Div([
            html.H3(f"Evento Identificado: {evento}"),
            html.P(descricao)
        ], style={'backgroundColor': '#f0f0f0', 'padding': '20px', 'border-radius': '5px', 'margin-top': '1cm'})
    return ""


app.layout = html.Div([titulo, selector,quest_um])


app.callback( Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))




if __name__ == '__main__':
    
    #layout = html.Div([title, table_tabs])

    
    
    app.run(debug=True)