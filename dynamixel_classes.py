import os
import msvcrt
import sys, tty, termios
from dynamixel_sdk import *  # Uses Dynamixel SDK library


class Dynamixel:  ## This class is specified in X_series
    def __init__(self, port, baudrate, id,vel_limit=128):

        # キーボードを使った手動操作用関数の宣言（LinuxとWindowsで場合分け）
        if os.name == "nt":

            def getch():
                return msvcrt.getch().decode()

        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)

            def getch():
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch

        # ********* DYNAMIXEL Model definition *********
        # ***** (Use only one definition at a time) *****
        self.__MY_DXL = "X_SERIES"  # X330 (5.0 V recommended), X430, X540, 2X430
        self.__ADDR_TORQUE_ENABLE = 64
        self.__ADDR_OPERATION_MODE = 11
        self.__ADDR_VELOCITY_LIMIT = 44
        self.__ADDR_GOAL_VELOCITY = 104
        self.__ADDR_PRESENT_VELOCITY = 128
        self.__ADDR_PRESENT_POSITION = 132

        self.__BAUDRATE = baudrate
        # DYNAMIXEL Protocol Version (1.0 / 2.0)
        # https://emanual.robotis.com/docs/en/dxl/protocol2/
        self.__PROTOCOL_VERSION = 2.0

        # Factory default ID of all DYNAMIXEL is 1
        self.__DXL_ID = id

        # Use the actual port assigned to the U2D2.
        # ex) Windows: "COM*", Linux: "/dev/ttyUSB*", Mac: "/dev/tty.usbserial-*"
        self.__DEVICENAME = port

        self.__TORQUE_ENABLE = 1  # Value for enabling the torque
        self.__TORQUE_DISABLE = 0  # Value for disabling the torque

        self.__VELOCITY_MODE = 1  # Velocity Move
        self.__VELOCITY_LIMIT = vel_limit
        self.__goal_velocity = 0

        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        self.__portHandler = PortHandler(self.__DEVICENAME)

        # Initialize PacketHandler instance
        # Set the protocol version
        # Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
        self.__packetHandler = PacketHandler(self.__PROTOCOL_VERSION)

        # Open port
        if self.__portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()

        # Set port baudrate
        if self.__portHandler.setBaudRate(self.__BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            quit()

        # Initialize Goal Velocity
        self.write_velocity(0)

        # Set Velocity Limit
        dxl_comm_result, dxl_error = self.__packetHandler.write4ByteTxRx(
            self.__portHandler,
            self.__DXL_ID,
            self.__ADDR_VELOCITY_LIMIT,
            self.__VELOCITY_LIMIT,
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.__packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.__packetHandler.getRxPacketError(dxl_error))

        # Set Velocity Mode
        dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(
            self.__portHandler,
            self.__DXL_ID,
            self.__ADDR_OPERATION_MODE,
            self.__VELOCITY_MODE,
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % packetHandler.getRxPacketError(dxl_error))

    def enable_torque(self):
        # Enable Dynamixel Torque
        dxl_comm_result, dxl_error = self.__packetHandler.write1ByteTxRx(
            self.__portHandler,
            self.__DXL_ID,
            self.__ADDR_TORQUE_ENABLE,
            self.__TORQUE_ENABLE,
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.__packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.__packetHandler.getRxPacketError(dxl_error))

    def disable_torque(self):
        dxl_comm_result, dxl_error = self.__packetHandler.write1ByteTxRx(
            self.__portHandler,
            self.__DXL_ID,
            self.__ADDR_TORQUE_ENABLE,
            self.__TORQUE_DISABLE,
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.__packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.__packetHandler.getRxPacketError(dxl_error))

    def write_velocity(self, vel):
        self.__goal_velocity = max(
            (-1) * self.__VELOCITY_LIMIT, min(vel, self.__VELOCITY_LIMIT)
        )
        dxl_comm_result, dxl_error = self.__packetHandler.write4ByteTxRx(
            self.__portHandler,
            self.__DXL_ID,
            self.__ADDR_GOAL_VELOCITY,
            self.__goal_velocity,
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.__packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.__packetHandler.getRxPacketError(dxl_error))
        print("SET POSITION")
        print("[ID:%03d]  GoalVel:%03d" % (self.__DXL_ID, self.__goal_velocity))

    def read_velocity(self):
        (
            dxl_present_velocity,
            dxl_comm_result,
            dxl_error,
        ) = self.__packetHandler.read4ByteTxRx(
            self.__portHandler, self.__DXL_ID, self.__ADDR_PRESENT_VELOCITY
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.__packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.__packetHandler.getRxPacketError(dxl_error))

        print(
            "[ID:%03d]  GoalVel:%03d  PresVel:%03d"
            % (self.__DXL_ID, self.__goal_velocity, dxl_present_velocity)
        )

        return dxl_present_velocity

    def close_port(self):
        self.__portHandler.closePort()
