import zc_id
from Xbee import *
from LCMBot import *
import time


if __name__=='__main__':
    rid = zc_id.get_id()
    xb = XbRssi('/dev/ttyUSB0')
    xb.start()
#    xb.stop_transmit()
    f = open("data.csv","w")
    try:
        i = 0
        while True:
	    print 'in-loop'
            last_RSSI = xb.get_rssi()
            last_addr = xb.get_addr()
    	    last_pkt = xb.get_data()
            data = str(last_addr) + ", " + str(i) + ", -" + str(last_RSSI) + ", " + str(last_pkt)+"\n"
            print "RSSI = -%d dBm @ address %d with pkt number %s at index %d" % ( last_RSSI, last_addr, last_pkt, i )
            f.write(data)
            i = i + 1
            time.sleep(1)
            print i
            if i>20:
                xb.send_stop_transmit_signal()
            if i>40:
                xb.send_start_transmit_signal()


    except KeyboardInterrupt:
        pass
    finally:
        f.close()
