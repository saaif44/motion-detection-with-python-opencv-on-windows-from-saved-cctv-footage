import cv2
import subprocess

# Function to detect motion in the ROI and save motion-detected parts
def motion_detection(video_path, output_path):
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error: Cannot open video file.")
        return

    # Read the first frame to allow the user to select ROI
    ret, frame = cap.read()
    if not ret:
        print("Error: Cannot read video frame.")
        return

    # Allow the user to select the ROI (Region of Interest)
    roi = cv2.selectROI("Select Region of Interest", frame, fromCenter=False, showCrosshair=True)
    x, y, w, h = roi

    # Close the ROI selection window
    cv2.destroyWindow("Select Region of Interest")

    # Get frame width and height for the output video
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Set up video writer to save motion-detected parts
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

    # Initialize background subtractor for motion detection
    backSub = cv2.createBackgroundSubtractorMOG2()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Crop the frame to the selected ROI
        roi_frame = frame[y:y+h, x:x+w]

        # Apply background subtraction to detect motion
        fg_mask = backSub.apply(roi_frame)

        # Find contours in the mask
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # If motion is detected (based on contour size)
        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Filter small movements
                motion_detected = True
                break

        # If motion is detected, save the frame to output video
        if motion_detected:
            out.write(frame)  # Save the full frame, not just the ROI

    cap.release()
    out.release()

    print(f"Motion-detected video saved at {output_path}")

# Function to play the saved video in VLC at 2x speed and full-screen
def play_video_in_vlc(video_path):
    command = ["vlc", "--rate", "2", "--fullscreen", video_path]
    subprocess.run(command)

# Example usage
input_video = "3.mp4"
output_video = "motion_detected_output3.mp4"
motion_detection(input_video, output_video)
play_video_in_vlc(output_video)
