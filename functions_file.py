import pandas as pd
from dash import callback_context
import datetime
import initial_values

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
        events_df.loc[:, date_column] = pd.to_datetime(events_df[date_column], infer_datetime_format=True)
        events_df[date_column] = events_df[date_column].apply(lambda x: datetime.date(x.year, x.month, x.day))
    return events_df

# в одной колонке - категория, в другой - количество встреч
# считаем количество запланированных встреч в дату.
def events_grapf_prep(planned_df, closed_df, include_zeros_checkbox_value):
    # planned_df_groupped - группируем по дате Plan_date и считаем сколько строк попало в выборку
    planned_df_groupped = planned_df.groupby('Plan_date').size().to_frame('size').reset_index()
    planned_qty = planned_df_groupped.loc[:, 'size'].sum()
    result_list_for_df = []
    planned_record = {'category': 'Запланировано', 'value': planned_qty}
    result_list_for_df.append(planned_record)
    closed_df_groupped = closed_df.groupby('Close_date').size().to_frame('size').reset_index()
    closed_qty = closed_df_groupped.loc[:, 'size'].sum()
    closed_record = {'category': 'Завершено', 'value': closed_qty}
    result_list_for_df.append(closed_record)
    df_graph = pd.DataFrame(result_list_for_df)

    # создаем выборку для построения графика по регионам
    planned_df_groupped_by_regions = planned_df.groupby(['Plan_date', 'Oblast']).size().to_frame('size').reset_index()
    # получаем список регионов и количество запланированных встреч
    planned_df_groupped_by_regions_sum = planned_df_groupped_by_regions.groupby(['Oblast'], as_index=False)['size'].sum().sort_values(by='size', ascending=False, ignore_index = True)
    closed_df_groupped_by_regions = closed_df.groupby(['Close_date', 'Oblast']).size().to_frame('size').reset_index()
    closed_df_groupped_by_regions_sum = closed_df_groupped_by_regions.groupby(['Oblast'], as_index=False)[
        'size'].sum().sort_values(by='size', ascending=False, ignore_index=True)
    # получаем список регионов
    regions_list = pd.DataFrame(initial_values.region_checklist_data()[1], columns=['Oblast'])

    oblast_dist_graph_data_prep_df = pd.merge(regions_list, planned_df_groupped_by_regions_sum, on='Oblast', how='left')
    oblast_dist_graph_data_prep_df.rename(columns = {'size': 'Planned_qty'}, inplace = True)
    oblast_dist_graph_data_prep_df = pd.merge(oblast_dist_graph_data_prep_df, closed_df_groupped_by_regions_sum, on='Oblast', how='left')
    oblast_dist_graph_data_prep_df.rename(columns={'size': 'Closed_qty'}, inplace=True)
    oblast_dist_graph_data_prep_df.fillna(0, inplace=True)

    # проверяем. Если в чек-боксе "Показать регионы с нулями" есть выбранное значение, то отдаем датафрейм с нулями.
    # Если чек-бокс пустой, то отдаем датафрем без нулей

    #if include_zeros_checkbox_value:

    oblast_dist_graph_data_df = oblast_dist_graph_data_prep_df.sort_values(by='Closed_qty', ascending=False, ignore_index = True)
    oblast_dist_graph_data_df_without_zeros_in_closed_events = oblast_dist_graph_data_df.loc[oblast_dist_graph_data_df['Closed_qty']>0]
    if include_zeros_checkbox_value:
        oblast_dist_graph_data__result_df = oblast_dist_graph_data_df
    else:
        oblast_dist_graph_data__result_df = oblast_dist_graph_data_df_without_zeros_in_closed_events

    return df_graph, oblast_dist_graph_data__result_df





def cut_df_by_dates_interval(df, date_field_name, start_date, end_date):
    start_date = start_date
    end_date = end_date
    after_start_date = df.loc[:, date_field_name] >= start_date
    before_end_date = df.loc[:, date_field_name] <= end_date
    between_two_dates = after_start_date & before_end_date
    result_df = df.loc[between_two_dates]
    return result_df


# группируем. 1. по запланированной дате
# today = datetime.datetime.now().date()
# planned_meetings_today_df = events_df.loc[events_df['Plan_date'] == today]
# planned_meetings_today_groupped_df = planned_meetings_today_df.groupby('Plan_date').size().to_frame('size').reset_index()
# print(planned_meetings_today_groupped_df)