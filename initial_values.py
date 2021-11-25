import pandas as pd
import json

#mode = 'actual'
mode = 'demo'

def prepare_events_csv():
    # готовим events.csv
    if mode == 'demo':
        events_df = pd.read_csv('Data/events_demo_source.csv')
    else:
        events_df = pd.read_csv('Data/events_source.csv')

    event_status_dict = {"Активная": 1, "Активная просроченная": 2, "Завершенная": 3}

    # values - этол для функции fillna - показываем в каких колонках чем заполнить пустые ячейки. '01.01.1970' - будет указанием на то, что здесь было пусто
    values = {"Create_date": '01.01.1970', "Deadline_date": '01.01.1970', "Close_date": '01.01.1970', "Plan_date": '01.01.1970'}

    # переименовываем заголовки колонок
    events_df = events_df.rename(columns={
        "ID события":"event_id",
        "Дата создания":"Create_date",
        "Планирование":"Plan_date",
        "Дата завершения":"Close_date",

        "Описание":"Description",
        "Ответственный":"user_code",
        "Завершить не позднее":"Deadline_date",
        "Статус":"Event_status",
        "ID клиента":"Customer_id",
        "Область":"Oblast",
        "ID сделки":"Deal_id",
        "Комментарий при завершении":"Close_comment",
    })
    events_df.fillna(value=values, inplace=True)
    regions_df = pd.read_csv('Data/regions.csv')

    # создаем линк на карточку встречи
    if mode == 'actual':
        main_domen = 'https://rb.bmtechnics.ru/#/'
        url_content = 'planner/events?filter=%7B%22sort%22:%7B%22deadline%22:4%7D,%22where%22:%7B%22connected_approved%22:false,%22type%22:%7B%22task%22:true,%22meeting%22:true%7D,%22priority%22:%7B%22high%22:true,%22normal%22:true,%22low%22:true%7D,%22data%22:%7B%22type%22:%22plan%22%7D,%22relation_company%22:%7B%22with%22:true,%22without%22:true%7D,%22relation_deal%22:%7B%22with%22:true,%22without%22:true%7D,%22search%22:%22'
        url_content_end = '%22%7D%7D'

        events_df['event_url'] =  main_domen + url_content + events_df['event_id'].map(str) + url_content_end
    else:
        main_domen = 'https://demo.redbridge-arm.com/#'
        url_content = 'planner/events?filter=%7B%22sort%22:%7B%22deadline%22:4%7D,%22where%22:%7B%22connected_approved%22:false,%22type%22:%7B%22task%22:true,%22meeting%22:true%7D,%22priority%22:%7B%22high%22:true,%22normal%22:true,%22low%22:true%7D,%22data%22:%7B%22type%22:%22plan%22%7D,%22relation_company%22:%7B%22with%22:true,%22without%22:true%7D,%22relation_deal%22:%7B%22with%22:true,%22without%22:true%7D,%22search%22:%22'
        url_content_end = '%22%7D%7D'

        events_df['event_url'] = main_domen + url_content + str(13) + url_content_end


    # region_dict нужен для того чтобы вставить в таблицу event колонку с кодом региона. Аналог ВПР
    region_dict = {}
    for index, row in regions_df.iterrows():
        region_dict[row['region_name']] = row['region_code']


    events_df['region_code'] = events_df['Oblast'].map(region_dict)

    events_df.fillna(value={"region_code": 0, 'Customer_id': -1, 'Deal_id': 0}, inplace=True)
    events_df = events_df.astype({"region_code": int, 'Customer_id': int, 'Deal_id': int})
    events_df_selected = events_df.loc[:, ['event_id', 'event_url', 'Create_date', 'Description', 'user_code', 'Deadline_date', 'Event_status', 'Close_date', 'Customer_id', 'Deal_id', 'Plan_date', 'region_code', 'Close_comment']]
    events_df_selected.replace({"Event_status": event_status_dict}, inplace=True)
    # конвертируем даты в даты
    # date_column_list = ['Create_date', 'Deadline_date', 'Close_date', 'Plan_date']
    # for date_column in date_column_list:
    #     events_df.loc[:, date_column] = pd.to_datetime(events_df[date_column], infer_datetime_format=True, format='%d.%m.%Y')
    #     events_df[date_column] = events_df[date_column].apply(lambda x: datetime.date(x.year, x.month, x.day))

    events_df_selected.to_csv('Data/events.csv')
prepare_events_csv()

def prepare_customers_csv():
    companies_df = pd.read_csv('Data/companies.csv')
    companies_df = companies_df.rename(columns={
            "ID":"Customer_id",
            "Наименование":"Customer_name",
            "Область": "Region_name",
        })
    companies_selected_df = companies_df.loc[:, ['Customer_id', 'Customer_name', 'Region_name']]
    companies_selected_df.to_csv('Data/companies_selected.csv')


def region_checklist_data():
    # нам нужно получить уникальный список регионов, которые есть в выборке events
    events = pd.read_csv('Data/events.csv')
    region_codes_from_events = pd.DataFrame(events['region_code'].unique(), columns=['region_code'])
    #print(region_codes_from_events)
    regions_df = pd.read_csv('Data/regions.csv')
    # лефт джойном получаем коды и имена регионов
    regions_df = pd.merge(region_codes_from_events, regions_df, on='region_code', how='left')
    regions_df_actual = regions_df.loc[ 1:,:]
    #print(regions_df_actual)
    #print(regions_df)
    region_checklist_data = []
    region_list = []
    for index, row in regions_df_actual.iterrows():
        dict_temp = {}
        dict_temp['label'] = " " + row['region_name']
        dict_temp['value'] = row['region_code']
        region_checklist_data.append(dict_temp)
        region_list.append(row['region_code'])
    return region_checklist_data, region_list
#print(region_checklist_data()[0])

#  собираем данные о менеджеерах и регионах из events
def prepare_users_list():
    events_df = pd.read_csv('Data/events.csv')
    list_of_users = events_df.loc[:, ['user_code']]
    list_of_unique_users = pd.DataFrame(list_of_users['user_code'].unique(), columns=['user_code'])
    result_df_list = []
    for index, row_user_code in list_of_unique_users.iterrows():
        dict_temp = {}
        user_code = row_user_code['user_code']
        temp_df = events_df.loc[events_df['user_code']==user_code]
        user_region_list = []
        for index, row_events_selection in temp_df.iterrows():
            region_code = row_events_selection['region_code']
            if region_code !=0 and region_code not in user_region_list:
                user_region_list.append(region_code)
        dict_temp['user_code'] = user_code
        dict_temp['regions_list'] = user_region_list
        result_df_list.append(dict_temp)
    user_region_df = pd.DataFrame(result_df_list)
    user_region_df.to_csv('Data/user_regions.csv')

    return list_of_unique_users

prepare_users_list()

def get_users_regions_df():
    if mode == 'actual':
        users_regions_df= pd.read_csv('Data/user_regions.csv')
    else:
        users_regions_df = pd.read_csv('Data/user_regions_demo.csv')
    users_regions_df['regions_list'] = users_regions_df['regions_list'].apply(lambda x: json.loads(x))
    return users_regions_df
#selected_regions = [36, 47]
#selected_user_region_list = test_df['regions_list'][5]

def check_user_in_region(a, b):
  return not set(a).isdisjoint(b)

def filter_users_by_regions(user_list, selected_region_list):
    users_regions_df = get_users_regions_df()

    user_list = user_list



#print(func(selected_regions, selected_user_region_list))
# готовим список пользователей
users_df = pd.read_csv('Data/users.csv')
def managers_checklist_data():
    managers_checklist_data = []
    managers_list = []
    for index, row in users_df.iterrows():
        dict_temp = {}
        dict_temp['label'] = row[0]
        dict_temp['value'] = row[0]
        managers_checklist_data.append(dict_temp)
    return managers_checklist_data
