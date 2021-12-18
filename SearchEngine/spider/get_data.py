#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# @Project -> File     ：informationResearch -> test
# @IDE      ：PyCharm
# @Author   ：Hongtao Liu
# @Date     ：2021/12/18 2:25 PM
# @Software : macOs python3.6.2

from bs4 import BeautifulSoup as BS
from urllib3 import PoolManager, ProxyManager
import urllib3
from FreeProxy import ProxyTool
import urllib
import requests
from collections import defaultdict
from multiprocessing import Pool

# def re_href()

def get_ip():
	"""

	:return:
	"""
	pt = ProxyTool.ProxyTool()
	proxies_ip = pt.getProxy(num_proxies=1, max_tries=10)
	proxies_ip = 'http://' + proxies_ip[0][0] + ':' + proxies_ip[0][1] + '/'
	print(proxies_ip)

	return proxies_ip


def get_html(proxies_ip):
	"""

	:return:
	"""
	response = requests.get('https://www.qidian.com/all/page100/')
	# http=ProxyManager(proxies_ip)
	# response=http.request('GET',"https://www.qidian.com/").read()
	print(type(response))
	html = BS(response.text, 'lxml')
	# sub_tag=html.find('div',{'class':"book-mid-info"}).find('href')
	# sub_tag=html(calss='book-mid-info')
	# for tag in html.
	# data_di=html.select('ul')
	sub = html.find('ul', {'class': "all-img-list cf"}).find_all('li')[0]
	print(sub)
	data_di = sub.select('h2 > a[href^="//book.qidian.com/info/"]', limit=1)[0].attrs
	data_di['title'] = sub.select('h2 > a[href^="//book.qidian.com/info/"]', limit=1)[0].text
	data_di['name'] = sub.find('p', {'class': "author"}).find('a', {'class': 'name'}).text
	data_di['label'] = sub.find('p', {'class': "author"}).text
	data_di['intro'] = sub.find('p', {'class': 'intro'}).text
	data_di.pop('target')
	data_di.pop('data-eid')
	print(data_di)
	return data_di

def get_every_page(pid):
	"""

	:return:
	"""
	data_di={}
	data_di['id']=pid
	response = requests.get('https://book.qidian.com/info/{}/'.format(pid))
	html=BS(response.text,'lxml')
	sub_book_info=html.find('div',{'class':'book-info'})
	data_di['title']=sub_book_info.select('em')[0].text
	data_di['writer']=sub_book_info.find('a',{'class':'writer'}).text
	di=sub_book_info.find('p',{"class":"tag"}).text.split('\n')
	data_di['tag']=[x for x in di if len(x)>0]
	data_di['intro']=sub_book_info.find('p',{'class':"intro"}).text
	data_di['book-intro']=''.join(html.find('div',{'class':"book-intro"}).find('p').text.replace(' ','').replace('\t','').replace('\n','').split())
	#di=''.join(di)
	print(data_di)


def get_status(file_path,i):
	"""

	:return:
	"""
	# for i in range(0,10):
	result_sub=[]
	for j in range(0, 10):
		for k in range(0, 10):
			for l in range(0, 10):
				for _i in range(0, 10):
					for _j in range(0, 10):
						for _k in range(0, 10):
							for _l in range(0, 10):
								id_sub = str(i) + str(_j) + str(_k) + str(_l) + str(_i) + str(_j) + str(_k) + str(_l)
								total_id = '10' + id_sub

								url = 'https://book.qidian.com/info/{}/'.format(total_id)
								status_code = requests.head(url)
								print(status_code.status_code)
								if status_code.status_code == 200:
									result_sub.append(total_id)
									#print(total_id)
	with open(file_path.format(i),'w',encoding='utf-8') as f:
		f.write('\n'.join(result_sub))


# print(type(status_code.status_code))

if __name__ == '__main__':
	pool=Pool(10)
	#file_path='/home/lht/informationResearch/SearchEngine/spider/data/id_{}.txt'
	file_path='/Users/rabin/Desktop/informationResearch/SearchEngine/spider/data/id_{}.txt'
	for i in range(0,10):
		pool.apply_async(get_status,(file_path,i,))

	pool.close()  # 等子进程执行完毕后关闭进程池
		# time.sleep(2)
		# p.terminate()     # 立刻关闭进程池
	pool.join()
	pool.terminate()
	# id_file='/home/lht/informationResearch/SearchEngine/spider/data/'
	# get_html('one')
	# proxies_ip=get_ip()
	#proxies_ip = 'none'
	# data=get_html(proxies_ip)
	get_every_page(pid='123456')
	#get_status()
