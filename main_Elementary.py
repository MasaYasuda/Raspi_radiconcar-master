# ライブラリのインポート
import pygame
import dynamixel_classes
import time
import os

try:
    os.environ["SDL_VIDEODRIVER"] = "dummy" # SSH接続で稼働させた際のディスプレイの仮想出力宣言
    
    pygame.init() # pygameモジュールの初期化
    j = pygame.joystick.Joystick(0) # JOYスティックのインスタンス生成
    j.init() #インスタンスの初期化
    
    print("コントローラのボタンを押してください")
    
    # id 1 =右輪　　id 2 = 左輪
    # Dynamixelのインスタンス生成
    dynamixel_1 = dynamixel_classes.Dynamixel("/dev/ttyUSB0", 57600, 1)
    dynamixel_2 = dynamixel_classes.Dynamixel("/dev/ttyUSB0", 57600, 2)
    # トルク有効化
    dynamixel_1.enable_torque()
    dynamixel_2.enable_torque()

    while True:
        events = pygame.event.get() # PS4コントローラーの情報を受け取る
        
        # 　十字座標に応じた出力
        
        if j.get_hat(0)[1] == 1: # 十字上ボタンが押されている場合
            print("前進")
            dynamixel_1.write_velocity(128)
            dynamixel_2.write_velocity(-128)
        elif j.get_hat(0)[1] == -1: # 十字下ボタンが押されている場合
            print("後退")
            dynamixel_1.write_velocity(128)
            dynamixel_2.write_velocity(-128)
        elif j.get_hat(0)[0] == 1: # 十字右ボタンが押されている場合
            print("時計回り")
            dynamixel_1.write_velocity(128)
            dynamixel_2.write_velocity(128)
        elif j.get_hat(0)[0] == 1: # 十字左ボタンが押されている場合
            print("反時計回り")
            dynamixel_1.write_velocity(-128)
            dynamixel_2.write_velocity(-128)
        else: # それ以外のボタンが押されている、あるいは、何も押されていない場合
            dynamixel_1.write_velocity(0)
            dynamixel_2.write_velocity(0)

        time.sleep(0.010) # 処理速度を少し落とす

except KeyboardInterrupt:
    print("プログラムを終了します")
    
    j.quit() # Joystickの切断
    
    # トルクを無効化
    dynamixel_1.disable_torque()
    dynamixel_2.disable_torque()
    
    time.sleep(0.010) # 無効化されるまで少し待つ
    
    dynamixel_1.close_port() # Dynamixelとの通信を切断
    dynamixel_2.close_port()
