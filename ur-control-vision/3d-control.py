import rtde_control
import socket
import json

# --- ROBOT CONFIG ---
ROBOT_IP = "192.168.1.15"
FIXED_ROT = [2.959, -0.680, 0.993]

# --- NETWORK CONFIG ---
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.setblocking(False)

def main():
    try:
        print(f"Connecting to Robot at {ROBOT_IP}...")
        rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
        
        # Home Position (X=0.350m, Y=0.0m, Z=0.375m)
        rtde_c.moveL([0.350, 0.0, 0.375] + FIXED_ROT, 0.2, 0.2)
        print("3D Control Ready!")

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                coords = json.loads(data.decode())

                # Convert mm (from JSON) to Meters (for UR)
                x_m = coords['x'] / 1000.0
                y_m = coords['y'] / 1000.0
                z_m = coords['z'] / 1000.0

                target_pose = [x_m, y_m, z_m] + FIXED_ROT

                # Real-time servoing
                # servoL(pose, accel, vel, dt, lookahead, gain)
                rtde_c.servoL(target_pose, 0.5, 0.2, 0.01, 0.1, 300)

            except BlockingIOError:
                continue

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'rtde_c' in locals():
            rtde_c.servoStop()
            rtde_c.disconnect()

if __name__ == "__main__":
    main()
