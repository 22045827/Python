import datetime
import requests
import time
import os
import re


def get_html(url):
    ep = re.search(r"\d+", url)
    ep = ep.group()
    print(ep)
    season_url = f"https://api.bilibili.com/pgc/view/web/season?ep_id={ep}"
    print(season_url)
    html = requests.get(season_url)
    html.close()
    return html


def basic_data(text):
    aid_list = []
    cid_list = []
    id_list = []
    name_list = []

    name = text.json()['result']['season_title']  # 番剧名称 *徒然喜欢你
    episodes = text.json()['result']['episodes']
    str_episodes = str(episodes)

    name_obj = re.compile(rf"'share_copy': '《.*?》(?P<name>.*?)',")  # 番剧话名
    aid_obj = re.compile(r"'aid': (?P<aaid>.*?),", re.S)
    cid_obj = re.compile(r"'cid': (?P<ccid>.*?),", re.S)
    eq_id_obj = re.compile(r"'id': (?P<id>.*?),", re.S)

    name_iter = name_obj.finditer(str_episodes)  # 第1话_告白
    aid_iter = aid_obj.finditer(str_episodes)  # 11884237
    cid_iter = cid_obj.finditer(str_episodes)  # 19620874
    eqid_iter = eq_id_obj.finditer(str_episodes)  # 113292
    # 使用迭代器，并输出到列表中
    for Name in name_iter:
        Name = Name.group("name").replace(" ", "_")
        name_list.append(Name)
        # print("name", Name)

    for Aid in aid_iter:
        aaid = Aid.group("aaid")
        aid_list.append(aaid)
        # print("aid", aaid)

    for Cid in cid_iter:
        ccid = Cid.group("ccid")
        cid_list.append(ccid)
        # print("cid", ccid)

    for id in eqid_iter:
        eqid = id.group("id")
        id_list.append(eqid)
        # print("id", eqid)

    title = len(name_list)  # 12
    print(title)
    return name_list, aid_list, cid_list, id_list, name, title


def gain_video_audio(aid, cid, eq_id, i, referer, name_title):
    cookie = "buvid3=E600B3E7-94A6-0F6D-38C3-7918DE8D532E23510infoc; b_nut=1673225523; CURRENT_FNVAL=4048; _uuid=6C383F97-A356-13B4-D46D-A97943FFF1010624176infoc; rpdid=|(k|lmYuJY~R0J'uY~JkkllkR; i-wanna-go-back=-1; buvid_fp_plain=undefined; header_theme_version=CLOSE; buvid4=E873D30E-AED2-2FFF-62D0-F54F4C78D20724099-023010908-bRruLdvSkHdjl8Al%2Fil6Gw%3D%3D; fingerprint=2136a27f8406ce22347ede8a9cb9aff8; nostalgia_conf=-1; buvid_fp=2136a27f8406ce22347ede8a9cb9aff8; msource=pc_web; deviceFingerprint=65e0a89fcd1c3e943c460e16d7084099; CURRENT_QUALITY=112; bsource=search_bing; innersign=0; b_ut=5; bp_video_offset_1324964282=766872118921003000; CURRENT_PID=eaae7c90-b8f7-11ed-aff8-33718d08905f; b_lsid=5ADDCFB6_186B5D18FFC; home_feed_column=5; PVID=1; SESSDATA=6de4062a%2C1693640160%2Cc3ea8%2A32; bili_jct=07cd148eca2ff2d3077be39ed83f340a; DedeUserID=2011380463; DedeUserID__ckMd5=549c506ccbedbba7; sid=569y7xal; bp_video_offset_2011380463=769824032763674600"
    # print("referer:", referer)
    playurl_header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
        "cookie": cookie,
        "referer": referer
    }
    playurl = f"https://api.bilibili.com/pgc/player/web/playurl?support_multi_audio=true&avid={aid[i]}&cid={cid[i]}&qn=112&fnver=0&fnval=4048&fourk=1&ep_id={eq_id[i]}&from_client=BROWSER&drm_tech_type=2"
    # print ("playurl  ", playurl)
    playurl_html = requests.get(playurl, headers=playurl_header)

    playurl_audio_json = playurl_html.json()['result']['dash']['audio']
    playurl_video_json = playurl_html.json()['result']['dash']['video']
    str_playurl_audio = str(playurl_audio_json)
    str_playurl_video = str(playurl_video_json)

    obj = re.compile(r"'base_url': '(?P<url>.*?)',", re.S)

    baseurl_audio = obj.findall(str_playurl_audio)[0]
    baseurl_video = obj.findall(str_playurl_video)[0]
    # print("(audio)", baseurl_audio)
    # print("(video)", baseurl_video)
    print(f"解析完成\n{name_title}开始下载")

    playurl_html.close()
    return baseurl_audio, baseurl_video


def download_url(audio, video, name_title, name, referer):
    download_header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.50",
        "referer": referer
    }

    video_html = requests.get(video, headers=download_header)

    audio_html = requests.get(audio, headers=download_header)

    # 视频
    with open(f"video/{name}/video/{name_title}.flv", mode="wb") as f:
        f.write(video_html.content)
    print(f"{name_title}.flv下载完成")

    # 音频
    with open(f"video/{name}/audio/{name_title}.aac", mode="wb") as f:
        f.write(audio_html.content)
    print(f"{name_title}.acc下载完成")
    video_html.close()
    audio_html.close()

    return

def video_path(name):
    path = f"./video/{name}/audio"
    if not os.path.exists(path):
        os.makedirs(path)

    path = f"./video/{name}/video"
    if not os.path.exists(path):
        os.makedirs(path)


def main(url_list):
    for u in range(len(url_list)):
        text = get_html(url_list[u])
        name_list, aid_list, cid_list, id_list, name, num = basic_data(text)
        video_path(name)
        for i in range(num):
            circulate_start = datetime.datetime.now()
            n = i + 1  # n是循环次数

            name_title = name_list[i]
            referer = f"https://www.bilibili.com/bangumi/play/ep{id_list[i]}?from_spmid=666.25.episode.0&from_outer_spmid=333.337.0.0"
            audio_url, video_url = gain_video_audio(aid_list, cid_list, id_list, i, referer, name_title)
            download_url(audio_url, video_url, name_title, name, referer)

            circulate_end = datetime.datetime.now()
            circulate_sum = (circulate_end - circulate_start).seconds
            print(f"=========第{n}次循环(circulate)用时{circulate_sum}s==========")
    return


if __name__ == '__main__':
    #  能够输入多个url并下载
    url_list = []
    flag = True
    while flag:
        urls = input("请输入URL:")
        url_list.append(urls)
        question = input("是否继续输入URL(y/n):")
        if question == "y":
            continue
        else:
            break
    main(url_list)
