import json
import requests
import time

url = 'https://api-sandbox.direct.yandex.ru/live/v4/json/'
token = ''


def json_encode(data):
    return json.dumps(data, ensure_ascii=False).encode('utf-8')


def create_report(keywords, regions):
    data = {
        'method': 'CreateNewWordstatReport',
        'token': token,
        'param': {
            'Phrases': keywords,
            'GeoID': regions
        }
    }
    report_id = requests.post(url, data=json_encode(data)).json()['data']
    return report_id


def get_report_list():
    data = {
        'method': 'GetWordstatReportList',
        'token': token
    }
    response = requests.post(url, data=json_encode(data)).json()['data']
    return response


def report_availability_check(report_id):
    report_list = get_report_list()
    for report in report_list:
        if report['ReportID'] == report_id:
            return report['StatusReport']


def get_report(report_id):
    while report_availability_check(report_id) != 'Done':
        time.sleep(2)
    data = {
        'method': 'GetWordstatReport',
        'token': token,
        'param': report_id
    }
    response = requests.post(url, data=json_encode(data)).json()['data'][0]
    del response['SearchedAlso']
    del response['Phrase']
    # TODO: make file name intelligible (Region Name [Region ID])
    file = open('report.json', 'w', encoding="utf-8")
    file.write(json.dumps(response, sort_keys=True, indent=4))
    file.close()


def clear_report_list():
    report_list = get_report_list()
    for report in report_list:
        delete_report(report['ReportID'])


def delete_report(report_id):
    data = {
        'method': 'DeleteWordstatReport',
        'token': token,
        'param': report_id
    }
    status = requests.post(url, data=json_encode(data)).json()['data']
    return status


def get_regions():
    data = {
        'method': 'GetRegions',
        'token': token
    }
    regions = requests.post(url, json_encode(data)).json()['data']
    return regions


def selection_of_regions(list_of_parent_region_id, nesting_level=0):
    regions = get_regions()
    regions_list = []
    for region in regions:
        try:
            list_of_parent_region_id.index(region['ParentID'])
        except ValueError:
            continue
        regions_list.append(region['RegionID'])
    scope = 0
    while scope < nesting_level:
        regions_list = selection_of_regions(regions_list)
        scope = scope + 1
    return regions_list


def create_regions_list():
    file = open('regions.json', 'w', encoding="utf-8")
    file.write(json.dumps(get_child_regions(get_regions(), 0), sort_keys=True, indent=4))
    file.close()


def get_child_regions(regions_list, parent_id):
    child_regions = []
    for region in regions_list:
        if region['ParentID'] == parent_id:
            children = get_child_regions(regions_list, region['RegionID'])
            if children:
                region['children'] = children
            child_regions.append(region)
    return child_regions

# TODO: function for create dict from region ID - region Name
