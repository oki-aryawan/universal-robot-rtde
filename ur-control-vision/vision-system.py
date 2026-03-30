import cv2
import numpy as np
import socket
import json

# --- CONFIGURATION ---
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
Y_MM_RANGE = [-100, 100]  # Robot Left/Right limits
Z_MM_RANGE = [300, 450]   # Robot Up/Down limits

# --- YELLOW COLOR CALIBRATION (HSV) ---
# Typical Yellow is around Hue 30. 
# [Hue, Saturation, Value]
LOWER_YELLOW = np.array([20, 100, 100]) 
UPPER_YELLOW = np.array([40, 255, 255])

# Initialize Camera and Socket
cap = cv2.VideoCapture(0)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Yellow Tracking Sender started. Use a yellow ball or tape.")

while True:
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1) # Mirror for intuitive control
    h, w, _ = frame.shape
    
    # 1. Convert to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 2. Create the Yellow Mask
    mask = cv2.inRange(hsv, LOWER_YELLOW, UPPER_YELLOW)
    
    # Clean up small "specks" of noise
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # 3. Find contours (blobs)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Find the largest yellow object in view
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Only track if it's a decent size (ignore noise)
        if cv2.contourArea(largest_contour) > 500:
            ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
            
            # Visual feedback
            cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            cv2.circle(frame, (int(x), int(y)), 5, (255, 255, 255), -1)

            # 4. Map Pixels to Robot MM
            # np.interp(input, [input_min, input_max], [output_min, output_max])
            target_y_mm = np.interp(x, [w * 0.1, w * 0.9], Y_MM_RANGE)
            target_z_mm = np.interp(y, [h * 0.1, h * 0.9], [Z_MM_RANGE[1], Z_MM_RANGE[0]])

            # 5. Send to Robot
            data = {"y": float(target_y_mm), "z": float(target_z_mm)}
            sock.sendto(json.dumps(data).encode(), (UDP_IP, UDP_PORT))

            cv2.putText(frame, f"YELLOW: Y={int(target_y_mm)} Z={int(target_z_mm)}", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    cv2.imshow("Yellow Object Tracker", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
