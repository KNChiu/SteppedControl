# =========== install ===========
# pip install pyserial
# =========== portset ===========
# port="/dev/ttyTHS1",                   # Jetson nano TX,RX
# port="/dev/ttyUSB0",                   # Jetson nano USB
# port='COM2',                           # 電腦


import time
import serial
# import io
# import threading

class Stepped_API():
    def __init__(self, serialPort, baudrate, toolmode=False):
        # serialPort="/dev/ttyTHS1",                       # Jetson nano TX,RX
        # serialPort="/dev/ttyUSB0",                       # Jetson nano USB
        # serialPort='COM20',                              # 電腦
        self.serialPort = serialPort
        self.baudrate = baudrate
        self.offline = False
        self.motoIsmoving = True
        self.setSerial()
        if toolmode==False:
            self.setMoto()
            time.sleep(0.1)
            self.motoZeroset()
            print("init Finish")

    def setSerial(self):                                # 設定連線通道
        self.serial_port = serial.Serial(
            port=self.serialPort,            
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,              # 8bit
            parity=serial.PARITY_NONE,              # 無同位檢查
            stopbits=serial.STOPBITS_ONE,           # 1停止位元
            xonxoff=True,                           # 流量控制
            timeout=10.0                            # 連線超時設定
        )
        time.sleep(0.1)

    def reconnect(self):                                # Serial port 重新連線
        self.serial_port.close()                    # 關閉 Serial port
        self.offline = True                         # 斷線旗標
        while self.offline:                         # 檢測是否回復
            try:
                self.serial_port.open()             # 開啟 Serial port
                self.offline = False                # 斷線旗標
            except:
                print("Error connection")
                self.offline = True                 # 斷線旗標
                continue
    
    def readSerial(self, strChar=True):                 # 監視序列
        serialData = ""                             # 讀取到的資料
        timeOutcheck = False                        # timeout 檢查旗標
        timestart = 0                               # timeout 計時
        while(serialData == ""):                    # 直到回傳資料不為空
            try:
                if timeOutcheck == False:           # 是否為檢察狀態
                    timestart = time.time()         # 開始計時
                    timeOutcheck = True             # 檢察狀態
                else:
                    if time.time() - timestart < 5 and timestart != 0:      # 是否超過5秒且有開始計時
                        if (self.serial_port.inWaiting() != 0):             # 等待序列(緩存中的字節數)
                            if strChar == True:                             # 字串模式
                                data_raw = self.serial_port.readline()      # 讀取直到"\n"
                            elif strChar == False:                          # 字元模式
                                data_raw = self.serial_port.read()          # 讀取1位元

                            data = data_raw.decode()                        # 解UTF-8格式
                            serialData = data.strip()                       # 移除頭尾無效字元空格，換行
                            self.serial_port.flushInput()                   # 清除輸入暫存器    
                    else:
                        print("time out:", time.time() - timestart)
                        break

            except UnicodeDecodeError:                          # 轉碼報錯
                print("UnicodeDecodeError")
                continue

            except TypeError as e:
                print('erro:', e)
                self.reconnect()
                continue

            except ValueError:                                  # 參數錯誤
                print("ValueError")
                continue

            except Exception as e:
                print("Get erro", e)

        return serialData

    def sendSerial(self, sendData, willreturn=True):    # 傳送序列副程式
        time.sleep(0.01)
        try:
            sendData = sendData + '\r\n'                                # 加入輸入與換行符號
            # print(sendData.encode('utf-8'))
            self.serial_port.write(sendData.encode('utf-8')) 
            time.sleep(0.05)
            if willreturn:                                              # 是否回傳狀態
                if sendData == 'r\r\n':                                 # 由於r(及時告知目前平台是否有移動)指令僅回傳1位元
                    returnCMD = self.readSerial(strChar=False)          # 讀取回應(字元模式)
                else:
                    returnCMD = self.readSerial(strChar=True)           # 讀取回應(字串模式)
                return returnCMD
        except Exception as e:
            print("Send erro", e)
            self.reconnect()                                            # 重啟 Serial port

    def checkMoto(self):                                # 確認馬達狀態
        self.motoIsmoving = True                                        # 馬達狀態旗標
        while self.motoIsmoving:
            time.sleep(0.01)
            check = self.sendSerial('r', willreturn=True)
            if check == 'L':
                self.motoIsmoving = False
            elif check == '.':
                self.motoIsmoving = True
            else:
                print("check moto is erro!")
                return False
        time.sleep(0.01)
        
        
    def setMoto(self):                                  # 設定馬達初始化
        self.sendSerial(":SI3000,16000,1000", willreturn=False)         # 改為高速控制器
        # self.sendSerial(":SI3000,8000,1000", willreturn=False)          # 一般速度控制器

    def motoAbsolute(self, lift, rotated):                              # 絕對座標控制(:P1000,1000,0)(步)
        motoCMD = ":P" + str(lift) + "," + str(rotated) + ",0"         
        self.sendSerial(motoCMD, willreturn=False) 
        self.checkMoto()

    def motoRelative (self, lift, rotated):                             # 相對座標控制(:F1000,1000,0)(步)
        motoCMD = ":F" + str(lift) + "," + str(rotated) + ",0"          
        self.sendSerial(motoCMD, willreturn=False)   
        self.checkMoto()

    def lift_absolute(self, lift):                                      # 升降台絕對座標控制(:X1000)(步)
        motoCMD = ":X" + str(lift)         
        self.sendSerial(motoCMD, willreturn=False) 
        self.checkMoto()

    def whirl_relative (self, angle):                                   # 旋轉台相對座標控制(:V1000)(度)
        # motoCMD = ":V" + str(angle * 400)                             # 1:45旋轉台
        motoCMD = ":V" + str(angle * 100)                               # 1:90旋轉台
        self.sendSerial(motoCMD, willreturn=False)   
        self.checkMoto()
 
    def motoZeroset(self):                                              # 座標歸零
        time.sleep(1)
        self.motoRelative(100000, 0)                                    # 相對座標控制(強制移動升降台到極限位置)
        # self.motoRelative(0, -500000)                                 # 相對座標控制(強制移動旋轉台到極限位置)

        self.checkMoto()
        while self.motoIsmoving:
            print(self.motoIsmoving)

        if self.motoIsmoving == False:
            self.sendSerial(":SP0,0,0", willreturn=False)
    
    def moto_whirl_zeroset(self):                                       # 旋轉台歸零
        while self.motoIsmoving:
            print(self.motoIsmoving)

        if self.motoIsmoving == False:
            self.sendSerial(":SY0", willreturn=False)

    def returnCoordinate(self):                                         # 回傳座標資訊
        return self.sendSerial(':RP')

    def stopMoto(self):                                                 # 立即停止
        return self.sendSerial(':b', willreturn=False)



if __name__ == '__main__':
    Stepped = Stepped_API(serialPort='COM2', baudrate=9600, toolmode=False)  # 初始化(COM, baudrate, toolmode)
    print("--------------------")
    time.sleep(1)
    
    
    # Stepped.lift_absolute(50000)                           # 升降台絕對控制
    # print(Stepped.returnCoordinate())                       # 回傳座標資訊
    
    start = time.time()
    Stepped.whirl_relative(360)
    print(time.time()-start)
    # for i in range(10):
    #     print("==============", i+1, "==============")
    #     Stepped.moto_whirl_zeroset()                        # 旋轉台歸零 
    #     Stepped.lift_absolute(-10000*(i+1))                 # 升降台絕對座標控制(步)
    #     print(Stepped.returnCoordinate())                   # 回傳座標資訊
    #     for j in range(12):
    #         Stepped.whirl_relative(30)                      # 旋轉台相對座標控制(度)
    #         print(Stepped.returnCoordinate())               # 回傳座標資訊
    #         time.sleep(2)

        