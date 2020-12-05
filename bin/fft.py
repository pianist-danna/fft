"""
リアルタイム・スペクトルアナライザー
"""

#%%
# cording = UTF-8

import os,configparser
import scipy,pyaudio
import numpy as np
import matplotlib as plt
from matplotlib.colors import LogNorm

print ("Scipy version:{0}".format(scipy.__version__))
print ("Pyaudio version:{0}".format(pyaudio.__version__))
print ("Numpy version:{0}".format(np.__version__))

###########################グローバル変数の初期値###########################
base_dir = os.path.dirname(__file__)    #カレントディレクトリ

a_index = 1  #オーディオインデックス

br = pyaudio.paInt16    #ビットレート
sr = 44100  #サンプリングレート
chunk = 1024  #ストリームサイズならびにFFTの窓幅

#%%
class inital:
    def __init__(self,base_dir,a_index,br,sr,chunk):
        #グローバル変数の取り込み
        self.base_dir = base_dir
        self.a_index = a_index,
        self.br = br
        self.sr = sr
        self.chunk = chunk
        self.pa = pyaudio.PyAudio()

    #オーディオインデックスの取得
    def set_indexes(self):
        print("***List of available audio devices:***")
        for i in range(self.pa.get_device_count()):
            print(i,self.pa.get_device_info_by_index(i).get("name"),sep = " - ")
        x = int(input("Select Audio device Index No."))
        print("***Selected audio device #{0}.***".format(x))
        return x

    #設定値の書き出し
    def save_ini(self):
        x = configparser.ConfigParser()

        x["General"] = {
            "base_dir":self.base_dir
        }

        if self.a_index == None:
            x["params"]["a_index"] = ""
        else:
            x["params"]["a_index"] = str(self.a_index)

        x["params"] = {
            "br":self.br,
            "sr":self.sr,
            "chunk":self.chunk
        }

        with open(os.path.splitext(
            os.path.basename(__file__))[0] + ".ini","w"
        ) as cfgfile:
            x.write(cfgfile)

    #設定値の読み出し
    def load_ini(self):
        x = configparser.configparser.ConfigParser()
        x.read(
            str(
                self.base_dir + os.path.splitext(
                    os.path.basename(__file__)
                )[0] + ".ini"
            )
        )

        #グローバル変数との区別の為全て頭に"l_"をつけて読みだす
        l_base_dir = x.get("General","base_dir")
        l_a_index = x.get("params","a_index")
        if l_a_index =="":
            l_a_index = None
        else:
            l_a_index = int(l_a_index)
        l_br = x.getint("params","br")
        l_sr = x.getint("params","sr")
        l_chunk = x.getint("params","chunk")

        return l_base_dir,l_a_index,l_br,l_sr,l_chunk

    #起動時処理
    def bootup(self):
        #iniファイルの有無判定 存在すればiniファイルから変数を読み出す
        if os.path.exists(
            str(
                self.base_dir + os.path.splitext(
                    os.path.basename(__file__)
                    )[0] + ".ini"
                )
            ):
            self.base_dir,self.a_index,self.br,self.sr,self.chunk = self.load_ini()
            print("Loaded initial settings.\n***Audio device #{0} - {1} is selected***"\
            .format(self.a_index,self.pa.get_device_info_by_index(self.a_index)\
                .get("name")))
        else:
            #オーディオインデックスを選択後、変数をiniファイルに格納する
            self.a_index = self.set_indexes()
            self.save_ini()
            print(
                "Saved deffault settings:" + os.path.splitext(
                    os.path.basename(__file__)
                    )[0] + ".ini"
            )
        return self.base_dir,self.a_index,self.br,self.sr,self.chunk


#%%
class core:
    def __init__(self,a_index,br,sr,chunk):
        #グローバル変数の取り込み
        self.a_index = a_index,
        self.br = br
        self.sr = sr
        self.chunk = chunk

        #マイクインプット関係の初期設定
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            format = br,
            channels = 1,
            rate = sr,
            input_device_index = a_index,
            frames_par_buffer = chunk
        )

        #バッファーの用意
        self.bulkdata = np.zeros(self.chunk)

        #fftの軸設定
        self.fft_axis = np.fft.fftfreq(len(self.bulkdata),d = 1.0/self.sr)
        
    def input(self):
        x = self.stream.read(self.chunk)
        x = np.frombuffer(x,dtype = "int16") / ((np.power(2,16)/2)-1)
        return x
    
