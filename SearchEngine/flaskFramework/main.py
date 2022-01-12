#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Project -> File     ：informationResearch -> path.py
# @IDE      ：PyCharm
# @Author   ：Hongtao Liu
# @Date     ：2021/12/28 4:07 PM
# @Software : macOs python3.6.2
__author__ = 'GSAI'

import json

from flask import Flask, render_template, request

import path
from search_engine import SearchEngine

import xml.etree.ElementTree as ET
import sqlite3
import configparser
import time

import jieba

app = Flask(__name__)

#doc_dir_path = ''
#db_path = ''
global page
global keys


def init():
	config = configparser.ConfigParser()
	config.read('../config.ini', 'utf-8')
	#global dir_path, db_path
	#dir_path = config['DEFAULT']['doc_dir_path']
	#db_path = config['DEFAULT']['db_path']


@app.route('/')
def main():
	init()
	return render_template('search.html', error=True)


# 读取表单数据，获得doc_ID
@app.route('/search/', methods=['POST'])
def search():
	try:
		global keys
		global checked
		checked = ['checked="true"', '', '']
		keys = request.form['key_word']
		# print(keys)
		if keys not in ['']:
			print(time.clock())
			page = searchidlist(keys)
			# if flag == 0:
			return render_template('search.html', error=False)
			#docs = cut_page(page, 0)
			#print(time.clock())
			#return render_template('high_search.html', checked=checked, key=keys, docs=docs, page=page,
			#                       error=True)
		else:
			return render_template('search.html', error=False)

	except:
		print('search error')


def searchidlist(key, selected=1):
	global page
	global doc_id
	flag=1
	se = SearchEngine('../config.ini', 'utf-8')
	id_list = se.search(key, selected)
	# 返回docid列表
	# print("flag is {} \n id_scores is {}".format(flag,id_scores))
	doc_id = [i for i, s in id_list]
	page = []
	for i in range(1, (len(doc_id) // 10 + 2)):
		page.append(i)
	return flag,page


def cut_page(page, no):
	docs = find(doc_id[no * 10:page[no] * 10])
	return docs


# 将需要的数据以字典形式打包传递给search函数
def find(docid, extra=False):
	docs = []
	#global dir_path, db_path
	for id in docid:
		with open(path.id_data_path + 'id_{}.txt'.format(id), 'r', encoding='utf-8') as f:
			line = f.readline()
			doc = json.loads(line)  # id,writer,intro,book-intro,tag
			doc['url'] = 'https://book.qidian.com/info/{}/'.format(id)
			docs.append(doc)

	return docs


@app.route('/search/page/<author>/', methods=['GET'])
def next_page(page_no):
	try:
		page_no = int(page_no)
		docs = cut_page(page, (page_no - 1))
		return render_template('high_search.html', checked=checked, key=keys, docs=docs, page=page,
		                       error=True)
	except:
		print('next error')


@app.route('/search/<key>/', methods=['POST'])
def high_search(key):
	try:
		selected = int(request.form['order'])
		for i in range(3):
			if i == selected:
				checked[i] = 'checked="true"'
			else:
				checked[i] = ''
		flag, page = searchidlist(key, selected)
		if flag == 0:
			return render_template('search.html', error=False)
		docs = cut_page(page, 0)
		return render_template('high_search.html', checked=checked, key=keys, docs=docs, page=page,
		                       error=True)
	except:
		print('high search error')


@app.route('/search/<novel>/', methods=['GET', 'POST'])
def content(id):
	try:
		doc = find([id], extra=True)
		return render_template('content.html', doc=doc[0])
	except:
		print('content error')


def get_k_nearest(db_path, docid, k=5):
	conn = sqlite3.connect(db_path)
	c = conn.cursor()
	c.execute("SELECT * FROM knearest WHERE id=?", (docid,))
	docs = c.fetchone()
	# print(docs)
	conn.close()
	return docs[1: 1 + (k if k < 5 else 5)]  # max = 5


if __name__ == '__main__':
	jieba.initialize()  # 手动初始化（可选）
	# app.run(host="0.0.0.0", port=5000) # 部署到服务器上，外网可通过服务器IP和端口访问
	app.run()
