#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Project -> File     ：informationResearch -> path.py
# @IDE      ：PyCharm
# @Author   ：Hongtao Liu
# @Date     ：2021/12/28 4:07 PM
# @Software : macOs python3.6.2

import jieba
import math
import operator
import sqlite3
import configparser
from datetime import *
import path
import utils
import pymysql
from collections import defaultdict
import copy


class SearchEngine:
	# stop_words = set()

	config_path = ''
	config_encoding = ''

	K1 = 0
	B = 0
	N = 0
	AVG_L = 0

	HOT_K1 = 0
	HOT_K2 = 0

	conn = None

	def __init__(self, config_path, config_encoding):
		self.config_path = config_path
		self.config_encoding = config_encoding
		config = configparser.ConfigParser()
		config.read(config_path, config_encoding)
		# f = open(config['DEFAULT']['stop_words_path'], encoding = config['DEFAULT']['stop_words_encoding'])
		# words = f.read()
		self.stop_words = utils.readStopWords()  # set(words.split('\n'))
		# self.conn = sqlite3.connect(config['DEFAULT']['db_path'])
		self.conn = pymysql.connect(host=config['DEFAULT']['host'], user=config['DEFAULT']['user'],
		                            password=config['DEFAULT']['password'], database=config['DEFAULT']['database'])
		# self.K1 = float(config['DEFAULT']['k1'])
		# self.B = float(config['DEFAULT']['b'])
		# self.N = int(config['DEFAULT']['n'])
		# self.AVG_L = float(config['DEFAULT']['avg_l'])
		# self.HOT_K1 = float(config['DEFAULT']['hot_k1'])
		# self.HOT_K2 = float(config['DEFAULT']['hot_k2'])

	def __del__(self):
		self.conn.close()

	def is_number(self, s):
		try:
			float(s)
			return True
		except ValueError:
			return False

	def sigmoid(self, x):
		return 1 / (1 + math.exp(-x))

	def clean_list(self, seg_list):
		cleaned_dict = {}
		n = 0
		for i in seg_list:
			i = i.strip().lower()
			if i != '' and not self.is_number(i) and i not in self.stop_words:
				n = n + 1
				if i in cleaned_dict:
					cleaned_dict[i] = cleaned_dict[i] + 1
				else:
					cleaned_dict[i] = 1
		return n, cleaned_dict

	def fetch_from_db(self, word, tp=0):
		result = []
		c = self.conn.cursor()
		if tp == 0:
			c.execute('SELECT id_novel FROM id_keyword WHERE key_word=?', (word,))
		elif tp == 1:
			c.execute("SELECT id_novel from id_title where key_word=?", (word,))
		else:
			c.execute("select id_novel from id_word where key_word=?", (word,))
		data = c.fetchall()
		for di in data:
			result.append(int(di[0]))
		return result  # (c.fetchone())

	def result_by_BM25(self, sentence):
		seg_list = jieba.lcut(sentence, cut_all=False)
		n, cleaned_dict = self.clean_list(seg_list)
		BM25_scores = {}
		for term in cleaned_dict.keys():
			r = self.fetch_from_db(term)
			if r is None:
				continue
			df = r[1]
			w = math.log2((self.N - df + 0.5) / (df + 0.5))
			docs = r[2].split('\n')
			for doc in docs:
				docid, date_time, tf, ld = doc.split('\t')
				docid = int(docid)
				tf = int(tf)
				ld = int(ld)
				s = (self.K1 * tf * w) / (tf + self.K1 * (1 - self.B + self.B * ld / self.AVG_L))
				if docid in BM25_scores:
					BM25_scores[docid] = BM25_scores[docid] + s
				else:
					BM25_scores[docid] = s
		BM25_scores = sorted(BM25_scores.items(), key=operator.itemgetter(1))
		BM25_scores.reverse()
		if len(BM25_scores) == 0:
			return 0, []
		else:
			print("type is {}".format(type(BM25_scores[0][0])))
			return 1, BM25_scores

	def result_by_keyword(self, sentence):
		seg_list = sentence.split(' ')
		result = defaultdict(list)
		union_set = []
		i = 0
		for word in seg_list:

			id_list = self.fetch_from_db(word, tp=0)
			if i == 0:
				union_set = copy.copy(id_list)
			result[word] = id_list
			for x in id_list:
				if x not in union_set:
					union_set.remove(x)
		final_result = copy.copy(union_set)
		for k, v in result.items():
			for id in v[:30]:
				if id not in final_result:
					final_result.append(id)
		return final_result

	def result_by_title(self, sentence):
		seg_list = jieba.lcut(sentence, cut_all=False)
		n, cleaned_dict = self.clean_list(seg_list)
		time_scores = {}
		for term in cleaned_dict.keys():
			r = self.fetch_from_db(term)
			if r is None:
				continue
			docs = r[2].split('\n')
			for doc in docs:
				docid, date_time, tf, ld = doc.split('\t')
				if docid in time_scores:
					continue
				news_datetime = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
				now_datetime = datetime.now()
				td = now_datetime - news_datetime
				docid = int(docid)
				td = (timedelta.total_seconds(td) / 3600)  # hour
				time_scores[docid] = td
		time_scores = sorted(time_scores.items(), key=operator.itemgetter(1))
		if len(time_scores) == 0:
			return 0, []
		else:
			return 1, time_scores

	def result_by_word(self, sentence):
		seg_list = jieba.lcut(sentence, cut_all=False)
		n, cleaned_dict = self.clean_list(seg_list)
		hot_scores = {}
		for term in cleaned_dict.keys():
			r = self.fetch_from_db(term)
			if r is None:
				continue
			df = r[1]
			w = math.log2((self.N - df + 0.5) / (df + 0.5))
			docs = r[2].split('\n')
			for doc in docs:
				docid, date_time, tf, ld = doc.split('\t')
				docid = int(docid)
				tf = int(tf)
				ld = int(ld)
				news_datetime = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
				now_datetime = datetime.now()
				td = now_datetime - news_datetime
				BM25_score = (self.K1 * tf * w) / (tf + self.K1 * (1 - self.B + self.B * ld / self.AVG_L))
				td = (timedelta.total_seconds(td) / 3600)  # hour
				#                hot_score = math.log(BM25_score) + 1 / td
				hot_score = self.HOT_K1 * self.sigmoid(BM25_score) + self.HOT_K2 / td
				if docid in hot_scores:
					hot_scores[docid] = hot_scores[docid] + hot_score
				else:
					hot_scores[docid] = hot_score
		hot_scores = sorted(hot_scores.items(), key=operator.itemgetter(1))
		hot_scores.reverse()
		if len(hot_scores) == 0:
			return 0, []
		else:
			return 1, hot_scores

	def search(self, sentence, sort_type=0):
		if sort_type == 0:
			return self.result_by_keyword(sentence)
		elif sort_type == 1:
			return self.result_by_title(sentence)
		elif sort_type == 2:
			return self.result_by_word(sentence)

	def result_by_time(self, sentence):
		seg_list = jieba.lcut(sentence, cut_all=False)
		n, cleaned_dict = self.clean_list(seg_list)
		time_scores = {}
		for term in cleaned_dict.keys():
			r = self.fetch_from_db(term)
			if r is None:
				continue
			docs = r[2].split('\n')
			for doc in docs:
				docid, date_time, tf, ld = doc.split('\t')
				if docid in time_scores:
					continue
				news_datetime = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
				now_datetime = datetime.now()
				td = now_datetime - news_datetime
				docid = int(docid)
				td = (timedelta.total_seconds(td) / 3600)  # hour
				time_scores[docid] = td
		time_scores = sorted(time_scores.items(), key=operator.itemgetter(1))
		if len(time_scores) == 0:
			return 0, []
		else:
			return 1, time_scores

	def result_by_hot(self, sentence):
		seg_list = jieba.lcut(sentence, cut_all=False)
		n, cleaned_dict = self.clean_list(seg_list)
		hot_scores = {}
		for term in cleaned_dict.keys():
			r = self.fetch_from_db(term)
			if r is None:
				continue
			df = r[1]
			w = math.log2((self.N - df + 0.5) / (df + 0.5))
			docs = r[2].split('\n')
			for doc in docs:
				docid, date_time, tf, ld = doc.split('\t')
				docid = int(docid)
				tf = int(tf)
				ld = int(ld)
				news_datetime = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
				now_datetime = datetime.now()
				td = now_datetime - news_datetime
				BM25_score = (self.K1 * tf * w) / (tf + self.K1 * (1 - self.B + self.B * ld / self.AVG_L))
				td = (timedelta.total_seconds(td) / 3600)  # hour
				#                hot_score = math.log(BM25_score) + 1 / td
				hot_score = self.HOT_K1 * self.sigmoid(BM25_score) + self.HOT_K2 / td
				if docid in hot_scores:
					hot_scores[docid] = hot_scores[docid] + hot_score
				else:
					hot_scores[docid] = hot_score
		hot_scores = sorted(hot_scores.items(), key=operator.itemgetter(1))
		hot_scores.reverse()
		if len(hot_scores) == 0:
			return 0, []
		else:
			return 1, hot_scores
