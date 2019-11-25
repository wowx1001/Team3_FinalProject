#!/usr/bin/env python
# coding: utf-8

# In[1]:

from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from sklearn import preprocessing
from sklearn.manifold import TSNE
import requests
import re
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
df_f = pd.read_csv('data/flower_word_kr_en_final.csv', encoding='cp949')
df_s = pd.read_csv('data/flower_word_kr_en_v2.csv', encoding='cp949')
df_q = pd.read_csv('data/Floriography_list_191113_v3.csv', sep=";", encoding="utf8")
df_sentence_list = []
for i in df_s['flower_word_en']:
    df_sentence_list.append(i)

def cos_sim(input_vectors):
    similarity = cosine_similarity(input_vectors)
    return similarity

def get_top_similar(sentence, sentence_list, similarity_matrix, topN):
    # find the index of sentence in list
    index = sentence_list.index(sentence)
    # get the corresponding row in similarity matrix
    similarity_row = np.array(similarity_matrix[index, :])
    # get the indices of top similar
    indices = similarity_row.argsort()[-topN:][::-1]
    return [sentence_list[i] for i in indices]

def translation_txt(txt):
    API_HOST = 'https://kapi.kakao.com'
    path = '/v1/translation/translate'
    url = API_HOST + path
    headers = {'Authorization': 'KakaoAK'}

    params = {"query": txt, "src_lang":"kr", "target_lang":"en"}
    resp =  requests.post(url, headers=headers, data=params)

    return re.split('"', resp.text)[3]
  
@app.route('/')
def student():
    return render_template('firstpage.html')

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        tf.compat.v1.disable_eager_execution()
        module_url = "https://tfhub.dev/google/tf2-preview/nnlm-en-dim128/1"
        embed = hub.KerasLayer(module_url)
        embeddings = embed(["A long sentence.", "single-word","http://example.com"])
        embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-large/4")

        sentence = request.form['uri']

        word = translation_txt(sentence)
        sentence_train = np.append(df_sentence_list, word)
        sentence_train = sentence_train.tolist()

        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

        print(embeddings.shape)
        with tf.compat.v1.Session() as session:
            session.run([tf.compat.v1.global_variables_initializer(), tf.compat.v1.tables_initializer()])
            message_embeddings = session.run(embed(sentence_train))


        for key, val in message_embeddings.items():
            v = val

        similarity_matrix = cos_sim(v)

        top_similar = get_top_similar(word, sentence_train, similarity_matrix, 16)
        top_similar = top_similar[1:]

        flower_word = []
        for i in range(len(top_similar)):
            for j in range(len(df_f.flower_word_kr[df_f['flower_word_en']==top_similar[i]])):
                flower_word.append(df_f.flower_word_kr[df_f['flower_word_en']==top_similar[i]].tolist()[j])
        m_result=pd.DataFrame(columns=['f_num','f_birth','f_name','f_lang','f_type'])
        for i in range(len(flower_word)):
            m_result = m_result.merge(df_q[df_q['f_lang'].str.match(r'.*('+flower_word[i]+').*')],how='outer')

        f_count = m_result[m_result['f_type']==1]['f_num'].reset_index(drop=True)
        g_count = m_result[m_result['f_type']==0]['f_num'].reset_index(drop=True)
        table = pd.concat([m_result[m_result['f_type']==0].reset_index(drop=True), m_result[m_result['f_type']==1].reset_index(drop=True)])
        arr_len = len(table)
        arr_result=[]
        if len(g_count)>1:
            for i in range(15):
                if (i>=len(g_count)):
                    arr_result.append(f_count[i%len(f_count)])
                else:
                    arr_result.append(g_count[i%len(g_count)])
        elif (len(g_count)==1):
            for i in range(15):
                if (i>=4):
                    arr_result.append(f_count[i%len(f_count)])
                else:
                    arr_result.append(g_count[0])        
        else:
            for i in range(15):
                arr_result.append(f_count[i%len(f_count)])
        return render_template("secondpage.html", result=table, result2 = arr_result, arr_len = arr_len, sentence = sentence)
if __name__ == '__main__':
    app.run(host = "127.0.0.1", debug = True, port=5000)

