import pyhelvarnet
import time

helvar = pyhelvarnet.HelvarNetClient("127.0.0.1", 50000)
helvar.RecallSceneOnGroup(10,1,6,500)
#print(helvar.QueryDeviceIsDisabled("1","1"))
