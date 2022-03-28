#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : Ht6
# @Time     : 2022/3/26 4:20 PM
# @File     : judge_functions.py
# @Project  : GAN&GT
# @e-mail   : ht6@ruc.edu.cn
import jieba


def seg_word(sentence):
    word_list = jieba.lcut(sentence, cut_all=False, HMM=True)
    return word_list


def judge_age(age, sex):
    # 0为未满16岁1为学生判断2为退休判断
    age = int(age)
    sex = int(sex)
    if age < 16:
        return 0
    elif (age >= 16 and age <= 60 and sex == 0) | (age >= 16 and age <= 55 and sex == 1):
        need_judge_student = 1
        return need_judge_student
    else:
        # 判断是否退休

        need_judge_pensioner = 2
        return need_judge_pensioner


class Judge_official(object):
    def __init__(self):
        self.key_word = []

        self.result = "none"

    def _young_official(self, had_protocol, protocol_name, protocol_same, is_tiefanwan):
        # print("执行1")
        if len(protocol_name) > 1:
            self.key_word = seg_word(protocol_name)
            self.judge_appoint()
            if self.result != 'none':
                # print("7")
                # print(self.result)
                return {"result": self.result}

        if had_protocol == 0:
            if protocol_same == 0:
                if is_tiefanwan == 0:
                    # print("3")
                    return {"result": "非劳动关系"}
            elif protocol_same == 1:
                # print("4")
                return {"result": "劳务派遣关系，与派遣单位是劳动合同关系"}
        else:
            # print("5")
            if is_tiefanwan == 0:
                return {"result": "非劳动关系"}
        return self.result

    def judge_appoint(self):
        if "委任" in self.key_word:

            self.result = "非劳动关系"
        elif "劳动合同" in self.key_word or ('劳动' in self.key_word and "合同" in self.key_word):
            self.result = "劳动合同"
        else:
            # print('6')
            self.result = "none"


class Judge_others(object):
    def __init__(self):
        """

        """
        self.labor_contract = 1
        self.salary_on_time = 1
        self.get_salary_by_company = 1
        self.normal_work_time = 1
        self.character_of_service = 1
        self.withholding_wages = 1
        self.get_salary = 1

    def judge_peasantry(self, work_address, work_license):
        """
        work_address: 0 北上广深 1 其他城市
        :return:
        """
        if work_address == 0:
            return {"result": '与包工头存在合同关系'}
        elif work_address == 1 and work_license == 0:
            return {"result": "存在劳动合同关系"}
        else:
            return {"result": "不存在合同关系"}

        # return {"result": "peasantry 判断错误"}

    def judge_rider(self, work_protocol):
        """

        :return:
        """
        if work_protocol == 0:
            return {"result": "与平台存在劳动合同关系"}
        elif work_protocol == 1:
            return {"result": "与平台是劳务派遣关系，不存在劳动合同关系"}
        else:
            return {"result": "rider判断失败"}

    def judge_other(self, labor_protocol, salary_on_time, get_salary_by_company, normal_work_time,
                    character_of_service, withholding_wages, get_salary):
        """

        :return:
        """

        if labor_protocol == 0:
            self.labor_contract = 1
        else:
            self.labor_contract = 0

        if salary_on_time == 0:
            self.salary_on_time = 1
        else:
            self.salary_on_time = 0

        if get_salary_by_company == 0:
            self.get_salary_by_company = 1
        else:
            self.get_salary_by_company = 0

        if normal_work_time == 0:
            self.normal_work_time = 1
        else:
            self.normal_work_time = 0

        if (self.labor_contract and self.salary_on_time and self.get_salary_by_company) or (
                self.salary_on_time and self.get_salary_by_company and self.normal_work_time):
            return {"result": "劳动合同关系"}

        if character_of_service == 0:
            self.character_of_service = 1
        else:
            self.character_of_service = 0
        if self.salary_on_time and self.normal_work_time and self.character_of_service:
            return {'result': "大概率为劳动合同"}

        if withholding_wages == 0:
            self.withholding_wages = 1
        else:
            self.withholding_wages = 0
        if get_salary == 0:
            self.get_salary = 1
        else:
            self.get_salary = 0
        if self.labor_contract and self.normal_work_time and self.character_of_service and self.withholding_wages and self.get_salary:
            return {'result': "倾向于劳动合同"}
        else:
            if not self.withholding_wages and not self.get_salary:
                return {'result': "无劳动合同关系"}
            return {'result': "others 无法判断"}


class JudgeLaboratoryOld(object):
    """未添加特殊职业、特殊职业退休年龄部分"""

    def __init__(self):
        self.whether_get_contract = 1
        self.contract_time = 1
        self.contract_start_time = 1

    def _old_person(self, get_protocol, protocol_time, protocol_start_time):
        # whether_get_pension = int(input("请问是否获得退休待遇（获取退休金或者退休证、养老保险等）\n 1.是 2.不是\n"))
        # if whether_get_pension == 2:
        # whether_get_contract = int(input("请问是否与用人单位签订了劳动合同\n 1. 是 2. 不是\n"))
        self.whether_get_contract = get_protocol
        self.contract_time = protocol_time
        self.contract_start_time = protocol_start_time
        if self.whether_get_contract == 1:
            return {"result": "不存在劳动关系"}
        else:
            # contract_time = int(input("请问签订的劳动合同是否到期: \n 1.是 2.不是\n"))
            result = self.judge_label_contract(self.contract_time)
            if isinstance(result, dict):
                return result
            else:
                #contract_start_time = int(input("请问是否是退休前签订的合同\n 1.是 2.不是\n"))
                result = self.judge_contract_time(self.contract_start_time)
                return result

    def judge_label_contract(self, is_labor_contract_end):

        if is_labor_contract_end == 0:
            print(is_labor_contract_end)
            return {"result":"劳务关系"}
        else:
            need_judge_contract_time = 1
            return need_judge_contract_time


    def judge_contract_time(self, contract_time):
        if contract_time == 0:
            return {"result":"劳动关系"}
        else:
            return {"result":"劳务关系"}
