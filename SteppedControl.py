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
        # port="/dev/ttyTHS1",                       # Jetson nano TX,RX
        # port="/dev/ttyUSB0",                       # Jetson nano USB
        # port='COM20',                              # 電腦
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

    def reconnect(self):
        self.serial_port.close()
        self.offline = True
        while self.offline:
            try:
                self.serial_port.open()
                self.offline = False
            except:
                print("Error connection")
                self.offline = True
    
    def readSerial(self):                            # 監視序列
        serialData = ""
        while(serialData == ""):                    # 直到回傳資料不為空
            try:
                if (self.serial_port.inWaiting() != 0):         # 等待序列
                    data_raw = self.serial_port.readline()      # 讀取直到"\"
                    data = data_raw.decode()                    # 解UTF-8格式
                    data = data.strip()                         # 移除頭尾無效字元空格，換行
                    
                    serialData = data
                    # Status, speeds, hitCount = data.split('\t',2)   # 以"\t"隔開
                    self.serial_port.flushInput()
            except UnicodeDecodeError:                          # 避免轉碼報錯
                print("try again")
                continue
            # except ValueError:                                  # 避免報錯
            #     print("try again")
            #     continue
        return serialData

    def sendSerial(self, sendData):
        try:
            self.serial_port.write((sendData+"\n").encode())
        except:
            print("Send erro")
            self.reconnect()



        
        

                
            
       




