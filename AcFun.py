from lxml import etree
import requests
import re
import os
import aiofiles
import asyncio
import aiohttp
import time

def get_html(url):
    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
        "cookie": "_did=web_147619780D1DFCFD; _did=web_147619780D1DFCFD; td_cookie=4229405045; csrfToken=y4Jg2g5_5J3HYaCSymmMAxoJ; webp_supported=%7B%22lossy%22%3Atrue%2C%22lossless%22%3Atrue%2C%22alpha%22%3Atrue%2C%22animation%22%3Atrue%7D; Hm_lvt_2af69bc2b378fb58ae04ed2a04257ed1=1677373449; lsv_js_player_v2_main=e4d400; stochastic=d3B2enBuMmppcA%3D%3D; acPasstoken=ChVpbmZyYS5hY2Z1bi5wYXNzdG9rZW4ScHZKKxzz342Warz9fdZq_HtRDdULUc9mDPI7ZuPRDpdVRPUoBrm2hC3dVefRQvnBucvKuO0CS8ni08ptuttOBhNThPevK_YsFpA_ODmPwjiW7RSAPWbv_cpqoMJhDHLwjPzJ8OH8ZPyGmyZsZcgZXwAaEpKwM4kzPw4j0kKfbi78eidLwiIg72EsdwojLJtGbq52EcwcTUHHTCIF3aQVQTkBXyS2_D8oBTAB; auth_key=65865944; ac_username=wwwwaae; acPostHint=68160ca05901d625f55aaf2cbd3a27373096; ac_userimg=https%3A%2F%2Fimgs.aixifan.com%2Fstyle%2Fimage%2FdefaultAvatar.jpg; safety_id=AAI9jCRHnHolB3PofOfYDauq; cur_req_id=3498977864EB9B4B_self_30f001aa4c842a398a0f483b47af616b; cur_group_id=3498977864EB9B4B_self_30f001aa4c842a398a0f483b47af616b_0; Hm_lpvt_2af69bc2b378fb58ae04ed2a04257ed1=1677399525"
    }
    html = requests.get(url, headers=header)
    html_text = html.text
    tree = etree.HTML(html_text)
    result = tree.xpath('/html/body/script[7]/text()')
    str_result = str(result).replace('\\', '')

    last_title = url.split('_')[-1]
    material_url_search = re.search(rf"(?P<material_url>.*?){last_title}", url)
    material_url = material_url_search.group("material_url")
    html.close()
    return str_result, material_url

def m3u8_url_def(str_result):
    m3u8_url_search = re.search(r'"backupUrl":(?P<m3u8_url>.*?),', str_result).group("m3u8_url")
    m3u8_url = m3u8_url_search.replace('["', '').replace('"]', '')
    return m3u8_url

def bangumiList_def(str_result):
    bangumiList_obj = re.compile(r"window.bangumiList = (?P<bangumiList>.*?);nn        window.likeDomain", re.S)
    bangumiList = bangumiList_obj.findall(str_result)
    str_bangumiList = str(bangumiList)
    return str_bangumiList

def itemid_title(bangumiList):
    itemid_lists = []
    title_lists = []
    itemid_obj = re.compile(r'"itemId":(?P<itemid>.*?),')  # 1707217
    title_obj = re.compile(r'"title":"(?P<title>.*?)"')  # 富士山与咖喱面
    itemid_iter = itemid_obj.finditer(bangumiList)
    title_iter = title_obj.finditer(bangumiList)
    for Itemid in itemid_iter:
        itemid = Itemid.group("itemid")
        itemid_lists.append(itemid)
    for Title in title_iter:
        title = Title.group("title").replace(" ","_")
        title_lists.append(title)
    return itemid_lists, title_lists

# 下载m3u8文件
def download_m3u8_file(url, name):
    m3u8 = requests.get(url)
    with open(name, mode='wb') as f:
        f.write(m3u8.content)
    print (f"{name}下载完成！")
    time.sleep(3)
    return

# 异步获取ts文件地址
async def aio_download(prefix, name, path_name):  # https://tx-safety-video.acfun.cn/mediacloud/acfun/acfun_video/hls/
    tasks = []
    n = 0
    async  with aiohttp.ClientSession() as session:
        async with aiofiles.open(name, mode="r", encoding="utf-8") as f:
            async for line in f:
                if line.startswith("#"):
                    continue
                line = line.strip()
                ts_url = prefix + line
                ts_name = str(n) + '.ts'
                n += 1
                task = asyncio.create_task(download_ts(ts_url, ts_name, session, path_name=path_name))
                tasks.append(task)
            await asyncio.wait(tasks)
    tasks_len = len(tasks)
    return tasks_len

# 异步下载ts文件
async def download_ts(url, name, session, path_name):
    async with session.get(url) as resp:
        async with aiofiles.open(f'Acfun/{path_name}/ts/{name}', mode='wb') as f:
            await f.write(await resp.content.read())
    print (f"{name}下载完成！")

def merge_ts(num,name,title_name):
    ts_list = []
    print (title_name)
    for i in range(num):
        ts = str(i) + '.ts'
        ts_list.append(fr'Acfun\{title_name}\ts\{ts}')
    u = "+".join(ts_list)
    print (u)

    os.system(fr"copy /b {u} Acfun\{title_name}\video\{name}.flv")
    print (f"{name}.flv 合并完毕！！！")
    for s in range(num):
        path = f'./Acfun/{title_name}/ts/{s}.ts'
        if os.path.exists(path):
            os.remove(path)
    print (f"ts文件全部删除成功")

def screen_path(path_name):
    ts_path = f"./Acfun/{path_name}/ts"
    video_path = f"./Acfun/{path_name}/video"

    if not os.path.exists(ts_path):
        os.makedirs(ts_path)
    if not os.path.exists(video_path):
        os.makedirs(video_path)
    print('路径创建成功')
    for i in range(3, 0, -1):
        print("\r现在暂停{}秒！".format(i), end="", flush=True)
        time.sleep(1)
    print("\r结束！")

def circulate_download(url_prefix, item, name, circulate, title_name):
    '''
    1. 循环用的url original_url_prefix + itemid(list)
    2. 解析 ==> 可以用get_html(get_urls)函数
    3. 拿到每个解析的url的m3u8文件地址 ==> 可以用m3u8_url_def(str_result)函数
    4. 下载m3u8文件 ==> 可以用download_m3u8_file(m3u8_url,m3u8_name)函数
    5. 一、ts文件前缀
       二、（异步协程）解析并下载ts文件 ==> 可以用asyncio.run(aio_download(http_prefix,m3u8_name))
    6. 合并ts文件 ==> 可以用merge_ts(num,itemid)
    * 需要参数 original_url_prefix itemid name(title 富士山与咖喱面) --<m3u8_name用>  len(循环计数用)
    '''
    u = 1
    for i in range(circulate):
        #  循环用url
        get_urls = url_prefix + item[i]
        #  解析url
        analysis_result = get_html(get_urls)[0]
        #  拿到m3u8文件地址
        m3u8_url = m3u8_url_def(analysis_result)
        m3u8_name = f"m3u8/{name[i]}_m3u8.txt"
        #  下载m3u8文件
        download_m3u8_file(m3u8_url,m3u8_name)
        #  ts_prefix --> https://tx-safety-video.acfun.cn/mediacloud/acfun/acfun_video/
        ts_prefix = re.search(r'(?P<hls>.*?)hls/.*?', m3u8_url).group("hls")
        #  http_prefix --> https://tx-safety-video.acfun.cn/mediacloud/acfun/acfun_video/hls/ 引用
        http_prefix = ts_prefix + 'hls/'
        num = asyncio.run(aio_download(http_prefix, m3u8_name, title_name))

        gather_name = f"第{u}话_{name[i]}"
        print(gather_name)
        merge_ts(num, gather_name, title_name)

        m3u8_path = f"./m3u8/{name[i]}_m3u8.txt"
        u += 1
        if os.path.exists(path=m3u8_path):
            os.remove(m3u8_path)
            print (f"成功删除{m3u8_name}")

        for i in range(10, 0, -1):
            print("\r现在休息{}秒！".format(i), end="", flush=True)
            time.sleep(1)
        print("\r休息结束！")
        print('===============')
    print ("成功！！！")
    return

def main(url):
    # 解析url
    str_result, original_url_prefix = get_html(url)
    bangumiList = bangumiList_def(str_result)
    name = re.search(r'"bangumiTitle":"(?P<bangumiTitle>.*?)",', bangumiList).group("bangumiTitle").replace(" ","")  # 番剧名如：摇曳露营△
    print (name)
    itemid, title = itemid_title(bangumiList)  # itemid ==> 1707217 title ==> 富士山与咖喱面
    late = len(itemid)  # 计数，循环用参数

    screen_path(name)

    circulate_download(original_url_prefix, itemid, title, late, name)

if __name__ == '__main__':
    # url = "https://www.acfun.cn/bangumi/aa6004596_36188_1759343"
    url = input("url:")
    main(url)
