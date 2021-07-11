import pandas as pd
pd.set_option('max_rows',20)
import plotly.express as px
import plotly.io as pio
pio.renderers.default = "browser"

import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

CONF_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
DEAD_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
RECV_URL = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'

rawConf = pd.read_csv(CONF_URL)
rawDead = pd.read_csv(DEAD_URL)
rawRecv = pd.read_csv(RECV_URL)

#get data in cleaned time series format for country
def data_processing(data,cntry='US',window=3):
    conf = data
    confCntry = conf[conf['Country/Region']==cntry]
    final_dataset = confCntry.T[4:].sum(axis='columns').diff().rolling(window=window).mean()[40:]
    df = pd.DataFrame(final_dataset,columns=['Total'])
    return df

#get overall wordlwide total for confirmed, recovered and dead cases
def getWorldTotal(df):
    return df.iloc[:,-1].sum()

confWorldTotal = getWorldTotal(rawConf)
deadWorldTotal = getWorldTotal(rawDead)
recvWorldTotal = getWorldTotal(rawRecv)
print('Overall Confirmed:',confWorldTotal)
print('Overall Dead:',deadWorldTotal)
print('Overall Recovered:',recvWorldTotal)

#get total for confirmed, recovered and dead for country
def getCntryTotal(df,cntry='India'):
    return df[df['Country/Region']==cntry].iloc[:,-1].sum()

cntry = 'India'
confCntryTotal = getCntryTotal(rawConf,cntry)
deadCntryTotal = getCntryTotal(rawDead,cntry)
recvCntryTotal = getCntryTotal(rawRecv,cntry)
print(f'{cntry} Confirmed:',confCntryTotal)
print(f'{cntry} Dead:',deadCntryTotal)
print(f'{cntry} Recovered:',recvCntryTotal)

def worldTrend(cntry='US',window=3):
    df = data_processing(data=rawConf,cntry=cntry,window=window)
    df.head(10)
    if window==1:
        yaxis_title = "Daily Cases"
    else:
        yaxis_title = "Daily Cases ({}-day MA)".format(window)
    fig = px.line(df, y='Total', x=df.index, title='Daily confirmed cases trend for {}'.format(cntry),height=600,color_discrete_sequence =['#403f3d'])
    fig.update_layout(title_x=0.5,plot_bgcolor='#2c5491',paper_bgcolor='#2c5491',xaxis_title="Date",yaxis_title=yaxis_title)
    return fig

external_stylesheets = [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'COVID-19 Dashboard'

colors = {
    'background': '#17263d',
    'bodyColor':'#2c5491',
    'text': '#f7f9fc'
}
def getPageHeadingStyle():
    return {'backgroundColor': colors['background']}


def getPageHeadingTitle():
    return html.H1(children='COVID-19 Dashboard',
                                        style={
                                        'textAlign': 'center',
                                        'color': colors['text']
                                    })

def getPageHeadingSubtitle():
    return html.Div(children='Visualize Covid-19 data generated from sources all over the world.',
                                         style={
                                             'textAlign':'center',
                                             'color':'#d2d2d4'
                                         })

def generatePageHeader():
    mainHeader =  dbc.Row(
                            [
                                dbc.Col(getPageHeadingTitle(),md=12)
                            ],
                            align="center",
                            style=getPageHeadingStyle()
                        )
    subtitleHeader = dbc.Row(
                            [
                                dbc.Col(getPageHeadingSubtitle(),md=12)
                            ],
                            align="center",
                            style=getPageHeadingStyle()
                        )
    header = (mainHeader,subtitleHeader)
    return header

def getCountryList():
    return rawConf['Country/Region'].unique()

def createDropdownList(cntryList):
    dropdownList = []
    for cntry in sorted(cntryList):
        tmpDict = {'label':cntry,'value':cntry}
        dropdownList.append(tmpDict)
    return dropdownList

def getCountryDropdown(id):
    return html.Div([
                        html.Label('Select Country'),
                        dcc.Dropdown(id='my-id'+str(id),
                            options=createDropdownList(getCountryList()),
                            value='India'
                        ),
                        html.Div(id='my-div'+str(id))
                    ])

def graph1():
    return dcc.Graph(id='graph1',figure=worldTrend('India'))
def generateCardContent(card_header,card_value,overall_value):
    cardHeadStyle = {'textAlign':'center','fontSize':'150%'}
    cardBodyStyle = {'textAlign':'center','fontSize':'200%'}
    cardHeader = dbc.CardHeader(card_header,style=cardHeadStyle)
    cardBody = dbc.CardBody(
        [
            html.H5(f"{int(card_value):,}", className="card-title",style=cardBodyStyle),
            html.P(
                "Worlwide: {:,}".format(overall_value),
                className="card-text",style={'textAlign':'center'}
            ),
        ]
    )
    card = [cardHeader,cardBody]
    return card

def generateCards(cntry='India'):
    confCntryTotal = getCntryTotal(rawConf,cntry)
    deadCntryTotal = getCntryTotal(rawDead,cntry)
    recvCntryTotal = getCntryTotal(rawRecv,cntry)
    cards = html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.Card(generateCardContent("Recovered",recvCntryTotal,recvWorldTotal), color="#219e53", inverse=True),md=dict(size=2,offset=3)),
                    dbc.Col(dbc.Card(generateCardContent("Confirmed",confCntryTotal,confWorldTotal), color="#f5a236", inverse=True),md=dict(size=2)),
                    dbc.Col(dbc.Card(generateCardContent("Dead",deadCntryTotal,deadWorldTotal),color="dark", inverse=True),md=dict(size=2)),
                ],
                className="mb-4",
            ),
        ],id='card1'
    )
    return cards

def getSlider():
    return html.Div([
                        dcc.Slider(
                            id='my-slider',
                            min=1,
                            max=15,
                            step=None,
                            marks={
                                1: '1',
                                3: '3',
                                5: '5',
                                7: '1-Week',
                                14: 'Fortnight'
                            },
                            value=3,
                        ),
                        html.Div([html.Label('Select Moving Average Window')],id='my-div'+str(id),style={'textAlign':'center'})
                    ])


def generateLayout():
    pageHeader = generatePageHeader()
    layout = dbc.Container(
        [
            pageHeader[0],
            pageHeader[1],
            html.Hr(),
            generateCards(),
            html.Hr(),
            dbc.Row(
                [
                    dbc.Col(getCountryDropdown(id=1), md=dict(size=4, offset=4))
                ]

            ),
            dbc.Row(
                [

                    dbc.Col(graph1(), md=dict(size=6, offset=3))

                ],
                align="center",

            ),
            dbc.Row(
                [
                    dbc.Col(getSlider(), md=dict(size=4, offset=4))
                ]

            ),
        ], fluid=True, style={'backgroundColor': colors['bodyColor']}
    )
    return layout

app.layout = generateLayout()

@app.callback(
    [Output(component_id='graph1',component_property='figure'), #line chart
    Output(component_id='card1',component_property='children')], #overall card numbers
    [Input(component_id='my-id1',component_property='value'), #dropdown
     Input(component_id='my-slider',component_property='value')] #slider
)
def updateOutputDiv(input_value1,input_value2):
    return worldTrend(input_value1,input_value2),generateCards(input_value1)

app.run_server(host= '0.0.0.0',debug=False)

