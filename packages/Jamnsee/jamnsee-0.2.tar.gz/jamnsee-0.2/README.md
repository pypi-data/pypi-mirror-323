CAMERA/WEBCAM-CAM utils: from JynPopMod.utils.camera_utils import *

### 1. **JynPopMod**
This function simply prints a message that provides information about "JynPopMod," linking to the relevant GitHub repository.

**Example Usage:**
```python
JynPopMod()  # Outputs the message with a GitHub link
```

---

### 2. **capture_photo**
This function captures a photo using your computer's webcam. It uses OpenCV to access the webcam and save a captured frame as an image file (in this case, as "captured_photo.jpg").

**Example Usage:**
```python
capture_photo()  # Captures a photo and saves it as "captured_photo.jpg"
```

---

### 3. **record_video**
This function records a video from your computer's webcam for a specified duration (default is 10 seconds). It writes the video to a file (`recorded_video.avi`) using OpenCV. The video recording can also be stopped manually by pressing the 'q' key.

**Example Usage:**
```python
record_video(15)  # Records a video for 15 seconds
```

---

### 4. **get_camera_resolution**
This function gets and prints the resolution of your webcam (width x height).

**Example Usage:**
```python
get_camera_resolution()  # Prints the current camera resolution
```

---

### 5. **camera_zoom**
This function zooms in on the camera feed by a specified factor. It enlarges the image by resizing the video frame from the webcam.

**Example Usage:**
```python
camera_zoom(3.0)  # Zooms in by a factor of 3 on the webcam feed
```

---

### 6. **capture_screenshot**
This function captures a screenshot of your screen and saves it to the specified output path (like a file on your computer).

**Example Usage:**
```python
capture_screenshot("screenshot.png")  # Saves a screenshot as "screenshot.png"
```