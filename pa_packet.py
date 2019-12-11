#!/usr/local/bin/python3
import struct
import time
# $IME 下行, PABOX/$IME 上行
# 指令集
codeDict={
    '00':{"NAME":"SETM","TYPE":"1","DESC":"工作模式转换"}, # 1 自控 0, 外控 1
    '01':{"NAME":"PING","TYPE":"2","DESC":"连接握手(sec)"}, # 2 秒数
    '02':{"NAME":"TSYN","TYPE":"7","DESC":"时间同步"}, # 7 year_2+mon_1+mday_1+hour_1+min_1+sec_1, 7bytes
    '03':{"NAME":"OFF_","TYPE":"0","DESC":"断开连接"}, # 0
    '04':{"NAME":"GETT","TYPE":"1,2","DESC":"获取温度(°C)"}, # 1+2   通道+温度
    '05':{"NAME":"SETT","TYPE":"1,2,2","DESC":"设置温度上限和下限参数(°C)"}, # 1+2+2 通道+温度上限和温度
    '06':{"NAME":"GETF","TYPE":"1,2","DESC":"获取风扇状态(mA)"}, # 1+2 风扇电流
    '07':{"NAME":"SETF","TYPE":"1,1","DESC":"控制风扇动作"}, # 1+1 控制风扇动作
    '08':{"NAME":"GETL","TYPE":"1,1","DESC":"查询锁的状态"}, # 1+1 通道+锁状态
    '09':{"NAME":"SETL","TYPE":"1,1","DESC":"控制开锁动作"}, # 1+1 通道+锁动作
    '0A':{"NAME":"BIND","TYPE":"1,1","DESC":"绑定风扇和温度控制"}, # 1+1 风扇通道+温度通道
    '0B':{"NAME":"LOG_","TYPE":"0,-1","DESC":"终端日志获取"}, # 0 
    '0C':{"NAME":"GPS_","TYPE":"0,-1","DESC":"GPS定位经纬度信息"}, # 0 DDDDDddddNDDDDDddddE
    '0D':{"NAME":"TCOM","TYPE":"2","DESC":"通信时间间隔(sec)"}, # 2 
    '0E':{"NAME":"TSEN","TYPE":"2","DESC":"历史数据储存时间间隔(sec)"}, # 2 
    '0F':{"NAME":"VBAT","TYPE":"2","DESC":"电池电压(mV)"}, # 2 
    '10':{"NAME":"VOUT","TYPE":"2","DESC":"外来电压(mV)"}, # 2
    '11':{"NAME":"SIGN","TYPE":"1","DESC":"通信信号强度(0~31)"}, # 1
    '12':{"NAME":"CIMI","TYPE":"0,-1","DESC":"SIM卡CIMI码"}, # 0
    '13':{"NAME":"FXMA","TYPE":"2","DESC":"风扇最大的工作电流(mA)"}, # 2
    '14':{"NAME":"DOWA","TYPE":"2","DESC":"舱门开启告警时间设定(sec)"}, # 2
    '15':{"NAME":"TWAR","TYPE":"1,1","DESC":"温度通道告警"}, # 1 + 1 通道+警告
    '80':{"NAME":"VLOW","TYPE":"2","DESC":"电池过低(mV)"}, # 2 mV
    '81':{"NAME":"FLOW","TYPE":"2","DESC":"风扇堵转或者故障(mA)"}, # 2 mA
    '82':{"NAME":"DOAL","TYPE":"2","DESC":"舱门开启时间过长告警(sec)"}, # s
    '83':{"NAME":"DOTI","TYPE":"2","DESC":"舱门开启动作(sec)"}, # 2 
    '84':{"NAME":"VOVA","TYPE":"2","DESC":"外供电开始(mV)"}, # 2 mV
    '85':{"NAME":"T_AL","TYPE":"1,2","DESC":"箱体温度告警(°C)"}, # 1+2 温度*10
    'E0':{"NAME":"SERV","TYPE":"0,-1","DESC":"平台域名"}, # 0 
    'F0':{"NAME":"_ON_","TYPE":"7","DESC":"数控启动"},  # 7 year_2+mon_1+mday_1+hour_1+min_1+sec_1, 7bytes
    'F1':{"NAME":"TCCS","TYPE":"0,-1","DESC":"温控状态变更设定"}, # 0 
    'F2':{"NAME":"DATT","TYPE":"1","DESC":"传输数据时机"}, # S 开机  D 正常  C下传
    'ZZ':{"NAME":"INIT","TYPE":"S","DESC":"起始设定"}, # 0
    }
class Upacket():
    def __init__(self):
        global codeDict
        self.bindata = b''
    def __str__(self):
        return (self.to_hex(self.bindata))
    def to_hex(self,bx):
        s = ["%02X"%b for b in bx]
        return (" ".join(s))
    def insert(self,code,data=[]):
        global codeDict
        p_data, p_type, p_len = b'', codeDict[code]["TYPE"], 0
        if p_type=='2': #'01','0D','0E','0F','10','13','14','80','81','82','83','84'
            p_data, p_len = struct.pack("h",data[0]), 2 # < 表示low byte在前
        elif p_type=='1': #'00','11','F2'
            p_data, p_len=struct.pack("B",data[0]), 1
        elif p_type=='7':  #'02','F0'
            t = time.localtime(time.time())
            p_data,p_len=struct.pack("h",t.tm_year)+ struct.pack("5B",t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min,t.tm_sec) ,7
        elif p_type=='1,2': #'04','06','15','85'
            p_data,p_len=struct.pack("B",data[0]) + struct.pack("h",data[1]),3
        elif p_type=='1,2,2': #'05'
            p_data,p_len=struct.pack("B",data[0]) + struct.pack("2h",data[1],data[2]),5
        elif p_type=='1,1': #'07','08','09','0A'
            p_data,p_len=struct.pack("2B",data[0],data[1]),2
        elif p_type=='0': #'03'
            p_data,p_len = b'', 0
        elif p_type=='0,-1': #'0B','0C','12'
            p_data=data[0].encode('utf8')
            p_len=len(p_data)
        elif p_type=='S': #'ZZ'
            if code=='ZZ':
                self.bindata = code.encode()
            return self.bindata
        self.bindata = self.bindata + struct.pack("2B",int(code,16),p_len) +  p_data
        return self.bindata
    def parse(self,pac): # code + len + data
        global codeDict
        self.data ,pac_len, idx = [], len(pac), 0
        try:
            if pac[0:2].decode('utf8')=='ZZ':
                currdata={'NAME':'INIT','CODE':'ZZ','TYPE':'0','DESC':'起始数据','VALUE':[]}
                self.data.append(currdata)
                return self.data
        except:
            pass
        while idx < pac_len:
            p_code = "%02X"%pac[idx]
            idx += 1
            cr = codeDict[p_code]
            currlen=int.from_bytes(pac[idx:idx+1],byteorder='little', signed=False)
            idx += 1
            try: # pac是byte array
                tt=cr['TYPE']
                varr=[]
                if tt=="2":
                    varr.append(int.from_bytes(pac[idx:idx+2], byteorder='little', signed=True))
                elif tt=="1,1":
                    varr.append(pac[idx])
                    varr.append(pac[idx+1])
                elif tt=="1":
                    varr.append(pac[idx])
                elif tt=="7":
                    q=[]
                    q.append(int.from_bytes(pac[idx:idx+2], byteorder='little', signed=False))
                    for i in range(0,5):
                        q.append(pac[idx+i+2])
                    varr.append("%4d-%02d-%02d %02d:%02d:%02d"%(q[0],q[1],q[2],q[3],q[4],q[5]))
                elif tt=="0":
                    pass
                elif tt=="0,-1":
                    dummy=pac[idx:(idx+currlen)]
                    varr.append(dummy.decode('utf8')) 
                elif tt=="1,2":
                    varr.append(pac[idx])
                    varr.append(int.from_bytes(pac[idx+1:idx+3], byteorder='little', signed=True))
                elif tt=="1,2,2":
                    varr.append(pac[idx])
                    varr.append(int.from_bytes(pac[idx+1:idx+3], byteorder='little', signed=True))
                    varr.append(int.from_bytes(pac[idx+3:idx+5], byteorder='little', signed=True))
                idx += currlen
            except:
                pass
            currdata={'NAME':cr['NAME'],'CODE':p_code,'TYPE':cr['TYPE'],'DESC':cr['DESC'],'VALUE':varr}
            self.data.append(currdata)
            #self.data[p_code]={'NAME':cr['NAME'],'DESC':cr['DESC'],'VALUE':varr}
        return self.data

if __name__ == "__main__":
    pass
    '''
    b=Upacket()
    b.insert("00",[1])
    b.insert("00",[0])
    b.insert("02")
    b.insert("04",[1,300])
    b.insert("0B",["test"])
    b.insert("02")
    b.insert("E0",["test.com.com"])
    b.insert("F1",["a"])
    dlist=b.parse(b.bindata)
    print(b)
    import json
    print(json.dumps(dlist, ensure_ascii=False,indent=2))
    b.insert("ZZ")
    print(b)
    dlist=b.parse(b.bindata)
    print(json.dumps(dlist, ensure_ascii=False,indent=2))
    '''
