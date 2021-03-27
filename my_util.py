# date : 2020/11/19
# 시뮬레이션에 사용하는 utilities
#
# 보다 자세한 내용을 아래 tistory 참고
# https://money-expert.tistory.com/34
#

# sdb-tick-info_2020-11-18 sbd tick info

import json
import csv
import time
import datetime
#
# for read data from cvs
#
# row : value list
def get_new_item(keys, row) :
    data = {}
    for i in range(len(row)) :
        data[keys[i]] = row[i]
    return data

# 첫 줄은 title이라고 가정, 이후에 title 값을 key로 갖는 dict로 읽기
def read_csv_to_dict(fname) :
    data = []
    keys =[]
    first = 1
    with open(fname, 'r', encoding='UTF8') as FILE :
        csv_reader = csv.reader(FILE, delimiter=',', quotechar='"')
        for row in csv_reader :
            if first : # make dict keys
                keys = row.copy()
#                for key in row :
#                    keys .append(key)
                first = 0
            else :                
                data.append(get_new_item(keys, row))
    return data

#
# for writing dic data to cvs format
#
def save_to_file_csv(file_name, data) :
    with open(file_name,'w',encoding="cp949") as make_file: 
        # title 저장
        vals = data[0].keys()
        ss = ''
        for val in vals:
            val = val.replace(',','')
            ss += (val + ',')
        ss += '\n'
        make_file.write(ss)

        for dt in data:
            vals = dt.values()
            ss = ''
            for val in vals:
                sval = str(val) 
                sval = sval.replace(',','')
                ss += (sval + ',')
            ss += '\n'
            make_file.write(ss)
    make_file.close()

# 같은 봉인지 확인 (interval, num 관점에서)
def is_diff_candle(comp1, comp2, interval, interval_num) :
    if interval == 'min' :
        min1 = int(int(comp1['time'].split(':')[1]) / interval_num)
        min2 = int(int(comp2['time'].split(':')[1]) / interval_num)
        if min1 != min2 :
            return True
    elif interval == 'day' :
        if comp1['date'] != comp2['date'] :
            return True
    return False

# 시간 관련
TODAY = time.strftime("%Y%m%d")
TODAY_TIME = time.strftime("%H%M%S")
TODAY_S = time.strftime("%Y-%m-%d")

def get_time_str(cont='T') :
    date=datetime.datetime.now()
    form = '%Y/%m/%d'+cont+'%H:%M:%S'
    return date.strftime(form)

# ticker의 길이를 len으로 일치, 뒤에 ' '를 추가
def get_aligned_ticker_name(self, ticker, len=10) :
    ret = ticker
    for i in range(len(ticker), len) :
        ret += ' '
    return ret


#
# for writing data with json format to file
#
def save_to_file_json(file_name, data) :
    with open(file_name,'w',encoding="cp949") as make_file: 
       json.dump(data, make_file, ensure_ascii=False, indent="\t") 
    make_file.close()

#
# for reading data with json format from file
#
def load_json_from_file(file_name, err_msg=1) :
    try :
        with open(file_name,'r',encoding="cp949") as make_file: 
           data=json.load(make_file) 
        make_file.close()
    except  Exception as e : # 또는 except : 
        data = {}
        if err_msg :
            print(e, file_name)
    return data

if __name__ == '__main__':

    print('myutil')
