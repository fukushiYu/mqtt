#!/usr/local/bin/python3
import paho.mqtt.client as mqtt
import mysql.connector
import json
import time
import pa_config as conf
import pa_packet

# todo:
#   可以将 所有的 print ,改为 fileio.write 写至log file
#   db 使用 postgresql
#   扩展trandata, 尽量往横向发展attribute，减少row
#   由命令行决定使用的 config file, import sys sys.argv

def on_connect(client, userdata, flags, rc):
    print("Connect %s MQTT: %s"%(conf.HOST,str(rc)))
    # 订阅的topic设定在 pa_config.py TOPICS 中,是一个List
    # 所以可以经过更改 import 不同名称的 pa_config,及不同的 TOPICS
    # 跑多个本程序接收不同的TOPICS
    for t in conf.TOPICS:
        client.subscribe( t+"/#" )
        print("订阅:%s/#"%(t,))

def on_message(client, userdata, msg):
    pac = pa_packet.Upacket()
    rpac = pa_packet.Upacket()
    rpac_codes, rd , do_reply = [], '', False
    # 若mysql断线或idle,则ping mysql,重新连线
    cnx.ping(True,3,3)
    cursor = cnx.cursor()
    now=time.strftime("%Y-%m-%d %X", time.localtime())
    if conf.DEBUG=="Y":
        print("--> ReceiveRawData:"+msg.topic+':'+pac.to_hex(msg.payload))
    # pdata 为接收到的payload 分解后的 list
    pdata = pac.parse(msg.payload) # pdata=[{'NAME':__,'CODE':__,'TYPE':__,'DESC':__,'VALUE':[__]}...]
    # topic是 PABOX/$imei
    topic = msg.topic
    topic_array = topic.split('/')
    imei = topic_array[1]  
    idx, time_d, display_str = 0, '', ''
    # 从DB item 取出code预设值，同时也是检验是已经注册的 imei
    cursor.execute(dbconfig['SQL']['item_attr'], (imei,)) # item dirty, item.attr01
    item_row = cursor.fetchone()
    print('--> '+now +':'+msg.topic+':Count(MessageCodes)='+str(len(pdata))) # 列印code Frame 内容
    for pd in pdata:
        print("\t("+str(idx)+')='+str(pd)) # 列印每个 code Frame 内容
        if idx==0:
            # 这里逻辑变得混乱, 变成要去判断F2的data来决定 F2的属性,其实不如增加 code F3,F4,F5...
            time_d= chr(pd['VALUE'][0]) if pd['CODE']=='F2' and pd['VALUE'][0] in [83,68,67] else ''    # F2 1 【S|D|C】
            if pd['CODE']=='ZZ' or  (pd['CODE']=='F2' and time_d=='C'):
                retain=True     # 此处做测试用，可能将来会不做,因为【他】可能收不了
            else:
                retain=False
        # 解开的资料,insert into mysql tran_data 
        r = (imei,pd['CODE'], pd['NAME'],time_d, pd['TYPE'], pd['DESC'], str(pd['VALUE']))
        cursor.execute(dbconfig['SQL']['add_trandata'], r)  # DB
        cnx.commit()
        try:
            org_code = pd['CODE']
            map_code= org_code + ( time_d if org_code=="F2" else '')
            rA=conf.MUST_REPLY_CODES[map_code]
            do_reply=True
            rd = rd+"["+map_code+"]"
        except:
            rA = {}
        reply_codes = rA
        try:
            if len(reply_codes) > 0:
                i = 0
                for k,v in reply_codes.items():
                    t = pa_packet.codeDict[k]
                    if v > 0:
                        val_arr = json.loads(item_row[v])   # item_row[position]
                        v_str = str(val_arr)
                    elif v == -1:
                        val_arr, v_str = [] , '["'+now+'"]' # timestamp
                    elif v == -10:
                        val_arr, v_str =  pd['VALUE'],str(pd['VALUE'])   
                    if k in rpac_codes:
                        pass
                    else:
                        rpac_codes.append(k)
                        rpac.insert(k,val_arr)    
                        display_str = display_str + ('' if i==0 else ',') + '"'+k+'":'+v_str
                    i += 1
        except:
            pass
        idx += 1
    # end of data loop , finish reply codes,  start publish 
    if do_reply==True: ###
        r1 = (imei, rd, '回复信息', '', '', '', "{"+display_str+"}")
        org_imei=imei
        imei += '/INIT' if retain==True else ''
        # 钉在mqtt上的
        if retain==True:
            print("Replybindata:"+imei+":"+rd+":"+rpac.to_hex(rpac.bindata)) ##        
            client.publish(imei, rpac.bindata, conf.QoS, retain)
        # 原来的
        print("Replybindata:"+org_imei+":"+rd+":"+rpac.to_hex(rpac.bindata)) ##        
        client.publish(org_imei, rpac.bindata, conf.QoS, False)
        cursor.execute(dbconfig['SQL']['add_trandata'], r1)
        cnx.commit()
        if conf.DEBUG=="Y":
            print('<-- '+time.strftime("%Y-%m-%d %X", time.localtime()) + ":Publish:"+imei+'/{'+ display_str+'}')
    pac, rpac = None, None
    cursor.close()

if __name__ == "__main__":
    dbconfig=conf.DBCNF['MYSQL']
    cnx = mysql.connector.connect(host=dbconfig['HOST'],user=dbconfig['USER'],passwd=dbconfig['PASS'],database=dbconfig['DATABASE'])
    #cnx.ping(reconnect=False, attempts=1, delay=0)
    cnx.ping(True)
    client = mqtt.Client()
    client.username_pw_set(conf.USER, conf.PASS)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(conf.HOST, conf.PORT, 60)
    print(conf.logo)
    client.loop_forever()
    cnx.close()
