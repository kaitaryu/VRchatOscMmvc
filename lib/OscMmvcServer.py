
import time
import datetime
import math

from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server

import threading


#buttonの立ち上がり、立ち下り、現在の状態を記録するクラス。
class OscButton():
    def __init__(self):
        self.Osclock = threading.RLock()
        self.button_up = False
        self.button_fall = False
        self.button_state = False
    #立ち下がりと立ち上がりを記録して、現在のbuttonの状態を取得する。
    def SetButtonState(self, args,state):
        print("[{0}] ~ {1}".format(args, state))
        with self.Osclock:
            self.button_fall = True if self.button_state and (not(state)) else self.button_fall
            self.button_up = True if (not(self.button_state)) and state else self.button_up
            self.button_state = state
            
    #立ち上がりを行ったかどうかを取得後、立ち上がりのフラグをリセットする。
    def GetButtonUp(self):
        tmp = self.button_up
        with self.Osclock:
            self.button_up = False 
        return tmp

    #立ち下がりを行たかどうかを取得後、立下りのフラグをリセットする。
    def GetButtonFall(self):
        tmp = self.button_fall
        with self.Osclock:
            self.button_fall = False 
        return tmp

#Toggleの現在の状態を記録するクラス。
class OscIntButton():
    def __init__(self,toggle_state_):
        self.Osclock = threading.RLock()
        self.button_up = False
        self.button_fall = False
        self.button_state = toggle_state_
    #現在のToggleの状態を取得する。
    def SetButtonState(self, args,state):
        print("[{0}] ~ {1}".format(args, state))
        with self.Osclock:
            self.button_fall = True if self.button_state < state else self.button_fall
            self.button_up = True if self.button_state > state else self.button_up
            self.button_state = state
            
    #立ち上がりを行ったかどうかを取得後、立ち上がりのフラグをリセットする。
    def GetButtonUp(self):
        tmp = self.button_up
        with self.Osclock:
            self.button_up = False 
        return tmp

    #立ち下がりを行たかどうかを取得後、立下りのフラグをリセットする。
    def GetButtonFall(self):
        tmp = self.button_fall
        with self.Osclock:
            self.button_fall = False 
        return tmp
#VRCのクライアントからのOSCの通信を受信するサーバー
class OscMmvcServer():
    def __init__(self,ip_str,port_int):

        self.start_button = OscButton()

        self.voice_button = OscIntButton(0)

        self.ip_str = ip_str
        self.port_int = port_int
    def SetServer(self):
        #サーバーの準備
        dispatcher_ = dispatcher.Dispatcher()

        dispatcher_.map("/avatar/parameters/start", self.start_button.SetButtonState)
        dispatcher_.map("/avatar/parameters/voicestate", self.voice_button.SetButtonState)


        self.server = osc_server.ThreadingOSCUDPServer(
            (self.ip_str , self.port_int), dispatcher_)



if __name__ == "__main__":
   test_class = OscClockServer("127.0.0.1",9001)
   test_class.SetServer()
   test_class.server.serve_forever()