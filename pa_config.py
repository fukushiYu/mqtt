DEBUG="Y"
## MQTT
HOST = "iothub.proadvancer.com" #139.198.19.224" 
PORT = 1883
USER = "pabox"
PASS = "1qaz2wsx3edc"
QoS  = 1
HTTP = 9000
SUB_TOPIC = "PABOX"
# Subscribe 的 Topics
TOPICS = [SUB_TOPIC]
# 订阅得到的msg.code ,设定发布回去的code及内容
MUST_REPLY_CODES = {
    # 02 05 0D 0E 14 82 E0
    #"02": {"02" : -1},     # 空  +
    #"05": {"05" :  1},     # item.attr02 (源自GET_SQL.item_attr) +
    #"09": {"09" :  2},     # item.attr03  +
    #"0D": {"0D" :  3},     # item.attr04  +
    #"0E": {"0E" :  4},     # item.attr05  +
    #"14": {"14" :  5},     # item.attr06  +
    #"82": {"82" :  6},     # item.attr07  +
    #"E0": {"E0" :  7},     # item.attr08  +
    #"F1": {"F1" :  8},     # item.attr09  +
    "F2S": {"02" : -1 , "82" : 6},
    "F2D": {"02" : -1 , "82" : 6}, 
    "F2C":  {"02" : -1,"05" : 1,"09":2 ,"0D" : 3,"0E" : 4, "14" : 5,  "E0" : 7, "F1" : 8, },
    "DIRTY":{"02" : -1,"05" : 1,"09":2 ,"0D" : 3,"0E" : 4, "14" : 5,  "E0" : 7,},
    "ZZ":   {"02" : -1,"05" : 1,"09":2 ,"0D" : 3,"0E" : 4, "14" : 5,  "E0" : 7,},
    }


## mysql
DBCNF={"MYSQL":
            { 'HOST':"127.0.0.1",
              'USER':"iot",
              'PASS':"iot",
              'DATABASE':'pabox',
              'SQL':{
                "add_trandata":("INSERT INTO `pabox`.`trandata`(`imei`,`code`,`code_name`,`seq`,`time_d`,`attr01`,`desc`,`data`) VALUES (%s, %s, %s, 1, %s, %s, %s, %s)"),
                "trandata":("SELECT * from `pabox`.`trandata` order by `line_id` desc limit 100"),
                "item":("SELECT * from `pabox`.`item`"),
                "item_attr":("SELECT attr01,attr02,attr03,attr04,attr05,attr06,attr07,attr08,attr09,attr10 from `pabox`.`item` where `imei`= %s"),
                "item_clear":("Update `pabox`.`item` set `attr01`='' WHERE `imei`= %s "),
                "item_on":("Update `pabox`.`item` set `on_time`= now() WHERE `imei` = %s "),
                }
            },
        'POSTGRESQL':
                {'HOST':"host=127.0.0.1",
                'USER':"user=iot password=iot",
                'PORT':"port=5432",
                'DATABASE':'dbname=pabox',
                'SQL':{
                    "add_trandata":('INSERT INTO pabox.trandata(imei,code,code_name,seq,time_d,attr01,"desc","data") VALUES (%s, %s, %s, 1, %s, %s, %s, %s)'),
                    "trandata":('SELECT * from pabox.trandata order by line_id desc limit 100'),
                    "item":('SELECT * from pabox.item'),
                    "item_attr":('SELECT attr01,attr02,attr03,attr04,attr05,attr06,attr07,attr08,attr09,attr10 from pabox.item where imei= %s'),
                    "item_clear":('Update pabox.item set attr01='' WHERE imei= %s '),
                    "item_on":('Update pabox.item set on_time= now() WHERE imei = %s '),
                }
            },
    }

logo='''
___________________________________________________________
 _______  __   __  ___   _  __   __  _______  __   __  ___  
|       ||  | |  ||   | | ||  | |  ||       ||  | |  ||   | 
|    ___||  | |  ||   |_| ||  | |  ||  _____||  |_|  ||   | 
|   |___ |  |_|  ||      _||  |_|  || |_____ |       ||   | 
|    ___||       ||     |_ |       ||_____  ||       ||   | 
|   |    |       ||    _  ||       | _____| ||   _   ||   | 
|___|    |_______||___| |_||_______||_______||__| |__||___| 
-----------------------------------------------------------
'''
