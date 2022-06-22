import pyhelvarnet
import time

helvar = pyhelvarnet.HelvarNetClient("127.0.0.1", 50000)

print(helvar.QueryDeviceIsDisabled("1","1"))
