"""Quick script to test RTSP camera connection directly."""
import os
from urllib.parse import quote
from dotenv import load_dotenv
import cv2

load_dotenv()

ip = os.getenv("TAPO_IP")
user = quote(os.getenv("TAPO_USER", ""), safe="")
pwd = quote(os.getenv("TAPO_PASSWORD", ""), safe="")

url = f"rtsp://{user}:{pwd}@{ip}:554/stream2"
print(f"Testing RTSP: rtsp://***:***@{ip}:554/stream2")

cap = cv2.VideoCapture(url)
ret, frame = cap.read()
cap.release()

if ret:
    print(f"SUCCESS! Frame size: {frame.shape[1]}x{frame.shape[0]}")
else:
    print("FAILED — RTSP connection refused or wrong credentials")
    print("Try these RTSP URLs manually in VLC:")
    print(f"  rtsp://{user}:{pwd}@{ip}:554/stream1")
    print(f"  rtsp://{user}:{pwd}@{ip}:554/stream2")
