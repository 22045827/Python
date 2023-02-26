import datetime
import requests
import time
import os
import re

time_start = time.time()

aid_list = []
cid_list = []
name_list = []

ep = "21315"  # 改
referer = "https://www.bilibili.com/bangumi/play/ss1175?from_spmid=666.25.series.0&from_outer_spmid=333.337.0.0"  # 改

season_url = f"https://api.bilibili.com/pgc/view/web/season?ep_id={ep}"

cookie = "buvid3=E600B3E7-94A6-0F6D-38C3-7918DE8D532E23510infoc; b_nut=1673225523; CURRENT_FNVAL=4048; _uuid=6C383F97-A356-13B4-D46D-A97943FFF1010624176infoc; rpdid=|(k|lmYuJY~R0J'uY~JkkllkR; i-wanna-go-back=-1; buvid_fp_plain=undefined; header_theme_version=CLOSE; buvid4=E873D30E-AED2-2FFF-62D0-F54F4C78D20724099-023010908-bRruLdvSkHdjl8Al%2Fil6Gw%3D%3D; fingerprint=2136a27f8406ce22347ede8a9cb9aff8; nostalgia_conf=-1; buvid_fp=2136a27f8406ce22347ede8a9cb9aff8; bp_video_offset_2011380463=765734339159785500; DedeUserID=1324964282; DedeUserID__ckMd5=e45cc368bde36ee2; msource=pc_web; deviceFingerprint=65e0a89fcd1c3e943c460e16d7084099; CURRENT_QUALITY=112; bsource=search_bing; PVID=1; bp_video_offset_1324964282=766584708298440800; SESSDATA=659cfca8%2C1692885672%2C0d5c9%2A22; bili_jct=e45feb0ef259c642c3470958b2d8867d; sid=8q1d11ac; innersign=0; b_ut=5; home_feed_column=4; b_lsid=183E1533_1868B1FB035"
print("referer:", referer)
playurl_header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
    "cookie": cookie,
    "referer": referer
}

download_header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
    "referer": referer
}

html = requests.get(season_url)
title = int(html.json()['result']['new_ep']['title'])  # 集数
name = html.json()['result']['season_title']  # 番剧名称
print("%d集" % title)
print(name)

path = f"./{name}/audio"
if not os.path.exists(path):
    os.makedirs(path)

path = f"./{name}/video"
if not os.path.exists(path):
    os.makedirs(path)

# 将返回的数据以json格式输出
# 定位到eqisodes下，并转换为str方便使用re模块获取
episodes = html.json()['result']['episodes']
str_episodes = str(episodes)

name_obj = re.compile(rf"'share_copy': '《.*?》(?P<name>.*?)',")  # 番剧话名
aid_obj = re.compile(r"'aid': (?P<aaid>.*?),", re.S)
cid_obj = re.compile(r"'cid': (?P<ccid>.*?),", re.S)
# eq_id_obj = re.compile(r"'id': (?P<id>.*?),", re.S)

name_iter = name_obj.finditer(str_episodes)
aid_iter = aid_obj.finditer(str_episodes)
cid_iter = cid_obj.finditer(str_episodes)
# eqid_iter = eq_id_obj.finditer(str_episodes)
# 使用迭代器，并输出到列表中
for Name in name_iter:
    Name = Name.group("name")
    name_list.append(Name)
    # print ("name",Name)

for Aid in aid_iter:
    aaid = Aid.group("aaid")
    aid_list.append(aaid)
    # print ("aid",aaid)

for Cid in cid_iter:
    ccid = Cid.group("ccid")
    cid_list.append(ccid)
    # print ("cid",ccid)

# for id in eqid_iter:
#     eqid = id.group("id")
#     id_list.append(eqid)
#     # print ("id",eqid)
print(name_list)

playurl = f"https://api.bilibili.com/pgc/player/web/playurl?support_multi_audio=true&avid={aid_list[0]}&cid={cid_list[0]}&qn=112&fnver=0&fnval=4048&fourk=1&ep_id={ep}&from_client=BROWSER&drm_tech_type=2"
# print ("playurl:",playurl)
playurl_html = requests.get(playurl, headers=playurl_header)
# print (playurl_html.json())
playurl_audio_json = playurl_html.json()['result']['dash']['audio']
playurl_video_json = playurl_html.json()['result']['dash']['video']
str_playurl_audio = str(playurl_audio_json)
str_playurl_video = str(playurl_video_json)

obj = re.compile(r"'base_url': '(?P<url>.*?)',", re.S)

baseurl_audio = obj.findall(str_playurl_audio)[0]
baseurl_video = obj.findall(str_playurl_video)[0]
# print(f"{name_title}(audio)", baseurl_audio)
# print(f"{name_title}(video)", baseurl_video)
print(f"解析完成\n{name}开始下载")
# 视频
with open(f"{name}/video/{name}.flv", mode="wb") as f:
    f.write(requests.get(baseurl_video, headers=download_header).content)
print(f"{name}.flv下载完成")

# 音频
with open(f"{name}/audio/{name}.aac", mode="wb") as f:
    f.write(requests.get(baseurl_audio, headers=download_header).content)
print(f"{name}.acc下载完成")

playurl_html.close()

time_end = time.time()
time_sum = (time_end - time_start)
print(f"执行程序总用时{time_sum}s,")

html.close()
