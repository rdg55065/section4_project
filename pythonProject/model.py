import pymysql
import re
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# MySQL 연동
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='0003',
                       database='music_chart',
                       charset='utf8')

cur = conn.cursor()

cur.execute('USE music_chart;')

cur.execute('SELECT * FROM Chart c;')

chart = cur.fetchall()

df = pd.DataFrame(chart)

df.columns = ['id', 'song_number', 'title', 'artist', 'album', 'genre', 'lyric', 'thumb']

df['kor_lyric'] = [re.sub('[^ 가-힣+]', '', s) for s in df['lyric']]
df['eng_lyric'] = [re.sub('[^ a-zA-Z+]', '', s) for s in df['lyric']]

kor_sentences = []
eng_sentences = []

for i in range(0, 100):
    ls = df['kor_lyric'][i].split(' ')
    ls = ' '.join(ls).split()
    kor_sentences.append(list(ls))

for i in range(0, 100):
    ls = df['eng_lyric'][i].split(' ')
    ls = ' '.join(ls).split()
    eng_sentences.append(list(ls))

df['kor_tfidf'] = [' '.join(sen) for sen in kor_sentences]
df['eng_tfidf'] = [' '.join(sen) for sen in eng_sentences]

tfidfv = TfidfVectorizer()
eng_tf = tfidfv.fit_transform(df['eng_tfidf'])
kor_tf = tfidfv.fit_transform(df['kor_tfidf'])

eng_tf_sim = cosine_similarity(eng_tf, eng_tf)
kor_tf_sim = cosine_similarity(kor_tf, kor_tf)

# 추천 알고리즘
def kor_music(word, sim=kor_tf_sim, n=5):

    # 특정 단어가 들어간 데이터프레임 추출
    lyric_df = df[df['kor_lyric'].str.contains(word)]
    lyrics_idx = lyric_df.index.values

    sim_sorted_ind = sim.argsort()[:, ::-1]

    if df.iloc[sim_sorted_ind[lyric_df.index][0][0]].lyric != word:

        idx_list = sim_sorted_ind[lyric_df.index][0].tolist()

        idx_list.remove(lyric_df.index.values.tolist()[0])

        sim_sorted_ind2 = np.array(idx_list)

        similar_idx = sim_sorted_ind2[0:n]

        result = df.iloc[similar_idx]

        result = result[['id', 'title', 'artist', 'album', 'genre', 'lyric', 'thumb']].reset_index()

    else:
        similar_idx = sim_sorted_ind[lyrics_idx, 1:[n+1]]

        result = df.lioc[similar_idx[0:n]]

        result = result[['id', 'title', 'artist', 'album', 'genre', 'lyric', 'thumb']].reset_index()

    return result
