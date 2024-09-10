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
#import pyhomogeneity as hg
import pymannkendall as mk

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

# Trecho para questionario 1-------------------------------------------------------
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
        elif resposta_a == 'Sim' and resposta_b == 'Não' and resposta_c == 'Sim':
            evento = 'ENXURRADA'
            descricao = 'É um escoamento superficial concentrado e com alta energia de transporte, que pode ou não estar associado aos rios. As enxurradas são capazes de carregar pessoas, carros, caçambas e outros objetos. Geralmente ocorrem em áreas com deficiência no sistema de drenagem, em locais com maior declividade, entre outras.'
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
            html.P(descricao),
            html.P('Fonte: Glossário Transdiciplinar (Projeto COPE - CEMADEN)')
        ], style={'backgroundColor': '#f0f0f0', 'padding': '20px', 'border-radius': '5px', 'margin-top': '1cm'})
    return ""

#Trecho para analise de serie de chuva --------------------------------------------------------------
arquivo_chuva = "dadosreais.csv"  # Alterar para colocar o caminho do arquivo de chuva anexado
dados_chuva = pd.read_csv(arquivo_chuva, sep=';', usecols=[0, 1], header=None)
dados_chuva.columns = ['Data', 'Precipitacao']
dados_chuva['Data'] = pd.to_datetime(dados_chuva['Data'], format='%Y-%m-%d') #formato que vem do site do INMET
dados_chuva = dados_chuva[dados_chuva['Precipitacao'].notna()]

resultado_mk_chuva = mk.original_test(dados_chuva['Precipitacao']) #teste de Mann-Kendall

analise_chuva = html.Div([
    html.H3("Análise da Série Temporal de Precipitação", style={'top-margin':'1cm'}),
    html.Div(id='resultado_mk_chuva', style={'padding': '20px', 'backgroundColor': '#f0f0f0', 'top-margin':'1cm'}),
    dcc.Graph(id='grafico_precipitacao'),
    ])

@app.callback(
    [Output('resultado_mk_chuva', 'children'),
     Output('grafico_precipitacao', 'figure'),
     Input('grafico_precipitacao', 'id')]
)
def tendencia_chuva(_):
    # Análise do resultado do teste de Mann-Kendall
    if resultado_mk_chuva.trend == 'no trend':
        desc_tend_chuva = 'De acordo com o teste de Mann-Kendall, não foi detectada tendência de mudança nas chuvas.'
    elif resultado_mk_chuva.trend == 'increasing':
        desc_tend_chuva = 'Foi detectada uma tendência de aumento nas chuvas.'
    else:
        desc_tend_chuva = 'Foi detectada uma tendência de diminuição nas chuvas.'

    # Criar gráfico de precipitação
    grafico_chuva = {
        'data': [
            go.Bar(
                x=dados_chuva['Data'],
                y=dados_chuva['Precipitacao'],
                name='Precipitação'
            )
        ],
        'layout': go.Layout(
            title='Série Temporal de Precipitação',
            xaxis_title='Data',
            yaxis_title='Precipitação (mm)',
            xaxis=dict(
                tickformat='%d-%m-%Y',
                dtick='M12',  # Marca de 1 ano
            ),
            shapes=[],
            hovermode='x'
        )
    }
    return desc_tend_chuva, grafico_chuva
   
#trecho para analise de nivel do rio --------------------------------------------------------------
arquivo_rio = "rio.csv"  # Alterar para colocar o caminho do arquivo de rio anexado
dados_rio = pd.read_csv(arquivo_rio, sep=';', usecols=[0, 1], header=None)
dados_rio.columns = ['Data', 'Nivel']
dados_rio['Data'] = pd.to_datetime(dados_rio['Data'], format='%Y-%m-%d') #diferente do site da ANA, mas mudado para ficar no mesmo formato da chuva
dados_rio = dados_rio[dados_rio['Nivel'].notna()]

resultado_mk_rio = mk.original_test(dados_rio['Nivel']) #teste de Mann-Kendall

analise_rio = html.Div([
    html.H3("Análise da Série Temporal de Nível do Rio", style={'top-margin':'1cm'}),
    html.Div(id='resultado_mk_rio', style={'padding': '20px', 'backgroundColor': '#f0f0f0', 'top-margin':'1cm'}),
    dcc.Graph(id='grafico_rio'),
    ])

@app.callback(
    [Output('resultado_mk_rio', 'children'),
     Output('grafico_rio', 'figure'),
     Input('grafico_rio', 'id')]
)
def tendencia_rio(_):
    # Análise do resultado do teste de Mann-Kendall
    if resultado_mk_rio.trend == 'no trend':
        desc_tend_rio = 'De acordo com o teste de Mann-Kendall, não foi detectada tendência de mudança no nível do rio.'
    elif resultado_mk_rio.trend == 'increasing':
        desc_tend_rio = 'Foi detectada uma tendência de aumento no nível do rio.'
    else:
        desc_tend_rio = 'Foi detectada uma tendência de diminuição no nível do rio.'

    # Criar gráfico de nível do rio
    grafico_rio = {
        'data': [
            go.Scatter(
                x=dados_rio['Data'],
                y=dados_rio['Nivel'],
                mode='lines',
                name='Nível_do_Rio'
            )
        ],
        'layout': go.Layout(
            title='Série Temporal de Nível do Rio',
            xaxis_title='Data',
            yaxis_title='Nível (cm)',
            xaxis=dict(
                tickformat='%d-%m-%Y',
                dtick='M1',  # Marca de 1 mês, apenas para este set de dados, porque tem menos de um ano, se set maior, o que é necessário, alterar para M12
            ),
            hovermode='x'
        )
    }

    return desc_tend_rio, grafico_rio

app.layout = html.Div([titulo, selector,quest_um, analise_chuva, analise_rio])

app.callback( Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))




if __name__ == '__main__':
    
    #layout = html.Div([title, table_tabs])

    
    
    app.run(debug=True)