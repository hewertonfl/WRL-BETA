import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import waitress
from flask import Flask
import sqlite3

global usinas
global dados
global value_site
global value_bico
global value_vida


BS = "/home/visiontech/Python/WRL/assets/css/bootstrap.min.css"
app = dash.Dash(external_stylesheets=[BS])
app.config['suppress_callback_exceptions'] = True
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


# Load the data

#usinas = pd.read_csv('usinas.csv')
#dados = pd.read_csv('BigData.csv')

banco = sqlite3.connect('/home/visiontech/Python/comp/database.db')

usinas_query = pd.read_sql_query("SELECT * FROM usinas", banco)
dados_query = pd.read_sql_query("SELECT * FROM dados", banco)

usinasDbToDataframe = pd.DataFrame(usinas_query)
dadosDbToDataframe = pd.DataFrame(dados_query)

usinasDbToDataframe.to_csv('usinas.csv', index=False)
dadosDbToDataframe.to_csv('data.csv', index=False)

usinas = pd.read_csv('usinas.csv')
dados = pd.read_csv('data.csv',  dtype=object)
usinas = usinas.dropna()
dados = dados.dropna()
dados = dados.astype({"Vida": int, "Angulo": float,"D1": float,"D2": float,"D3": float,"D4": float,"D5": float,"D6": float,"D_Externo": float})
sidebar = html.Div(
    [
        html.H2("WRL Dashboard", className="display-5"),
        html.Hr(),
        html.P(
            "Acompanhamento dos diâmetros de furos nos bicos de lanças.", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Home", href="/", active="exact"),
                dbc.NavLink("Dados", href="/page-1", active="exact"),
                
               
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
    
def render_page_content(pathname):
    global usinas
    global dados
    if pathname == "/":
        # Load the data
        banco = sqlite3.connect('/home/visiontech/Python/comp/database.db')
        usinas_query = pd.read_sql_query("SELECT * FROM usinas", banco)
        dados_query = pd.read_sql_query("SELECT * FROM dados", banco)
        usinasDbToDataframe = pd.DataFrame(usinas_query)
        dadosDbToDataframe = pd.DataFrame(dados_query)

        usinasDbToDataframe.to_csv('usinas.csv', index=False)
        dadosDbToDataframe.to_csv('data.csv', index=False)
        
        usinas = pd.read_csv('usinas.csv')
        dados = pd.read_csv('data.csv', dtype=object)
        usinas = usinas.dropna()
        dados = dados.dropna()
        dados = dados.astype({"Vida": int, "Angulo": float,"D1": float,"D2": float,"D3": float,"D4": float,"D5": float,"D6": float,"D_Externo": float})
        return html.Div(children=[
            html.H3(children='Lista de usinas.'),
            dbc.Table.from_dataframe(usinas, striped=True, bordered=True, hover=True)
        ])
    elif pathname == "/page-1":
        # Load the data
        banco = sqlite3.connect('/home/visiontech/Python/comp/database.db')
        usinas_query = pd.read_sql_query("SELECT * FROM usinas", banco)
        dados_query = pd.read_sql_query("SELECT * FROM dados", banco)
        usinasDbToDataframe = pd.DataFrame(usinas_query)
        dadosDbToDataframe = pd.DataFrame(dados_query)

        usinasDbToDataframe.to_csv('usinas.csv', index=False)
        dadosDbToDataframe.to_csv('data.csv', index=False)

        usinas = pd.read_csv('usinas.csv')
        dados = pd.read_csv('data.csv', dtype=object)
        usinas = usinas.dropna()
        dados = dados.dropna()
        dados = dados.astype({"Vida": int, "Angulo": float,"D1": float,"D2": float,"D3": float,"D4": float,"D5": float,"D6": float,"D_Externo": float})
        return html.Div(children=[
            html.H3(children='USINA'),
            
            dcc.Dropdown(
                id='usina_dropdown',
                options=[{'label': s, 'value': s} for s in sorted(dados.Site.unique())],
                value=None,
                clearable=False),
            html.Br(),   
            html.Div(id='usina_output_container'),
            html.Br(),
            html.H3(children='BICO'),
            
            dcc.Dropdown(id='data_dropdown',
                         options=[],
                         value=[],
                         multi=False),
            html.Br(),   
            html.Div(id='bico_output_container'),
            html.Br(),
            dcc.Graph(id='d1_graph'),
            html.H4(children='VIDA'),
            dcc.Dropdown(id='vida_dropdown',
                         options=[],
                         value=[],
                         multi=False),
            html.Br(),   
            html.Div(id='vida_output_container'),
            html.Br(),
            
            html.Div(id='vida_images_container'),html.Br(),
            #html.Div(html.A("Timelapse",className="btn btn-primary",style={"padding":"1rem"}, href="http://10.42.0.1:8050", target="_blank")),
        ])
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )
    
@app.callback(
    Output('usina_output_container', 'children'),
    Input('usina_dropdown', 'value')
)
def update_output(value):
    global value_site
    value_site = value
    return dbc.Table.from_dataframe(usinas.loc[usinas['Site'] == value_site], striped=True, bordered=True, hover=True)

@app.callback(
    Output('bico_output_container', 'children'),
    Input('data_dropdown', 'value')
)
def update_output_bico(value):
    global filtered_dados_bico
    global dados
    global value_site
    global value_bico
    value_bico = value
    if bool(value_bico) == False:
        return dash.no_update
    if type(value_bico) is list:
        return dash.no_update

    filtered_dados = dados[dados['Bico_id'] == value_bico]
    filtered_dados = filtered_dados[filtered_dados['Site'] == value_site]
    filtered_dados_bico = filtered_dados
    filtered_dados = filtered_dados.loc[filtered_dados.index[[-1]]]
    filtered_dados = filtered_dados[['Bico_id','Tipo', 'Vida','Carro','Operador','Data']] #filtered_dados[['Bico_id','Tipo', 'Vida','Convertedor','Carro','Operador','Data']]
    return dbc.Table.from_dataframe(filtered_dados.loc[filtered_dados['Bico_id'] == value_bico], striped=True, bordered=True, hover=True)    


@app.callback(
    Output('vida_output_container', 'children'),
    Input('vida_dropdown', 'value')
)
def update_output_vida(value):
    global dados
    global filtered_dados_bico
    global value_site
    global value_bico
    global value_vida
    
    value_vida = value
    
    if type(value_vida) is list:
        return dash.no_update
    filtered_dados = filtered_dados_bico[filtered_dados_bico['Vida'] == value_vida]
    if(str(filtered_dados.iloc[0]['Tipo']) == 'Slagless 4 Furos'):
        filtered_dados = filtered_dados[['Bico_id','Tipo','Vida','Carro','Convertedor','Operador','Data','Posição','D1','D2','D3','D4','D_Externo','Angulo']] #filtered_dados[['Bico_id','Vida','Convertedor','Carro','Operador','Data','d1','d2','d3','d4']]
    else: #elif (str(filtered_dados.iloc[0]['Tipo']) == 'Slagless 6 Furos'):
        filtered_dados = filtered_dados[['Bico_id','Tipo','Vida','Carro','Convertedor','Operador','Data','Posição', 'D1','D2','D3','D4','D5','D6','D_Externo','Angulo']] #filtered_dados[['Bico_id','Vida','Convertedor','Carro','Operador','Data', 'd1','d2','d3','d4','d5','d6']]
    return dbc.Table.from_dataframe(filtered_dados.loc[filtered_dados['Vida'] == value_vida], striped=True, bordered=True, hover=True)   
    
@app.callback(
    Output('vida_images_container', 'children'),
    Input('vida_dropdown', 'value')
)
def update_image_vida(value):
    global dados
    global filtered_dados_bico
    global value_site
    global value_bico
    global value_vida
    
    value_vida = value

    if type(value_vida) is list:
        return dash.no_update
    filtered_dados = filtered_dados_bico[filtered_dados_bico['Vida'] == value_vida]
    usinaToImage = filtered_dados.iloc[0]['Site']
    bicoToImage = filtered_dados.iloc[0]['Bico_id']
    vidaToImage = filtered_dados.iloc[0]['Vida']
    
    with open('nomeImagem.txt', 'w') as f:
    	f.write(str(usinaToImage)+"-"+str(bicoToImage))
    with open('nomeUsina.txt', 'w') as f:
    	f.write(str(usinaToImage))
    orig_card = dbc.Card(
    [
        dbc.CardBody(html.P("Imagem original", className="card-text")),
        dbc.CardImg(src="./assets/"+str(usinaToImage)+"-"+str(bicoToImage)+"-"+str(int(vidaToImage))+"-A.jpg", bottom=True),

    ],
    style={"width": "25rem"},
    )
    
    seg_card = dbc.Card(
    [
        dbc.CardBody(html.P("Imagem segmentada", className="card-text")),
        dbc.CardImg(src="./assets/"+str(usinaToImage)+"-"+str(bicoToImage)+"-"+str(int(vidaToImage))+"-B.jpg", bottom=True),
    ],
    style={"width": "25rem"},
    )  
        
    return dbc.Row([dbc.Col(orig_card, width="auto"),dbc.Col(seg_card, width="auto"),])
   
   
   
@app.callback(
    Output('data_dropdown', 'options'),
    Output('data_dropdown', 'value'),
    Input('usina_dropdown', 'value'),
)
def set_data_options(chosen_usina):
    global usinas
    global dados     
    global value_site
    global value_bico
    global value_vida
    global chosen_usi
    
    chosen_usi = chosen_usina

    dff = dados[dados.Site==chosen_usina]
    bicos_of_usina = [{'label': c, 'value': c} for c in sorted(dff.Bico_id.unique())]
    values_selected = [x['value'] for x in bicos_of_usina]
    return bicos_of_usina, values_selected  
    
@app.callback(
    Output('vida_dropdown', 'options'),
    Output('vida_dropdown', 'value'),
    Input('data_dropdown', 'value'),
)
def set_data_options_vida(chosen_bico):
    global usinas
    global dados   
    global value_site
    global value_bico
    global value_vida
    global chosen_usi
    
    if bool(chosen_bico) == False:
        return dash.no_update
    if type(chosen_bico) is list:
        return dash.no_update    
    dff = dados[dados.Bico_id==chosen_bico]
    dff = dff[dados.Site==chosen_usi]
    vida_of_usina = [{'label': c, 'value': c} for c in sorted(dff.Vida.unique())]
    values_selected = [x['value'] for x in vida_of_usina]
    return vida_of_usina, values_selected  
    
@app.callback(
    Output(component_id='d1_graph', component_property='figure'),
    Input(component_id='data_dropdown', component_property='value')
)
def update_graph(selected_bico):
    global usinas
    global dados 
    global value_site
    global value_bico
    global value_vida
    global chosen_usi
    
    if bool(selected_bico) == False:
        return dash.no_update
    if type(selected_bico) is list:
        return dash.no_update     
    filtered_dados = dados[dados.Bico_id == selected_bico]
    filtered_dados = filtered_dados[filtered_dados.Site==chosen_usi]
    if(str(filtered_dados.iloc[0]['Tipo']) == 'Slagless 4 Furos'):
        line_fig = px.line(filtered_dados,
                           x='Vida', y=['D1','D2','D3','D4','D_Externo'],
                           range_y =(40,60),
                           title=f'Diâmetros do bico {selected_bico}', markers=True)
        return line_fig
    else: #elif (str(filtered_dados.iloc[0]['Tipo']) == 'Slagless 6 Furos'):
        line_fig = px.line(filtered_dados,
                           x='Vida', y=['D1','D2','D3','D4','D5','D6','D_Externo'],
                           range_y =(40,60),
                           title=f'Diâmetros do bico {selected_bico}',  markers=True)
        return line_fig

#if __name__ == "__main__":
#    app.run_server(debug=True, host='0.0.0.0', port=8880)
    
# Run local server with waitress for deploying an application to production
if __name__ == "__main__":
    from waitress import serve
    porta = 8888
    print('Run server on 0.0.0.0:'+str(porta))
    serve(app.server, host="0.0.0.0", port=porta)
