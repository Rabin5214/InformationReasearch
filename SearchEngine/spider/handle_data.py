#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Project -> File     ：corruption -> handle_data.py         
# @IDE      ：PyCharm
# @Author   ：Hongtao Liu
# @Date     ：2021/12/28 4:05 PM
# @Software : macOs python3.6.2
import os
import sqlite3
import time

import jieba
import utils
import path
import json
import math
from collections import defaultdict, Counter
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer, TfidfTransformer
import pymysql

# from sklearn.feature_extraction.text import CountVectorizer

stop_words = utils.readStopWords()
had_spider = []
file_dir = os.listdir(path.id_data_path)

for file in file_dir:
	if os.path.splitext(file)[1] == '.txt':
		had_spider.append(file)
all_sentences = []
all_di = []

for file in had_spider:
	with open(path.id_data_path+file, 'r', encoding='utf-8') as f:
		print(file)

		line = f.readline()#.strip()
		print(line)
		#time.sleep((1000))
		#try:
		content=json.loads(line)
		print(content)
		#except:
		#	continue
		if isinstance(content['intro'],str):
			intro = content['intro']
		else:
			intro=' '
		if isinstance(content['book-intro'],str):
			book_intro=content['book-intro']
		else:
			book_intro=' '
		#sentence_book_intro = json.loads(line)['book-intro']
		all_di.append(json.loads(line))
		all_sentences.append(intro + book_intro)


def calculate_tfidf(sentence):
	"""
	计算每一个词的tfidf值
	:return:
	"""
	word_list_tfidf = {}
	word_list = utils.segWordsList(sentence)
	word_count = Counter(word_list)
	word_list = list(set(word_list))
	for word in word_list:
		try:
			tfidf = round((word_count[word] * 1.0 / (count_words[word] * 1.0)) * idf_words[word], 5)
		except:
			tfidf = 0.0
		word_list_tfidf[word] = tfidf

	return word_list_tfidf


def calculate_idf():
	"""
	计算每个词的idf值
	:return:
	"""
	all_idf_words = {}
	for sentence in all_sentences:
		if isinstance(sentence, str):
			seg_sentence_list = utils.segWordsList(sentence)
			if isinstance(seg_sentence_list, list):
				if len(seg_sentence_list) > 1:
					for word in seg_sentence_list:
						if word in all_idf_words.keys():
							all_idf_words[word] += 1
						else:
							all_idf_words[word] = 1
	num_docs = len(all_sentences)
	_all_idf_word = {}
	for k, v in all_idf_words.items():
		idf = round(math.log(num_docs * 1.0 / (v + 1) * 1.0), 5)
		_all_idf_word[k] = idf
	# with open(path.idf_save_path, 'w', encoding='utf-8') as f:
	# 	for k, v in _all_idf_word.items():
	# 		f.write(k + ',' + str(v) + '\n')
	# all_tfidf_sentence.append(seg_sentence)
	return _all_idf_word, all_idf_words


count_words, idf_words = calculate_idf()
print(count_words)

def calculate_word2id():
	"""
	计算词对应的id集合
	:return:{word:[id]} ,id通过tf-idf值排序,keyword2id,title2id
	"""
	word2id_ = defaultdict(list)
	keyword2id = defaultdict(list)
	title2id = defaultdict(list)
	for data in all_di:
		id = data['id']
		title = data['title']
		keyword = data['tag']
		keyword.append(data['writer'])
		if id not in title2id[title]:
			title2id[title].append(id)
		for k in keyword:
			if id not in keyword2id[k]:
				keyword2id[k].append(id)
		key_words = data['intro'] + data['book-intro']
		words_tfidf = calculate_tfidf(key_words)  # (word,tf_idf)
		for k, v in words_tfidf.items():
			word2id_[k].append((id, v))
	word2id = defaultdict(list)
	for k,v in word2id_.items():
		v.sort(key=lambda x:x[1],reverse=True)
		result=[x[0] for x in v]
		word2id[k]=result

	return word2id,keyword2id,title2id

def store_mysql(keyword2id_tuple,title2id_tuple,word2id_tuple):
	"""
	存储数据到数据库
	:return:
	"""
	sql_keyword = "insert ignore into id_keyword (key_word,id_novel) values(%s,%s)"
	sql_title="insert ignore into id_title (key_word,id_novel) values (%s,%s)"
	sql_word="insert ignore into id_word (key_word,id_novel) values(%s,%s)"
	db=pymysql.connect(host='localhost',user='root',password='rabin5214',database='IR')
	cursor=db.cursor()
	cursor.executemany(sql_keyword,keyword2id_tuple)
	cursor.executemany(sql_title,title2id_tuple)
	cursor.executemany(sql_word,word2id_tuple)
	db.commit()
	db.close()

if __name__ == '__main__':
	word2id, keyword2id, title2id = calculate_word2id()
	word2id_list=[]
	keyword2id_list=[]
	title2id_list=[]
	for k,v in word2id.items():
		for id in v:
			word2id_list.append((k,id))
	word2id_tuple=tuple(word2id_list)
	for k,v in keyword2id.items():
		for id in v:
			keyword2id_list.append((k,id))
	keyword2id_tuple=tuple(keyword2id_list)
	for k,v in title2id.items():
		for id in v:
			title2id_list.append((k,id))
	title2id_tuple=tuple(title2id_list)

	store_mysql(keyword2id_tuple,title2id_tuple,word2id_tuple)
	# word2id,keyword2id,title2id=calculate_word2id()
	# print('word2id is {}'.format(word2id))
	# print('keyword2id is {}'.format(keyword2id))
	# print('title2id is {}'.format(title2id))
	# with open(path.word2id_path,'w',encoding='utf-8') as f:
	# 	for k,v in word2id.items():
	# 		for id in v:
	# 			f.write(str(k)+','+str(id)+'\n')
	# with open(path.keyword2id_path,'w',encoding='utf-8') as f:
	# 	for k,v in keyword2id.items():
	# 		for id in v:
	# 			f.write(str(k)+','+str(id)+'\n')
	# with open(path.title2id_path,'w',encoding='utf-8') as f:
	# 	for k,v in title2id.items():
	# 		for id in v:
	# 			f.write(str(k)+','+str(id)+'\n')
