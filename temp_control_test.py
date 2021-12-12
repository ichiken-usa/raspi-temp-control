#!/usr/bin/env python
# -*- coding: utf-8 -*-

# インストール必要
# sudo apt install cpufrequtils
# sudo apt install python3-matplotlib

import time
import subprocess 
import threading
import matplotlib.pyplot as plt 
import numpy as np


# CPUクロックをPIDコントロールするスレッド
class ControlCpuThread(threading.Thread):

    # Threadクラスを継承することでマルチスレッドに必要な機能を追加
    # runメソッドをオーバーライトすることでスレッドとして起動可能 = メイン処理はrunに書く
    # initで引数を与えることも可能。今回は無し。

    def __init__(self, test_cycle):

        super(ControlCpuThread, self).__init__()
        self.freq_MAX = 2.0 # デフォルトは1.5GHz
        self.freq_MIN = 0.5
        self.password = 'sudo password'+'\n' # sudoパスワード
        self.test_cycle = test_cycle
        return
    

    def read_temp(self):

        Cmd = 'vcgencmd measure_temp'
        result = subprocess.run(Cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        
        CpuTemp = result.stdout.split()
        temp = CpuTemp[0]
        temp = float(temp[5:9])

        return temp

    def set_freq(self,freq):

        if self.freq_MIN <= freq and freq <= self.freq_MAX:

            subprocess.run('sudo -S cpufreq-set -f '+str(freq)+'GHz',shell=True,input=self.password,text=True)
            #result = subprocess.run('cpufreq-info -f',shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)

            print(f'Freq: {freq} GHz')

    def set_ondemand(self):

        result = subprocess.run('sudo -S cpufreq-set -g ondemand',shell=True,input=self.password,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        print('set ondemand')


    def output(self,power):

        freq = round(power * self.freq_MAX, 1) #小数点一桁丸め

        # 上限調整
        if freq > self.freq_MAX:
            freq = self.freq_MAX
        
        # 下限調整
        if freq < self.freq_MIN:
            freq = self.freq_MIN

        self.set_freq(freq)

        return freq

    def p(self,temp, target, kp):
        d = target - temp
        if d < 0:
            return 0
        power = d / target * kp
        return power

    def i(self,prev, now, target, ki):
        if prev == 0:
            return 0
        d1 = target - now
        d2 = target - prev
        if d1 < 0:
            return 0
        if d2 < 0:
            d2 = 0
        return (d1 + d2) / 2 * ki

    def d(self,prev, now, kp):
        d = prev - now
        if d < 0:
            return 0
        return d * kp

    def run(self):
        
        target = 70 # 狙いのCPU温度設定（摂氏）
        prev=0

        # グラフ用
        x = []
        y_freq = []
        y_temp = []

        try:
            for k in range(self.test_cycle):
                print('------------------------------------')
                temp = self.read_temp()
                print (f'Target = {target}℃  Now = {temp}℃  Deff = {temp-target:.1f} ℃')

                # PID Coefficient
                pg = self.p(temp, target,6)
                ig = self.i(prev, temp, target, 0.4)
                dg = self.d(prev, temp, 0.1)
                power = pg + ig + dg
                prev = temp

                print(f'P ={pg:.3f}')
                print(f'I ={ig:.3f}')
                print(f'D ={dg:.3f}')
                print(f'power = {power:.2f}')
                
                # CPUクロック設定
                freq = self.output(power)

                # グラフ用配列にデータ格納
                x.append(k)
                y_freq.append(freq)
                y_temp.append(temp)
                
                time.sleep(1)

        except Exception as e:
            print(f'Exception: {e}')

        finally:
            self.set_ondemand()
            
            # グラフ表示
            fig, ax1 = plt.subplots()
            ax2 = ax1.twinx()

            ax1.plot(x,y_temp,color='red')
            ax2.plot(x,y_freq)

            ax1.set_ylim([50,80])
            ax2.set_ylim([0,4.0])

            plt.show()

            print('負荷スレッドは動作継続中。Ctrl+Cで抜けてください。')


# 負荷をかけるスレッド
class LoadThread(threading.Thread):

    def run(self):

        # 乗算をひたすらループ
        while True:
            rand1 = np.random.rand(1000,1000)
            rand2 = np.random.rand(1000,1000)
            rand3 = rand1 * rand2


if __name__ == "__main__":

    test_cycle = 10
    thread1 = LoadThread() 
    thread2 = ControlCpuThread(test_cycle) 

    # 各スレッド起動
    thread1.start()
    thread2.start()    