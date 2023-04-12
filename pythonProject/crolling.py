import pymysql  # MySQL 연동 라이브러리
from selenium import webdriver as wd
from selenium.webdriver.chrome.service import Service
import time
from bs4 import BeautifulSoup

melon_url = 'https://www.melon.com/chart/index.htm'
lyrics_url = 'https://www.melon.com/song/detail.htm?songId='
chrome_path = "C:\chromedriver\chromedriver_win32\chromedriver.exe"

rank_list = [] #
song_no_list = [] #
title_list = [] #
singer_list = [] #
albums_list = [] #
lyrics_list = [] #
genre_list = [] #
thumb_list = []

# 랭크 입력
for i in range(1, 101):
    rank_list.append(i)

# selenium을 통해 멜론 차트에 들어가기
driver = wd.Chrome(service=Service(chrome_path))
driver.get(melon_url)

html = driver.page_source

# beautifulsoup으로 크롤링
soup = BeautifulSoup(html, 'html.parser')

# 차트 크롤링
table_soup = soup.find('table')

# 타이틀 크롤링
title_soup = table_soup.find_all('div', attrs={'class': 'ellipsis rank01'})

for titles in title_soup:
    title = titles.get_text()
    title_list.append(title.replace('\n', ''))

time.sleep(2)

# 가수 크롤링
singer_soup = table_soup.find_all('div', attrs={'class': 'ellipsis rank02'})

for singers in singer_soup:
    singer = singers.find('a').get_text()
    singer_list.append(singer.replace('\n', ''))

time.sleep(2)
#
# 노래 넘버 크롤링
tbody_soup_50 = table_soup.select('tbody>tr.lst50')
tbody_soup_100 = table_soup.select('tbody>tr.lst100')

for line in tbody_soup_50:
    song_no_list.append(line['data-song-no'])

for line in tbody_soup_100:
    song_no_list.append(line['data-song-no'])

time.sleep(2)

# 앨범 이름 크롤링
albums_soup = table_soup.find_all('div', attrs={'class': 'ellipsis rank03'})

for albums in albums_soup:
    album = albums.find('a').get_text()
    albums_list.append(album.replace('\n', ''))

time.sleep(2)

# 가사 크롤링
for i in range(len(song_no_list)):
    driver.get(lyrics_url + song_no_list[i])

    html = driver.page_source

    soup = BeautifulSoup(html, 'html.parser')

    lyric = soup.find('div', attrs={'class': 'lyric'}).find_all(text=True)
    lyric1 = lyric[1::]
    lyric2 = ' '.join(lyric1)
    lyric3 = lyric2.replace('\t', '')
    lyric4 = lyric3.replace('\n', '')
    lyric5 = lyric4.replace("'", "\'")
    lyric6 = lyric5.replace('"', '\"')
    lyrics_list.append(lyric6)

    genre = soup.find('dl', attrs={'class': 'list'})
    genre_list.append(genre.find_all('dd')[2].get_text())

    thumb = soup.find('span', attrs={'class': 'cnt'})
    thumb = int(thumb.get_text().replace(',', ''))
    thumb_list.append(thumb)

    time.sleep(2)

tuple_list = []

for i in range(len(rank_list)):
    song_tuple = (rank_list[i],
                  song_no_list[i],
                  title_list[i],
                  singer_list[i],
                  albums_list[i],
                  genre_list[i],
                  lyrics_list[i],
                  thumb_list[i])
    tuple_list.append(song_tuple)

# MySQL 연동
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='0003',
                       database='music_chart',
                       charset='utf8')
cur = conn.cursor()

cur.execute('USE music_chart')

cur.execute('DROP TABLE IF EXISTS Chart;')

cur.execute("""
CREATE TABLE Chart (
    Id INTEGER NOT NULL PRIMARY KEY,
    Song_number INTEGER,
    Title VARCHAR(100),
    Artist VARCHAR(50),
    Album VARCHAR(100),
    Genre VARCHAR(20),
    Lyric VARCHAR(5000),
    Thumb INTEGER);
""")

for t in tuple_list:
    cur.execute("INSERT INTO Chart VALUES (%s, %s, %s, %s, %s, %s, %s, %s);", t)

conn.commit()
