import pandas as pd

def region_checklist_data():
    regions_df = pd.read_csv('Data/regions.csv')
    region_checklist_data = []
    region_list = []
    for index, row in regions_df.iterrows():
        dict_temp = {}
        dict_temp['label'] = " " + row[0]
        dict_temp['value'] = row[0]
        region_checklist_data.append(dict_temp)
        region_list.append(row[0])
    return region_checklist_data, region_list


def managers_checklist_data():
    managers_df = pd.read_csv('Data/managers.csv')
    managers_checklist_data = []
    for index, row in managers_df.iterrows():
        dict_temp = {}
        dict_temp['label'] = row[0]
        dict_temp['value'] = row[0]
        managers_checklist_data.append(dict_temp)
    return managers_checklist_data
