# **AI Video Proctoring System**  

An AI-powered video proctoring system that analyzes video footage to detect potential cheating behavior during an exam. The system uses **MediaPipe** for facial landmark detection and tracks **eye movement, head movement, and mouth activity** to determine the probability of suspicious behavior.  

## **Features**  
- **Video Upload & Processing**: Users can upload a video file for analysis.  
- **Facial Landmark Detection**: Tracks **eye movement, head movement, and mouth movement**.  
- **Cheating Probability Calculation**: Computes a **cheating probability score** based on movements.  
- **Real-time Graphs**: Displays live updates of movement intensity and probability trends.  
- **Interactive UI**: Built with **Tkinter**, providing controls for **pause, resume, and stop analysis**.  
- **Cheating Event Logging**: Records potential cheating events for review.  


## **Project Structure**  

📦 src
 ┣ 📜 analyzer.py        # Video analysis logic using OpenCV and MediaPipe  
 ┣ 📜 ui.py              # Tkinter-based GUI with real-time graphs  
 ┗ 📜 main.py            # Entry point for launching the application    


## 🛠️ **Installation**
1️⃣ Clone the Repository
    git clone https://github.com/gsaikumar-123/Video_Proctoring_Analysis.git
    cd Video_Proctoring_Analysis/src
2️⃣ Install Dependencies
    Make sure you have Python 3.8+ installed. Then, install the required packages:
    pip install -r requirements.txt

## 🎯 **Usage**  

### **Run the Application**  
python main.py

### **Steps to Analyze a Video**  
1️⃣ Click **"Upload Video"** and select a file (`.mp4`, `.avi`, `.mov`, `.mkv`).  
2️⃣ Click **"Analyze"** to start video processing.  
3️⃣ View real-time updates on **video display** and **graphs**.  
4️⃣ Use **"Pause"**, **"Resume"**, or **"Stop"** buttons to control analysis.  
5️⃣ After completion, the result will be displayed based on the detected behavior.  


## ⚙️ **How It Works**  

### **Cheating Detection Algorithm**  
🔍 The system calculates **cheating probability** based on:  
- **Eye movement**: Frequent rapid movement might indicate looking away.  
- **Head movement**: Sudden or excessive turning suggests distraction.  
- **Mouth movement**: Frequent talking could indicate communication.  

The probability formula:  
cheating_score = (0.4 * eye_tracking) + (0.4 * head_movement) + (0.2 * mouth_movement)

- **Low Risk (0-30%)** ✅ – No suspicious behavior.  
- **Moderate Risk (30-60%)** ⚠️ – Some unusual activity.  
- **High Risk (60-100%)** ❌ – Strong suspicion of cheating.  

---

## 🛠 **Customization & Improvements**  
🔧 You can modify:  
- **Frame skipping rate (`FRAME_SKIP`)** to optimize processing speed.  
- **Threshold values** for cheating probability.  
- **Graph refresh rates** for real-time plotting.  
