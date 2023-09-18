
import time
import datetime
import math

from pythonosc import udp_client
from pythonosc import dispatcher

from OscMmvcServer import * 
import threading
import sys

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys 

#0をそのまま入力するとなぜかfloatの最大が入力されるのでbinary32のイプシロンをZEROとする使う
ZERO = 1.193e-7



class OscMmvcClient():
    def __init__(self,ip_str,port_str,server):
        self.client = udp_client.SimpleUDPClient(ip_str,port_str)
        self.server = server
        

        self.thread = threading.Thread(target = self.MoveMmvc)
        
        self.MOVE_THREADING = True

        self.status_vol = 0
        self.state_model = 0
        self.state_start_button = "stop"
        self.state_transition_num = 0

        

        options = webdriver.ChromeOptions()
        #SSL認証画面のエラーを無視する。
        options.add_argument('ignore-certificate-errors')
        #ポップアップで許可を求める機能を停止する。
        options.add_argument('--use-fake-ui-for-media-stream')

        self.driver_path = ChromeDriverManager().install()
        self.driver = webdriver.Chrome(service=Service(executable_path=self.driver_path ),options=options)
        self.driver.implicitly_wait(5) 
        self.driver.get("https://192.168.100.13:18888/")
    def ClickStart(self):
        #メッセージが出たらbody-button　startを押す。
        start_button_list = self.driver.find_elements(By.CLASS_NAME, "body-button") 
        while True:
            for start_button in start_button_list:
                if start_button.text == "スタート":
                    start_button.click()
                    return       
    def GaneSetting(self):
        #GAINのOutputを３にする
        slider_list = self.driver.find_elements(By.CLASS_NAME, "character-area-slider-control-slider") 
        slider = slider_list[1].find_elements(By.TAG_NAME, "input")
        
        output_gain = float(slider[0].get_attribute("value"))
        step =  float(slider[0].get_attribute("step"))

        if output_gain < 3:
            count = int((3 - output_gain )/step)
            push_keys = Keys.RIGHT
        else:
            count = int((output_gain - 3 )/step)
            push_keys = Keys.LEFT

        for I in range(0,count):
            slider[0].send_keys(push_keys)           
    def AudioSetting(self):
        #AUDIOの初期設定をする。 
        body_select = self.driver.find_elements(By.CLASS_NAME, "body-select") 
        #input
        option = body_select[5].find_elements(By.TAG_NAME, "option")
        for I in option:
            body_select[5].send_keys(Keys.UP)
        for mike_name in option:
            #マイク (Realtek USB Audio)を選択する
            if "マイク (Realtek USB Audio)" in mike_name.text:
                break
            body_select[5].send_keys(Keys.DOWN)
        #output
        option = body_select[6].find_elements(By.TAG_NAME, "option")
        for I in option:
            body_select[6].send_keys(Keys.UP)
        for speaker_name in option:
            #CABLE Input (VB-Audio Virtual Cable)を選択する
            if "CABLE Input (VB-Audio Virtual Cable)" in speaker_name.text:
                break
            body_select[6].send_keys(Keys.DOWN)
    def ChunkSetting(self):
        body_select = self.driver.find_elements(By.CLASS_NAME, "body-select") 
        #CHUNK
        option = body_select[2].find_elements(By.TAG_NAME, "option")
        for I in option:
            body_select[2].send_keys(Keys.UP)
        for chunk_value in option:
            #CABLE Input (VB-Audio Virtual Cable)を選択する
            if  int(chunk_value.get_attribute("value")) > 80:
                break
            body_select[2].send_keys(Keys.DOWN) 
    def ModelSetting(self):
        #model-slot-tile-dscription 声を1番に合わせる
        voice = self.driver.find_elements(By.CLASS_NAME, "model-slot-tile-dscription")
        if self.state_model >= len(voice):
            self.state_model = len(voice) -1
        elif self.state_model < 0 :
            self.state_model = 0
        voice[self.state_model].click()
    def StartMmvc(self):
        self.ClickStart()
        self.GaneSetting()
        self.AudioSetting()
        self.ChunkSetting()
        self.ModelSetting()
    def MoveThreading(self):
        self.thread.start()
    def MoveMmvc(self):
        #初期化処理をする。
        self.StartMmvc()
        while self.MOVE_THREADING:
            self.OneMoveMmvc()
        
        self.driver.quit()
    def StartButtonSetting(self,click_button_name = "start"):
        #character-area-control-buttons
        start_button = self.driver.find_elements(By.CLASS_NAME, "character-area-control-buttons")
        button_list = start_button[0].find_elements(By.TAG_NAME, "div")

        for button in button_list:
            if click_button_name in  button.text:
                button.click()
                break
    def SetState(self,num):
        self.state_transition_num = num


 
    def OneMoveMmvc(self):
        #volumeを取得する
        self.status_vol = self.driver.find_elements(By.ID, "status-vol")[0].text
        print(self.status_vol)
        #stsrtを押す命令が渡されたら。
        if self.server.start_button.GetButtonUp():
            self.state_start_button = "start"
            print("start button click.")
            self.StartButtonSetting(self.state_start_button)
        #stopを押す命令が渡されたら。
        if self.server.start_button.GetButtonFall():
            self.state_start_button = "stop"
            print("stop button click.")
            self.StartButtonSetting(self.state_start_button)
        #
        if self.server.voice_button.GetButtonFall() or self.server.voice_button.GetButtonUp():
            self.state_model = self.server.voice_button.button_state
            print("chenge voice model.:" + str(self.state_model))
            self.StartButtonSetting("stop")
            time.sleep(0.1)
            self.ModelSetting()
            time.sleep(1.3)
            self.StartButtonSetting(self.state_start_button)

        time.sleep(0.3)


if __name__ == "__main__":
    test_server = OscMmvcServer("127.0.0.1",9001)
    test_client = OscMmvcClient("127.0.0.1",9000,test_server)
    test_server.SetServer()
    test_client.MoveThreading()
    
    try:
        test_server.server.serve_forever()
    except KeyboardInterrupt:
        MOVE_THREADING = False
        test_client.thread.join(2)

