#-*- coding: utf-8 -*-
from kivy.app import App
from kivy.uix.widget import Widget

from kivy.properties import StringProperty 
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.resources import resource_add_path
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.core.window import Window


from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from PIL import Image, ImageOps

import os,sys
import threading
import csv
import time
import datetime
import numpy
import configparser
import shutil
import glob


resource_add_path("IPAexfont00301")
LabelBase.register(DEFAULT_FONT, "ipaexg.ttf")

date_today_str = datetime.date.today().strftime('%Y%m%d')

ini = configparser.ConfigParser()
ini.read('./config.ini', 'UTF-8')
print(ini['info']['target directory'])
print(ini['info']['length of barcode'])
print(ini['info']['position of body number'])

global length_of_barcode
global position_of_body_number

length_of_barcode = int(ini['info']['length of barcode'])
position_of_body_number = int(ini['info']['position of body number'])

# 監視対象ディレクトリを指定する
target_dir = ini['info']['target directory']

hokuren_dir = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + '\\Desktop\\hokuren'

h_today_dir = hokuren_dir + '\\' + date_today_str
mirror_dir = h_today_dir + '\\ミラー型撮影装置'
pixel_dir = h_today_dir + '\\スマホ台形補正'
complete_dir = h_today_dir + '\\mirror'
surface_dir = h_today_dir + '\\枝肉概観'
diffect_dir = h_today_dir + '\\瑕疵'
resize_image_dir = h_today_dir + '\\resize'



if(not os.path.exists(hokuren_dir)):
    os.mkdir(hokuren_dir)
if(not os.path.exists(h_today_dir)):
    os.mkdir(h_today_dir)
if(not os.path.exists(mirror_dir)):
    os.mkdir(mirror_dir)
if(not os.path.exists(resize_image_dir)):
    os.mkdir(resize_image_dir)
if(not os.path.exists(pixel_dir)):
    os.mkdir(pixel_dir)
if(not os.path.exists(surface_dir)):
    os.mkdir(surface_dir)
if(not os.path.exists(diffect_dir)):
    os.mkdir(diffect_dir)
if(not os.path.exists(complete_dir)):
    os.mkdir(complete_dir)


'''chikudai_dir = 'C:\\Users\\kuchida\\Desktop\\chikudai'
c_today_dir = chikudai_dir + '\\' + date_today_str

if(not os.path.exists(chikudai_dir)):
    os.mkdir(chikudai_dir)
if(not os.path.exists(c_today_dir)):
    os.mkdir(c_today_dir)'''

global i_m
i_m = 0
global i_p
i_p = 0




mirror_image_path_list = glob.glob(mirror_dir+'\\*.jpg')
mirror_image_path_list.sort()

pixel_image_path_list = glob.glob(pixel_dir+'\\*.jpg')
pixel_image_path_list.sort()

print(mirror_image_path_list)
print(pixel_image_path_list)

barcode_list = []
body_number_list = []
carcass_order_list = []


class LoadDialog(FloatLayout):
    desktop_dir = os.getenv("HOMEDRIVE") + os.getenv("HOMEPATH") + '\\Desktop'
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class TextWidget(Widget):
    global carcass_list
    carcass_order = StringProperty()    # プロパティの追加
    body_number = StringProperty()
    body_number_2 = StringProperty()
    body_number_3 = StringProperty()
    barcode = StringProperty()
    csv_input = StringProperty()
    mirror_image = ObjectProperty(None)
    mirror_image_src = StringProperty('')
    pixel_image = ObjectProperty(None)
    pixel_image_src = StringProperty('')
    mirror_name = StringProperty()
    pixel_name = StringProperty()
    carcass_list = []


    def __init__(self, **kwargs):
        super(TextWidget, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self) 
        self._keyboard.bind(on_key_down=self._on_keyboard_down) 
        self.body_number = '枝肉番号:    '
        self.body_number_2 = ''
        self.body_number_3 = '' 
        self.carcass_order = '出場順:    '
        self.barcode = ''
        self.mirror_image_src = 'black.png'
        self.pixel_image_src = 'black.png'
        self.csv_input = 'csv'
        self.mirror_name = ''
        self.pixel_name = ''
        self.next_image_set()
        Clock.schedule_interval(self.update, 1)
        pass


    def _keyboard_closed(self): 
        self._keyboard.unbind(on_key_down=self._on_keyboard_down) 
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers): 
        if keycode[1] == 'right': 
            self.okClicked()
        return True

    def update(self, dt):
        self.ids.mirror_image.reload()
        self.ids.pixel_image.reload()


    def okClicked(self):        # ボタンをクリック時
        global i_m
        global i_p
        if i_m < len(mirror_image_path_list) and i_p < len(pixel_image_path_list):
            if not mirror_image_path_list[i_m] == mirror_dir+'\\'+self.carcass_order[4:]+'_'+self.body_number[5:]+'.jpg':
                if not '見つかりません' in self.carcass_order:
                    shutil.copyfile(mirror_image_path_list[i_m],complete_dir+'\\'+self.carcass_order[4:]+'_'+self.body_number[5:]+'.jpg')
                    ##self.rotate_mirror_image(mirror_dir+'\\'+self.carcass_order[4:]+'_'+self.body_number[5:]+'.jpg')
                    print("copyed"  + str(mirror_image_path_list[i_m]) + '  to  ' + str(complete_dir+'\\'+self.carcass_order[4:]+'_'+self.body_number[5:]+'.jpg'))
                else:
                    shutil.copyfile(mirror_image_path_list[i_m],complete_dir+'\\'+ date_today_str +'_'+self.body_number[5:]+'.jpg')
                    ##self.rotate_mirror_image(mirror_dir+'\\'+self.carcass_order[4:]+'_'+self.body_number[5:]+'.jpg')
                    print("copyed"  + str(mirror_image_path_list[i_m]) + '  to  ' + str(complete_dir+'\\'+date_today_str+'_'+self.body_number[5:]+'.jpg'))
            i_m += 1
            i_p += 1
            self.next_image_set()

    def next_image_set(self):
        if i_m < len(mirror_image_path_list) and i_p < len(pixel_image_path_list):
            self.resize_image(mirror_image_path_list[i_m],'mirror')
            self.resize_image(pixel_image_path_list[i_p],'pixel')
            ##self.mirror_image_src = resize_image_dir + '\\' + mirror_image_path_list[i_m]
            ##self.pixel_image_src = resize_image_dir + '\\' + pixel_image_path_list[i_p]
            self.mirror_name = mirror_image_path_list[i_m] + '\n\n' + str(i_m+1) + '/' + str(len(mirror_image_path_list))
            self.pixel_name = pixel_image_path_list[i_p] + '\n\n' + str(i_p+1) + '/' + str(len(pixel_image_path_list))
            self.body_number = '枝肉番号:' + pixel_image_path_list[i_p][-8:-4]

            body_number = pixel_image_path_list[i_p][-8:-4]
            if body_number in [d[1] for d in carcass_list]:
                self.carcass_order =  '出場順:' + str(carcass_list[[d[1] for d in carcass_list].index(body_number)][0])
            else:
                self.carcass_order = '出場順が見つかりません'
        if i_m >= len(mirror_image_path_list):
            self.mirror_image_src = 'black.png'
            self.mirror_name = '写真が見つかりません'
        if i_p >= len(pixel_image_path_list):
            self.pixel_image_src = 'black.png'
            self.pixel_name = '写真が見つかりません'
        
    def resize_image(self,src,sort):
        filename = src[src.rfind('\\')+1:]
        filename = filename[:filename.rfind('.')]
        if not os.path.exists(resize_image_dir +'\\'+ filename + '.jpg'):
            img = Image.open(src)
            img = img.resize((int(img.width / 4), int(img.height / 4)))
            img = img.transpose(Image.ROTATE_180)
            img = ImageOps.mirror(img)
            img.save(resize_image_dir +'\\'+ filename + '.jpg')
        if sort == 'mirror':
            self.mirror_image_src = resize_image_dir +'\\'+ filename + '.jpg'
        elif sort == 'pixel':
            self.pixel_image_src = resize_image_dir +'\\'+ filename + '.jpg'
    
    def rotate_mirror_image(self,src):
        img = Image.open(src)
        img = img.transpose(Image.ROTATE_270)
        img = ImageOps.mirror(img)
        img.save(src + '_2.jpg', quality=98, exif=img.info['exif'],subsampling=0)

    def m_bClicked(self):
        global i_m
        if 0 < i_m:
            i_m -=1
            self.next_image_set()
    def m_fClicked(self):
        global i_m
        if  i_m < len(mirror_image_path_list)-1:
            i_m +=1
            self.next_image_set()

    def p_bClicked(self):
        global i_p
        if 0 < i_p:
            i_p -=1
            self.next_image_set()

    def p_fClicked(self):
        global i_p
        if i_p < len(pixel_image_path_list)-1:
            i_p +=1
            self.next_image_set()

    
    def sansyoClicked(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()
 
    def dismiss_popup(self):
        self._popup.dismiss()
 
    def load(self, path, filename):
        load_filepath = str(filename[0])  #filenameは配列で返ってくる
        self.dismiss_popup()
        load_carcass_list = numpy.loadtxt(fname=load_filepath,skiprows=0,delimiter=",",dtype="U20")[:,0:2]
        for line in load_carcass_list:
            line[0] = line[0].zfill(4)
            line[1] = line[1].zfill(4)
            carcass_list.append([line[0],line[1]])
        self.csv_input = 'read'
        self.next_image_set()

        
        
class TestApp(App):
    def __init__(self, **kwargs):
        super(TestApp, self).__init__(**kwargs)
        self.title = 'greeting'

    def build(self):
        TestApp.widget = TextWidget()
        return TestApp.widget


def set_image_src(src):
    TestApp().set_image_src(src)

def list_reset():
    global display_image_path_list
    global hokuren_image_path_list
    global original_image_path_list
    global barcode_list
    global body_number_list
    global carcass_order_list
    display_image_path_list = []
    original_image_path_list = []
    hokuren_image_path_list = []
    barcode_list = []
    body_number_list = []
    carcass_order_list = []

def resize_mirror_image(path, a):
    for src in path:
        filename = src[src.rfind('\\')+1:]
        filename = filename[:filename.rfind('.')]
        if not os.path.exists(resize_image_dir +'\\'+ filename + '.jpg'):
            img = Image.open(src)
            img = img.resize((int(img.width / 4), int(img.height / 4)))
            img = img.transpose(Image.ROTATE_180)
            img = ImageOps.mirror(img)
            img.save(resize_image_dir +'\\'+ filename + '.jpg')

def rotate_pixel_image(path, a):
    for src in path:
        filename = src[src.rfind('\\')+1:]
        filename = filename[:filename.rfind('.')]
        if not os.path.exists(resize_image_dir +'\\'+ filename + '.jpg'):
            img = Image.open(src)
            img = img.transpose(Image.ROTATE_180)
            img.save(resize_image_dir +'\\'+ filename + '.jpg')


if __name__ == '__main__':
    resize_thread = threading.Thread(target=resize_mirror_image, args=(mirror_image_path_list,0))
    resize_thread.start()
    rotate_thread = threading.Thread(target=rotate_pixel_image, args=(pixel_image_path_list,0))
    rotate_thread.start()
    TestApp().run()
    



    


