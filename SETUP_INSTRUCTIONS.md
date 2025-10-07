# 🔬 NailScanner ESP32 Hotspot Setup Guide

## 📋 Step-by-Step Instructions

### Step 1: Upload ESP32 Code
1. Open Arduino IDE
2. Install ESP32 board support if not already installed:
   - Go to File → Preferences
   - Add this URL to Additional Board Manager URLs: 
     `https://dl.espressif.com/dl/package_esp32_index.json`
   - Go to Tools → Board → Boards Manager
   - Search "ESP32" and install "ESP32 by Espressif Systems"

3. Install required libraries:
   - Go to Tools → Manage Libraries
   - Install: "ArduinoJson" by Benoit Blanchon

4. Select your ESP32 board:
   - Tools → Board → ESP32 Arduino → "ESP32 Dev Module"
   - Tools → Port → Select your ESP32 COM port

5. Open `esp32_hotspot_code.ino` and upload to your ESP32

### Step 2: Power On ESP32
1. Connect ESP32 to power (USB or external)
2. Wait for the built-in LED to turn on (indicates ready)
3. ESP32 will create a WiFi hotspot named "NailScanner"

### Step 3: Connect Your Devices

#### Connect Laptop to ESP32:
1. On your laptop, go to WiFi settings
2. Connect to network: **NailScanner**
3. Password: **12345678**
4. Your laptop will get IP: 192.168.4.2
5. ESP32 IP will be: 192.168.4.1

#### Connect Mobile to ESP32:
1. On your mobile, go to WiFi settings
2. Connect to network: **NailScanner** 
3. Password: **12345678**
4. Mobile will get IP: 192.168.4.x (automatic)

### Step 4: Run Python App on Laptop
1. Make sure laptop is connected to "NailScanner" WiFi
2. Open terminal/command prompt
3. Navigate to your project folder:
   ```
   cd "d:\ranjith projects\Cardi_Nail"
   ```
4. Run the app:
   ```
   python app.py
   ```
5. App will start on: http://192.168.4.2:5000

### Step 5: Access on Mobile
1. Open web browser on mobile
2. Go to: **http://192.168.4.1/mobile**
3. You'll see the mobile-optimized interface
4. The interface will show live predictions from the laptop

## 🌐 Access URLs

| Device | URL | Purpose |
|--------|-----|---------|
| Laptop Control | http://192.168.4.1 | ESP32 control panel |
| Mobile Interface | http://192.168.4.1/mobile | Mobile nail scanner view |
| Python App | http://192.168.4.2:5000 | Direct Flask app access |

## 📱 Mobile Interface Features

- **Portrait Mode Optimized**: Perfect for mobile viewing
- **Real-time Updates**: Shows predictions every 2 seconds
- **Visual Indicators**: 
  - 🟢 Green: Healthy nails
  - 🟡 Yellow: Place finger/waiting
  - 🔴 Red: Health concerns detected
- **Connection Status**: Dot indicator shows ESP32 connection
- **Fullscreen Mode**: Tap fullscreen button for immersive view

## 🔧 Troubleshooting

### ESP32 Not Creating Hotspot:
- Check if code uploaded successfully
- Look for "Setting up Access Point..." in Serial Monitor
- Try power cycling the ESP32

### Can't Connect to NailScanner WiFi:
- Make sure you're using password: **12345678**
- Try forgetting and reconnecting to the network
- Check if ESP32 LED is on (indicates ready)

### Mobile Shows "Connection Lost":
- Verify mobile is connected to "NailScanner" WiFi
- Try refreshing the page
- Check if ESP32 is powered on

### Python App Won't Start:
- Make sure laptop is connected to "NailScanner" WiFi
- Check if camera is connected and working
- Verify all Python packages are installed: `pip install -r req.txt`

### No Predictions on Mobile:
- Make sure Python app is running on laptop
- Check laptop IP is 192.168.4.2
- Verify camera is working in Python app

## 💡 Tips

1. **Keep ESP32 Powered**: ESP32 needs constant power to maintain hotspot
2. **Camera Position**: Point camera at white background to see "Place finger" message
3. **Network Range**: Stay within WiFi range of ESP32 (usually 10-30 meters)
4. **Battery Saving**: Mobile interface auto-refreshes, close when not needed
5. **Multiple Devices**: Multiple mobiles can connect to same ESP32 hotspot

## 🔋 Power Options for ESP32

- **USB Power**: Connect to laptop/power bank via USB cable
- **External Power**: Use 5V DC adapter (recommended for permanent setup)
- **Battery Pack**: Use portable battery pack for mobile operation

## 📊 LED Indicators

| LED Pattern | Meaning |
|-------------|---------|
| Solid ON | ESP32 ready, hotspot active |
| Slow Blink | Healthy nail detected |
| Fast Blink | Health concern detected |
| OFF | Power issue or not ready |

---

**🚀 You're all set! Your mobile nail scanner is ready to use!**
