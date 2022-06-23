import socket
import re


class HelvarNetClient:
    def __init__(self, server, port):
        self.server = server
        self.port = port
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

    def QueryLastSceneInBlock(self, group: str, block: str):
        ''' Returns the last scene in block, format is ?V:1,C:103,G:5,B:2=4#
        '''
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

    def QueryDeviceType(self, subnet: str, device: str, ):
        ''' There's a full description of the device types in "DALI Device Type Information.txt"
        I will just give you the return of the router, IDK how helvar does the conversion from HEX to ASCII in this case (WTF Helvar)
        '''
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

    def QueryGroupDescription(self, group: str):
        '''
        Returns the group description in string format
        '''
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

    def QueryDeviceDescription(self, subnet: str, device: str):
        '''
        Returns the device description in string format
        '''
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

    def QueryDeviceState(self, subnet: str, device: str):
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

    def QueryDeviceIsDisabled(self, subnet: str, device: str):
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

    def QueryDeviceIsMissing(self, subnet: str, device: str):
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

    def QueryDeviceIsFaulty(self, subnet: str, device: str):
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

    def QueryEmergencyBatteryFailure(self, subnet: str, device: str):
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

    def QueryDeviceMeasurement(self, subnet: str, device: str):
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

    def QueryDeviceInputState(self, subnet: str, device: str):
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

    def QueryLoadLevel(self, subnet: str, device: str):
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
    def QueryDevicePowerCompsumption(self, subnet: str, device: str):
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

    def QueryGroupPowerCompsumption(self, group: str):
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
    def QueryEmergencyFunctionTestTime(self, subnet: str, device: str):
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

    def QueryEmergencyFunctionTestState(self, subnet: str, device: str):
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

    def QueryEmergencyDurationTestTime(self, subnet: str, device: str):
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

    def QueryEmergencyDurationTestState(self, subnet: str, device: str):
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

    def QueryEmergencyBatteryCharge(self, subnet: str, device: str):
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

    def QueryEmergencyBatteryTime(self, subnet: str, device: str):
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

    def QueryEmergencyTotalLampTime(self, subnet: str, device: str):
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
        print("Asking the helvarNet version.")
        print("Sent command looks like: " + message)
        received = self.__SendTCPMessageAndRecv(
            self.server, self.port, message)
        received = re.search(
            "(?<=\=).*(?=#)", str(received)).group()
        return received

# BOOKMARK - PAGE 38
    ################# Control Commands #################

    def RecallSceneOnGroup(self, group: str, block: str, scene: str, fade: str):
        """It sends an string that looks like this: 
        >V:1,G:1,B:1,S:1,F:300# 
        via TCP socket to the address of the Helvar dali router you defined 
        while you instantiated the object"""
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

    def RecallSceneOnDevice(self, subnet: str, device: str, block: str, scene: str, fade: str):
        ''' If ip is 192.168.1.10 for the helvar router, 
        192.168.<- this is removed | this is the starting prefix of the devide address ->1.10
        Next goes the DALI or DMX subnet id, 1 if theres only 1.
        And then the device id (Dali address)
        The full device address for a device with dali address 1 and subnet 1, looks like:
        1.10.1.1
        '''
        message = self.__COMMAND +\
            self.__HLVVER + "1" + "," +\
            self.__HLVCMD + "12" + "," +\
            self.__HLVBLOCK + block + "," +\
            self.__HLVSCN + scene + "," +\
            self.__HLVFADET + fade + "," +\
            "@" + self.clusterID + "." + self.memberID + "." + subnet + "." + device +\
            self.__TERMINATOR
        print("Recalled Scene " + scene + " for device " + device + " on subnet " + subnet + ".")
        print("Sent command looks like: " + message)
        self.__SendTCPMessageAndContinue(self.server, self.port, message)

    def SetGroupAbsoluteLevel(self, group: str, level: str, fade: str):
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

    def SetDeviceAbsoluteLevel(self, subnet: str, device: str, level: str, fade: str):
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
        print("TBD")

    def SetDeviceLevelAbsoluteProportion(self):
        print("TBD")

    def SetGroupLevelModifyProportion(self):
        print("TBD")

    def SetDeviceLevelModifyProportion(self):
        print("TBD")
