#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leohuang'
__date__ = '2016/5/10'
__version__ = '0.1-dev'

import re
import time
import os

"""
居民身份证由17位数字和一位校验码构成。
其中校验码可能为0-9的10个数字或者是一个字符X，字符X为罗马数字，即数字10。
"""
class IdFinder:
    def __init__(self, location_dict={}):
        self.id_regx = "(^\d{15}$)|(^\d{17}(\d|X|x)$)"
        self.weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]   #前17位权重
        #校验码的计算是通过一个校验和除以11取余数得到的，所以有10种可能
        self.validation_code = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        self.location_dict = location_dict

    def __checksum(self, cid):
        sum = 0
        for i in range(0, 17):
            sum += int(cid[i])*self.weight[i]

        return self.validation_code[sum%11]

    def __isValidDate(self, check_date):
        try:
            time.strptime(check_date, "%Y%m%d")
            return True
        except:
            return False

    def isValid(self, cid):
        m = re.match(self.id_regx, cid)
        if m:
            nid = self.normalize(cid)
            if (nid[17] == self.__checksum(nid)) and self.__isValidDate(nid[6:14]):
                return True

        return False

    def normalize(self, cid):
        if len(cid)==15:
            # 中间补上两位年份
            nid = "%s19%s" %(cid[:6], cid[6:])
            nid = "%s%s" %(nid, self.__checksum(nid))
            return nid
        return cid

    def get_location(self, cid):
        isValid_flag = self.isValid(cid)
        if self.isValid(cid):
            cid = self.normalize(cid)
            province_code = cid[:2] + "0000"
            city_code = cid[:4] + "00"
            area_code = cid[:6]
            province = self.location_dict[province_code] if province_code in self.location_dict else ""
            city = self.location_dict[city_code] if city_code in self.location_dict else ""
            area = self.location_dict[area_code] if area_code in self.location_dict else ""
            return cid, isValid_flag, province, city, area
        else:
            return cid, isValid_flag, "", "", ""


def get_location(location_dict, result_file):

    ## get id database info from dat
    id_db_file = "db\\id.dat"
    location_dict = {}     # id_code: id_place
    try:
        idf = open(os.path.join(os.getcwd(), id_db_file))
        idb_data = idf.readlines()
        idf.close()
        for line in idb_data:
            place_code, place_name = line.strip().split(" ")
            location_dict[place_code] = place_name
    except Exception, e:
        print "Get location dict error!", str(e)

    #print location_dict
    idf = IdFinder(location_dict)

    rf = open(result_file, 'w')
    f = open(raw_file)
    while 1:
        lines = f.readlines(1024)
        if not lines: break
        tmp_str = ""
        for line in lines:
            r_idc = line.strip()
            #'''
            if r_idc:
                idc, valid, province, city, area = idf.get_location(r_idc)
                if not valid:
                    print "%s is Invalid!!!" %(r_idc)
                print idc, province, city, area
                tmp_str += "%s\t%s\t%s\t%s\n" %(
                                                    r_idc,
                                                    province,
                                                    city,
                                                    area
                                                    )
        rf.write(tmp_str)
        #break

    f.close()
    rf.close()

if __name__ == "__main__":

    raw_file = "id.txt"
    result_file = "location.txt"
    get_location(raw_file, result_file)

