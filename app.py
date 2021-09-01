import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import ruptures as rpt
import plotly.express as px
import plotly.graph_objects as go
import datetime
from datetime import  date

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    }, dbc.themes.BOOTSTRAP
]
# import data
covid_data = pd.read_csv('covid_preds.csv')
subway_data = pd.read_csv('subway_preds.csv')

# round figures
covid_data["Abs 7 day Difference"] = covid_data["Abs 7 day Difference"].round(2)
subway_data["Abs 7 day Difference"] = subway_data["Abs 7 day Difference"].round(2)
covid_data["Abs 14 day Difference"] = covid_data["Abs 14 day Difference"].round(2)
subway_data["Abs 14 day Difference"] = subway_data["Abs 14 day Difference"].round(2)

# Convert dates to datetime format
covid_data["Date"] = pd.to_datetime(covid_data["Date"])
subway_data["Date"] = pd.to_datetime((subway_data["Date"]))

# Converting String dates to datetime format
jhu_df = pd.read_csv('jhu_events.csv')
ds = jhu_df["Date"]
nds = []
for d in ds:
    d = d.replace(',', '')
    d = datetime.datetime.strptime(d, '%b %d %Y').strftime('%d/%m/%Y')
    nds.append(d)
jhu_df["Date"] = nds
jhu_df = jhu_df[["Date", "Event Description"]]
jhu_df["Date"] = pd.to_datetime(jhu_df["Date"])
jhu_df = jhu_df.loc[jhu_df["Date"] < "2021-03-01"]

# condense all events on the same day to 1 cell
event_data = jhu_df.groupby('Date')["Event Description"].apply('----> \n'.join).reset_index()

covid_data = covid_data.merge(event_data, left_on="Date", right_on="Date", how="left")
covid_data["Event Description"].fillna(method="ffill", inplace=True)

subway_data = subway_data.merge(event_data, left_on="Date", right_on="Date", how="left")
subway_data["Event Description"].fillna(method="ffill", inplace=True)

#covid_data.to_csv('test.csv')

ev_covid_fig = go.Figure(data=go.Scatter(x=covid_data["Date"], y=covid_data["MA Cases"], mode="lines",
                                         name="Moving Average of COVID-19 Cases in New York City"))
ev_covid_fig.add_trace(go.Scatter(x=covid_data["Date"], y=covid_data["7 days Ahead Forecasted Values"], mode="lines",
                                  name="LSTM 7 Prediction"))

ev_covid_fig.update_layout(
    xaxis_tickformat='%B <br>%Y'
)
ev_covid_fig.update_layout(
    {'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)', })
ev_subway_fig = go.Figure(data=go.Scatter(x=subway_data["Date"], y=subway_data["MA Entries"], mode="lines",
                                          name="Moving Average of Subway Entries in New York City"))
ev_subway_fig.add_trace(go.Scatter(x=subway_data["Date"], y=subway_data["7 days Ahead Forecasted Values"], mode="lines",
                                   name="LSTM 7 Prediction"))
ev_subway_fig.update_layout(
    xaxis_tickformat='%B <br>%Y'
)

ev_subway_fig.update_layout(
    {'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)', })

rt_covid_df = pd.read_csv('rt_covid.csv')

rt_subway_df = pd.read_csv('rt_subway.csv')

rt_covid_fig = go.Figure(data=go.Scatter(x=rt_covid_df["date_of_interest"], y=rt_covid_df["MA Cases"], mode="lines",
                                         name="Moving Average of COVID-19 Cases in New York City"))
rt_covid_fig.add_trace((go.Scatter(x= rt_covid_df["date_of_interest"], y= rt_covid_df["CASE_COUNT"], mode="lines", name="COVID-19 Cases in New York City")))

rt_subway_fig = go.Figure(data=go.Scatter(x=rt_subway_df["Date"], y=rt_subway_df["MA Entries"], mode="lines",
                                         name="Moving Average of COVID-19 Cases in New York City"))
rt_subway_fig.add_trace(go.Scatter(x=rt_subway_df["Date"], y=rt_subway_df["Subways: Total Estimated Ridership"], mode="lines",
                                   name="Subway Usage Numbers in New York City"))

app = dash.Dash(__name__, external_stylesheets= external_stylesheets, suppress_callback_exceptions=True)
server = app.server


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                dcc.Location(id="url", refresh=False),
                html.Div(id='page-content')
            ]
        ),
    ]
)

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink('Home', href="/")),
        dbc.NavItem(dbc.NavLink("By Events", href="/events")),
        dbc.NavItem(dbc.NavLink("By Change Points", href="/changepoints")),
        dbc.NavItem(dbc.NavLink("Real-time Data", href="/real-time-data"))
    ],
    brand="",
    brand_href="#",
    color="black",
    dark=True,
)

title = html.Div(
            children=[
                html.P(children="📊", className="header-emoji"),
                html.H1(
                    children="Impact of Public Policies and Events on COVID-19 Cases & Subway Usage in NYC", className="header-title"
                ),
                html.P(
                    children=""
                             ""
                             "",
                    className="header-description",
                ),
            ],
            className="header",
        )

event_title = html.Div(
            children=[
                html.P(children="📊", className="header-emoji"),
                html.H1(
                    children="Ranked By Event", className="header-title"
                ),
                html.P(
                    children=""
                             ""
                             "",
                    className="header-description",
                ),
            ],
            className="header",
        )
real_time_title = html.Div(
            children=[
                html.P(children="📊", className="header-emoji"),
                html.H1(
                    children="Real-time Data", className="header-title"
                ),
                html.P(
                    children=""
                             ""
                             "",
                    className="header-description",
                ),
            ],
            className="header",
        )
event_graphs = html.Div(
            children=[
                    dbc.Button("Calculate Top 10 Most Impactful Events", id="calculate-btn", n_clicks=0, className="btn"),
                    html.Div("COVID-19 Cases in NYC"),
                    dcc.Graph(
                        id="events-covid-chart",
                        figure= ev_covid_fig,
                        config={"displayModeBar": False}
                    ),
                    html.Div("LSTM 7 Table"),
                    dash_table.DataTable(
                        style_cell={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'fontSize': 14, 'font-family': 'sans-serif'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'Event Description'},
                                'textAlign': 'left'
                            }
                        ],
                        id="covid-event-table",
                        columns=[],
                        data=[]
                    ),
                    html.Div("LSTM 14 Table"),
                    dash_table.DataTable(
                        style_cell={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'fontSize': 14, 'font-family': 'sans-serif'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'Event Description'},
                                'textAlign': 'left'
                            }
                        ],
                        id="covid-event-14table",
                        columns=[],
                        data=[]
                    ),

                    html.Div("Subway Entries in NYC"),
                    dcc.Graph(
                        id="events-subway-chart",
                        figure= ev_subway_fig,
                        config={"displayModeBar": False}
                    ),
                    html.Div("LSTM 7 Table"),
                    dash_table.DataTable(
                        style_cell={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'fontSize': 14, 'font-family': 'sans-serif'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'Event Description'},
                                'textAlign': 'left'
                            }
                        ],
                        id="subway-event-table",
                        columns=[],
                        data=[]
                    ),
                    html.Div("LSTM 14 Table"),
                    dash_table.DataTable(
                        style_cell={
                            'whiteSpace': 'normal',
                            'height': 'auto',
                            'fontSize': 14, 'font-family': 'sans-serif'
                        },
                        style_cell_conditional=[
                            {
                                'if': {'column_id': 'Event Description'},
                                'textAlign': 'left'
                            }
                        ],
                        id="subway-event-14table",
                        columns=[],
                        data=[]
                    ),
                    #table,
            ],
            className="card",
        )
rt_graphs = html.Div(
    children=[
        html.Div("COVID-19 Cases in NYC"),
        dcc.Graph(
            id="rt-covid-chart",
            figure=rt_covid_fig,
            config={"displayModeBar": False}
        ),
        html.Div("Subway Usage in NYC"),
        dcc.Graph(
            id="rt-subway-chart",
            figure=rt_subway_fig,
            config={"displayModeBar": False}
        ),
    ]

)

upload=html.Div(
        children=[
dcc.Upload(
    id='upload-data',
    children=html.Div([
        'Drag and Drop or ',
        html.A('Select Files')
    ]),
    style={
        'width': '50%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center',
        'margin': '20px auto 0 auto',
    },
    # Allow multiple files to be uploaded
    multiple=True,
),
html.Div(id='output-data-upload'),
    ]
)
index_page = html.Div(
    children=[
        title,
        html.Div(
            children=[
                dcc.Link(dbc.Button('Ranked By Events', className='mp-btn1'), href="/events"),
                dcc.Link(dbc.Button('Ranked By Change Points', className='mp-btn2'), href="/changepoints"),
                dcc.Link(dbc.Button('Realtime Data', className='mp-btn1'), href="/real-time-data")
            ],
            className='menu3'
        ),
    ]
    ,
)
events_page = html.Div(
    children=[
        navbar,
        event_title,
        html.Div(
            children=[
                html.Div(
                    children="Add an Event",
                    className="menu-title"
                ),
                dcc.DatePickerSingle(
                    id="calendar-date-picker",
                    min_date_allowed=subway_data.Date.min().date(),
                    max_date_allowed=subway_data.Date.max().date(),
                    initial_visible_month=subway_data.Date.min().date(),
                    date=date(2020, 3, 3)
                ),
            ],
            className="menu",
        ),
        upload,
        event_graphs
    ]
)
change_points_page = html.Div(
    children=[
        navbar,
        title,
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Number of change points for COVID-19", className="menu-title"),
                        dcc.Dropdown(
                            id="change-point-filter",
                            options=[
                                {"label": number, "value": number}
                                for number in range(1, 160)
                            ],
                            value=1,
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
            ],
            className="menu",
        ),

        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="covid-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Number of Change Points for Subway Usage", className="menu-title"),
                        dcc.Dropdown(
                            id="subway-change-point-filter",
                            options=[
                                {"label": number, "value": number}
                                for number in range(1, 160)
                            ],
                            value=1,
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
            ],
            className="menu2",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="subway-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
        ),


    ]
)
real_time_data = html.Div(
    children=[
        navbar,
        real_time_title,
        html.Div(
            children=[
                html.Div(
                    children="Add an Event",
                    className="menu-title"
                ),
                dcc.DatePickerSingle(
                    id="calendar-date-picker-rt",
                    min_date_allowed=subway_data.Date.min().date(),
                    max_date_allowed=subway_data.Date.max().date(),
                    initial_visible_month=subway_data.Date.min().date(),
                    date=date(2020, 3, 3)
                ),
            ],
            className="menu",
        ),
        rt_graphs
    ]
)

# events-page callbacks
@app.callback(
    [Output("events-covid-chart", "figure"), Output("events-subway-chart", "figure"),
     Output("covid-event-table", "columns"), Output("covid-event-table", "data"),
     Output("subway-event-table", "columns"), Output("subway-event-table", "data"),
    Output("covid-event-14table", "columns"), Output("covid-event-14table", "data"),
    Output("subway-event-14table", "columns"), Output("subway-event-14table", "data")],
    [
        Input("calculate-btn", "n_clicks"),
        Input('calendar-date-picker', "date")
    ],
)
def on_click_calc(n_clicks, date_val):
    ctx = dash.callback_context

    if not ctx.triggered:
        what_was_clicked = "nothing"
    else:
        what_was_clicked = ctx.triggered[0]['prop_id'].split('.')[0]


    no_cps = len(event_data["Date"].unique())

    ma_cases = covid_data["MA Cases"].values
    c_algo = rpt.Dynp(model="l2", jump=1).fit(ma_cases)
    ccps = c_algo.predict(no_cps)
    covid_cps = covid_data.loc[covid_data.index.isin(ccps)]
    #covid_cps["Date"] = covid_cps['Date'].dt.strftime('%Y-%m-%d')
    covid_cps = covid_cps.groupby("Event Description").nth(0).reset_index()

    ma_entries = subway_data["MA Entries"].values
    s_algo = rpt.Dynp(model="l2", jump=1).fit(ma_entries)
    scps = s_algo.predict(no_cps)

    subway_cps = subway_data.loc[subway_data.index.isin(scps)]
    #subway_cps["Date"] = subway_cps['Date'].dt.strftime('%Y-%m-%d')
    subway_cps = subway_cps.groupby("Event Description").nth(0).reset_index()


    if what_was_clicked == "calendar-date-picker":
        cov_graph = ev_covid_fig
        date_val = datetime.datetime.strptime(date_val, "%Y-%m-%d")
        x_dates = [date_val] #, date_val + datetime.timedelta(days=30)] #, date_val+ datetime.timedelta(days=2), date_val + datetime.timedelta(days=3)]
        impact = covid_cps.loc[covid_cps["Date"] <= date_val]
        impact = impact.sort_values(by= "Date")
        #print(impact[["Date", "7 day Difference", "MA Cases"]])
        impact = impact.tail(1)
        y_vals = impact["Abs 7 day Difference"]
        #width = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.4]
        cov_graph.add_trace(go.Bar(x=x_dates,y=y_vals, width= 1000 * 3600 * 24 *2, name="Added Event Impact"))

        sub_graph = ev_subway_fig
        sub_impact = subway_cps.loc[subway_cps["Date"] <= date_val]
        sub_impact = sub_impact.sort_values(by= "Date")
        sub_impact = sub_impact.tail(1)
        sub_y = sub_impact["Abs 7 day Difference"]
        sub_graph.add_trace(go.Bar(x= x_dates, y= sub_y, width= 1000*3600 *24 *2, name="Added Event Impact"))
        return cov_graph,sub_graph, [], [], [], [], [], [], [], []

    elif what_was_clicked == "calculate-btn" and (n_clicks >0):

        covid_cps7 = covid_cps.sort_values(by=["Abs 7 day Difference"], ascending=False).head(10)
        covid_cps14 = covid_cps.sort_values(by=["Abs 14 day Difference"], ascending=False).head(10)

        events_covid_chart_figure = ev_covid_fig

        events_covid_chart_figure.add_bar(x=covid_cps7["Date"].head(10),
                                          y=covid_cps7["Abs 7 day Difference"].head(10),
                                          name="Top 10 Event Impacts")




        subway_cps7 = subway_cps.sort_values(by=["Abs 7 day Difference"], ascending=False).head(10)
        subway_cps14 = subway_cps.sort_values(by=["Abs 14 day Difference"], ascending=False).head(10)

        events_subway_chart_figure = ev_subway_fig

        events_subway_chart_figure.add_bar(x= subway_cps7["Date"].head(10), y= subway_cps7["Abs 7 day Difference"].head(10),name="Event Impact")

        cols = ["Date", "Abs 7 day Difference", "Event Description"]
        cols = [{"name": i, "id": i} for i in cols]

        cols14 = ["Date", "Abs 14 day Difference", "Event Description"]
        cols14 = [{"name": i, "id": i} for i in cols14]

        sub_cols =["Date", "Abs 7 day Difference", "Event Description"]
        sub_cols = [{"name": j, "id": j} for j in sub_cols]

        sub_cols14 = ["Date", "Abs 14 day Difference", "Event Description"]
        sub_cols14 = [{"name": j, "id": j} for j in sub_cols14]

        c_data = covid_cps7[["Date", "Abs 7 day Difference", "Event Description"]].to_dict('records')
        c_data14 = covid_cps14[["Date", "Abs 14 day Difference", "Event Description"]].to_dict('records')

        s_data = subway_cps7[["Date", "Abs 7 day Difference", "Event Description"]].to_dict('records')
        s_data14 = subway_cps14[["Date", "Abs 14 day Difference", "Event Description"]].to_dict('records')

        return events_covid_chart_figure, events_subway_chart_figure, cols, c_data, sub_cols, s_data, cols14, c_data14, sub_cols14, s_data14
    else:
        return ev_covid_fig, ev_subway_fig, [], [], [], [], [], [], [], []
    print(what_was_clicked)
    print(date_val)


# change-points-page callbacks
@app.callback(
    Output("covid-chart", "figure"),
    [
        Input("change-point-filter", "value")
    ],
)
def update_covid(no_cp):
    ma_cases = covid_data["MA Cases"].values
    algo = rpt.Dynp(model="l2", jump= 1).fit(ma_cases)
    cps = algo.predict(no_cp)
    dates = covid_data["Date"].loc[covid_data.index.isin(cps)]
    covid_chart_figure = px.line(
        covid_data, x="Date", y= ["MA Cases", "7 days Ahead Forecasted Values"],
    )
    for date in dates:
        covid_chart_figure.add_vline(x = date, line_width = 1, line_color = "green")
    covid_chart_figure.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)',})
    return covid_chart_figure

@app.callback(
    Output("subway-chart", "figure"),
    [
        Input("subway-change-point-filter", "value")
    ],
)
def update_subway(no_cp):
    ma_entries = subway_data["MA Entries"].values
    algo = rpt.Dynp(model="l2", jump= 1).fit(ma_entries)
    cps = algo.predict(no_cp)
    dates = subway_data["Date"].loc[subway_data.index.isin(cps)]
    subway_chart_figure = px.line(
        subway_data, x="Date", y = ["MA Entries", "7 days Ahead Forecasted Values"],
    )
    for date in dates:
        subway_chart_figure.add_vline(x = date, line_width = 1, line_color = "green")
    subway_chart_figure.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)', 'paper_bgcolor': 'rgba(0, 0, 0, 0)',})
    return subway_chart_figure

@app.callback(Output('page-content', 'children'),
              [Input('url','pathname')])
def display_page(pathname):
    if pathname == "/events":
        return events_page
    elif pathname == "/changepoints":
        return change_points_page
    elif pathname == "/real-time-data":
        return real_time_data
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
