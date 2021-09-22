# =========== install ===========
# pip install pyserial
# =========== portset ===========
# port="/dev/ttyTHS1",                   # Jetson nano TX,RX
# port="/dev/ttyUSB0",                   # Jetson nano USB
# port='COM20',                          # 電腦


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
        
        # self.CMDARRARY = ["NULL", b"START\n", b"STOP\n", b"RESPOND\n", b"SPEEDUP\n"]  # 預設指令

    def setSerial(self):      # 設定連線通道
        self.serial_port = serial.Serial(
            port=self.serialPort,            
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,              # 8bit
            parity=serial.PARITY_NONE,              # 檢查
            stopbits=serial.STOPBITS_ONE,           # 停止位元
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
    

    def readSerial(self):                            # 監視序列
        serialData = ""
        while(serialData == ""):                    # 直到回傳資料不為空
            try:
                if (self.serial_port.inWaiting() != 0):         # 等待序列(緩存中的字節數)
                    data_raw = self.serial_port.readline()      # 讀取直到"\n"
                    data = data_raw.decode()                    # 解UTF-8格式
                    data = data.strip()                         # 移除頭尾無效字元空格，換行
                    
                    serialData = data
                    self.serial_port.flushInput()

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

        return serialData


    def sendSerial(self, sendData):
        try:
            self.serial_port.write((sendData+"\n").encode())    
        except:
            print("Send erro")
            self.reconnect()                                    # 重啟 Serial port
    

    def motoAbsolute(self, rotated, lift):
        motoCMD = ":PX0" + ",Y" + str(rotated) + ",Z" + str(lift)           # 絕對座標控制(:PX1000,Y1000,Z1000)
        self.sendSerial(motoCMD.encode('utf-8').strip() + b"\n")            # 轉為 bytes
        motoGET = self.readSerial()                                         # 讀取回應
        return_X, rotatedGET, liftGET = motoGET.split('\t',2)                # 以"\t"隔開
        return rotatedGET, liftGET

if __name__ == '__main__':
    Stepped = Stepped_API(serialPort='COM20', baudrate=9600)
    rotatedGET, liftGET = Stepped.motoAbsolute(100, 200)
    print("移動後絕對座標 :", rotatedGET, liftGET)


        
        

                
            
       




