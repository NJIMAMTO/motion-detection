import configparser
# ファイルの存在チェック用モジュール
import os
import errno

import cv2

from util import CamSetting
from util import CamRecording


#=======#configファイルの読み込み#=======#
config = configparser.ConfigParser()
config_ini_path = "config.ini"
# 指定したiniファイルが存在しない場合、エラー発生
if not os.path.exists(config_ini_path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_ini_path)
config.read(config_ini_path, encoding="utf-8")

filepath = config['SETTING']['InputFile']
if not os.path.exists(filepath):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filepath)
output_folder = config['SETTING']['OutputFolder']
if not os.path.exists(output_folder):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), output_folder)
kernel_size = config['SETTING']['MedianFilterKernelSize']

#=======#configファイルの読み込み 終わり#=======#

#カメラもしくは映像の読み込み
cap = CamSetting(filepath)

#比較用フレーム
avg = None

#ビデオ保存用インスタンスの生成
rec = CamRecording(cap, output_folder)

#録画可能状態の監視フラグ
flag = -1

while True:
    # 1フレームずつ取得する。
    ret, frame = cap.read()
    if not ret:
        break

    # グレースケールに変換
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 比較用のフレームを取得する
    if avg is None:
        avg = gray.copy().astype("float")
        continue

    # 現在のフレームと移動平均との差を計算
    cv2.accumulateWeighted(gray, avg, 0.6)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

    # 差分画像を閾値処理を行う
    thresh = cv2.threshold(frameDelta, 3, 255, cv2.THRESH_BINARY)[1]

    #ノイズ除去
    ksize=int(kernel_size)
    #メディアンフィルタ
    thresh = cv2.medianBlur(thresh, ksize)

    # 画像の閾値に輪郭線を入れる
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    frame = cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)

    if contours:
        #録画停止モードから録画可能モードに遷移する
        if flag == -1:
            #ビデオ保存用インスタンスの生成
            rec = CamRecording(cap, output_folder)
        #検知する動体がある場合にビデオを保存する
        flag = rec.Recording(frame)
    else:
        flag = rec.Recording()

    # 結果を出力
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(30)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()