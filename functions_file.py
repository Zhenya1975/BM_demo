import pandas as pd
from dash import callback_context
import datetime
import initial_values
import json
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
# получаем список регионов в виде кодов регионов
regions_list = pd.DataFrame(initial_values.region_checklist_data()[1], columns=['region_code'])
regions = initial_values.region_checklist_data()[0]
regions_full = pd.read_csv('Data/regions.csv')
if initial_values.mode == 'demo':
    users_full = pd.read_csv('Data/users_proto.csv')
else:
    users_full = pd.read_csv('Data/users.csv')

def selectall_relese_all_buttons(id_select_all_button, id_release_all_button, options):
    """Обработчик Выбрать все / Снять выбор"""
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]
    full_list = [option["value"] for option in options]
    if id_select_all_button in changed_id:
        selected_values = [option["value"] for option in options]
        return selected_values
    elif id_release_all_button in changed_id:
        selected_values = []
        return selected_values
    return full_list

# готовим event_df заполняем пустые поля с датами и конвертируем поля с датами в формат даты
def get_event_df():
    """чтение csv файла и подготовка уevent_df"""
    events_df = pd.read_csv('Data/events.csv')
    # values - этол для функции fillna - показываем в каких колонках чем заполнить пустые ячейки. '01.01.1970' - будет указанием на то, что здесь было пусто
    values = {"Create_date": '01.01.1970', "Deadline_date": '01.01.1970', "Close_date": '01.01.1970', "Plan_date": '01.01.1970'}
    events_df.fillna(value=values, inplace=True)

    date_column_list = ['Create_date', 'Deadline_date', 'Close_date', 'Plan_date']
    # конвертируем даты в даты
    for date_column in date_column_list:
        events_df.loc[:, date_column] = pd.to_datetime(events_df[date_column], infer_datetime_format=True, format='%d.%m.%Y')
        events_df[date_column] = events_df[date_column].apply(lambda x: datetime.date(x.year, x.month, x.day))
    #events_df.replace({"Event_status": initial_values.event_status()}, inplace=True)
    #events_df.to_csv('Data/events_df_delete.csv')
    return events_df
region_list_names = pd.read_csv('Data/regions.csv')
def planned_graph_prep(planned_df, include_zeros_checkbox_value):
    """данные для графика запланированных встреч по регионам"""
    planned_df_groupped_by_users = planned_df.groupby(['Plan_date', 'user_code']).size().to_frame('size').reset_index()
    planned_df_groupped_by_users_sum = planned_df_groupped_by_users.groupby(['user_code'], as_index=False)[
        'size'].sum()
    planned_users_dist_graph_data_prep_df = pd.merge(planned_df_groupped_by_users_sum, users_full, on='user_code', how='left')
    planned_users_dist_graph_data_prep_df.rename(columns={'size': 'Planned_qty'}, inplace=True)

    planned_users_dist_graph_data_prep_df.fillna(0, inplace=True)
    planned_users_dist_graph_data_prep_df.sort_values(['Planned_qty'], inplace=True)

    # создаем выборку для построения графика по регионам
    planned_df_groupped_by_regions = planned_df.groupby(['Plan_date', 'region_code']).size().to_frame('size').reset_index()
    # получаем список регионов и количество запланированных встреч
    planned_df_groupped_by_regions_sum = planned_df_groupped_by_regions.groupby(['region_code'], as_index=False)[
        'size'].sum()

    # planned_oblast_dist_graph_data_prep_df - это список - области  - запланированные встречи
    planned_oblast_dist_graph_data_prep_df = pd.merge(planned_df_groupped_by_regions_sum, regions_list, on='region_code',
                                                      how='left')
    planned_oblast_dist_graph_data_prep_df.rename(columns={'size': 'Planned_qty'}, inplace=True)
    planned_oblast_dist_graph_data_prep_df.fillna(0, inplace=True)
    planned_oblast_dist_graph_data_prep_df.sort_values(['Planned_qty'], inplace=True)

    planned_oblast_dist_graph_data_prep_df_with_region_names = pd.merge(planned_oblast_dist_graph_data_prep_df, region_list_names, on = 'region_code', how='left')

    if include_zeros_checkbox_value:
        oblast_dist_prep_graph_data_df = planned_oblast_dist_graph_data_prep_df_with_region_names

    else:
        oblast_dist_prep_graph_data_df = planned_oblast_dist_graph_data_prep_df_with_region_names.loc[planned_oblast_dist_graph_data_prep_df_with_region_names['Planned_qty']>0]

    return oblast_dist_prep_graph_data_df, planned_users_dist_graph_data_prep_df

def closed_graph_prep(closed_df, include_zeros_checkbox_value):
    """подготовка данных для графика завершенных встреч. [0] отдает по регионам, [1] отдает по юзерам"""

    # На вход получили closed_df - это выборка из events по дате заверщения
    closed_df_groupped_by_users = closed_df.groupby(['Close_date', 'user_code']).size().to_frame('size').reset_index()

    closed_df_groupped_by_users_sum = closed_df_groupped_by_users.groupby(['user_code'], as_index=False)['size'].sum()
    closed_users_dist_graph_data_prep_df = pd.merge(closed_df_groupped_by_users_sum, users_full, on='user_code', how='left')
    closed_users_dist_graph_data_prep_df.rename(columns={'size': 'Closed_qty'}, inplace=True)
    closed_users_dist_graph_data_prep_df.fillna(0, inplace=True)
    closed_users_dist_graph_data_prep_df.sort_values(['Closed_qty'], inplace=True)

    # готовим данные для завершенных ивентов по регионам
    closed_df_groupped_by_regions = closed_df.groupby(['Close_date', 'region_code']).size().to_frame('size').reset_index()

    closed_df_groupped_by_regions_sum = closed_df_groupped_by_regions.groupby(['region_code'], as_index=False)['size'].sum()

    closed_oblast_dist_graph_data_prep_df = pd.merge(closed_df_groupped_by_regions_sum, regions_list, on='region_code',
                                                     how='left')

    closed_oblast_dist_graph_data_prep_df.rename(columns={'size': 'Closed_qty'}, inplace=True)

    closed_oblast_dist_graph_data_prep_df.fillna(0, inplace=True)
    closed_oblast_dist_graph_data_prep_df.sort_values(['Closed_qty'], inplace=True)
    closed_oblast_dist_graph_data_prep_df_with_region_names = pd.merge(closed_oblast_dist_graph_data_prep_df,
                                                                        region_list_names, on='region_code', how='left')
    if include_zeros_checkbox_value:
        oblast_dist_closed_graph_data_df = closed_oblast_dist_graph_data_prep_df_with_region_names

    else:
        oblast_dist_closed_graph_data_df = closed_oblast_dist_graph_data_prep_df_with_region_names.loc[
            closed_oblast_dist_graph_data_prep_df_with_region_names['Closed_qty'] > 0]

    return oblast_dist_closed_graph_data_df, closed_users_dist_graph_data_prep_df

# просроченные. Если статус не равен "Завершенная" и дата планиварования раньше текущей даты
def overdue_graph_prep(overdue_meetings_date_selected_df, include_zeros_checkbox_value):
    # Выбираем строки в которых статус не равен "завершенный"
    #overdue_meetings_date_selected_df.to_csv('Data/overdue_before_selected_delete.csv')
    overdue_selected = overdue_meetings_date_selected_df.loc[overdue_meetings_date_selected_df['Event_status'].isin([1,2])]
    overdue_df_groupped_by_users = overdue_selected.groupby(['Plan_date', 'user_code']).size().to_frame(
        'size').reset_index()
    overdue_df_groupped_by_users_sum = overdue_df_groupped_by_users.groupby(['user_code'], as_index=False)[
        'size'].sum()
    overdue_users_dist_graph_data_prep_df = pd.merge(overdue_df_groupped_by_users_sum, users_full, on='user_code',
                                                    how='left')
    overdue_users_dist_graph_data_prep_df.rename(columns={'size': 'Overdue_qty'}, inplace=True)
    overdue_users_dist_graph_data_prep_df.fillna(0, inplace=True)
    overdue_users_dist_graph_data_prep_df.sort_values(['Overdue_qty'], inplace=True)



    overdue_df_groupped_by_regions = overdue_selected.groupby(['Plan_date', 'region_code']).size().to_frame('size').reset_index()
    overdue_df_groupped_by_regions_sum = overdue_df_groupped_by_regions.groupby(['region_code'], as_index=False)['size'].sum()
    overdue_oblast_dist_graph_data_prep_df = pd.merge(regions_list, overdue_df_groupped_by_regions_sum, on='region_code',
                                                     how='left')
    overdue_oblast_dist_graph_data_prep_df.rename(columns={'size': 'Overdue_qty'}, inplace=True)
    overdue_oblast_dist_graph_data_prep_df.fillna(0, inplace=True)
    overdue_oblast_dist_graph_data_prep_df.sort_values(['Overdue_qty'], inplace=True)
    overdue_oblast_dist_graph_data_prep_df_with_region_names = pd.merge(overdue_oblast_dist_graph_data_prep_df,
                                                                       region_list_names, on='region_code', how='left')
    if include_zeros_checkbox_value:
        oblast_dist_overdue_graph_data_df = overdue_oblast_dist_graph_data_prep_df_with_region_names
    else:
        oblast_dist_overdue_graph_data_df = overdue_oblast_dist_graph_data_prep_df_with_region_names.loc[
            overdue_oblast_dist_graph_data_prep_df_with_region_names['Overdue_qty'] > 0]
    return oblast_dist_overdue_graph_data_df, overdue_users_dist_graph_data_prep_df

def cut_df_by_dates_interval(df, date_field_name, start_date, end_date):
    start_date = start_date
    end_date = end_date
    after_start_date = df.loc[:, date_field_name] >= start_date
    before_end_date = df.loc[:, date_field_name] <= end_date
    between_two_dates = after_start_date & before_end_date
    result_df = df.loc[between_two_dates]
    return result_df

def query_selections(df):
    """query_selections - это выборки списков кодов регионов и пользователей"""
    # events_df_temp = df.loc[df['region_code']>0]
    events_df_temp = df
    region_code_full_list = events_df_temp['region_code']
    region_code_unique = pd.DataFrame(region_code_full_list.unique(), columns=['region_code'])

    users_full_list = df['user_code']
    users_unique = pd.DataFrame(users_full_list.unique(), columns=['user_code'])
    users_unique.sort_values('user_code', ignore_index = True)
    return region_code_unique, users_unique

def get_unique_region(planned_selections, closed_selections, overdue_selections):
    """получаем данные для чек-боксов регионов"""
    # склеиваем списки регионов
    region_list_planned = planned_selections['region_code']
    region_list_closed = closed_selections['region_code']
    region_list_overdue = overdue_selections['region_code']
    regions_concat_list = pd.concat([region_list_planned, region_list_closed, region_list_overdue], ignore_index=True)
    regions_unique_list = pd.DataFrame(regions_concat_list.unique(), columns=['region_code'])
    # left join кодов регионов и наименований регионов
    regions_with_names = pd.merge(regions_unique_list, regions_full, on='region_code', how='left')
    regions_with_names.sort_values('region_name', inplace=True)
    region_checklist_data = []
    region_list = []
    for index, row in regions_with_names.iterrows():
        dict_temp = {}
        dict_temp['label'] = " " + row['region_name']
        dict_temp['value'] = row['region_code']
        region_checklist_data.append(dict_temp)
        region_list.append(row['region_code'])
    return region_checklist_data, region_list

def check_user_in_region(a, b):
  return not set(a).isdisjoint(b)

def get_unique_users(planned_selections, closed_selections, overdue_selections, region_list_value, managers_from_checklist):
    """получаем данные для чек-боксов пользователей"""

    users_list_planned = planned_selections['user_code']
    users_list_closed = closed_selections['user_code']
    users_list_overdue = overdue_selections['user_code']
    users_concat_list = pd.concat([users_list_planned, users_list_closed, users_list_overdue], ignore_index=True)
    users_unique_list = pd.DataFrame(users_concat_list.unique(), columns=['user_code'])

    # users_regions_df - код юзера - список регионов
    users_regions_df = initial_values.get_users_regions_df()


    # region_list - список регионов, выбранных в фильтрах.

    region_list = region_list_value

    # нужно ответить на вопрос есть ли юзеры в списке users_unique_list в выбранных регионах
    # джойним users_unique_list с users_regions_df

    users_unique_list_with_regions = pd.merge(users_unique_list, users_regions_df, on='user_code', how='left')

    user_list_cut_by_regions = []
    for index, row in users_unique_list_with_regions.iterrows():
        a = row['regions_list']
        b = region_list
        if check_user_in_region(a, b):
            user_list_cut_by_regions.append(row['user_code'])


    user_list_cut_by_regions_df = pd.DataFrame(user_list_cut_by_regions, columns=['user_code'])

    users_with_names = pd.merge(user_list_cut_by_regions_df, users_full, on='user_code', how='left')

    users_with_names.sort_values('Name', inplace=True)

    users_checklist_data = []
    users_list = []
    for index, row in users_with_names.iterrows():
        dict_temp = {}
        dict_temp['label'] = " " + str(row['Name']) + ', ' + str(row['Position'])
        dict_temp['value'] = row['user_code']
        users_checklist_data.append(dict_temp)
        users_list.append(row['user_code'])

    return users_checklist_data, user_list_cut_by_regions

def prepare_meetings_data(df, select_meeting_type):
    """данные для построения таблицы со встречами"""
    # сначала фильтруем строки из исходных таблиц
    df_filtered = df.loc[df['Event_status'].isin(select_meeting_type)]
    event_status_dict = {1: "Запланирована", 2: "Просрочена", 3: "Завершена"}
    df_filtered['status_name'] = df_filtered['Event_status'].map(event_status_dict)
    event_table_list = []
    for index, row in df_filtered.iterrows():
        temp_dict = {}
        link_text = str(row['event_id']) + '. ' + str(row['Description'])

        temp_dict['Описание'] = [html.A(html.P(link_text), href=row['event_url'], target="_blank")]
        temp_dict['Клиент'] = str(row['Customer_name']) + ', ' + str(row['Region_name'])
        temp_dict['Ответственный'] = row['Name']
        temp_dict['Статус встречи'] = row['status_name']
        plan_date = row['Plan_date'].strftime("%d.%m.%Y")
        if plan_date == '01.01.1970':
            temp_dict['Дата планирования'] = ' '
        else:
            temp_dict['Дата планирования'] = plan_date
        close_date = row['Close_date'].strftime("%d.%m.%Y")
        if close_date == '01.01.1970':
            temp_dict['Дата завершения'] = ' '
        else:
            temp_dict['Дата завершения'] = close_date

        temp_dict['Комментарий при завершении'] = row['Close_comment']



        event_table_list.append(temp_dict)

    result_df = pd.DataFrame(event_table_list)


    return result_df






# в одной колонке - категория, в другой - количество встреч
# считаем количество запланированных встреч в дату.
#def events_grapf_prep(planned_df, closed_df, include_zeros_checkbox_value):
# def events_grapf_prep(planned_df, closed_df):
#     # planned_df_groupped - группируем по дате Plan_date и считаем сколько строк попало в выборку, начиная с сегодняшнего дня и в будущее
#     #planned_df_groupped = planned_df.groupby('Plan_date').size().to_frame('size').reset_index()
#     #planned_qty = planned_df_groupped.loc[:, 'size'].sum()
#     #result_list_for_df = []
#     #planned_record = {'category': 'Запланировано', 'value': planned_qty}
#     #result_list_for_df.append(planned_record)
#     #closed_df_groupped = closed_df.groupby('Close_date').size().to_frame('size').reset_index()
#     #closed_qty = closed_df_groupped.loc[:, 'size'].sum()
#     #closed_record = {'category': 'Завершено', 'value': closed_qty}
#     #result_list_for_df.append(closed_record)
#     #df_graph = pd.DataFrame(result_list_for_df)
#
#     # создаем выборку для построения графика по регионам
#     planned_df_groupped_by_regions = planned_df.groupby(['Plan_date', 'Oblast']).size().to_frame('size').reset_index()
#     # получаем список регионов и количество запланированных встреч
#     planned_df_groupped_by_regions_sum = planned_df_groupped_by_regions.groupby(['Oblast'], as_index=False)['size'].sum()
#
#     # получаем список регионов
#     regions_list = pd.DataFrame(initial_values.region_checklist_data()[1], columns=['Oblast'])
#
#     # planned_oblast_dist_graph_data_prep_df - это список - области  - запланированные встречи
#     planned_oblast_dist_graph_data_prep_df = pd.merge(regions_list, planned_df_groupped_by_regions_sum, on='Oblast', how='left')
#     planned_oblast_dist_graph_data_prep_df.rename(columns = {'size': 'Planned_qty'}, inplace = True)
#     planned_oblast_dist_graph_data_prep_df.fillna(0, inplace=True)
#     planned_oblast_dist_graph_data_prep_df.sort_values(['Planned_qty'], inplace = True)
#
#     # готовим данные для завершенных ивентов
#     closed_df_groupped_by_regions = closed_df.groupby(['Close_date', 'Oblast']).size().to_frame('size').reset_index()
#     closed_df_groupped_by_regions_sum = closed_df_groupped_by_regions.groupby(['Oblast'], as_index=False)['size'].sum()
#     closed_oblast_dist_graph_data_prep_df = pd.merge(regions_list, closed_df_groupped_by_regions_sum, on='Oblast', how='left')
#     closed_oblast_dist_graph_data_prep_df.rename(columns={'size': 'Closed_qty'}, inplace=True)
#     closed_oblast_dist_graph_data_prep_df.fillna(0, inplace=True)
#     closed_oblast_dist_graph_data_prep_df.sort_values(['Closed_qty'], inplace=True)
#
#
#     #oblast_dist_graph_data_prep_df = pd.merge(oblast_dist_graph_data_prep_df, closed_df_groupped_by_regions_sum, on='Oblast', how='left')
#     #oblast_dist_graph_data_prep_df.rename(columns={'size': 'Closed_qty'}, inplace=True)
#     #oblast_dist_graph_data_prep_df.fillna(0, inplace=True)
#
#     # проверяем. Если в чек-боксе "Показать регионы с нулями" есть выбранное значение, то отдаем датафрейм с нулями.
#     # Если чек-бокс пустой, то отдаем датафрем без нулей
#
#     #if include_zeros_checkbox_value:
#
#     #oblast_dist_graph_data_df = oblast_dist_graph_data_prep_df.sort_values(by='Closed_qty', ascending=False, ignore_index = True)
#     #oblast_dist_graph_data_df_without_zeros_in_closed_events = oblast_dist_graph_data_df.loc[oblast_dist_graph_data_df['Closed_qty']>0]
#     # if include_zeros_checkbox_value:
#     #     oblast_dist_graph_data__result_df = oblast_dist_graph_data_df
#     # else:
#     #     oblast_dist_graph_data__result_df = oblast_dist_graph_data_df_without_zeros_in_closed_events
#
#     return closed_oblast_dist_graph_data_prep_df, planned_oblast_dist_graph_data_prep_df


# группируем. 1. по запланированной дате
# today = datetime.datetime.now().date()
# planned_meetings_today_df = events_df.loc[events_df['Plan_date'] == today]
# planned_meetings_today_groupped_df = planned_meetings_today_df.groupby('Plan_date').size().to_frame('size').reset_index()
