import datetime
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import dash
import pandas as pd
import functions_file
import plotly.graph_objects as go
import tab_calendar_actions

#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(__name__)
app.title = " BM Demo dashboard"
server = app.server

body = html.Div([
    dbc.Container([
        html.Div(style={'paddingLeft': '15px', 'paddingRight': '20px', 'paddingTop': '5px', 'paddingBottom': '5px',
                         'color': 'white'},
            children=[
                dbc.Row([
                    dbc.Col(width=12, children=[html.H3('ОТЧЕТЫ'), ]),
                ])],
        ),
        html.Div([
            dcc.Tabs(
                id="tabs-with-classes",
                value='tab_calendar_actions',
                parent_className='custom-tabs',
                className='custom-tabs-container',
                children=[
                    tab_calendar_actions.calendar_actions(),
                    # tab2(),
                    # tab3(),
                ]
            ),
        ])
    ],
        fluid=True, className='dash-bootstrap')

])
app.layout = html.Div([body])

# обработчик кнопок Снять все/Выбрать чек-боксов "Этапы сделки" во вкладке "ЗАКАЗЫ-СКЛАДЫ-СДЕЛКИ"
@app.callback(
    Output("region_selector_checklist_calendar_actions_tab", "value"),
    [Input('select_all_regions_button_tab_calendar_actions', 'n_clicks'),
     Input('release_all_regions_button_tab_calendar_actions', 'n_clicks')],
    [State("region_selector_checklist_calendar_actions_tab", "options")],
)
def button_productgroup_callback_func(select_all_regions_button_tab_calendar_actions, release_all_regions_button_tab_calendar_action, options):
    full_list = functions_file.selectall_relese_all_buttons('select_all_regions_button_tab_calendar_actions',
                                                            'release_all_regions_button_tab_calendar_action', options)
    return full_list

# получаем датафрейм со встречами
event_df = functions_file.get_event_df()
@app.callback([Output('meetings_day_distribution_graph', 'figure'),
               Output('meetings_distribution_by_oblast_graph', 'figure'),
               ],
              [Input('region_selector_checklist_calendar_actions_tab', 'value'),
               Input('my-date-picker-range', 'start_date'),
               Input('my-date-picker-range', 'end_date'),
               Input('include_zeros_regions', 'value'),
               ])
def events_distribution(selected_regions, start_date, end_date, include_zeros_checkbox_value):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    plan_date_selected_df = functions_file.cut_df_by_dates_interval(event_df, 'Plan_date', start_date, end_date)
    close_date_selected_df = functions_file.cut_df_by_dates_interval(event_df, 'Close_date', start_date, end_date)
    graph_data = functions_file.events_grapf_prep(plan_date_selected_df , close_date_selected_df, include_zeros_checkbox_value)[0]
    oblast_dist_data = functions_file.events_grapf_prep(plan_date_selected_df , close_date_selected_df, include_zeros_checkbox_value)[1]
    x_oblast_dist = oblast_dist_data['Oblast']
    y_planned = oblast_dist_data['Planned_qty']
    y_closed = oblast_dist_data['Closed_qty']

    fig_dist_oblast = go.Figure()
    fig_dist_oblast.add_trace(go.Bar(name='Запланировано', x=x_oblast_dist, y=y_planned))
    fig_dist_oblast.add_trace(go.Bar(name='Завершено', x=x_oblast_dist, y=y_closed))

    # Change the bar mode
    fig_dist_oblast.update_layout(
        barmode='group',
        template= 'plotly_dark',
        title = "Встречи по областям, кол-во",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        #legend_title_text='Встречи по областям, кол-во'

        #legend_orientation="h"
    )
    #figure = go.Figure()
    x = graph_data['value']
    y = graph_data['category']
    #print(x, type(x))
    #print(y, type(y))

    trace = go.Funnel(
        y=y,
        x=x,
        textposition="inside",
        textinfo="value",
    )
    layout = {'template': 'plotly_dark', 'title': {'text': 'Встречи, кол-во'},}

    return go.Figure(data=trace, layout = layout), fig_dist_oblast

if __name__ == "__main__":
    app.run_server(debug=True)
