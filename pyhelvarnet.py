import socket
import re
import datetime

class HelvarNetClient:
    def __init__(self, server, port):
        self.server = server
        self.port = port
        # Cluster ID and Member ID are part of the internal device addresses,
        # the control device generates them using the IP address info
        self.clusterID = server.split(".")[2]
        self.memberID = server.split(".")[3]

        # Message Components
        # Message Types
        self.__COMMAND = ">"  # Command starter
        self.__NTRCOMMAND = "<"  # Internal Command starter
        self.__REPLY = "?"  # Internal Command reply
        self.__ERRORDIAG = "!"  # TODO

        # Special
        self.__TERMINATOR = "#"
        self.__ANSWER = "="

        # Delimiters
        # STDDELIM = ","
        # PARAMDELIM = ":"
        # ADDRDELIM = "."

        # Parameters of the commands
        self.__HLVSEQNUM = "Q:"  # Secuence Number - Internal commands only
        self.__HLVVER = "V:"  # HelvarNet Version - Assumes version 1
        self.__HLVCMD = "C:"  # Command
        self.__HLVACK = "A:"  # Acknowledgement - Assumes = 0 - Optional
        self.__HLVADDR = "@:"  # Address
        self.__HLVGROUP = "G:"  # Fixture group - Optional
        self.__HLVSCN = "S:"  # Scene - Optional
        self.__HLVBLOCK = "B:"  # Block - Optional
        self.__HLVFADET = "F:"  # Fade Time - Optional
        self.__HLVLEVEL = "L:"  # Light Level
        self.__HLVPROP = "P:"  # Proportion
        self.__HLVDISP = "D:"  # Display Screen
        self.__HLVTIME = "T:"  # Time
        self.__HLVLAT = "N:"  # Latitude
        self.__HLVLON = "E:"  # Longitude
        self.__HLVTIMEZ = "Z:"  # Time Zone Difference
        self.__HLVDST = "Y:"  # Daylight Saving Time
        self.__HLVCLS = "K:"  # Constant Light Scene - Optional
        self.__HLVFSE = "O:"  # Force Store Scene - Optional

    def __GetCurrentTimeEpoch():
        epoch = datetime.datetime.now().strftime('%s')
        return str(epoch)

    def __SendTCPMessageAndRecv(self, HOST, PORT, Message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            try:
                s.connect((HOST, PORT))
                s.sendall(Message.encode())
                data = s.recv(1024)
                return data
            except socket.error:
                return None

    def __SendTCPMessageAndContinue(self, HOST, PORT, Message):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(Message.encode())


    ################# Query Commands #################
    def QueryClusters(self):
        ''' Returns comma separates list of clusters in the format of ?V:1,C:101=1,2,253# from
        the router.
        then we create a python list for easy parsing
        '''
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "101" +\
            self.__TERMINATOR
        print("Clusters Queried.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group().split(',')
        return received

    def QueryRouters(self):
        ''' Returns comma separates list of routers in the format of ?V:1,C:102,@253=252,253,254# from the router.
        then we create a python list for easy parsing
        '''
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "102" + "," +\
            "@" + self.clusterID +\
            self.__TERMINATOR
        print("Routers Queried.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group().split(',')
        return received

    def QueryLastSceneInBlock(self, group, block):
        ''' Returns the last scene in block, format is ?V:1,C:103,G:5,B:2=4#
        '''
        group = str(group)
        block = str(block)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "103" + "," +\
            self.__HLVGROUP + group + "," +\
            self.__HLVBLOCK + block + "," +\
            self.__TERMINATOR
        print("Last Scene Queried.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryDeviceType(self, subnet, device):
        ''' There's a full description of the device types in "DALI Device Type Information.txt"
        I will just give you the return of the router, IDK how helvar does the conversion from HEX to ASCII in this case (WTF Helvar)
        '''
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "104" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Queried device type.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryGroupDescription(self, group):
        '''
        Returns the group description in string format
        '''
        group = str(group)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "105" + "," +\
            self.__HLVGROUP + group +\
            self.__TERMINATOR
        print("Queried group description.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryDeviceDescription(self, subnet, device):
        '''
        Returns the device description in string format
        '''
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "106" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Queried device description")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryDeviceState(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        # Check device state table
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "110" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Queried device state")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryDeviceIsDisabled(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "111" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Checking if device is disabled.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        if received == "1":
            return True
        elif received == "0":
            return False

    def QueryDeviceIsMissing(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "113" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Checking if device is missing.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        if received == "1":
            return True
        elif received == "0":
            return False

    def QueryDeviceIsFaulty(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "114" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Checking if device is faulty.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        if received == "1":
            return True
        elif received == "0":
            return False

    def QueryEmergencyBatteryFailure(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "129" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Checking if battery is faulty.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        if received == "1":
            return True
        elif received == "0":
            return False

    def QueryDeviceMeasurement(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "150" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Retrieving measurements...")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryDeviceInputState(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "151" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Asking for the device input state...")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryLoadLevel(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "152" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Asking for the load level...")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    # POWER
    def QueryDevicePowerCompsumption(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "160" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Asking for the device power consumption...")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryGroupPowerCompsumption(self, group):
        group = str(group)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "161" + "," +\
            self.__HLVGROUP + group +\
            self.__TERMINATOR
        print("Asking for the group power consumption...")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    # EMERGENCY TEST
    def QueryEmergencyFunctionTestTime(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "170" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Asking the emergency function test time.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryEmergencyFunctionTestState(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "171" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Asking the emergency function test state.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryEmergencyDurationTestTime(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "172" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Asking the emergency duration test time.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryEmergencyDurationTestState(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "173" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Asking the emergency duration test state.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryEmergencyBatteryCharge(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "174" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Checking emergency battery charge level.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryEmergencyBatteryTime(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "175" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Checking emergency battery time left.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryEmergencyTotalLampTime(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "176" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Checking emergency total lamp time.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryTime(self):
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "185" +\
            self.__TERMINATOR
        print("Asking the time.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryLongitude(self):
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "186" +\
            self.__TERMINATOR
        print("Asking the longitude.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryLatitude(self):
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "187" +\
            self.__TERMINATOR
        print("Asking the latitude.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryTimeZone(self):
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "188" +\
            self.__TERMINATOR
        print("Asking the timezone.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryDST(self):
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "189" +\
            self.__TERMINATOR
        print("Asking if we are in daylight savings.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        if received == "1":
            return True
        elif received == "0":
            return False

    def QuerySWVersion(self):
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "190" +\
            self.__TERMINATOR
        print("Asking the software version.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    def QueryHelvarNetVersion(self):
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "191" +\
            self.__TERMINATOR
        print("Asking the HelvarNet version.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

    ################# Configuration Commands #################
    # Scenes
    def StoreSceneForGroup(self, group, force: bool, block, scene, level):
        '''
        For now helvar only gives us the interface to change scene levels, no colors yet :((
        The "Force" flag overwrites scenes with "ignore" set.
        '''
        group = str(group)
        block = str(block)
        scene = str(scene)
        level = str(level)
        force = "1" if force == True else "0"
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "201" + "," +\
            self.__HLVGROUP + group + "," +\
            self.__HLVFSE + force + "," +\
            self.__HLVBLOCK + block + "," +\
            self.__HLVSCN + scene + "," +\
            self.__HLVLEVEL + level +\
            self.__TERMINATOR
        print("Stored Scene for group " + group + ".")
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    def StoreSceneOnDevice(self, subnet, device, force: bool, block, scene, level):
        subnet = str(subnet)
        device = str(device)
        block = str(block)
        scene = str(scene)
        level = str(level)
        force = "1" if force == True else "0"
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "202" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__HLVFSE + force + "," +\
            self.__HLVBLOCK + block + "," +\
            self.__HLVSCN + scene + "," +\
            self.__HLVLEVEL + level +\
            self.__TERMINATOR
        print("Stored Scene for device " + device + ".")
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    def StoreCurrSceneForGroup(self, group, force: bool, block, scene):
        group = str(group)
        block = str(block)
        scene = str(scene)
        force = "1" if force == True else "0"
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "203" + "," +\
            self.__HLVGROUP + group + "," +\
            self.__HLVFSE + force + "," +\
            self.__HLVBLOCK + block + "," +\
            self.__HLVSCN + scene +\
            self.__TERMINATOR
        print("Stored Scene for group " + group + ".")
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    def StoreCurrSceneForDevice(self, subnet, device, force: bool, block, scene):
        subnet = str(subnet)
        device = str(device)
        block = str(block)
        scene = str(scene)
        force = "1" if force == True else "0"
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "204" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__HLVFSE + force + "," +\
            self.__HLVBLOCK + block + "," +\
            self.__HLVSCN + scene +\
            self.__TERMINATOR
        print("Stored Scene for device " + device + ".")
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)
    # Emergecy Lights

    def ResetGroupEmergencyLampBatTime(self, group):
        group = str(group)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "205" + "," +\
            self.__HLVGROUP + group +\
            self.__TERMINATOR
        print("Resetted emergency lights for group: " + group + ".")
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    def ResetDeviceEmergencyLampBatTime(self, subnet, device):
        subnet = str(subnet)
        device = str(device)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "206" + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Resetted emergency lights for device: " +
              device + "on subnet: " + subnet + ".")
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    ## Time and location
    def SetRouterCurrentDateTime(self):
        epoch = self.__GetCurrentTimeEpoch()
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "241" + "," +\
            self.__HLVTIME + epoch +\
            self.__TERMINATOR
        print("Updated time and date using the epoch: " + epoch)
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    def SetLatitude(self):
        print("To be developed")

    def SetLongitude(self):
        print("To be developed")

    def SetTimezone(self, hours):
        secs = hours * (60 ** 2)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "244" + "," +\
            self.__HLVTIMEZ + secs +\
            self.__TERMINATOR
        print("We are in timezone hours: " + hours)
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    def SetDaylightSavingTime(self, isDst: bool):
        dst = "1" if isDst else "0"
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "245" + "," +\
            self.__HLVDST + dst +\
            self.__TERMINATOR
        print("Daylight saving time enabled: " + str(isDst))
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    ################# Control Commands #################

    def RecallSceneOnGroup(self, group, block, scene, fade):
        """It sends an string that looks like this:
        >V:1,G:1,B:1,S:1,F:300#
        via TCP socket to the address of the Helvar dali router you defined
        while you instantiated the object"""
        group = str(group)
        block = str(block)
        scene = str(scene)
        fade = str(fade)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "11" + "," +\
            self.__HLVGROUP + group + "," +\
            self.__HLVBLOCK + block + "," +\
            self.__HLVSCN + scene + "," +\
            self.__HLVFADET + fade +\
            self.__TERMINATOR
        print("Recalled Scene for group " + group + ".")
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    def RecallSceneOnDevice(self, subnet, device, block, scene, fade):
        ''' If ip is 192.168.1.10 for the helvar router,
        192.168.<- this is removed | this is the starting prefix of the devide address ->1.10
        Next goes the DALI or DMX subnet id, 1 if theres only 1.
        And then the device id (Dali address)
        The full device address for a device with dali address 1 and subnet 1, looks like:
        1.10.1.1
        '''
        subnet = str(subnet)
        device = str(device)
        block = str(block)
        scene = str(scene)
        fade = str(fade)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "12" + "," +\
            self.__HLVBLOCK + block + "," +\
            self.__HLVSCN + scene + "," +\
            self.__HLVFADET + fade + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Recalled Scene " + scene + " for device " +
              device + " on subnet " + subnet + ".")
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    def SetGroupAbsoluteLevel(self, group, level, fade):
        group = str(group)
        level = str(level)
        fade = str(fade)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "13" + "," +\
            self.__HLVGROUP + group + "," +\
            self.__HLVLEVEL + level + "," +\
            self.__HLVFADET + fade +\
            self.__TERMINATOR
        print("Level Set!")
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    def SetDeviceAbsoluteLevel(self, subnet, device, level, fade):
        subnet = str(subnet)
        device = str(device)
        level = str(level)
        fade = str(fade)
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "14" + "," +\
            self.__HLVLEVEL + level + "," +\
            self.__HLVFADET + fade + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Level Set!")
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    def SetGroupLevelAbsoluteProportion(self):
        print("To be developed")

    def SetDeviceLevelAbsoluteProportion(self):
        print("To be developed")

    def SetGroupLevelModifyProportion(self):
        print("To be developed")

    def SetDeviceLevelModifyProportion(self):
        print("To be developed")