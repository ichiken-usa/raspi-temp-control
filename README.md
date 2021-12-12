# raspi-temp-control
ラズパイのCPUクロックをPID制御して狙いのCPU温度になるようにコントロールできるかどうかをテストするソフトです。

## 概要
こちらの記事で解説しています。  
https://ichiken-usa.blogspot.com/2021/05/cpufreq-pid.html

## インストールが必要なライブラリ
cpufrequtils(sudo apt install cpufrequtils)  
matplotlib(sudo apt install python3-matplotlib)

## 使用方法
- ラズパイのsudoパスワードをself.password = 'sudo password'+'\n'のsudo passwordの部分と置き換えてください。
- 狙いの温度はtarget = 70 # 狙いのCPU温度設定（摂氏）　の部分で決めています。
- temp_control_test.pyを起動すると温度を上昇させるために演算ループさせます。
- テストとしてグラフ出力するようにしているのでtest_cycleでコントロールのループを終えるようにしています。
