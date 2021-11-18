import datetime
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State, callback_context
import dash
import pandas as pd
import functions_file
import plotly.graph_objects as go
import tab_calendar_actions
import tab_settings
import initial_values
#app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(__name__)
app.title = " BM Demo dashboard"
server = app.server

body = html.Div([
    dbc.Container([
        # dcc.Store stores the intermediate value
        dcc.Store(id='intermediate-value'),
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
                    #tab_settings.tab_settings(),
                    # tab2(),
                    # tab3(),
                ]
            ),
        ])
    ],
        fluid=True, className='dash-bootstrap')

])
app.layout = html.Div([body])


@app.callback(
    Output('intermediate-value', 'data'),
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date')])
def data(start_date, end_date):
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    # plan_date_selected_df - это event_df обрезанный по датам от сегодня в будущее
    plan_date_start = datetime.datetime.now().date()
    close_date_finish = datetime.datetime.now().date()
    overdue_date_finish = datetime.datetime.now().date()

    plan_date_selected_df = functions_file.cut_df_by_dates_interval(event_df, 'Plan_date', plan_date_start, end_date)
    output_data = plan_date_selected_df.to_json(date_format='iso', orient='split')
    # more generally, this line would be
    # json.dumps(cleaned_df)
    return output_data
# попробуем получить через dcc.Store



# обработчик кнопок Снять все/Выбрать
# @app.callback(
#     Output("region_selector_checklist_calendar_actions_tab", "value"),
#     #Output("region_selector_checklist_calendar_actions_tab", "options"),
#     [Input('select_all_regions_button_tab_calendar_actions', 'n_clicks'),
#      Input('release_all_regions_button_tab_calendar_actions', 'n_clicks')],
#     [State("region_selector_checklist_calendar_actions_tab", "options")],
# )
# def button_regions_callback_func(select_all_regions_button_tab_calendar_actions, release_all_regions_button_tab_calendar_action, options):
#     full_list = functions_file.selectall_relese_all_buttons('select_all_regions_button_tab_calendar_actions',
#                                                             'release_all_regions_button_tab_calendar_action', options)
#
#     return full_list

# получаем датафрейм со встречами
event_df = functions_file.get_event_df()
@app.callback([
    #Output('meetings_day_distribution_graph', 'figure'),
    Output("region_selector_checklist_calendar_actions_tab", "value"),
    Output("region_selector_checklist_calendar_actions_tab", "options"),
    Output('closed_meetings_day_distribution_graph', 'figure'),
    Output('open_meetings_day_distribution_graph', 'figure'),
    Output('overdue_meetings_day_distribution_graph', 'figure'),
   ],

    [
        Input('select_all_regions_button_tab_calendar_actions', 'n_clicks'),
        Input('release_all_regions_button_tab_calendar_actions', 'n_clicks'),

        Input('region_selector_checklist_calendar_actions_tab', 'value'),
        Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('include_zeros_regions', 'value'),
   ])
def events_distribution(select_all_regions_button_tab_calendar_actions, release_all_regions_button_tab_calendar_action, regions_from_checklist, start_date, end_date, include_zeros_checkbox_value):
    # Готовим выборку из events в срезах Запланированные встречи, Завершенные встречи и Просроченные встречи
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    # plan_date_selected_df - это event_df обрезанный по датам от сегодня в будущее
    plan_date_start = datetime.datetime.now().date()
    close_date_finish = datetime.datetime.now().date()
    overdue_date_finish = datetime.datetime.now().date()

    plan_date_selected_df = functions_file.cut_df_by_dates_interval(event_df, 'Plan_date', plan_date_start, end_date)
    # здесь нам нужно получить список регионов и список options для чек-листа, которые попали в выборку по датам Плановой даты
    # отдаем plan_date_selected_df - получаем списки регионов и пользователей
    planned_selections = functions_file.query_selections(plan_date_selected_df)

    # close_date_selected_df - это event_df обрезанный по датам завершения из прошлого до сегодня.
    close_date_selected_df = functions_file.cut_df_by_dates_interval(event_df, 'Close_date', start_date, close_date_finish)
    closed_selections = functions_file.query_selections(close_date_selected_df)

    # Просроченные встречи
    # режем диапазон дат. По полю "Plan_date"
    overdue_meetings_date_selected_df = functions_file.cut_df_by_dates_interval(event_df, 'Plan_date', start_date, overdue_date_finish)
    overdue_selections = functions_file.query_selections(overdue_meetings_date_selected_df)

    # Получаем уникальные списки регионов и пользователей
    regions_data = functions_file.get_unique_region_and_users(planned_selections[0], closed_selections[0], overdue_selections[0])
    regions_options = regions_data[0]
    regions_list = regions_data[1]

    region_list_value = regions_list
    region_list_options = regions_options
    id_checklist = 'region_selector_checklist_calendar_actions_tab'
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    if id_checklist in changed_id:
        region_list_value = regions_from_checklist

    # Обработчик кнопок Снять / Выбрать в блоке Регионы
    id_select_all_button = "select_all_regions_button_tab_calendar_actions"
    id_release_all_button = "release_all_regions_button_tab_calendar_actions"
    if id_select_all_button in changed_id:
        region_list_value = regions_list
    elif id_release_all_button in changed_id:
        region_list_value = []


    # надо подать список регионов для формирования графика
    plan_date_selected_with_regions_df = plan_date_selected_df.loc[plan_date_selected_df['region_code'].isin(region_list_value)]
    planned_graph_data = functions_file.planned_graph_prep(plan_date_selected_with_regions_df, include_zeros_checkbox_value)
    #  общее количество Запланировано. Для вывода в заголовок графика
    planned_total_qty = int(planned_graph_data['Planned_qty'].sum())
    planned_graph_fig = go.Figure()
    planned_graph_fig.add_trace(go.Bar(
            x=planned_graph_data['Planned_qty'],
            y=planned_graph_data['region_name'],

            orientation='h'))
    start_open = plan_date_start.strftime("%d.%m.%y")
    end_open = end_date.strftime("%d.%m.%y")
    planned_graph_fig.update_layout(
        template ='plotly_dark', title='Запланировано: {}<br><sup>c {} по {}</sup> '.format(planned_total_qty, start_open, end_open),
    )

    close_date_selected_df = close_date_selected_df.loc[close_date_selected_df['region_code'].isin(region_list_value)]
    closed_graph_data = functions_file.closed_graph_prep(close_date_selected_df, include_zeros_checkbox_value)
    closed_total_qty = int(closed_graph_data['Closed_qty'].sum())
    closed_graph_fig = go.Figure()
    closed_graph_fig.add_trace(go.Bar(
        x=closed_graph_data['Closed_qty'],
        y=closed_graph_data['region_name'],
        orientation='h'))
    start_close = start_date.strftime("%d.%m.%y")
    end_close = close_date_finish.strftime("%d.%m.%y")
    closed_graph_fig.update_layout(
        template='plotly_dark', title='Завершено: {}<br><sup>c {} по {}</sup> '.format(closed_total_qty, start_close, end_close),
    )

    overdue_meetings_date_selected_df = overdue_meetings_date_selected_df.loc[overdue_meetings_date_selected_df['region_code'].isin(region_list_value)]
    overdue_graph_data = functions_file.overdue_graph_prep(overdue_meetings_date_selected_df, include_zeros_checkbox_value)


    overdue_graph_fig = go.Figure()
    overdue_graph_fig.add_trace(go.Bar(
        x=overdue_graph_data['Overdue_qty'],
        y=overdue_graph_data['region_name'],

        orientation='h'))
    overdue_total_qty = int(overdue_graph_data['Overdue_qty'].sum())
    start_overdue = start_date.strftime("%d.%m.%y")
    overdue_end_open = overdue_date_finish.strftime("%d.%m.%y")
    overdue_graph_fig.update_layout(
        template='plotly_dark',
        title='Просрочено: {}<br><sup>c {} по {}</sup> '.format(overdue_total_qty, start_overdue, overdue_end_open),
    )



    return region_list_value, region_list_options, closed_graph_fig, planned_graph_fig, overdue_graph_fig

if __name__ == "__main__":
    app.run_server(debug=True)
