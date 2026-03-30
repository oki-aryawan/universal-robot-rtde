import cv2
import numpy as np
import socket
import json

# --- CONFIGURATION ---
UDP_IP = "127.0.0.1"
UDP_PORT = 5005

# Robot Limits (mm)
Y_MM_RANGE = [-100, 100]  # Left/Right
Z_MM_RANGE = [300, 450]   # Up/Down
X_MM_RANGE = [250, 450]   # Forward/Backward (mapped from Area)

# Area Calibration (From your measurements)
AREA_MIN = 300   # Far position
AREA_MAX = 6000  # Close position

# Yellow HSV
LOWER_YELLOW = np.array([20, 100, 100]) 
UPPER_YELLOW = np.array([40, 255, 255])

cap = cv2.VideoCapture(0)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Smoothing (Low Pass Filter)
prev_x, prev_y, prev_z = 350.0, 0.0, 375.0
alpha = 0.2 

print(f"3D Tracking Active. Accepting Area: {AREA_MIN} to {AREA_MAX}")

while True:
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    mask = cv2.inRange(hsv, LOWER_YELLOW, UPPER_YELLOW)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)
        
        # ONLY ACCEPT VALUES IN YOUR SPECIFIED RANGE
        if AREA_MIN <= area <= AREA_MAX:
            ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
            
            # --- MAPPING ---
            raw_y = np.interp(x, [w * 0.1, w * 0.9], Y_MM_RANGE)
            raw_z = np.interp(y, [h * 0.1, h * 0.9], [Z_MM_RANGE[1], Z_MM_RANGE[0]])
            
            # Map Area (300-6000) to X (250-450mm)
            # Since 6000 is "Close", it maps to 450mm (Extended)
            # Since 300 is "Far", it maps to 250mm (Retracted)
            raw_x = np.interp(area, [AREA_MIN, AREA_MAX], X_MM_RANGE)

            # --- SMOOTHING ---
            smooth_x = (alpha * raw_x) + ((1 - alpha) * prev_x)
            smooth_y = (alpha * raw_y) + ((1 - alpha) * prev_y)
            smooth_z = (alpha * raw_z) + ((1 - alpha) * prev_z)
            
            prev_x, prev_y, prev_z = smooth_x, smooth_y, smooth_z

            # --- SEND DATA ---
            data = {"x": float(smooth_x), "y": float(smooth_y), "z": float(smooth_z)}
            sock.sendto(json.dumps(data).encode(), (UDP_IP, UDP_PORT))

            # UI Feedback
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 0), 2)
            cv2.putText(frame, f"ROBOT X:{int(smooth_x)} Y:{int(smooth_y)} Z:{int(smooth_z)}", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, f"OUT OF RANGE (Area: {int(area)})", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("3D Yellow Tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
