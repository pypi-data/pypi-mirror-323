"""                                               PRIVATE USE AND DERIVATIVE LICENSE AGREEMENT 

        By using this software (the "Software"), you (the "User") agree to the following terms:  

1. Grant of License:  
    The Software is licensed to you for personal and non-commercial purposes, as well as for incorporation into your own projects, whether for private or public release.  

2. Permitted Use:  
    - You may use the Software as part of a larger project and publish your program, provided you include appropriate attribution to the original author (the "Licensor").  
    - You may modify the Software as needed for your project but must clearly indicate any changes made to the original work.  

3. Restrictions:  
     - You may not sell, lease, or sublicense the Software as a standalone product.  
     - If using the Software in a commercial project, prior written permission from the Licensor is required.(Credit,Cr)
     - You may not change or (copy a part of) the original form of the Software.  

4. Attribution Requirement:  
      Any published program or project that includes the Software, in whole or in part, must include the following notice:  
      *"This project includes software developed by [Jynoqtra], © 2025. Used with permission under the Private Use and Derivative License Agreement."*  

5. No Warranty:  
      The Software is provided "as is," without any express or implied warranties. The Licensor is not responsible for any damage or loss resulting from the use of the Software.  

6. Ownership:  
      All intellectual property rights, including but not limited to copyright and trademark rights, in the Software remain with the Licensor.  

7. Termination:  
     This license will terminate immediately if you breach any of the terms and conditions set forth in this agreement.  

8. Governing Law:  
      This agreement shall be governed by the laws of [the applicable jurisdiction, without regard to its conflict of law principles].  

9. Limitation of Liability:  
     In no event shall the Licensor be liable for any direct, indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenue, data, or use, incurred by you or any third party, whether in an action in contract, tort (including but not limited to negligence), or otherwise, even if the Licensor has been advised of the possibility of such damages.  

            Effective Date: [2025]  

            © 2025 [Jynoqtra]
"""

import cv2
import time
import pyautogui

def JynPopMod():
    print("Click to see about JynPopMod https://github.com/Jynoqtra/JynPopMod that made by Jynoqtra")

def capture_photo():
    cap = cv2.VideoCapture(0)
    try:
        ret, frame = cap.read()
        if ret:
            filename = "captured_photo.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved Captured Photo: {filename}")
    except Exception as e:
        print(f"Error capturing photo: {e}")
    finally:
        cap.release()

def record_video(duration=10):
    cap = cv2.VideoCapture(0)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('recorded_video.avi', fourcc, 20.0, (frame_width, frame_height))
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            out.write(frame)
            cv2.imshow('Recording Video Press q To Stop.', frame)
            if time.time() - start_time > duration:
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    except Exception as e:
        print(f"Error recording video: {e}")
    finally:
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        print("Video Recorded.")

def get_camera_resolution():
    cap = cv2.VideoCapture(0)
    try:
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera resolution: {width}x{height}")
    finally:
        cap.release()

def camera_zoom(factor=2.0):
    cap = cv2.VideoCapture(0)
    try:
        ret, frame = cap.read()
        if ret:
            height, width = frame.shape[:2]
            new_width = int(width * factor)
            new_height = int(height * factor)
            zoomed_frame = cv2.resize(frame, (new_width, new_height))
            cv2.imshow("Zoomed In", zoomed_frame)
            if cv2.waitKey(0) & 0xFF == ord('q'):
                pass
    finally:
        cap.release()
        cv2.destroyAllWindows()

def capture_screenshot(output_path):
    screen = pyautogui.screenshot()
    screen.save(output_path)
