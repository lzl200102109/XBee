from xbee import XBee
import serial, time, zc_id

def main():
    """
    Sends an API AT command to read the lower-order address bits from 
    an XBee Series 1 and looks for a response
    """
    ser = serial.Serial('/dev/ttyUSB0', 57600)
    xbee = XBee(ser)
    rid = zc_id.get_id()
    rid = rid.split("/",1)[1] 
    xbee.at(frame='A', command='MY', parameter='\x20'+chr(int(rid)))
    xbee.at(frame='B', command='CH', parameter='\x0e')
    xbee.at(frame='C', command='ID', parameter='\x99\x99')
    f = open("data.csv","w")    
    try:
        i = 0
        while(1):
            response = xbee.wait_read_frame()
            print response
            lastRSSI = ord(response.get('rssi'))
            lastAddr = response.get('source_addr')
            print "RSSI = -%d dBm @ %d at index %d" % (lastRSSI,ord(lastAddr[1]), i)
            data = str(i) + ", -" + str(lastRSSI) +"\n"
            f.write(data)
            i = i+1
    except KeyboardInterrupt:
        pass
    finally:
        f.close()
        ser.close()

if __name__ == '__main__':
    main()
