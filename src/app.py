
'''
 # @ Create Time: 2024-05-02 13:26:29.162436
'''

import pathlib
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


app = Dash(__name__, title="PB Dashboard",external_stylesheets=[dbc.themes.SANDSTONE, dbc.icons.BOOTSTRAP])

server = app.server


LOGO = 'assets/PB_Logo_White.png'
def load_data(data_file: str) -> pd.DataFrame:
    '''
    Load data from /data directory
    '''
    PATH = pathlib.Path(__file__).parent
    DATA_PATH = PATH.joinpath("data").resolve()
    return pd.read_csv(DATA_PATH.joinpath(data_file))

df = load_data("Weekly_Data.csv")

df.dropna(subset=['Site'], inplace=True)
#df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
df['Date'] = np.array(pd.to_datetime(df['Date'], dayfirst=True, errors ='coerce'))
df=df.replace([np.nan, -np.inf], 0)
df['Dine In'] = df['Food Eat in £'] + df['Drink Eat in £']
df['Take Out'] = df['Food T/O £'] + df['Drink T/O £']
df['Instore'] = df['Dine In']+ df['Take Out']
df['External'] = df['Deliveroo'] + df['WholeSale'] + df['Catering'] + df['Catering- Partner']
df['Sales'] = df['Instore'] + df['External']
source = df[['Site','Date','Food Eat in £','Drink Eat in £','Food T/O £','Drink T/O £','Deliveroo','WholeSale','Catering','Catering- Partner']]
#np.array(pd.to_datetime(df['Date']).dt.strftime('%m/%d/%Y'))
#df["Date"] = df["Date"].astype('datetime64[ns]')
#df['NPS'].astype(int)

#dfg grouped sites by date
dfg = df.groupby(['Date'])[['Net sales','Labour £','Labour %','NPS', 'COGS']].sum()
dfg.reset_index(inplace=True)
sourceg = df.groupby(['Date'])[['Food Eat in £','Drink Eat in £','Food T/O £','Drink T/O £','Deliveroo','WholeSale','Catering','Catering- Partner']].sum()

#### weekly sales ####
weekly_sales = df.groupby(['Date','Site']).agg({'Net sales':'sum'}).reset_index()
weekly_labour = df.groupby(['Date','Site']).agg({'Labour £':'sum'}).reset_index()
weekly_nps = df.groupby(['Date','Site']).agg({'NPS':'sum'}).reset_index()

#========================================

group_sales = df.groupby(['Date']).agg({'Net sales':'sum'}).reset_index()



##########################################

#graph - all sites

#--- Navbar definged

navbar = dbc.Navbar(id= 'navbar', children = [
    dbc.Row([
        dbc.Col(html.Img(src = LOGO, height = "70px"), style={'display':'flex'},xs = 12, sm = 3, md = 3, lg = 3, xl = 3),
        
        dbc.Col(
            dbc.NavbarBrand('PARIS BAGUETTE UK', style = {'color' :'White','fontSize':'30px','float':'left'}),width=9, className='d-none d-sm-block',
                            )
            ],align = 'center',className = 'ml-auto'),
        dbc.Col()
        ], style={'padding-left':'20px', 'padding-right':'20px'})

# define content of cards


    
body_app = dbc.Container([
    
    
    
    html.Br(),
    
    html.Div(id = 'dropdown-div', children =[
        dcc.Dropdown(id = 'site-dropdown',
                 options = [{'label': i, 'value' : i} for i in np.append(['ALL'],df['Site'].unique())],
                 value = 'ALL')],style = {'width':'100%', 'padding': '15px', 'text-align':'center'}),
            
    
    html.Br(),
    
        dbc.Row([
            dbc.Col([dbc.Card(id= 'card_sales',style={'height':'160px'})],xs = 12, sm = 12, md = 6, lg = 3, xl = 3, style = {'padding':'12px 12px 12px 12px'}),
            dbc.Col([dbc.Card(id= 'card_labour', style={'height':'160px'})],xs = 12, sm = 12, md = 6, lg = 3, xl = 3, style = {'padding':'12px 12px 12px 12px'}),
            dbc.Col([dbc.Card(id= 'card_cogs', style={'height':'160px'})],xs = 12, sm = 12, md = 6, lg = 3, xl = 3, style = {'padding':'12px 12px 12px 12px'}),
            dbc.Col([dbc.Card(id= 'card_nps', style={'height':'160px'})],xs = 12, sm = 12, md = 6, lg = 3, xl = 3, style = {'padding':'12px 12px 12px 12px'})
           
            ]),
        dbc.Row([
            dbc.Col([
                  dcc.Graph('sales_graph'),
              ], width=6, md=6,xs=12,style = {'padding':'12px 12px 12px 12px'}),
            
        html.Br(),

            dbc.Col([
                  dcc.Graph('source_graph')  
              ], width=6, md=6,xs=12,style = {'padding':'12px 12px 12px 12px'})
          ]),
        
                    
        ], fluid = True)

#---- app layout

app.layout= html.Div([
    html.Div(id = 'parent', children = [navbar, body_app]),
    html.Br(),


                  ])

#============= callbacks=====================


@app.callback([Output('card_sales','children'),
# =============================================================================
                Output('card_labour', 'children'),
                Output('card_cogs', 'children'),
                Output('card_nps', 'children')
                ],

# =============================================================================
              [Input(component_id= 'site-dropdown', component_property= 'value')])
        
def update_cards(base):
    
    
   
   
    if base == 'ALL':
        
        sales_base = dfg['Net sales'].iloc[-1]
        sales_comp = dfg['Net sales'].iloc[-2]
        diff_1 = sales_base - sales_comp
        icon = "bi bi-caret-up-fill text-success" if diff_1 >0 else "bi bi-caret-down-fill text-danger"
        
        
        labour_base = (dfg['Labour £'].iloc[-1])/(dfg['Net sales'].iloc[-1])
        labour_comp = dfg['Labour £'].iloc[-2]/dfg['Net sales'].iloc[-2]
        diff_2 = labour_base - labour_comp
        icon2 = "bi bi-caret-up-fill text-danger" if diff_2 >0 else "bi bi-caret-down-fill text-success"
    
    
        cogs_base = (dfg['COGS'].iloc[-1])/(dfg['Net sales'].iloc[-1])+0.02
        cogs_comp = dfg['COGS'].iloc[-2]/dfg['Net sales'].iloc[-2]+0.02
        diff_4 = cogs_base - cogs_comp
        icon4 = "bi bi-caret-up-fill text-danger" if diff_4 >0 else "bi bi-caret-down-fill text-success"
        
        nps_base = df['NPS'].iloc[-3:-1].mean()
        nps_comp = df['NPS'].iloc[-5:-3].mean()
        diff_3 = nps_base - nps_comp
        NPStext = 'NPS'
        icon3 = "bi bi-caret-up-fill text-success" if diff_3 >0 else "bi bi-caret-down-fill text-danger"
        
        
    elif base == 'SOT':
        
        sales_base = df[df['Site'] ==base]['Net sales'].iloc[-1]
        sales_comp = df[df['Site'] ==base]['Net sales'].iloc[-2]
        diff_1 = sales_base - sales_comp
        icon = "bi bi-caret-up-fill text-success" if diff_1 >0 else "bi bi-caret-down-fill text-danger"
        
        labour_base = df[df['Site'] ==base]['Labour %'].iloc[-1]
        #labour_base2 = df[df['Site'] ==base]['Labour £'].iloc[-1]
        labour_comp = df[df['Site'] ==base]['Labour %'].iloc[-2]
        #labour_comp2 = df[df['Site'] ==base]['Labour £'].iloc[-2]
        diff_2 = labour_base - labour_comp
        icon2 = "bi bi-caret-up-fill text-danger" if diff_2 >0 else "bi bi-caret-down-fill text-success"
        
        cogs_base = df[df['Site'] ==base]['COGS'].iloc[-1]/df[df['Site'] ==base]['Net sales'].iloc[-1]
        #labour_base2 = df[df['Site'] ==base]['Labour £'].iloc[-1]
        cogs_comp = df[df['Site'] ==base]['COGS'].iloc[-2]/df[df['Site'] ==base]['Net sales'].iloc[-2]
        #labour_comp2 = df[df['Site'] ==base]['Labour £'].iloc[-2]
        diff_4 = cogs_base - cogs_comp
        icon4 = "bi bi-caret-up-fill text-danger" if diff_4 >0 else "bi bi-caret-down-fill text-success"
        
        nps_base = df[df['Site'] ==base]['Items Sold'].iloc[-1]
        nps_comp = df[df['Site'] ==base]['Items Sold'].iloc[-2]
        diff_3 = nps_base - nps_comp
        NPStext = 'Production'
        icon3 = "bi bi-caret-up-fill text-success" if diff_3 >0 else "bi bi-caret-down-fill text-danger"
    
# ========================================================================

    else:
    
        sales_base = df[df['Site'] ==base]['Net sales'].iloc[-1]
        sales_comp = df[df['Site'] ==base]['Net sales'].iloc[-2]
        diff_1 = sales_base - sales_comp
        icon = "bi bi-caret-up-fill text-success" if diff_1 >0 else "bi bi-caret-down-fill text-danger"
        
        labour_base = df[df['Site'] ==base]['Labour %'].iloc[-1]
        #labour_base2 = df[df['Site'] ==base]['Labour £'].iloc[-1]
        labour_comp = df[df['Site'] ==base]['Labour %'].iloc[-2]
        #labour_comp2 = df[df['Site'] ==base]['Labour £'].iloc[-2]
        diff_2 = labour_base - labour_comp
        icon2 = "bi bi-caret-up-fill text-danger" if diff_2 >0 else "bi bi-caret-down-fill text-success"
        
        cogs_base = df[df['Site'] ==base]['COGS'].iloc[-1]/df[df['Site'] ==base]['Net sales'].iloc[-1]+0.02
        cogs_comp = df[df['Site'] ==base]['COGS'].iloc[-2]/df[df['Site'] ==base]['Net sales'].iloc[-2]+0.02
        diff_4 = cogs_base - cogs_comp
        icon4 = "bi bi-caret-up-fill text-danger" if diff_4 >0 else "bi bi-caret-down-fill text-success"
        
                
        nps_base = df[df['Site'] ==base]['NPS'].iloc[-1]
        nps_comp = df[df['Site'] ==base]['NPS'].iloc[-2]
        diff_3 = nps_base - nps_comp
        NPStext = 'NPS'
        icon3 = "bi bi-caret-up-fill text-success" if diff_3 >0 else "bi bi-caret-down-fill text-danger"
     
#==================== if all =====
    
    card_content = [
      
        dbc.CardBody(
            [
                html.H6('Sales', style = {'fontWeight':'Light','textAlign':'center' }),
                    
                html.H3(children=[' {0}{1:,} '.format('£', sales_base),html.I(className= icon)], style ={'color':'#090059', 'textAlign':'center'}),
                
            
                dcc.Markdown(dangerously_allow_html= True,
                    children = ['{0}{1:,}'.format('Previous Week £', sales_comp)], style={'textAlign':'center'}),
                
                dcc.Markdown(dangerously_allow_html= True,
                    children = ['{0}{1:,}'.format('£', diff_1).replace('£-','-£')], style={'textAlign':'center'})
                 
                ]
            
            )
        ]
    
    card_content2= [
      
        dbc.CardBody(
            [
                html.H6('Labour', style = {'fontWeight':'Light','textAlign':'center' }),
                    
                html.H3(children=['{}{:.2%} '.format('', labour_base), html.I(className= icon2)], style ={'color':'#090059', 'textAlign':'center'}),
                
                
                dcc.Markdown(dangerously_allow_html= True,
                    children = ['{}{:.2%}'.format('Previous Week ', labour_comp)], style={'textAlign':'center'}),
                
                dcc.Markdown(dangerously_allow_html= True,
                    children = ['{:.2%} pt.'.format(diff_2)], style={'textAlign':'center'}),
                
                
                ]
            
            )
        
        ]
    
    card_content3= [
      
        dbc.CardBody(
            [
                html.H6('COGS', style = {'fontWeight':'Light','textAlign':'center' }),
                    
                html.H3(children=['{}{:.2%} '.format('', cogs_base), html.I(className= icon4)], style ={'color':'#090059', 'textAlign':'center'}),
               
                dcc.Markdown(dangerously_allow_html= True,
                    children = ['{}{:.2%}'.format('Previous Week ', cogs_comp)], style={'textAlign':'center'}),
                
                dcc.Markdown(dangerously_allow_html= True,
                    children = ['{:.2%} pt.'.format(diff_4)], style={'textAlign':'center'})
                
                ]
            
            )
            
        ]

    
    card_content4= [
      
        dbc.CardBody(
            [
                html.H6(NPStext, style = {'fontWeight':'Light','textAlign':'center' }),
                    
                html.H3(children=['{:.0f} '.format(nps_base ),html.I(className= icon3)], style ={'color':'#090059', 'textAlign':'center'}),
                
                dcc.Markdown(dangerously_allow_html= True,
                    children = ('Previous Week ', nps_comp), style={'textAlign':'center'}),
                
                dcc.Markdown(dangerously_allow_html= True,
                    children = ['{}'.format(int( diff_3))], style={'textAlign':'center'})
                
                ]
            
            )
            
        ]
    

    return card_content, card_content2, card_content3, card_content4

@app.callback(Output('sales_graph', 'figure'),
     [Input(component_id= 'site-dropdown', component_property= 'value')])

def update_figure(base):
    
    df_site = df[df['Site']== base]
    
    if base =='ALL':
        
        fig = px.line(dfg, x="Date", y= ["Net sales","Labour £"], title='Net Sales and Labour')
        fig.update_xaxes(showgrid=False)
        fig.update_traces(hovertemplate=None)

        fig.update_layout(    
            title="",
            xaxis_title="",
            yaxis_title="",
            legend_title="",
            hovermode="x unified",
            legend=dict(
            yanchor="top",
            y=-0.40,
            xanchor="left",
            x=-0.01
        ))

        fig.update_layout(
        margin=dict(l=5, r=10, t=10, b=10),
        paper_bgcolor="LightSteelBlue",)
        
        fig.update_layout(
            xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    
    else:
        
        fig = px.line(df_site, x="Date", y= ["Net sales","Labour £"], title='Net Sales and Labour' )
        fig.update_xaxes(showgrid=False)
        #fig. update_layout(showlegend=False)
        fig.update_xaxes(showgrid=False)
        fig.update_traces(hovertemplate=None)

        fig.update_layout(    
            title="",
            xaxis_title="",
            yaxis_title="",
            legend_title="",
            hovermode="x unified",
            legend=dict(
            yanchor="top",
            y=-0.40,
            xanchor="left",
            x=-0.01
        ))

        fig.update_layout(
        margin=dict(l=5, r=10, t=10, b=10),
        paper_bgcolor="LightSteelBlue",)
      

        fig.update_layout(
            xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label="1m",
                         step="month",
                         stepmode="backward"),
                    dict(count=6,
                         label="6m",
                         step="month",
                         stepmode="backward"),
                    dict(count=1,
                         label="YTD",
                         step="year",
                         stepmode="todate"),
                    dict(count=1,
                         label="1y",
                         step="year",
                         stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

  
    return fig

@app.callback(Output('source_graph', 'figure'),
     [Input(component_id= 'site-dropdown', component_property= 'value')])

def update_sourcefig(base):
    
    source_site = source[source['Site']== base]
    
    if base =='ALL':
        
        source_group = sourceg.iloc[-1]
        newg = source_group.transpose().reset_index()
        newg.insert( 0,"Total", ['Dine In', 'Dine In','Take Out','Take Out', 'Delivery','Delivery','Catering','Catering'], True)
        newg.insert( 0, "Sub",['Instore', 'Instore','Instore','Instore', 'External','External','External','External'], True)
        newg.columns = ['Source1','Source2','Source3','Total']
        newg.replace({"Food Eat in £": "Food","Drink Eat in £":"Drink",
                     "Food T/O £":"Food","Drink T/O £":"Drink"}, 
                   inplace=True)
        
        fig = px.sunburst(newg.assign(hole='All'), path=['hole','Source1','Source2','Source3'],
                          values = 'Total',
                          title="Sales Source",
                          color_discrete_sequence=px.colors.sequential.dense,
                          
                          )
        fig.update_traces(textinfo="label+percent parent",hovertemplate=None)
        fig.add_trace(go.Sunburst(insidetextorientation='horizontal'))
    
        fig.update_layout(
        margin=dict(l=15, r=15, t=30, b=20),
        paper_bgcolor="LightSteelBlue",)
        fig.update_layout(title_text='Sales Source', title_x=0.5,title_y=0.98)
       # fig.update_layout(
            #margin = dict(t=60, l=10, r=10, b=10),title_text='Sales Source', title_y=0.5)
        #fig.update_layout(title_text='Your title', title_x=0.5)
    
       
    
    else:
        

        
        source_site1 = source_site.iloc[-1]
        new = source_site1.transpose().reset_index()
        new.insert( 0,"Total", ['', '', 'Dine In', 'Dine In','Take Out','Take Out', 'Delivery','Delivery','Catering','Catering'], True)
        new.insert( 0, "Sub",['', '', 'Instore', 'Instore','Instore','Instore', 'External','External','External','External'], True)
        new2 = new.drop(0).drop(1)
        new2.columns = ['Source1','Source2','Source3','Total']
        new2.replace({"Food Eat in £": "Food","Drink Eat in £":"Drink",
                     "Food T/O £":"Food","Drink T/O £":"Drink"}, 
                   inplace=True)
        
        fig = px.sunburst(new2.assign(hole=base), path=['hole','Source1','Source2','Source3'],
                          values = 'Total',
                          title="Sales Source",
                         color_discrete_sequence=px.colors.sequential.dense)
        fig.update_traces(textinfo="label+percent parent",hovertemplate=None)
        fig.add_trace(go.Sunburst(insidetextorientation='horizontal'))
       
        fig.update_layout(
        margin=dict(l=15, r=15, t=30, b=20),
        paper_bgcolor="LightSteelBlue",)
        fig.update_layout(title_text='Sales Source', title_x=0.5,title_y=0.98)
  
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
