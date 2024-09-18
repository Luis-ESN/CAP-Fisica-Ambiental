# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 10:05:56 2024

@author: luise
"""

from dash import Dash, dcc, html, dash_table, Input, Output, State, callback
import dash_mantine_components as dmc

import base64
from datetime import datetime, date
import io

import pandas as pd

import pymannkendall as mk
import plotly.graph_objects as go
import numpy as np

#import plotly.graph_objects as go
#from plotly.subplots import make_subplots
#from plotly.colors import qualitative

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dmc.styles.DATES]

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)





# Parte referente ao título da página
titulo = html.Div([
    html.H2('Interactive Dashboard for Extreme Events Auditing', 
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
            html.Div([
            html.H3("Análise da Série Temporal de Precipitação", style={'top-margin':'1cm'}),
            html.Div(id='resultado_mk_chuva', style={'padding': '20px', 'backgroundColor': '#f0f0f0', 'top-margin':'1cm'}),
            dcc.Graph(id='grafico_precipitacao'),
            ]),
            html.Div([
                html.H3("Análise de exogenia e endogenia", style={'top-margin':'1cm'}),
                dcc.Graph(id='grafico_potenciometro'),
                
                ])
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

################
dados_chuva = None
resultado_mk_chuva = None


def nivel_endogenia(dados):
  window_size = 1000
  if len(dados) < 1000:
      window_size= 100
  if len(dados) < 100:
      window_size = 10
  limiar_pico = 0.6 #Poncentagem
  peso_exogena = 1
  penalidade_endogena = 3
  penalidade_exogena = 0.5
  contador_exogena = 0
  contador_endogena = 0
  total_janelas = 0
  
  df = dados.copy()
  media = df.iloc[:, -1].mean()
  std = df.iloc[:, -1].std()
  df.iloc[:, -1] = (df.iloc[:, -1] - media) / std
  def tem_pico_discrepante(janela, limiar_pico):
    media = np.mean(janela)
    desvio_padrao = np.std(janela)
    coef_variabilidade = desvio_padrao / media  #Coeficiente de variabilidade
    return coef_variabilidade > limiar_pico


  def tendencia_crescimento(janela, limiar_diferenca=0.3):
      diferencas = [abs(janela[i + 1] - janela[i]) for i in range(len(janela) - 1)]
      medida = np.std(diferencas)
      return medida <= limiar_diferenca


  for i in range(len(df) - window_size + 1):
    # janela = df['amplitude'].iloc[i:i + window_size].values
    janela = df.iloc[:, -1].iloc[i:i + window_size].values
    total_janelas += 1

    if tendencia_crescimento(janela):
        if contador_exogena > 0:
            contador_exogena -= peso_exogena + penalidade_exogena
        if contador_endogena > 0:
            contador_endogena += 1
    else:
        if tem_pico_discrepante(janela, limiar_pico):
            contador_exogena += peso_exogena
        else:
            contador_endogena += penalidade_endogena

    total_classificacoes = contador_exogena + contador_endogena
    if total_classificacoes > 0:
        prob_exogena = contador_exogena / total_classificacoes * 100
        prob_endogena = contador_endogena / total_classificacoes * 100
    else:
        prob_exogena = 0
        prob_endogena = 0
  total_classificacoes_final = contador_exogena + contador_endogena
  if total_classificacoes_final > 0:
      prob_exogena_final = contador_exogena / total_classificacoes_final * 100
      prob_endogena_final = contador_endogena / total_classificacoes_final * 100
  else:
      prob_exogena_final = 0
      prob_endogena_final = 0

  return prob_endogena_final



@callback(
    [Output('resultado_mk_chuva', 'children'),
     Output('grafico_precipitacao', 'figure'),
     Output('grafico_potenciometro', 'figure'),
     Input('grafico_precipitacao', 'id'),
     Input('grafico_potenciometro', 'id')],
)

def tendencia_chuva(_, __):
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
        
        grafico_potenciometro = {
            'data': [
                go.Indicator(
                    mode = "gauge+number",
                    value = None,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                      gauge = {
                      'axis': {'range': [0, 100]},
                      }
                )
            ],
            'layout': go.Layout(
                title = {'text': "Nível de Endogenia"},
            )
        }
        

        return desc_tend_chuva, grafico_chuva, grafico_potenciometro
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
        
        grafico_potenciometro = {
            'data': [
                go.Indicator(
                    mode = "gauge+number",
                    value = nivel_endogenia(dados_chuva),
                        domain = {'x': [0, 1], 'y': [0, 1]},
                      gauge = {
                      'axis': {'range': [0, 100]},
                      }
                )
            ],
            'layout': go.Layout(
                title = {'text': "Nível de Endogenia"},
            )
        }
        return desc_tend_chuva, grafico_chuva, grafico_potenciometro
    
####################################################

# Trecho para questionario 1-------------------------------------------------------
quest_um = html.Div([
    html.Div([
    html.H3("Questionário sobre Eventos",style={'margin-top':'0.5cm'}),
    
    # Pergunta A
    html.Label("Possui algum rio no local do evento?", style={'margin-top':'0.5cm'}),
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
    html.Label("Em caso positivo, houve um transbordamento do rio?", style={'margin-top':'0.5cm'}),
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
    html.Label("Houve escoamento de água superficial com alta energia de transporte?", style={'margin-top':'0.5cm'}),
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
    
    html.Button('Enviar', id='Enviar', n_clicks=0, style={'margin-top':'0.5cm'}),
    ], style={'width': '45%', 'display': 'inline-block', 'margin-left':'5%'}),
    html.Div(id='resposta_quest_um', 
             style={'verticalAlign': 'top', 'width': '45%', 'display': 'inline-block', 'margin-right':'5%', 'textAlign': 'center'}) #espaco onde sera exibido o retorno
], style={'verticalAlign': 'top'})

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
        ], style={'verticalAlign': 'center', 'padding':'20px', 'backgroundColor': '#f0f0f0', 'border-radius': '5px', 'margin-top': '10%'})
    return ""




####################################################

# Trecho para questionario 1-------------------------------------------------------
quest_dois = html.Div([
    html.Div([
    html.H3("Questionário sobre Eventos",style={'margin-top':'0.5cm'}),
    
    # Pergunta D
    html.Label("Qual a data do evento?", style={'margin-top':'0.5cm'}),
    dcc.DatePickerSingle(
        id='pergunta_d',
        #min_date_allowed=date(1995, 8, 5),
        max_date_allowed=date.today(),
        initial_visible_month=date.today(),
        date=date.today()
    ),
    
    # Pergunta E
    html.Label("Qual o local do evento?", style={'margin-top':'0.5cm'}),
    dcc.Input(
            id="pergunta_e",
            type="text",
            placeholder="Ex: Jacareí/São Paulo/Brasil",
            value=''
        ),
    
    # Pergunta F
    html.Label("O evento ocorreu em área urbana ou rural??", style={'margin-top':'0.5cm'}),
    dcc.Dropdown(
        id='pergunta_f',
        options=[
            {'label': 'Rural', 'value': 'Rural'},
            {'label': 'Urbana', 'value': 'Urbana'}
        ],
        value=None,
        placeholder='Selecione uma resposta',
        style={'width':'7cm'}
    ),
    
    # Pergunta G
    html.Label("Como poderia ser classificada a vulnerabilidade desta área?", style={'margin-top':'0.5cm'}),
    dcc.Dropdown(
        id='pergunta_g',
        options=[
            {'label': 'Nula', 'value': 'Nula'},
            {'label': 'Baixa', 'value': 'Baixa'},
            {'label': 'Intermediaria', 'value': 'Intermediaria'},
            {'label': 'Alta', 'value': 'Alta'},
            {'label': 'Devastadora', 'value': 'Devastadora'},
        ],
        value=None,
        placeholder='Selecione uma resposta',
        style={'width':'7cm'}
    ),
    
    
    # Pergunta H
    html.Label("Existe alguma condição climática específica que merece ser destacada no local e data do evento?", style={'margin-top':'0.5cm'}),
    dcc.Input(
            id="pergunta_h",
            type="text",
            placeholder="Ex: Época de secas, de chuvas ou outras",
            value=''
        ),
    
    # Pergunta I
    html.Label("Existe algum modo de variabilidade climático atuante no local e data do evento?", style={'margin-top':'0.5cm'}),
    dcc.Input(
            id="pergunta_i",
            type="text",
            placeholder="Ex: El Niño, El Niña ou outras",
            value=''
        ),
    
    # Pergunta J
    html.Label("Existem variáveis medidas antes, durante e após o evento que podem ajudar a descrevê-lo como um fenômeno de causa(s) e efeito(s)?", style={'margin-top':'0.5cm'}),
    dcc.Input(
            id="pergunta_j",
            type="text",
            placeholder="Ex: Precepitação, vento e ou outras",
            value=''
        ),
    
    # Pergunta K
    html.Label("É possível quantificar/dimensionar o impacto do evento no meio ambiente?", style={'margin-top':'0.5cm'}),
    dcc.Dropdown(
        id='pergunta_k',
        options=[
            {'label': 'Sim', 'value': 'Sim'},
            {'label': 'Não', 'value': 'Não'}
        ],
        value=None,
        placeholder='Selecione uma resposta',
        style={'width':'7cm'}
    ),
    
    # Pergunta L
    html.Label("É possível reverter e/ou mitigar os efeitos negativos ao meio ambiente?", style={'margin-top':'0.5cm'}),
    dcc.Dropdown(
        id='pergunta_l',
        options=[
            {'label': 'Sim', 'value': 'Sim'},
            {'label': 'Não', 'value': 'Não'}
        ],
        value=None,
        placeholder='Selecione uma resposta',
        style={'width':'7cm'}
    ),
    
    # Pergunta M
    html.Label("É possível apontar responsáveis pelo evento em função de um estudo técnico-científico?", style={'margin-top':'0.5cm'}),
    dcc.Input(
            id="pergunta_m",
            type="text",
            placeholder="Ex: Não ou, se sim, quais?",
            value=''
        ),
    
    html.P(),
    html.Button('Enviar', id='Enviar2', n_clicks=0, style={'margin-top':'0.5cm'}),
    ], style={'width': '45%', 'display': 'inline-block', 'margin-left':'5%'}),
    html.Div(id='resposta_quest_dois', 
             style={'verticalAlign': 'top', 'width': '45%', 'display': 'inline-block', 'margin-right':'5%', 'textAlign': 'center'}) #espaco onde sera exibido o retorno
], style={'verticalAlign': 'top'})


@callback(
    Output('resposta_quest_dois', 'children'),
    Input('Enviar2', 'n_clicks'),  
    State('pergunta_d', 'date'),
    State('pergunta_e', 'value'),
    State('pergunta_f', 'value'),
    State('pergunta_g', 'value'),
    State('pergunta_h', 'value'),
    State('pergunta_i', 'value'),
    State('pergunta_j', 'value'),
    State('pergunta_k', 'value'),
    State('pergunta_l', 'value'),
    State('pergunta_m', 'value')
)


def survey(n_clicks, resposta_d, resposta_e, resposta_f, resposta_g, resposta_h, resposta_i, resposta_j, resposta_k, resposta_l, resposta_m):
    '''if n_clicks > 0: 
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
            descricao = 'Por favor, verifique suas respostas.
            '''
    if n_clicks > 0:
        return html.Div([
            #html.H3(f"Evento Identificado: {evento}"),
            #html.P(descricao),
            html.P('Fonte: Glossário Transdiciplinar (Projeto COPE - CEMADEN)')
        ], style={'verticalAlign': 'center', 'padding':'20px', 'backgroundColor': '#f0f0f0', 'border-radius': '5px', 'margin-top': '10%'})
    return ""


app.layout = html.Div([titulo, quest_um, selector, quest_dois])#, analise_chuva, analise_rio])
if __name__ == '__main__':
    app.run(debug=True)