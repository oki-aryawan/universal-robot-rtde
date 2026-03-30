import rtde_receive
import time
import math  # Needed for degree conversion

ROBOT_IP = "192.168.1.15"

try:
    rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
    print("Connected! Reading data...\n")

    while True:
        # 1. Get Pose and convert X, Y, Z to mm
        tcp_pose = rtde_r.getActualTCPPose()
        tcp_mm = [val * 1000 if i < 3 else val for i, val in enumerate(tcp_pose)]

        # 2. Get Joints and convert ALL to degrees
        joint_q_rad = rtde_r.getActualQ()
        joint_q_deg = [math.degrees(q) for q in joint_q_rad]

        # Display results
        # Format TCP to 2 decimal places, Joints to 1 decimal place
        print(f"TCP [mm]: X={tcp_mm[0]:.2f}, Y={tcp_mm[1]:.2f}, Z={tcp_mm[2]:.2f}")
        print(f"Joints [deg]: {['{:.1f}°'.format(d) for d in joint_q_deg]}")
        print("-" * 40)

        time.sleep(0.5)

except Exception as e:
    print(f"Error: {e}")
