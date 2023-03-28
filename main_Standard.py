# ライブラリのインポート
import pygame
import dynamixel_classes
import time
import os

try:
    os.environ["SDL_VIDEODRIVER"] = "dummy"  # SSH接続で稼働させた際のディスプレイの仮想出力宣言

    pygame.init()  # pygameモジュールの初期化
    j = pygame.joystick.Joystick(0)  # JOYスティックのインスタンス生成
    j.init()  # インスタンスの初期化

    print("コントローラのボタンを押してください")

    # id 1 = 右輪　　id 2 = 左輪
    # Dynamixelのインスタンス生成
    dynamixel_1 = dynamixel_classes.Dynamixel("/dev/ttyUSB0", 57600, 1)
    dynamixel_2 = dynamixel_classes.Dynamixel("/dev/ttyUSB0", 57600, 2)
    # トルク有効化
    dynamixel_1.enable_torque()
    dynamixel_2.enable_torque()

    while True:
        events = pygame.event.get()  # PS4コントローラーの情報を受け取る

        move = j.get_axis(0)[1]  # 左スティックのy座標取得 (前進後退量)
        rot = (-1) * j.get_axis(0)[0]  # 左スティックのx座標取得（回転量）

        # JoyStickのわずかな傾きは無視する
        if abs(move) < 0.1:
            move = 0
        if abs(rot) < 0.1:
            rot = 0

        # 運動学（簡易版）の計算
        R_value = move - rot
        L_value = move + rot

        # 大きすぎる値（1以上）のとき圧縮する
        R_abs = abs(R_value)  # 絶対値を求める
        L_abs = abs(L_value)  # 絶対値を求める

        if R_abs > 1 or L_abs > 1:
            if R_abs >= L_abs:
                R_value = R_value / R_abs  # 圧縮
                L_value = L_value / R_abs  # 圧縮
            elif R_abs < L_abs:
                R_value = R_value / L_abs
                L_value = L_value / L_abs

        # 出力用の数値へ
        R_velocity = R_value * 128
        L_velocity = L_value * 128

        # 出力
        dynamixel_1.write_velocity(R_velocity)
        dynamixel_2.write_velocity(L_velocity)

        time.sleep(0.010)  # 処理速度を少し落とす

except KeyboardInterrupt:
    print("プログラムを終了します")

    j.quit()  # Joystickの切断

    # トルクを無効化
    dynamixel_1.disable_torque()
    dynamixel_2.disable_torque()

    time.sleep(0.010)  # 無効化されるまで少し待つ

    dynamixel_1.close_port()  # Dynamixelとの通信を切断
    dynamixel_2.close_port()
