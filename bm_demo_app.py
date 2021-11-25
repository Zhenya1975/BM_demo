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
mode = initial_values.mode

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
    Output("managers_selector_checklist_calendar_actions_tab", "value"),
    Output("managers_selector_checklist_calendar_actions_tab", "options"),
    Output('closed_meetings_day_distribution_graph', 'figure'),
    Output('open_meetings_day_distribution_graph', 'figure'),
    Output('overdue_meetings_day_distribution_graph', 'figure'),
    Output('open_meetings_user_distribution_graph', 'figure'),
    Output('closed_meetings_user_distribution_graph', 'figure'),
    Output('overdue_meetings_user_distribution_graph', 'figure'),
    Output('meetings-data-table', 'children'),
   ],

    [
        Input('select_all_regions_button_tab_calendar_actions', 'n_clicks'),
        Input('release_all_regions_button_tab_calendar_actions', 'n_clicks'),
        Input('region_selector_checklist_calendar_actions_tab', 'value'),
        Input('select_all_managers_button_tab_calendar_actions', 'n_clicks'),
        Input('release_all_managers_button_tab_calendar_actions', 'n_clicks'),
        Input('managers_selector_checklist_calendar_actions_tab', 'value'),
        Input('my-date-picker-range', 'start_date'),
        Input('my-date-picker-range', 'end_date'),
        Input('include_zeros_regions', 'value'),
        Input('select_meeting_type', 'value'),

   ])
def events_distribution(select_all_regions_button_tab_calendar_actions, release_all_regions_button_tab_calendar_action, regions_from_checklist, select_all_managers_button_tab_calendar_actions, release_all_regions_button_tab_calendar_actions, managers_from_checklist, start_date, end_date, include_zeros_checkbox_value, select_meeting_type):
    # Готовим выборку из events в срезах Запланированные встречи, Завершенные встречи и Просроченные встречи
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
    # plan_date_selected_df - это event_df обрезанный по датам от сегодня в будущее
    plan_date_start = datetime.datetime.now().date()
    close_date_finish = datetime.datetime.now().date()
    overdue_date_finish = datetime.datetime.now().date()

    plan_date_selected_df = functions_file.cut_df_by_dates_interval(event_df, 'Plan_date', plan_date_start, end_date)

    plan_data = plan_date_selected_df.copy()
    plan_data.loc[:, 'Event_status'] = 1

    # здесь нам нужно получить список регионов и список options для чек-листа, которые попали в выборку по датам Плановой даты
    # отдаем plan_date_selected_df - получаем списки регионов и пользователей
    planned_selections = functions_file.query_selections(plan_data)

    # close_date_selected_df - это event_df обрезанный по датам завершения из прошлого до сегодня.
    close_date_selected_df = functions_file.cut_df_by_dates_interval(event_df, 'Close_date', start_date, close_date_finish)
    close_data = close_date_selected_df.copy()
    close_data.loc[:, 'Event_status'] = 3
    closed_selections = functions_file.query_selections(close_data)

    # Просроченные встречи
    # режем диапазон дат. По полю "Plan_date"
    overdue_meetings_date_selected_df = functions_file.cut_df_by_dates_interval(event_df, 'Plan_date', start_date, overdue_date_finish)
    overdue_meetings_date_selected_df = overdue_meetings_date_selected_df.loc[overdue_meetings_date_selected_df['Close_date'] == datetime.datetime.strptime('1970-01-01', "%Y-%m-%d").date()]
    overdue_data = overdue_meetings_date_selected_df.copy()
    overdue_data.loc[:, 'Event_status'] = 2
    overdue_selections = functions_file.query_selections(overdue_data)

    # Получаем уникальные списки регионов
    regions_data = functions_file.get_unique_region(planned_selections[0], closed_selections[0], overdue_selections[0])
    regions_options = regions_data[0]
    regions_list = regions_data[1]
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]


    if regions_from_checklist:
        region_list_value = regions_from_checklist
    else:
        region_list_value = regions_list

    region_list_options = regions_options
    id_checklist_region = 'region_selector_checklist_calendar_actions_tab'

    if id_checklist_region in changed_id:
        region_list_value = regions_from_checklist



    # Обработчик кнопок Снять / Выбрать в блоке Регионы
    id_select_all_button = "select_all_regions_button_tab_calendar_actions"
    id_release_all_button = "release_all_regions_button_tab_calendar_actions"

    if id_select_all_button in changed_id:
        region_list_value = regions_list
    elif id_release_all_button in changed_id:
        region_list_value = []

    ################# блок получения данных для чек-листа пользователей ################
    users_data = functions_file.get_unique_users(planned_selections[1], closed_selections[1], overdue_selections[1],
                                                 region_list_value, managers_from_checklist)
    users_list_options = users_data[0]
    users_list_values = users_data[1]



    id_checklist_users = 'managers_selector_checklist_calendar_actions_tab'
    if id_checklist_users in changed_id:
        users_list_values = managers_from_checklist

    # Обработчик кнопок Снять / Выбрать в блоке Пользователи
    id_select_all_users_button = "select_all_managers_button_tab_calendar_actions"
    id_release_all_users_button = "release_all_managers_button_tab_calendar_actions"

    if id_select_all_users_button in changed_id:
        users_list_values = users_data[1]
    elif id_release_all_users_button in changed_id:
        users_list_values = []

    # список регионов для формирования графика



    plan_date_selected_with_regions_df = plan_date_selected_df.loc[plan_date_selected_df['region_code'].isin(region_list_value) & plan_date_selected_df['user_code'].isin(users_list_values)]
    planned_graph_data = functions_file.planned_graph_prep(plan_date_selected_with_regions_df, include_zeros_checkbox_value)[0]
    planned_graph_data_by_users = functions_file.planned_graph_prep(plan_date_selected_with_regions_df, include_zeros_checkbox_value)[1]
    #  общее количество Запланировано. Для вывода в заголовок графика
    planned_by_users_total_qty = int(planned_graph_data_by_users['Planned_qty'].sum())
    planned_by_users_graph_fig = go.Figure()
    planned_by_users_graph_fig.add_trace(go.Bar(
        x=planned_graph_data_by_users['Planned_qty'],
        y=planned_graph_data_by_users['Name'],

        orientation='h'))
    start_open = plan_date_start.strftime("%d.%m.%y")
    end_open = end_date.strftime("%d.%m.%y")
    planned_by_users_graph_fig.update_layout(
        template='plotly_dark',
        title='Запланировано: {}<br><sup>c {} по {}</sup> '.format(planned_by_users_total_qty, start_open, end_open),
    )

    ######### Запланированное кол-во по регионам ###########################
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

    close_date_selected_df = close_date_selected_df.loc[close_date_selected_df['region_code'].isin(region_list_value) & close_date_selected_df['user_code'].isin(users_list_values)]
    closed_graph_data = functions_file.closed_graph_prep(close_date_selected_df, include_zeros_checkbox_value)[0]
    closed_graph_data_by_users = functions_file.closed_graph_prep(close_date_selected_df, include_zeros_checkbox_value)[1]
    ############### график закрытых ивентов по юзерам ################
    #  общее количество Запланировано. Для вывода в заголовок графика
    closed_by_users_total_qty = int(closed_graph_data_by_users['Closed_qty'].sum())
    closed_by_users_graph_fig = go.Figure()
    closed_by_users_graph_fig.add_trace(go.Bar(
        x=closed_graph_data_by_users['Closed_qty'],
        y=closed_graph_data_by_users['Name'],

        orientation='h'))
    start_close = start_date.strftime("%d.%m.%y")
    end_close = close_date_finish.strftime("%d.%m.%y")
    closed_by_users_graph_fig.update_layout(
        template='plotly_dark',
        title='Завершено: {}<br><sup>c {} по {}</sup> '.format(closed_by_users_total_qty, start_close, end_close),
    )





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

    overdue_meetings_date_selected_df = overdue_meetings_date_selected_df.loc[overdue_meetings_date_selected_df['region_code'].isin(region_list_value) & overdue_meetings_date_selected_df['user_code'].isin(users_list_values) & overdue_meetings_date_selected_df['Event_status'].isin([1,2])]

    overdue_graph_data = functions_file.overdue_graph_prep(overdue_meetings_date_selected_df, include_zeros_checkbox_value)[0]
    overdue_graph_user_data = functions_file.overdue_graph_prep(overdue_meetings_date_selected_df, include_zeros_checkbox_value)[1]
    # overdue_graph_user_data.to_csv('Data/overdue_graph_user_data_delete.csv')
    overdue_graph_user_fig = go.Figure()
    overdue_graph_user_fig.add_trace(go.Bar(
        x=overdue_graph_user_data['Overdue_qty'],
        y=overdue_graph_user_data['Name'],

        orientation='h'))
    overdue_user_total_qty = int(overdue_graph_user_data['Overdue_qty'].sum())
    start_overdue = start_date.strftime("%d.%m.%y")
    overdue_end_open = overdue_date_finish.strftime("%d.%m.%y")
    overdue_graph_user_fig.update_layout(
        template='plotly_dark',
        title='Просрочено: {}<br><sup>c {} по {}</sup> '.format(overdue_user_total_qty, start_overdue, overdue_end_open),
    )



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

    # готовим таблицу с данными по встречам
    # Завершенные встречи
    users_df = pd.read_csv('Data/users.csv')

    close_data_filtered_df = close_data.loc[close_data['region_code'].isin(region_list_value) & close_data['user_code'].isin(users_list_values)]
    close_date_selected__with_names_df = pd.merge(close_data_filtered_df, users_df, on='user_code', how='left')

    if mode == 'demo':
        customers_df = pd.read_csv('Data/companies_selected_demo.csv')
    else:
        customers_df = pd.read_csv('Data/companies_selected.csv')

    close_date_selected__with_names_and_customers_df = pd.merge(close_date_selected__with_names_df, customers_df, on='Customer_id', how='left')

    # готовим таблицу с данными по встречам
    # Запланированные встречи
    planned_data_filtered_df = plan_data.loc[plan_data['region_code'].isin(region_list_value) & plan_data['user_code'].isin(users_list_values)]
    plan_date_selected__with_names_df = pd.merge(planned_data_filtered_df, users_df, on='user_code', how='left')
    plan_date_selected__with_names_and_customers_df = pd.merge(plan_date_selected__with_names_df, customers_df,
                                                                on='Customer_id', how='left')

    overdue_data_filtered_df = overdue_data.loc[overdue_data['region_code'].isin(region_list_value) & overdue_data['user_code'].isin(users_list_values)]
    overdue_date_selected__with_names_df = pd.merge(overdue_data_filtered_df, users_df, on='user_code', how='left')
    overdue_date_selected__with_names_and_customers_df = pd.merge(overdue_date_selected__with_names_df, customers_df,
                                                               on='Customer_id', how='left')

    # передаем в функцию создания данных таблицы список из фильтров и три таблицы с данными
    closed_meeting_data_df = functions_file.prepare_meetings_data(close_date_selected__with_names_and_customers_df, select_meeting_type)
    planned_meeting_data_df = functions_file.prepare_meetings_data(plan_date_selected__with_names_and_customers_df, select_meeting_type)
    overdue_meeting_data_df = functions_file.prepare_meetings_data(overdue_date_selected__with_names_and_customers_df, select_meeting_type)


    event_table_df = pd.concat([closed_meeting_data_df, planned_meeting_data_df, overdue_meeting_data_df], ignore_index=True)


    # таблицу со встречами получаем в html.Div(id='meetings-data-table') На него ссылается в колбэке, ожидая от него children, то есть html

    # переменная table_plan_output нужна для того, чтобы передаеть ее в return
    # table_plan_output = html.Div([meetings_table])


    meetings_table = dbc.Table().from_dataframe(event_table_df, style={'color': 'white'})

    ######################
    ###############
    #title = ['Hi Dash', 'Hello World']
    #link = [html.A(html.P('Link'), href="https://yahoo.com", target="_blank"), html.A(html.P('Link'), href="google.com")]

    # dictionary = {"title": title, "link": link}
    # df = pd.DataFrame(dictionary)
    #
    # table = dbc.Table.from_dataframe(df,
    #                                  #striped=True,
    #                                  #bordered=True,
    #                                  hover=True,
    #                                  style={'color': 'white'})
    table_plan_output = html.Div([meetings_table])
    ################

    #######################

    return region_list_value, region_list_options, users_list_values, users_list_options, closed_graph_fig, planned_graph_fig, overdue_graph_fig, planned_by_users_graph_fig, closed_by_users_graph_fig, overdue_graph_user_fig, table_plan_output

if __name__ == "__main__":
    app.run_server(debug=True)
