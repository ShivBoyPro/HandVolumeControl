import cv2
import mediapipe as mp
import math
import numpy as np
import os
import subprocess

def get_mac_volume():
    cmd = "osascript -e 'output volume of (get volume settings)'"
    try:
        result = subprocess.check_output(cmd, shell=True)
        return int(result.strip())
    except:
        return 50

# --- SETUP ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.8, min_tracking_confidence=0.8)
mp_draw = mp.solutions.drawing_utils
cap = cv2.VideoCapture(0)

is_pinching = False
last_hand_y = 0    
virtual_vol = float(get_mac_volume()) 
smooth_vol = virtual_vol # The actual volume that gets sent to Mac
last_sent_vol = -1 

# --- AGGRESSION DAMPENERS ---
sensitivity = 0.4    # Low sensitivity for precision
smoothing = 0.15     # Lower = smoother/heavier. Higher = snappier/aggressive.
log_exponent = 1.1   # Almost linear to stop the "dropping" feel

while cap.isOpened():
    success, img = cap.read()
    if not success: break

    img = cv2.flip(img, 1)
    h, w, c = img.shape
    results = hands.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

    if results.multi_hand_landmarks:
        hand_lms = results.multi_hand_landmarks[0]
        lmList = [[id, int(lm.x * w), int(lm.y * h)] for id, lm in enumerate(hand_lms.landmark)]

        if lmList:
            x1, y1 = lmList[4][1], lmList[4][2] 
            x2, y2 = lmList[8][1], lmList[8][2] 
            hand_y = lmList[5][2] 
            dist = math.hypot(x2 - x1, y2 - y1)

            if dist < 65: # Slightly tighter pinch detection
                if not is_pinching:
                    is_pinching = True
                    last_hand_y = hand_y
                    virtual_vol = float(get_mac_volume())
                    smooth_vol = virtual_vol
                
                dy = last_hand_y - hand_y 
                if abs(dy) < 2: dy = 0 
                
                # Update the target (virtual) volume
                virtual_vol += dy * sensitivity
                virtual_vol = np.clip(virtual_vol, 0, 100)
                last_hand_y = hand_y

                # --- THE DAMPENING ENGINE ---
                # smooth_vol "chases" virtual_vol but only moves a fraction of the distance per frame
                smooth_vol += (virtual_vol - smooth_vol) * smoothing
                
                # Apply very shallow log
                final_vol = int(math.pow(smooth_vol / 100, log_exponent) * 100)

                if final_vol != last_sent_vol:
                    os.system(f"osascript -e 'set volume output volume {final_vol}'")
                    last_sent_vol = final_vol

                # HUD
                cv2.putText(img, f"SMOOTHED: {final_vol}%", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            else:
                is_pinching = False
                mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("Damped Volume Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()