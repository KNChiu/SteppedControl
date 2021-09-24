# =========== install ===========
# pip install pyserial
# =========== portset ===========
# port="/dev/ttyTHS1",                   # Jetson nano TX,RX
# port="/dev/ttyUSB0",                   # Jetson nano USB
# port='COM2',                           # 電腦


import time
import serial
import io
import threading

class Stepped_API():
    def __init__(self, serialPort, baudrate):
        # serialPort="/dev/ttyTHS1",                       # Jetson nano TX,RX
        # serialPort="/dev/ttyUSB0",                       # Jetson nano USB
        # serialPort='COM20',                              # 電腦
        self.serialPort = serialPort
        self.baudrate = baudrate
        self.offline = False
        self.setSerial()

    def setSerial(self):                            # 設定連線通道
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


    def reconnect(self):                            # Serial port 重新連線
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
    

    def readSerial(self, strChar=True):             # 監視序列
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


    def sendSerial(self, sendData, willreturn=True):
        try:
            sendData = sendData + '\r\n'                                # 加入輸入與換行符號
            self.serial_port.write(sendData.encode('utf-8')) 
            time.sleep(0.001)

            if willreturn:                                              # 是否回傳狀態
                if sendData == 'r\r\n':                                 # 由於r(及時告知目前平台是否有移動)指令僅回傳1位元
                    returnCMD = self.readSerial(strChar=False)          # 讀取回應(字元模式)
                else:
                    returnCMD = self.readSerial(strChar=True)           # 讀取回應(字串模式)

                return returnCMD
        except Exception as e:
            print("Send erro", e)
            self.reconnect()                                    # 重啟 Serial port
    

    def motoAbsolute(self, lift, rotated):
        motoCMD = ":P" + str(lift) + "," + str(rotated) + ",0"          # 絕對座標控制(:P1000,1000,0)
        self.sendSerial(motoCMD, willreturn=False)                      
        # return_X, rotatedGET, liftGET = motoGET.split('\t',2)           # 以"\t"隔開
        # return rotatedGET, liftGET
    
    def motoRelative (self, lift, rotated):
        motoCMD = ":F" + str(lift) + "," + str(rotated) + ",0"          # 相對座標控制(:F1000,1000,0)
        self.sendSerial(motoCMD, willreturn=False)                      
        # return_X, rotatedGET, liftGET = motoGET.split('\t',2)           # 以"\t"隔開
        # return rotatedGET, liftGET

if __name__ == '__main__':
    Stepped = Stepped_API(serialPort='COM2', baudrate=9600)
    # rotatedGET, liftGET = Stepped.motoAbsolute(-1000, 500)
    # print("移動後絕對座標 :", rotatedGET, liftGET)

    # returnCMD = Stepped.sendSerial(':F1000,-500,0')
    returnCMD = Stepped.sendSerial(':RP')
    print(returnCMD)

    # Stepped.motoRelative(-1000, 500)
    # Stepped.motoAbsolute(-80000, 2000)


    
    


        
        

                
            
       




