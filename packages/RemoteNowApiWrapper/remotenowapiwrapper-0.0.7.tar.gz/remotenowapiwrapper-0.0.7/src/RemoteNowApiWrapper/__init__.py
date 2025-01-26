from typing import Callable, Union
import paho.mqtt.client as mqtt
import json
import os


class RemoteNowApi:
    uiServiceBase = "/remoteapp/tv/ui_service"
    platformServiceBase = "/remoteapp/tv/platform_service"
    remoteServiceBase = "/remoteapp/tv/remote_service"
    mobileBase = "/remoteapp/mobile"

    def __init__(self, hostname, identifer="remoteNowApiWrapper"):
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        certPath = f"{dir_path}/hisense.cert"

        self._hostname = hostname
        self.identifer = identifer
        self._connected = False

        # system info
        self._vendorBrand = None
        self._boardVersion = None
        self._produceDate = None
        self._uniqueDeviceId = None
        self._softwareVersion = None
        self._chipplatform = None
        self._devicemsg = None

        self._on_SourceList = []
        self._on_capability = []
        self._on_tvInfo = []
        self._on_channelListInfo = []
        self._on_channelList = []
        self._on_state = []
        self._on_sourceinsert = []
        self._on_volumeChange = []
        self._on_connected = []
        self._on_disconnected = []

        # command Topics
        self._getTVStateTopic = (
            f"{self.uiServiceBase}/{self.identifer}/actions/gettvstate"
        )
        self._sendAuthenticationCodeTopic = (
            f"{self.uiServiceBase}/{self.identifer}/actions/authenticationcode"
        )
        self._changeSourceTopic = (
            f"{self.uiServiceBase}/{self.identifer}/actions/changesource"
        )
        self._changeChannelTopic = (
            f"{self.uiServiceBase}/{self.identifer}/actions/changechannel"
        )
        self._changeVolumeTopic = (
            f"{self.platformServiceBase}/{self.identifer}/actions/changevolume"
        )
        self._getSourceList = (
            f"{self.uiServiceBase}/{self.identifer}/actions/sourcelist"
        )
        self._getCapabilityTopic = (
            f"{self.uiServiceBase}/{self.identifer}/actions/capability"
        )
        self._getTvInfoTopic = (
            f"{self.platformServiceBase}/{self.identifer}/actions/gettvinfo"
        )
        self._getChannelListInfoTopic = (
            f"{self.platformServiceBase}/{self.identifer}/actions/getchannellistinfo"
        )
        self._getChannelListTopic = (
            f"{self.platformServiceBase}/{self.identifer}/actions/channellist"
        )
        self._sendkeyTopic = (
            f"{self.remoteServiceBase}/{self.identifer}/actions/sendkey"
        )

        # information Topics
        self._SourceListTopic = (
            f"{self.mobileBase}/{self.identifer}/ui_service/data/sourcelist"
        )
        self._capabilityTopic = (
            f"{self.mobileBase}/{self.identifer}/ui_service/data/capability"
        )
        self._tvInfoTopic = (
            f"{self.mobileBase}/{self.identifer}/platform_service/data/gettvinfo"
        )
        self._channelListInfoTopic = f"{self.mobileBase}/{self.identifer}/platform_service/data/getchannellistinfo"
        self._channelListTopic = (
            f"{self.mobileBase}/{self.identifer}/platform_service/data/channellist"
        )
        self._stateTopic = "/remoteapp/mobile/broadcast/ui_service/state"
        self._sourceInsertTopic = (
            "/remoteapp/mobile/broadcast/platform_service/actions/sourceinsert"
        )
        self._volumeChangeTopic = (
            "/remoteapp/mobile/broadcast/platform_service/actions/volumechange"
        )

        self._mqttc = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.identifer,
            clean_session=True,
        )

        self._mqttc.username_pw_set(
            username="hisenseservice", password="multimqttservice"
        )
        self._mqttc.tls_set(ca_certs=certPath)
        self._mqttc.tls_insecure_set(True)

        self._mqttc.on_connect = self.on_connect
        self._mqttc.on_message = self.on_message
        self._mqttc.on_disconnect = self.on_disconnect

    def publish(self, mqttTopic, payload):
        #print(f"Send: {mqttTopic}")

        if payload == "":
            self._mqttc.publish(topic=mqttTopic)
        else:
            #print(payload)
            self._mqttc.publish(topic=mqttTopic, payload=payload)

    def connect(self):
        #print("connection")
        self._mqttc.connect_async(self._hostname, 36669, 60)
        self._mqttc.loop_start()

    def getVendor(self):
        return self._vendorBrand

    def getBoardVersion(self):
        return self._boardVersion

    def getProduceDate(self):
        return self._produceDate

    def getUniqueDeviceId(self):
        return self._uniqueDeviceId

    def getSoftwareVersion(self):
        return self._softwareVersion

    def getChipplatform(self):
        return self._chipplatform

    def getDevicemsg(self):
        return self._devicemsg

    # request authcode
    def getAuthCode(self):
        self.getTvState()

    # request authentication code
    def getTvState(self):
        mqttTopic = self._getTVStateTopic
        payload = '""'

        self.publish(mqttTopic=mqttTopic, payload=payload)

    # send authentication code
    def sendAuthenticationCode(self, authCode="0000"):
        mqttTopic = self._sendAuthenticationCodeTopic
        payload = {"authNum": f"{authCode}"}

        self.publish(mqttTopic=mqttTopic, payload=json.dumps(payload))

    # change source
    def changeSource(self, sourceId=0):
        mqttTopic = self._changeSourceTopic
        payload = {"sourceid": f"{sourceId}"}

        self.publish(mqttTopic=mqttTopic, payload=json.dumps(payload))

    # change channel
    def changeChannel(self, channel_param=""):
        mqttTopic = self._changeChannelTopic
        payload = {"channel_param": f"{channel_param}"}

        self.publish(mqttTopic=mqttTopic, payload=json.dumps(payload))

    # change volume
    def changeVolume(self, percentage):
        mqttTopic = self._changeVolumeTopic
        payload = percentage

        self.publish(mqttTopic=mqttTopic, payload=json.dumps(payload))

    def sendKey(self, key):
        mqttTopic = self._sendkeyTopic
        payload = key

        self.publish(mqttTopic=mqttTopic, payload=payload)

    # request sourcelist
    def getSourceList(self):
        mqttTopic = self._getSourceList
        payload = ""

        self.publish(mqttTopic=mqttTopic, payload=payload)

    # request capabilities
    def getCapability(self):
        mqttTopic = self._getCapabilityTopic
        payload = ""

        self.publish(mqttTopic=mqttTopic, payload=payload)

    # request tvinfo
    def getTvInfo(self):
        mqttTopic = self._getTvInfoTopic
        payload = ""

        self.publish(mqttTopic=mqttTopic, payload=payload)

    # request request channel list info
    def getChannelListInfo(self):
        mqttTopic = self._getChannelListInfoTopic
        payload = ""

        self.publish(mqttTopic=mqttTopic, payload=payload)

    # request channellist
    def getChannelList(self, list_para, list_name):
        mqttTopic = self._getChannelListTopic
        payload = {
            "list_para": f"{list_para}",
            "list_name": f"{list_name}",
        }

        self.publish(mqttTopic=mqttTopic, payload=json.dumps(payload))

    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, reason_code, properties):
        #print(f"Connected with result code {reason_code}")
        client.subscribe(self._SourceListTopic)
        client.subscribe(self._capabilityTopic)
        client.subscribe(self._tvInfoTopic)
        client.subscribe(self._channelListInfoTopic)
        client.subscribe(self._channelListTopic)
        client.subscribe(self._stateTopic)
        client.subscribe(self._sourceInsertTopic)
        client.subscribe(self._volumeChangeTopic)

        self.getCapability()

        self.handle_on_connected()

        self._connected = True

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        #print(f"Receive: {msg.topic}")
        payload = json.loads(msg.payload)

        match msg.topic:
            case self._SourceListTopic:
                return self.handle_on_SourceList(payload)
            case self._capabilityTopic:
                return self.handle_on_capability(payload)
            case self._tvInfoTopic:
                return self.handle_on_tvInfo(payload)
            case self._channelListInfoTopic:
                return self.handle_on_channelListInfo(payload)
            case self._channelListTopic:
                return self.handle_on_channelList(payload)
            case self._stateTopic:
                return self.handle_on_state(payload)
            case self._sourceInsertTopic:
                return self.handle_on_sourceinsert(payload)
            case self._volumeChangeTopic:
                return self.handle_on_volumeChange(payload)

    # Handle TV disconnect
    def on_disconnect(self, client, userdata, reason_code, properties, rc):
        #print("disconnected")
        self._connected = False

        self.handle_on_disconnected()()

    def get_Connected(self):
        if self._vendorBrand is None:
            return False

        return self._connected

    # SourceList
    def register_handle_on_SourceList(self, func: Callable):
        self._on_SourceList.append(func)

    def handle_on_SourceList(self, payload):
        for func in self._on_SourceList:
            func(payload)

    # Capability
    def register_handle_on_capability(self, func: Callable):
        self._on_capability.append(func)

    def handle_on_capability(self, payload):
        self._vendorBrand = payload["vendorBrand"]
        self._boardVersion = payload["boardVersion"]
        self._produceDate = payload["produceDate"]
        self._uniqueDeviceId = payload["uniqueDeviceId"]
        self._softwareVersion = payload["softwareVersion"]
        self._chipplatform = payload["chipplatform"]
        self._devicemsg = payload["devicemsg"]

        for func in self._on_volumeChange:
            func(payload)

    # TvInfo
    def register_handle_on_tvInfo(self, func: Callable):
        self._on_tvInfo.append(func)

    def handle_on_tvInfo(self, payload):
        for func in self._on_tvInfo:
            func(payload)

    # ChannelListInfo
    def register_handle_on_channelListInfo(self, func: Callable):
        self._on_channelListInfo.append(func)

    def handle_on_channelListInfo(self, payload):
        for func in self._on_channelListInfo:
            func(payload)

    # ChannelList
    def register_handle_on_channelList(self, func: Callable):
        self._on_channelList.append(func)

    def handle_on_channelList(self, payload):
        for func in self._on_channelList:
            func(payload)

    # State
    def register_handle_on_state(self, func: Callable):
        self._on_state.append(func)

    def handle_on_state(self, payload):
        for func in self._on_state:
            func(payload)

    # Source Change
    def register_handle_on_sourceinsert(self, func: Callable):
        self._on_sourceinsert.append(func)

    def handle_on_sourceinsert(self, payload):
        for func in self._on_sourceinsert:
            func(payload)

    # volume Change
    def register_handle_on_volumeChange(self, func: Callable):
        self._on_volumeChange.append(func)

    def handle_on_volumeChange(self, payload):
        for func in self._on_volumeChange:
            func(payload)

    # connected
    def register_handle_on_connected(self, func: Callable):
        self._on_connected.append(func)

    def handle_on_connected(self):
        for func in self._on_connected:
            func()

    # disconnected
    def register_handle_on_disconnected(self, func: Callable):
        self._on_disconnected.append(func)

    def handle_on_disconnected(self):
        for func in self._on_disconnected:
            func()
