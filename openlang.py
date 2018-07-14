#coding: utf-8
import requests
import os
from bs4 import BeautifulSoup
import urllib
from urlparse import urlparse
from io import open as iopen
import sys

base_url = "https://openlanguage.com"
host = "openlanguage.com"
headers = {
    'Accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'Accept-Encoding':"gzip, deflate, br",
    'Accept-Language':"en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6",
    'Cache-Control':"max-age=0",
    'Content-Type':"application/x-www-form-urlencoded",
    'Host':host,
    'Origin':base_url,
    'User-Agent':"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36"
}
session = requests.session()


level_map = {'6':"C2-Advanced",'5':"C1-Upper-Intermediate",'4':"B2-Intermediate",
                 '3':"B1-Pre-Intermediate", '2':"A2-Elementary", '1':"A1-Beginner"}

def login(email, password):
    url = 'https://openlanguage.com/accounts/login'
    session.get(url, headers=headers)  # 访问首页产生 cookies
    headers['Referer'] = "https://openlanguage.com/"
    login_url = "https://openlanguage.com/accounts/login"
    postdata = {
        "password": password,
        "is_remember": 1,
        "email": email
    }
    login_resp = session.post(login_url, data=postdata, headers=headers)
    return login_resp.status_code

def list(level):
    page = 1
    total = 0
    while (True):
        list_url = base_url + "/library/learn-english/9/level?academic_level=" + level + "&page=" + str(page)
        resp = session.get(list_url, headers=headers)
        soup = BeautifulSoup(resp.text, 'html.parser')
        li_list = soup.find('div', {'id': "lessonPagination"}).find_all('li')
        li_list.reverse()
        for li in li_list:
            li_text = li.find('a').string
            if li_text == u"Next →":
                total = int(li_list[1].find('a').string)
                break
            else:
                total = int(li_list[0].find('a').string)
                break

        if page > total:
            break

        soup_list = soup.find_all('div', {'class': "col-xs-6", 'style': "margin-bottom: 40px;"})
        for soup_item in soup_list:
            soup_item_a = soup_item.find('a')
            item_url = soup_item_a.get('href')
            item_title = soup_item_a.find('h3').string
            print u"start: page = " + str(page) + u" title = " + item_title
            item(level, item_url, item_title)

        page += 1

def item(level, url, title):

    savePath = level_map[level] + "/" + title
    if not os.path.exists(savePath):
        os.makedirs(savePath)
    url = base_url + url
    parsed_url = urlparse(url)
    paths = parsed_url.path.split('/')
    doc_base_url = base_url + "/" + paths[1] + "/" + paths[2]
    resp = session.get(url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    soup_audio = soup.find('div', {'class':"lesson-audio-button"}).find('a').get('onclick')
    soup_dialogue = soup.find('div', {'class':"lesson-dialogue-button"}).find('a').get('onclick')
    soup_vocab = soup.find('div', {'class':"lesson-vocab-button"}).find('a').get('onclick')
    soup_audio_url = base_url + soup_audio.split("mp3:").pop().split("'")[1]
    soup_dialogue_url = base_url + soup_dialogue.split("mp3:").pop().split("'")[1]
    soup_vocab_url = base_url + soup_vocab.split("mp3:").pop().split("'")[1]
    source = {'audio':soup_audio_url, 'dialogue':soup_dialogue_url, 'vocab':soup_vocab_url}
    downloadMP3(savePath, source)
    downloadDOC(savePath, doc_base_url)
    #exit(0)

def downloadMP3(savePath, source):
    for key, url in source.items():
        filemp3 = savePath.decode('utf-8') + "/" + key.decode('utf-8') + u".mp3"
        r = session.get(url)
        with iopen(filemp3, 'wb') as file:
            file.write(r.content)

def downloadDOC(savePath, doc_base_url):
    dialogue_url = doc_base_url + "/dialogue"
    vocabulary_url = doc_base_url + "/vocabulary"
    culture_url = doc_base_url + "/culture"
    resp = session.get(dialogue_url, headers=headers)
    soup = BeautifulSoup(resp.text, 'html.parser')
    soup_trs = soup.find('div', {'id':"lesson-dialogue"}).find_all('tr')
    full_dialogue = ''
    for row in soup_trs:
        soup_tds = row.find_all('td')
        soup_who = soup_tds[0].string
        soup_what = soup_tds[1].find('div').contents
        soup_what_chinese = soup_tds[1].find('div', {'class':'source-lang'}).string
        content = ''
        for word in soup_what:
            if not isinstance(word.find('span'), int):
                content += word.find('span').string
            else:
                content += word
        sentence = soup_who + "\t\t" + content + "\r\n \t\t" + soup_what_chinese
        full_dialogue += "\r\n" + sentence
    filetxt_dialogue = savePath.decode('utf-8') + "/" + u"dialogue.txt"
    filehtml_vocabulary = savePath.decode('utf-8') + "/" + u"vocabulary.html"
    filehtml_culture = savePath.decode('utf-8') + "/" + u"culture.html"
    with open(filetxt_dialogue, 'w') as f:
        f.write(full_dialogue)
    resp_v = session.get(vocabulary_url, headers=headers)
    resp_c = session.get(vocabulary_url, headers=headers)
    with open(filehtml_vocabulary, 'w') as f:
        f.write(resp_v.text)
    with open(filehtml_culture, 'w') as f:
        f.write(resp_c.text)

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    email = "XXX"
    password = "XXX"
    login(email, password)
    list('4')
