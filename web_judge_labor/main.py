#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : Ht6
# @Time     : 2022/3/26 2:32 PM
# @File     : main.py
# @Project  : labor
# @e-mail   : ht6@ruc.edu.cn
__author__ = "GSAI"

import json

import flask
from flask import render_template, Flask, request
import sqlite3
import configparser
import time
from judge_functions import judge_age, Judge_official, Judge_others,JudgeLaboratoryOld
import jieba

judge_official = Judge_official()
judge_others = Judge_others()
judge_old=JudgeLaboratoryOld()
app = Flask(__name__)


def init():
    config = configparser.ConfigParser()
    config.read('./config.ini', 'utf-8')


@app.route('/')
def main():
    init()
    return render_template('start_judge.html', error=True)


@app.route('/judge/', methods=['POST'])
def search():
    age = request.form['age']
    sex = request.form['sex']
    typo = judge_age(age, sex)

    if typo == 0:
        # doc=json.dumps({"result":"未成年"})
        doc = {"result": "平等的民事法律关系，不存在劳动关系或者劳务关系，适用民法典"}
        return render_template('result.html', doc=doc)
    elif typo == 1:
        return render_template('adult_judge.html', error=True)
    else:
        return render_template("elder_judge.html", error=True)


@app.route('/judge_official/', methods=["POST"])
def official_search_():
    had_protocol = int(request.form['whether_protocol'])
    protocol_name = request.form['protocol_name']
    protocol_same = int(request.form['protocol_same'])
    is_tiefanwan = int(request.form['is_tiefanwan'])
    # print("{}\{}\{}\{}".format(had_protocol,protocol_name,protocol_same,is_tiefanwan))
    result = judge_official._young_official(had_protocol, protocol_name, protocol_same, is_tiefanwan)
    # print(result)
    if isinstance(result, dict):
        return render_template("result.html", doc=result)
    else:
        return render_template("result.html", doc={'result': "计算错误"})


@app.route('/judge_peasantry/', methods=["POST"])
def peasantry_search():
    work_address = int(request.form['work_address'])
    work_license = int(request.form['work_license'])
    result = judge_others.judge_peasantry(work_address, work_license)
    if isinstance(result, dict):
        return render_template("result.html", doc=result)
    else:
        return render_template('result.html', doc={"result": "peasantry 判断错误"})


@app.route('/judge_rider/', methods=["POST"])
def rider_judge():
    work_protocol = int(request.form['work_protocol'])
    result = judge_others.judge_rider(work_protocol)
    if isinstance(result, dict):
        return render_template("result.html", doc=result)
    else:
        return render_template('result.html', doc={"result": "rider 判断错误"})


@app.route('/judge_other/', methods=["POST"])
def other_judge():
    labor_protocol = int(request.form['labor_protocol'])
    salary_on_time = int(request.form['salary_on_time'])
    get_salary_by_company = int(request.form['get_salary_by_company'])
    normal_work_time = int(request.form['normal_work_time'])
    character_of_service = int(request.form['character_of_service'])
    withholding_wages = int(request.form['withholding_wages'])
    get_salary = int(request.form['get_salary'])
    result = judge_others.judge_other(labor_protocol, salary_on_time, get_salary_by_company, normal_work_time,
                                      character_of_service, withholding_wages, get_salary)
    if isinstance(result, dict):
        return render_template("result.html", doc=result)
    else:
        return render_template('result.html', doc={"result": "rider 判断错误"})


@app.route('/judge_elder/', methods=['POST'])
def elder_search():
    """

    :return:
    """
    get_pension=int(request.form["get_pension"])
    if get_pension==0:
        return render_template('result.html',doc={'result':"不存在劳动关系"})

@app.route('/judge_elder_/',methods=["POST"])
def elder_search_():
    get_protocol=int(request.form['get_protocol'])
    protocol_time=int(request.form['protocol_time'])
    protocol_start_time=int(request.form['protocol_start_time'])
    result=judge_old._old_person(get_protocol,protocol_time,protocol_start_time)
    if isinstance(result, dict):
        return render_template("result.html", doc=result)
    else:
        return render_template('result.html', doc={"result": "elder 判断错误"})



if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=False)
