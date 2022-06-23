# PyHelvarnet
This is a library that allows communication with Helvar™  compatible products

I tested it a bit on a real device, and is done following the Helvar™ documentation on the protocol.

You can just add the pyhelvarnet.py file to your program folder and use it like this:

```python
import pyhelvarnet
# Create the object configuring the IP and port of the Helvar™ device
dalirouter = pyhelvarnet.HelvarNetClient("192.168.0.200", 50000)

# Print the result of the query (subnet, device)
print(dalirouter.QueryDeviceIsDisabled("1","1"))

# Recall on group 10, block 1, scene 6 with 5 seconds of fade
dalirouter.RecallSceneOnGroup("10","1","6","500")
```
Queries return values with the response of the device.

Control commands does not return anything.

# Disclaimer

Halvar™ is a registered trademark of Helvar Ltd.

This software is not officially endorsed by Helvar Ltd in any way.

The authors of this software provide no support, guarantees, or warranty for its use, features, safety, or suitability for any task. We do not recommend you use it for anything at all, and we don't accept any liability for any damages that may result from its use.

This software is licensed under the GNU GPL 3.0 See the LICENSE file for more details.