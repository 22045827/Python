import requests
import re
from lxml import etree
import xlsxwriter as xw


def get_html(url):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50"
    }
    html = requests.get(url, headers=header)
    html_text = html.text
    str_html_text = str(html_text)
    html.close()
    return str_html_text


#  公交路线 函数 -->  公交路线名，公交路线url
def bus_route_def(text):
    route_url_list = []
    route_name_list = []

    init_search = re.search(r'.*?<table .*?>(?P<search>.*?)</table>', text, re.S)
    table = init_search.group("search")
    #  路线url，路线名
    url_title_obj = re.compile(r'<a href="(?P<bus_url>.*?)" target="_blank" title=".*?">(?P<title>.*?)</a>', re.S)
    url_title_item = url_title_obj.finditer(table)
    for i in url_title_item:
        url_all = i.group("bus_url")
        title_all = i.group("title")
        route_url_list.append(url_all)
        route_name_list.append(title_all)
    le = len(route_url_list)
    return route_name_list, route_url_list, le


#  停靠站点 函数 --> 站点名，站点url
def site_def(url):
    resp = requests.get(url)
    resp_text = resp.text
    str_resp_text = str(resp_text)

    site_name_list = []
    site_url_list = []

    initial_html = re.search(r'<table .*?>(?P<html>.*?)</table>', str_resp_text, re.S)
    html = initial_html.group("html")
    #  站点名
    title_obj = re.compile(r'<a .*?>(?P<title>.*?)</a>', re.S)
    title_item = title_obj.finditer(html)
    for a_title in title_item:
        title = a_title.group("title")
        site_name_list.append(title)
    #  站点url后缀
    site_url_obj = re.compile(r'<a href="(?P<site_url>.*?)">')
    site_url_item = site_url_obj.finditer(html)
    for i in site_url_item:
        site_url = i.group("site_url")
        site_url_list.append(site_url)

    site_num = len(site_url_list)
    resp.close()
    return site_name_list, site_url_list, site_num


def site_range_def(url):
    resp = requests.get(url)
    resp_text = resp.text
    str_resp_text = str(resp_text)
    site_list = []
    start_time = []
    end_time = []

    site_obj = re.compile(r'<div class="linename">(?P<site_name>.*?)</div>')
    site_item = site_obj.finditer(str_resp_text)
    for i in site_item:
        site = i.group("site_name")
        site_list.append(site)

    time = re.compile(
        r'<span style="float:right;">.*?时间(?P<start>.*?)      &emsp;终点站首末车时间(?P<end>.*?)         </span>',
        re.S)
    time_item = time.finditer(str_resp_text)
    for i in time_item:
        start = i.group("start")
        end = i.group("end")
        start_time.append(start)
        end_time.append(end)
    resp.close()
    return site_list, start_time, end_time


def basic_data_def(html_text, name):
    global data
    savepath = f'{name}.xls'
    print(savepath)
    workbook = xw.Workbook(savepath)
    worksheet1 = workbook.add_worksheet(name=name)
    worksheet1.activate()
    title = ['公交路线', '停靠站点', '站点路线', '起点站首末班车', '终点站首末班车']
    worksheet1.write_row("A1", title)
    route_name, route_url_list, route_num = bus_route_def(html_text)
    r = 2
    for i in range(route_num):
        get_bus_url = f"http://www.gongjiaowang.cn{route_url_list[i]}"
        #  站点url,站点名 函数
        site_name, site_url_list, site_num = site_def(get_bus_url)
        for u in range(site_num):
            get_site_url = f"http://www.gongjiaowang.cn{site_url_list[u]}"
            site_range_name, start_time, end_time = site_range_def(get_site_url)
            for c in range(len(site_range_name)):
                try:
                    data = [route_name[i], site_name[u], site_range_name[c], start_time[c], end_time[c]]
                except IndexError:
                    data = [route_name[i], site_name[u], site_range_name[c]]
                print(data)
                row = 'A' + str(r)
                worksheet1.write_row(row, data)
                r += 1
    workbook.close()


def name_def(text):
    tree = etree.HTML(text)
    xpath_name = tree.xpath('/html/body/div[2]/div[3]/div[2]/div/div/h1/text()')
    str_name = str(xpath_name)
    name_search = re.search(r"'(?P<name>.*?)公交车线路查询'", str_name)
    name = name_search.group("name")
    print(name)
    return name


def main(url):
    html_text = get_html(url)
    name = name_def(html_text)
    basic_data_def(html_text, name)


if __name__ == '__main__':
    url = input("请输入URL:")
    main(url)
