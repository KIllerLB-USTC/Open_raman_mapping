import serial
import serial.tools.list_ports
import time

class ASI_control:
    def __init__(self):
       self.ser = None
       self.mappingpatharray = []
       self.testx=0
       self.testy=0
       self.refactor = 9.8
       self.conutdown_time = 2
       self.port_list = []
       self.stop_signal = False

    def avalable_serial_asi(self):
                # 获取所有串口设备端口
        self.port_list = list(serial.tools.list_ports.comports())
        # 打印端口信息
        
        if self.port_list:
            print("avaliable Port：")
            for port in self.port_list:
                print(port.device)
                print(port.name)
        else:
            print("No avaliable Port")
        
    def select_available_ports(self):
        select_port = input("Please select the port: ")
        for port in self.port_list:
            if port.name == select_port:
               self.ser = serial.Serial(port.device, 9600, timeout=1)
               print(self.ser.name)
               print("Port selected")
            else:
                print("Port not found")

    def ASI_XY_control_Array(self):
        if self.ser != None:
            for item in self.mappingpatharray:
                if self.stop_signal:
                    break
                x,y,id = item
                x = int(round(x*self.refactor,0))
                y = int(round(y*self.refactor,0))
                self.ser.write(f'M X={x} Y={y} Z=0 \r'.encode('utf-8'))
                print(f'moving{id} to {x},{y}')
                time.sleep(self.conutdown_time)
        else:
            print("Please select the port first")

    def ASI_XY_move_single(self,x,y):
        if self.ser != None:
            x = int(round(-x*float(self.refactor),0))
            y = int(round(y*float(self.refactor),0))
            self.ser.write(f'M X={x} Y={y} \r'.encode('utf-8'))
            print(f'moving to {x},{y}')
            time.sleep(self.conutdown_time)
        else:
            print("Please select the port first")
    def stop_sginal_change(self):
        if not self.stop_signal:
            self.stop_signal = True

    def ASI_XY_test(self):
        self.ser.write(f'M X={self.x} Y={self.y} Z=0 \r'.encode('utf-8'))
        


# ASI = ASI_control()
# ASI.avalable_serial_asi()
# ASI.mappingpatharray = [[1,2,3],[4,5,6],[7,8,9]]
# ASI.ASI_XY_control()