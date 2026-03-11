1. Gesture Volume Control (macOS):
This is a Python tool that lets you control your Mac's volume using hand gestures. It uses Mediapipe for hand tracking and AppleScript to talk to the system.The goal wasn't just to make it work, but to make it feel "premium"—like using a high-end physical slider rather than a jittery webcam hack.

2. Why this is different:
Most gesture controllers use "absolute mapping" (reaching from the floor to the ceiling to go from 0 to 100%). That’s exhausting. This project uses a Relative Clutch system:

  The Grab: Volume only changes when you pinch your thumb and index together.
  The Scroll: Once pinched, you only need to move your hand about 3–4 inches to cover the full volume range.
  The Release: Open your hand to "lock" the volume in place.

3. The Math (Making it feel natural):
    1. Natural Hearing: Humans don't hear volume linearly. If you change volume in straight lines, it feels too jumpy at the top and too         quiet at the bottom. I used a power curve to mimic how we actually hear:

                                                "Volume =(V_virtual/100)^1.15 × 100"

4. Eliminating Jitter:
Webcams are noisy, and hands shake. I added a Low-Pass Filter so the volume "floats" smoothly to your hand position rather than teleporting instantly. This gets rid of the "stutter" typical in most vision projects.

5. How to use it:
  1. Pinch:	Activate volume slider
  2. Move Up/Down:	Adjust volume levels
  3. Open Palm:	Stop tracking (Standby)

6. Quick Start
    Install dependencies:
                                                "pip install opencv-python mediapipe"

python main.py


Note: You'll need to give your Terminal "Accessibility" permissions in System Settings so it can change the volume.


