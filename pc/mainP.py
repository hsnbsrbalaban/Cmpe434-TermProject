import bluetooth
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

host_mac='00:17:E9:BA:84:C6' # robot's mac address
port=4
backlog=1
size=9
s=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
s.bind(("", port))
s.listen(backlog)

try:
    client, clientInfo = s.accept()
    while True:
        data = client.recv(size)
        if data:
            print(data)
            
            # client.send(data) # Echo back to client
except:	
    print("Closing socket")
    client.close()
    s.close()