#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Project -> File     ：corruption -> util         
# @IDE      ：PyCharm
# @Author   ：Hongtao Liu -> Rabin
# @Date     ：2021/10/19 10:58 上午
# @Software : macOs python3.6
import re

import path
import jieba
def readStopWords(path=path.stop_words_path):
	"""
	获取停用词词典
	:param stop_words:
	:return:
	"""
	stop_words=[]
	with open(path,'r',encoding='utf-8') as f:
		lines=f.readlines()

		for line in lines:
			if isinstance(line,str):
				word=line.strip('\n')
				if word not in stop_words:
					stop_words.append(word)

	return stop_words

stop_words=readStopWords()

def segWords(sentence):
	result=[]
	if len(sentence)>0 and isinstance(sentence,str):
		word_list=jieba.lcut(sentence,cut_all=False,HMM=True)
		word_list=[x for x in word_list if x !='']
		for word in word_list:
			if word not in stop_words:
				result.append(word)
	if len(result)>0:
		return ' '.join(result)
	else:
		return None

def segWordsList(sentence):
	result=[]
	if len(sentence)>0 and isinstance(sentence,str):
		word_list=jieba.lcut(sentence,cut_all=False,HMM=True)
		word_list=[x for x in word_list if x !='']
		for word in word_list:
			if word not in stop_words:
				result.append(word)
	return result
