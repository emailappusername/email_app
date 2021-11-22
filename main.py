import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Output, Input
import plotly.express as px 
import regex as re
from dash import dash_table 
import json 
import dash_app_functions
import warnings
import pickle 
warnings.filterwarnings("ignore", 'This pattern has match groups')


data = dash_app_functions.read_load_clean("data/data.pkl")

# load in bigram data 
bi_gram_data = dash_app_functions.read_load_clean("data/bigram_data.pkl")

# load in the trigram data 

tri_gram_data = dash_app_functions.read_load_clean("data/trigram_data.pkl")

# load in number of words in data
with open('data/num_words.pkl', 'rb') as f:
    length_words = pickle.load(f)




app = dash.Dash(__name__)
app.title = "LB Email Analytics"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Large Business Email Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze the content of emails "
                    " looking at words, their occurence over time and the relevant documents",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Ngram", className="menu-title"),
                        dcc.Dropdown(
                            id="radio_buttons",
                        options=[
                            {'label': 'Single Word', 'value': 'single_word'},
                            {'label': 'Bi-Gram', 'value': 'bi_gram'},
                            {'label': 'Tri-Gram', 'value': 'tri_gram'}
                            ],
                            value='single_word',
                            clearable=False,
                            className="dropdown",
                        ),
                    ], style={"width": "30%"}
                ),
                html.Div(
                    children=[
                        html.Div(children="Words", className="menu-title"),
                        dcc.Dropdown(
                            id="amount-word-filter",
                            options=[
                                 {"label": amount, "value": amount}
                                    for amount in length_words
                            ],
                            value=10,
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                     style={"width": "30%"}
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                            ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.date.min().date(),
                            max_date_allowed=data.date.max().date(),
                            start_date=data.date.min().date(),
                            end_date=data.date.max().date(),
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
                        id='graph-with-dates', figure = { 'layout': {
                'clickmode': 'event+select'
            }}, config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id='words-over-time', config={"displayModeBar": False},
                    ),
                    className="card",
                ), 
                html.P("Table of relevant documents"),
                html.Div(
                   children=dash_table.DataTable(id = "table", 
                       columns = [{'name': 'md5', 'id': 'md5'}, {'name': 'date', 'id': 'date'}],
                       page_size = 5, 
                           data = data.to_dict('records'), 
                           export_format="csv",
                               style_data={
                        'whiteSpace': 'normal',
                    'height': 'auto',
                 },),
                    className="card",
                ),

            ],
            className="wrapper",
        ),
    ]
)



@app.callback(
    Output('graph-with-dates', 'figure'),
        Input("amount-word-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"), 
        Input("radio_buttons", "value")
)
def update_word_chart(amount, start_date, end_date, radio_button_select): 
    
   

    if radio_button_select == "single_word": 

        # mask = (
        # (data.date >= start_date)
        # & (data.date <= end_date)
        # )

        # filtered_data = data.loc[mask, :]


        filtered_data = dash_app_functions.filter_date(data, start_date=start_date, end_date = end_date)
        # filter based on the words selected now: 
        filtered_data = pd.Series(" ".join(filtered_data.content).split()).value_counts()

    elif radio_button_select == "bi_gram": 

        filtered_data =  dash_app_functions.filter_date(bi_gram_data, start_date=start_date, end_date = end_date)

        filtered_data = filtered_data['content'].value_counts()

    else: 

        filtered_data = dash_app_functions.filter_date(tri_gram_data, start_date=start_date, end_date = end_date)

        filtered_data = filtered_data['content'].value_counts()

    # subset the data based on word selection: 
    filtered_data = filtered_data[0:amount]

    filtered_data = filtered_data.to_frame(name = "count").reset_index()

    title = f"Count of selected Ngram for entire document corpus from {start_date} to {end_date}"

    word_chart_figure = px.bar(filtered_data, x = "index", y = "count", title = title, template = "plotly_white")

    return word_chart_figure



# make a stationary app.callback for the word plot over time instead? 
# maybe to avoid it bugging out so often? 


# new callback for new plot over time for given word: 

@app.callback(
    Output('words-over-time', 'figure'),
        Input('graph-with-dates', 'clickData'),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"), 
        Input("radio_buttons", "value")
)
def update_word_chart(clickData, start_date, end_date, radio_button_select): 

    # to switch between style of bar charts
    if radio_button_select == "single_word": 

        filtered_data = dash_app_functions.filter_date(data, start_date=start_date, end_date = end_date)

    elif radio_button_select == "bi_gram": 
       
       filtered_data = dash_app_functions.filter_date(bi_gram_data, start_date=start_date, end_date = end_date)
        
    else: 
        filtered_data = dash_app_functions.filter_date(tri_gram_data, start_date=start_date, end_date = end_date)

    
    # obtain the word that has been selected by clicking on bar chart        
    word_to_use = dash_app_functions.obtain_clicked_word(event_type=clickData, radio_button_select=radio_button_select)

    # if clickData is not None: 
       
        
    #     clicked_word = json.dumps(clickData, indent = 2)
        
    #     clicked_word = json.loads(clicked_word)

    #     clicked_word = clicked_word['points'][0]['label']

    #     actual_word = clicked_word # for the title only 

    #     clicked_word = re.compile("(" + clicked_word + ")")

        

        
    # elif clickData is None: 

    #     clicked_word = "is"
        
    #     actual_word = clicked_word # for the title only

    #     clicked_word = re.compile("(" + clicked_word + ")")



 
    # filtered_data['occurences'] = data.content.str.count(clicked_word.pattern)
    filtered_data['occurences'] = data.content.str.count(word_to_use[0].pattern)
   
    # caluclate the mentions over time:

    filtered_data = filtered_data[['date', 'occurences']].groupby('date', as_index=False)[['occurences']].sum()


    # generate plot now 

    title = f"Occurences of word: {word_to_use[1]} from {start_date} to {end_date}"

    word_over_time_figure = px.line(filtered_data, x = "date", y = "occurences", title = title, template =  "plotly_white")
 
    word_over_time_figure.update_traces(mode='lines+markers',marker_color='#17B897', line_color = '#17B897')

   


    return word_over_time_figure




# new callback based on the click event of the barchart: 

@app.callback(
    Output('table', 'data'),
    Input('graph-with-dates', 'clickData'), 
    Input("date-range", "start_date"),
    Input("date-range", "end_date"), 
    Input("radio_buttons", "value"))
def display_click_data(clickData, start_date, end_date, radio_button_select):
    
    updated_data = dash_app_functions.filter_date(data, start_date=start_date, end_date = end_date)
   
    # obtain the word that has been selected by clicking on bar chart        
    word_to_use = dash_app_functions.obtain_clicked_word(event_type=clickData, radio_button_select=radio_button_select)
        
    # if clickData is not None: 

        
        
    #     clicked_word = json.dumps(clickData, indent = 2)
        
    #     clicked_word = json.loads(clicked_word)

    #     clicked_word = clicked_word['points'][0]['label']

    #     clicked_word = re.compile("(" + clicked_word + ")")



        
    # elif clickData is None:
    #     clicked_word = 'is'
    #     clicked_word = re.compile("(" + clicked_word + ")")
        

        # caluclate the mentions over time:
    updated_data = updated_data[updated_data['content'].str.contains(word_to_use[0].pattern) == True]
    # only select the md5 rows and the date 
    updated_data = updated_data[["md5", "date"]]
    # generate plot now 
    updated_data = updated_data.to_dict("records")


    return updated_data





if __name__ == "__main__":
    app.run_server(debug =True, port=8050, host='0.0.0.0')