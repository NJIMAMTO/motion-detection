import cv2
import uuid

def CamSetting(video_name=None):
    if video_name is None:
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(video_name)
    
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
    video_file = []
    def __init__(self, camera, output_folder):
        # 動画ファイル保存用の設定
        fps = int(camera.get(cv2.CAP_PROP_FPS))                    # カメラのFPSを取得
        w = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))              # カメラの横幅を取得
        h = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))             # カメラの縦幅を取得
        fourcc = cv2.VideoWriter_fourcc('W', 'M', 'V', '1')
        #fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')        # 動画保存時のfourcc設定（mp4用）
        
        #生成されたビデオの一覧を追加しておく
        file_name = str(uuid.uuid4())[:6]
        self.video_file = output_folder + file_name + '.wmv'
        self.__class__.video_file.append(self.video_file)
        
        self.video = cv2.VideoWriter(self.video_file,
                                       fourcc, 
                                       fps,
                                       (w, h))  # 動画の仕様（ファイル名、fourcc, FPS, サイズ
   
        self._counter = 0

    def Recording(self, frame, recordable=False):
        if recordable is True:
            self.video.write(frame)
            self._counter = 0
            return 0
        else:
            self._counter += 1
            #動体検知がなにも検知しない状態が
            #30フレーム続いたら録画を終了する
            if self._counter == 30:
                self.video.release()
                return -1
            elif self._counter > 30:
                return -1 #録画終了状態を継続
            else:
                self.video.write(frame)
                return 0
            return 0


    def __del__(self):
        self.video.release()