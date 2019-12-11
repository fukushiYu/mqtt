#!/usr/local/bin/python3
import paho.mqtt.publish as pahopublish
import time
import pa_packet
import pa_config as conf

def pub():
    pac = pa_packet.Upacket()
    now = time.strftime("%Y-%m-%d %X", time.localtime())
    try:
        topic = conf.SUB_TOPIC + '/XXX'
        data_array=[]
        cmd="ZZ"
        message = pac.insert(cmd,data_array)
        pahopublish.single(topic= topic, payload=message, 
            qos = conf.QoS, 
            hostname=conf.HOST, 
            port=conf.PORT, 
            auth = {'username':conf.USER, 'password':conf.PASS})
    except:
        pac=None
        print(now + ":ERROR:"+topic+' message:'+cmd+"+"+str(data_array))
    else:
        pac=None
        print(now + ":Publish:"+topic+' message:'+cmd+"+"+str(data_array))


if __name__ == "__main__":
    pub()