import time, threading, serial, zc_id
from xbee import XBee
from numpy import *

class XbRssi(object):
    # initialization
    def __init__(self, serial_port): 
        self.ser = serial.Serial(serial_port, 57600)
        self.xbee = XBee(self.ser)
        self.rid = zc_id.get_id()
        self.rid = self.rid.split("/",1)[1] 
        self.id = chr(int(self.rid))
        self.xbee.at(frame='A', command='MY', parameter='\x20'+chr(int(self.rid)))
        self.xbee.at(frame='B', command='CH', parameter='\x0e')
        self.xbee.at(frame='C', command='ID', parameter='\x99\x99')
        self.updateTransmitThread = threading.Thread(target=self.transmit_loop)
        self.updateTransmitThread.daemon = True
        self.updateReceiveThread = threading.Thread(target=self.receive_loop)
        self.updateReceiveThread.daemon = True
        self.transmit_peroid = 0.01     # in second

        self.response = 0
        self.rssi = 0
        self.addr = 0
        self.data = 0
        self.sendMessage = ''
        self.transmit = True

        #self.response = self.xbee.wait_read_frame()
        #self.rssi = -ord(self.response.get('rssi'))
        #self.addr = ord(self.response.get('source_addr')[1])
        #self.data = self.response.get('rf_data')

        self.pktNum = 0
        self.sendingCommand = False
        self.ser.flush()

    # define transmit and receive loop
    def transmit_loop(self):
        while True:
            self.transmit_rssi()

    def receive_loop(self):
        while True:
            self.response = self.xbee.wait_read_frame()
            self.rssi = -ord(self.response.get('rssi'))
            self.addr = ord(self.response.get('source_addr')[1])
            self.data = self.response.get('rf_data')
            #print self.data + ", RSSI = %d dBm @ address %d" % ( self.rssi, self.addr )
    
    # transmitter function
    def transmit_rssi(self):
        if (self.transmit == True):
            if (self.sendingCommand == False):
                msg = self.build_packet_prefix()
            else:
                msg = self.build_packet_prefix() + self.sendMessage
            #print "Sending Msg:" + msg
            self.xbee.tx(dest_addr='\xFF\xFF', data = msg)
            self.pktNum = self.pktNum + 1
            time.sleep(self.transmit_peroid)
        else:
            time.sleep(5)

    # get 30 received rssi values
    def get_rssi_list(self):
        rssi_list = []
        index_list = []
        
        rssi_list.append(self.rssi)
        index_list.append(self.get_index(self.data))

        i = 1
        while i < 30:
            index = self.get_index(self.data)

            if index != index_list[-1]:
                rssi_list.append(self.rssi)
                index_list.append(index)
                i = i + 1

            time.sleep(self.transmit_peroid)

        return rssi_list

    # data processing functions
    def get_max_rssi(self):
        rssi_list = self.get_rssi_list()
        rssi_max = max(rssi_list)
        return rssi_max, rssi_list

    def get_min_rssi(self):
        rssi_list = self.get_rssi_list()
        rssi_min = min(rssi_list)
        return rssi_min, rssi_list

    def get_med_rssi(self):
        rssi_list = self.get_rssi_list()
        rssi_med = median(rssi_list)
        return rssi_med, rssi_list

    def get_avg_rssi(self):
        rssi_list = self.get_rssi_list()
        rssi_avg = mean(rssi_list)
        return rssi_avg, rssi_list

    # build packet prefix
    def build_packet_prefix(self):
        return repr(self.pktNum) + "-" + str(self.rid) + "~" 

    # get specific data from a message
    def get_sender_id(self, msg):
        if msg == 0:
            return 'NO_SENDER'
        else:
            try:
                sender_start_index = msg.index('-')
                sender_end_index = msg.index('~')
                return msg[sender_start_index+1:sender_end_index]
            except:
                print "SENDER_ID_ERROR: " + msg

    def get_index(self, msg):
        if msg == 0:
            return 'NO_INDEX'
        else:
            index_end_index = msg.index('-')
            return msg[:index_end_index]

    def get_command(self, msg):
        if msg == 0:
            return 'NO_COMMAND'
        else:
            cmd_start_index = msg.index('~')
            return msg[cmd_start_index+1:]

    def get_intended_recipient(self, msg):
        if msg == 0:
             return 'NO_RECIPIENT'
        else:
            try:
                recipient_start_index = msg.index(':')
            
                recipient = msg[recipient_start_index+1:]
                if (len(msg[recipient_start_index+1:]) == 0):
                    return 0
                else:
                    return msg[cmd_start_index+1:]
            except:
                return 0

    def trim_packet(self, msg):
        if msg == 0:
            return 'NO_INDEX'
        else:
            index_end_index = msg.index('-')
            return msg[index_end_index+1:]

    def get_command_in_ack(self, msg):
        try:
            if msg == 0:
                return 'NO_COMMAND_IN_STOP_ACK'
            else:
                cmd_start_index = msg.index('=')
                cmd_end_index = msg.index(':')

                return msg[cmd_start_index+1:cmd_end_index ]
        except:
            return ''
    # start threading
    def start(self):
        self.updateTransmitThread.start()
        self.updateReceiveThread.start()

    def close(self):
        self.ser.close()
    def __del__ (self):
        self.ser.close()


if __name__=='__main__':
    xb = XbRssi('/dev/ttyUSB0')
    xb.start()
    # xb.receive_loop()
    # xb.get_rssi_list()
    rssi_max, rssi_list = xb.get_max_rssi()
    print "the maximum is: ", rssi_max
    rssi_min, rssi_list = xb.get_min_rssi()
    print "the minimum is: ", rssi_min
    rssi_avg, rssi_list = xb.get_avg_rssi()
    print "the average is: ", rssi_avg
    rssi_med, rssi_list = xb.get_med_rssi()
    print "the median is: ", rssi_med
