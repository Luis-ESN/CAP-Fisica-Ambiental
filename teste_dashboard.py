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

import pymannkendall as mk
import plotly.graph_objects as go

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


#app.layout = html.Div([titulo, selector])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')
    global dados_chuva, resultado_mk_chuva

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')), sep=';', usecols=[0, 1], header=None)
            
            dados_chuva = df.copy()
            dados_chuva.columns = ['Data', 'Precipitacao']
            dados_chuva['Data'] = pd.to_datetime(dados_chuva['Data'], format='%Y-%m-%d') #formato que vem do site do INMET
            dados_chuva = dados_chuva[dados_chuva['Precipitacao'].notna()]

            resultado_mk_chuva = mk.original_test(dados_chuva['Precipitacao']) #teste de Mann-Kendall

        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded), sep=';', usecols=[0, 1], header=None)
            
            dados_chuva = df.copy()
            dados_chuva.columns = ['Data', 'Precipitacao']
            dados_chuva['Data'] = pd.to_datetime(dados_chuva['Data'], format='%Y-%m-%d') #formato que vem do site do INMET
            dados_chuva = dados_chuva[dados_chuva['Precipitacao'].notna()]

            resultado_mk_chuva = mk.original_test(dados_chuva['Precipitacao']) #teste de Mann-Kendall

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
            #'''dash_table.DataTable(
             #   df.to_dict('records'),
              #  [{'name': i, 'id': i} for i in df.columns]
            #),'''
        ])

@callback(Output('output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))


def update_output(list_of_contents, list_of_names, list_of_dates):
    
    if list_of_contents is not None:
        children = [
            parse_contents(list_of_contents, list_of_names, list_of_dates)]
        return children
    
####################################################

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

@callback(
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

################
dados_chuva = None
resultado_mk_chuva = None

analise_chuva = html.Div([
    html.H3("Análise da Série Temporal de Precipitação", style={'top-margin':'1cm'}),
    html.Div(id='resultado_mk_chuva', style={'padding': '20px', 'backgroundColor': '#f0f0f0', 'top-margin':'1cm'}),
    dcc.Graph(id='grafico_precipitacao'),
    dcc.Interval(
            id='interval-component',
            interval=1 * 1000,
            n_intervals=0
    ),
    ])

@callback(
    [Output('resultado_mk_chuva', 'children'),
     Output('grafico_precipitacao', 'figure'),
     Input('grafico_precipitacao', 'id')]
)

def tendencia_chuva(_):
    # Análise do resultado do teste de Mann-Kendall
    global resultado_mk_chuva
    
    if resultado_mk_chuva == None:
        # Criar gráfico de precipitação
        grafico_chuva = {
            'data': [
                go.Bar(
                    x=[],
                    y=[],
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
        desc_tend_chuva = 'Selecione o arquivo com o evento'
        return desc_tend_chuva, grafico_chuva
    else:
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

app.layout = html.Div([titulo, selector, quest_um, analise_chuva])#, analise_chuva, analise_rio])
if __name__ == '__main__':
    app.run(debug=True)