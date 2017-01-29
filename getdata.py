from bs4 import BeautifulSoup
import re
import requests

def get_timetable(test_id):
    # test_id = 580610678
    # test_id = 560651018 #tba
    # test_id = 560610004  #time double fixed
    test_sem = 159
    res = requests.get("https://www3.reg.cmu.ac.th/regist"+str(test_sem)+"/public/result.php?id="+str(test_id))
    res.encoding = "tis-620"

    soup = BeautifulSoup(res.text, "html.parser")
    data = soup.find_all('tr', {"class": "msan8"})
    stdList = []
    listData = []

    if len(data) > 0:
        for num in range(2, len(data)):
            raw_sidData = data[num].find_all('td')

            if len(raw_sidData) >= 10: # filter Lab table header
                if raw_sidData[0].text.isnumeric():
                    for num2 in range(1, len(raw_sidData)):
                        if num2 == 7:
                            # clean double day
                            temp_ppy = []
                            for ppy in raw_sidData[num2]:
                                if str(type(ppy)) == "<class 'bs4.element.Tag'>":
                                    temp_ppy.append(ppy.text)
                                else:
                                    temp_ppy.append(ppy)
                            ty = temp_ppy
                        elif num2 == 8:
                            # clean double time to mod 4 format
                            ty = re.sub("([ -])","",str(raw_sidData[num2].text.strip()))
                        else:
                            ty = raw_sidData[num2].text.strip()
                        listData.append(ty)
                        # print(ty)
                    list2 = [x for x in listData if x != []]
                stdList.append(list2)
            listData = []

    for index_gid, data_gid in enumerate(stdList):
        pdata = {
            "s_course1":stdList[index_gid][0],
            "s_lec1":stdList[index_gid][2],
            "s_lab1":stdList[index_gid][3],
            "op": "bycourse"
        }
        new_re = requests.post("https://www3.reg.cmu.ac.th/regist"+str(test_sem)+"/public/search.php?act=search", data=pdata)
        new_re.encoding = 'utf-8'

        data = BeautifulSoup(new_re.text,'html.parser')
        data2 = data.find_all("table")

        mount_name = ['JAN', 'FEB', 'MAR', 'APR', 'MAY','JUN', 'JUL','AUG','SEP', 'OCT', 'NOV', 'DEC']
        date_stamp = []
        temp_date = []
        teacher_name = []

        if len(data2) <= 0:
            # if is table_header except this and add empty_list_data_time
            temp_date.append([])
            temp_date.append([])
            temp_time = list()
            temp_time.append([])
            temp_time.append([])
        else:
            for index, val in enumerate(data2[0].find_all("td")):
                if index == 9:
                    stdList[index_gid].append(val.text)

                if index == 10:
                    for x in val:
                        text = re.sub('(<br>|<b>)|<br/>|</br>',"|",str(x)).strip('|').replace("</b>","").split('|')
                        for t in text:
                            teacher_name.append(t.strip())

                if index == 11:
                    temp_date.append([])
                    temp_date.append([])
                    for idt, tag in enumerate(val):
                        # Filter REGULAR EXAM
                        if val.text != "REGULAR":
                            if len(val) == 1:
                                time_temp_strip = str(tag.text).strip().split(" ")
                                temp_date[1].append(int(time_temp_strip[2]))
                                temp_date[1].append(int(time_temp_strip.index(time_temp_strip[1]) + 1))
                                temp_date[1].append(int(time_temp_strip[0]))
                            elif len(val) == 2:
                                time_temp_strip = str(tag.text).strip().split(" ")
                                temp_date[idt].append(int(time_temp_strip[2]))
                                temp_date[idt].append(int(time_temp_strip.index(time_temp_strip[1]) + 1))
                                temp_date[idt].append(int(time_temp_strip[0]))

                if index == 12:
                    temp_time = list()
                    temp_time.append([])
                    temp_time.append([])
                    if val.text != "EXAM":
                        for idt, tag in enumerate(val):
                            time_temp_strip_half = str(tag.text).strip().split("-")
                            time_temp_strip = []
                            for k in time_temp_strip_half:
                                time_temp_strip.append(k.strip().split(":"))
                            if len(val) == 1:
                                temp_date[1].append(time_temp_strip)
                            elif len(val) == 2:
                                temp_date[idt].append(time_temp_strip)

        stdList[index_gid].append(temp_date)
        stdList[index_gid].append(teacher_name)

    return stdList




