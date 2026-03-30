import rtde_control
import time

# --- CONFIGURATION ---
ROBOT_IP = "192.168.1.15"

# Define your 3 Targets: [Xmm, Ymm, Zmm, Rx_rad, Ry_rad, Rz_rad]
# These are example points—make sure they are in a safe area for your UR3!
targets = [
    [300.0, 100.0, 367.0, 2.959, -0.680, 0.993],  # Target 1 (High)
    [250.0, 100.0, 367.0, 2.959, -0.680, 0.993],  # Target 2 (Middle)
    [250.0, 200.0, 367.0, 2.959, -0.680, 0.993]  # Target 3 (Side)
]

pose_target = []

# Movement parameters
velocity = 0.1  # 100 mm/s
acceleration = 0.2  # 200 mm/s^2


def move_tcp_mm_rad(rtde_c, pose_custom, vel, acc):
    """Converts [mm, mm, mm, rad, rad, rad] to SI and moves."""
    target_pose_si = [
        pose_custom[0] / 1000.0,
        pose_custom[1] / 1000.0,
        pose_custom[2] / 1000.0,
        pose_custom[3],
        pose_custom[4],
        pose_custom[5]
    ]
    return rtde_c.moveL(target_pose_si, vel, acc)


def main():
    try:
        print(f"Connecting to {ROBOT_IP}...")
        rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
        print("Connected!\n")

        cycle_count = 0

        # --- INFINITE LOOP ---
        while True:
            cycle_count += 1
            print(f"--- Starting Cycle {cycle_count} ---")

            for i, pose in enumerate(targets):
                print(f"  Moving to Target {i + 1}: {pose[:3]} mm")
                move_tcp_mm_rad(rtde_c, pose, velocity, acceleration)
                time.sleep(0.2)  # Small pause between points

            print(f"--- Cycle {cycle_count} Complete ---\n")
            time.sleep(0.5)  # Pause before starting the next full loop

    except KeyboardInterrupt:
        print("\nStop signal received (Ctrl+C).")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'rtde_c' in locals():
            rtde_c.disconnect()
        print("Disconnected. Robot stopped.")

if __name__ == "__main__":
    main()
