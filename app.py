import os, io, time, json, threading
from PIL import Image
import numpy as np
import torch
import torch.nn as nn
from torchvision import transforms, models
from flask import Flask, render_template, Response, request, jsonify
import cv2

# CONFIG
MODEL_PATH = "model.pth"
CLASSES_JSON = "classes.json"
CAMERA_INDEX = 0
INFER_EVERY_N_FRAMES = 3
USE_GPU = torch.cuda.is_available()
HOST = "0.0.0.0"
PORT = 5000
CONF_THRESHOLD = 0.6 

latest_prediction = "Waiting..."
latest_confidence = 0.0
prediction_lock = threading.Lock()

app = Flask(__name__)

if os.path.exists(CLASSES_JSON):
    with open(CLASSES_JSON, "r") as f:
        CLASS_NAMES = json.load(f)
else:
    CLASS_NAMES = ["blue_finger", "clubbing", "healthy"]
print("CLASS_NAMES:", CLASS_NAMES)
NUM_CLASSES = len(CLASS_NAMES)

device = torch.device("cuda" if USE_GPU else "cpu")
print("Device:", device)
def build_model(num_classes):
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model
model = build_model(NUM_CLASSES).to(device)
state = torch.load(MODEL_PATH, map_location=device)
if any(k.startswith("module.") for k in state.keys()):
    from collections import OrderedDict
    new_state = OrderedDict()
    for k,v in state.items():
        new_state[k.replace("module.", "")] = v
    state = new_state
model.load_state_dict(state)
model.eval()
softmax = nn.Softmax(dim=1)

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

latest_prediction = "Waiting..."
latest_confidence = 0.0
prediction_lock = threading.Lock()
class VideoCamera:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1600)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1200)
        self.lock = threading.Lock()
        self.running = True
        self.frame = None
        t = threading.Thread(target=self._reader, daemon=True)
        t.start()

    def _reader(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.05)
                continue
            with self.lock:
                self.frame = frame

    def get_frame(self):
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()

    def release(self):
        self.running = False
        try:
            self.cap.release()
        except:
            pass

camera = VideoCamera(src=CAMERA_INDEX)

def is_white_background(frame, white_threshold=200, white_percentage=0.7):

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    white_pixels = np.sum(gray > white_threshold)
    total_pixels = gray.shape[0] * gray.shape[1]
    white_ratio = white_pixels / total_pixels
    
    return white_ratio > white_percentage

def predict_pil(img_pil):
    x = transform(img_pil).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(x)
        probs = softmax(logits).cpu().numpy()[0]
    idx = int(np.argmax(probs))
    return CLASS_NAMES[idx], float(probs[idx]), {CLASS_NAMES[i]: float(probs[i]) for i in range(len(probs))}

def gen_frames():
    frame_count = 0
    last_label = None
    last_conf = 0.0
    global latest_prediction, latest_confidence
    
    while True:
        frame = camera.get_frame()
        if frame is None:
            time.sleep(0.05)
            continue
        frame_count += 1

        is_white_bg = is_white_background(frame)

        if frame_count % INFER_EVERY_N_FRAMES == 0:
            try:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil = Image.fromarray(rgb)
                label, conf, probs = predict_pil(pil)
                last_label, last_conf = label, conf
                
                with prediction_lock:
                    if is_white_bg:
                        latest_prediction = "Place your finger"
                        latest_confidence = 0.0
                    elif conf < CONF_THRESHOLD:
                        latest_prediction = "Place your finger"
                        latest_confidence = conf
                    else:
                        latest_prediction = label
                        latest_confidence = conf
                        
            except Exception as e:
                print("Inference error:", e)
                last_label, last_conf = None, 0.0
                with prediction_lock:
                    latest_prediction = "Error"
                    latest_confidence = 0.0

        if is_white_bg:
            text = "Place your finger"
            color = (0, 0, 255)  # red warning
        elif last_label is not None:
            if last_conf < CONF_THRESHOLD:
                text = "Place your finger"
                color = (0, 0, 255)  # red warning
            else:
                text = f"{last_label} ({last_conf*100:.1f}%)"
                color = (0,255,0)
                if last_label.lower().startswith("clubb"):
                    color = (0,200,200)
                elif "blue" in last_label.lower():
                    color = (255,150,0)
        else:
            text = "Place your finger"
            color = (0, 0, 255)  
        
        cv2.rectangle(frame, (5,5), (350,45), (0,0,0), -1)
        cv2.putText(frame, text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2, cv2.LINE_AA)

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        jpg = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpg + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/predict_upload', methods=['POST'])
def predict_upload():
    if 'image' not in request.files:
        return jsonify({"error": "No image"}), 400
    f = request.files['image']
    img_bytes = f.read()
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    label, conf, probs = predict_pil(img)
    return jsonify({"label": label, "confidence": conf, "probs": probs})

@app.route('/api/output')
def api_output():
    """API endpoint for ESP32 to get current prediction status"""
    global latest_prediction, latest_confidence
    with prediction_lock:
        return jsonify({
            "prediction": latest_prediction,
            "confidence": latest_confidence,
            "timestamp": time.time(),
            "status": "active"
        })

@app.route('/esp32_status')
def esp32_status():
    global latest_prediction, latest_confidence
    with prediction_lock:
        return jsonify({
            "prediction": latest_prediction,
            "confidence": latest_confidence,
            "timestamp": time.time(),
            "status": "active"
        })

@app.route('/mobile')
def mobile_view():
    return render_template('mobile.html')

@app.route('/shutdown', methods=['POST'])
def shutdown():
    camera.release()
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return "shutting down"

if __name__ == '__main__':
    try:
        print("Starting app on", HOST, PORT)
        app.run(host=HOST, port=PORT, debug=False)
    finally:
        camera.release()
