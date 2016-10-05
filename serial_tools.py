import os
import serial
from serial.tools import list_ports
import serial_tools

class Serial_Tools(object):
    def __init__(self, ser):

        self.ser = ser
        self.waiting_for = 0

        self.show_messages = False
        
        self.wait_commands = ["X", "Y", "Z", "U", "D", "A", "T"]


    def issue(self, m):
        self.ser.write(m)
        self.waiting_for += len(m)
        if self.show_messages and m != "?":
            print "S: " + m

    def clear_waiting(self):
        r = self.ser.read(self.waiting_for)
        self.waiting_for = self.waiting_for - len(r)
        if self.show_messages and r != "?":
            print " R: " + r

    def issue_wait(self, m): # Try not to use this.
        self.issue(m)
        self.clear_waiting()
        
    def issue_safe(self, m):
        sep = []
        for char in range(len(m)):
            if m[char] in self.wait_commands:
                self.issue_wait(m[char])
            else:
                self.issue(m[char])

    def read(self, bytes):
        r = self.ser.read(bytes)
        print "  S_T.READ: " + str(r)
        return r

    def get_ports(self):
        """Returns a generator for all available serial ports"""
        if os.name == 'nt':
            # Windows
            for i in range(256):
                try:
                    s = serial.Serial(i)
                    s.close()
                    yield 'COM' + str(i + 1)
                except serial.SerialException:
                    pass
        else:
            # Unix-likes
            for port in list_ports.comports():
                yield port[0]

    def find_device(self, bs_ls = ["BS0010","BS0005"]):
        ports = (list(self.get_ports())) # Gather all coms ports
        usb = []
        if os.name == 'nt':
            usb = ports
        else:
            for i in ports: # Filter USB ports into their own list
                if (i.find("USB")) != -1:
                    usb.append(i)

        temp_ser = None
        device_found = False

        finding = True
        for port in usb:
            try:
                temp_ser = serial.Serial(port, 19200, timeout=0.2)
                temp_ser.write("?")
                model = temp_ser.read(20)[2:8]
                if model in bs_ls:
                    device_found = True
                    break # Found a device, break out.
            except:
                device_found = False

        if device_found:
            self.ser = temp_ser
            temp_ser.writeTimeout = 0.1

            return temp_ser
        else:
            return None
