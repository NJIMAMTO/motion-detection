#configファイルの読み込み
import configparser
# ファイルの存在チェック用モジュール
import os
import errno
#モジュールのバージョンチェック
from distutils.version import StrictVersion
#opencv
import cv2
#zipファイル圧縮用
import zipfile
#フォルダ削除用
import shutil

#セルフモジュール
from util import CamSetting
from util import CamRecording
from mailing import SendMail

#=======#configファイルの読み込み#=======#
config = configparser.ConfigParser()
config_ini_path = "config.ini"
# 指定したiniファイルが存在しない場合、エラー発生
if not os.path.exists(config_ini_path):
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), config_ini_path)
config.read(config_ini_path, encoding="utf-8")

filepath = config['SETTING']['InputFile']
if not(filepath == '' or 'None'):
    if not os.path.exists(filepath):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filepath)
output_folder = config['SETTING']['OutputFolder']
if not os.path.exists(output_folder):
    os.mkdir(output_folder)
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
    if StrictVersion(cv2.__version__) >= StrictVersion('4.0'):
        contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    elif StrictVersion(cv2.__version__) < StrictVersion('4.0'):
        _ ,contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    frame = cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)

    if contours:
        #録画停止モードから録画可能モードに遷移する
        if flag == -1:
            #ビデオ保存用インスタンスの生成
            rec = CamRecording(cap, output_folder)
        #検知する動体がある場合にビデオを保存する
        flag = rec.Recording(frame, True)
    else:
        flag = rec.Recording(frame, False)

    # 結果を出力
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(30)
    if key == 27:
        break

del rec
cap.release()
cv2.destroyAllWindows()

#生成された動画ファイルを圧縮する
zip_filename = './output/new_comp.zip'
with zipfile.ZipFile(zip_filename, 'w', compression=zipfile.ZIP_STORED) as new_zip:
    for filepath in CamRecording.video_file:
    #for filepath in CamRecording.video_file:
        basename = os.path.basename(filepath)
        new_zip.write(filepath, arcname=basename)

#GmailでZipファイルを送信
SendMail(zip_filename)

#動画ファイルとZipファイルをディレクトリごと削除する
shutil.rmtree('./output/')
