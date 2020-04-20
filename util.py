import cv2

import uuid

def CamSetting(filepath=None):
    if filepath is None:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(filepath)
    
    #画像サイズを変更する(MAX:720×480)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    if width > 720 or height > 480:
        width = 720
        height = width/height * 480
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width) # カメラ画像の横幅をwidthに設定
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height) # カメラ画像の縦幅をheightに設定

    return cap

class CamRecording():
    def __init__(self, camera):
        # 動画ファイル保存用の設定
        fps = int(camera.get(cv2.CAP_PROP_FPS))                    # カメラのFPSを取得
        w = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))              # カメラの横幅を取得
        h = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))             # カメラの縦幅を取得
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')        # 動画保存時のfourcc設定（mp4用）
        file_name = str(uuid.uuid4())[:6]
        self.video = cv2.VideoWriter(file_name + '.mp4', fourcc, fps, (w, h))  # 動画の仕様（ファイル名、fourcc, FPS, サイズ

    def Recording(self, frame):
        self.video.write(frame)

    def __del__(self):
        self.video.release()