import cv2

from util import CamSetting
from util import CamRecording

#カメラもしくは映像の読み込み
filepath = "dorobou.mp4"
cap = CamSetting(filepath)

#比較用フレーム
avg = None

#ビデオ保存用インスタンスの生成
rec = CamRecording(cap)

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
    ksize=15
    #メディアンフィルタ
    thresh = cv2.medianBlur(thresh,ksize)

    # 画像の閾値に輪郭線を入れる
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        #検知する動体がある場合にビデオを保存する
        rec.Recording(frame)
    else:
        del rec
        #ビデオ保存用インスタンスの生成
        rec = CamRecording(cap)

    frame = cv2.drawContours(frame, contours, -1, (0, 255, 0), 3)

    # 結果を出力
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(30)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()