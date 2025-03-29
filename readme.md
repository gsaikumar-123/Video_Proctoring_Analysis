# **AI Video Proctoring System**  

An AI-powered video proctoring system that analyzes video footage to detect potential cheating behavior during an exam. The system uses **MediaPipe** for facial landmark detection and **YOLOv4** for object detection, tracking **eye movement, head movement, mouth activity, and prohibited objects** to determine cheating probability.


## **Features**  
✅ **Video Upload & Processing**: Upload and analyze exam recordings  
✅ **Facial Analysis**: Tracks **eye, head, and mouth movements**  
✅ **Object Detection**: Flags **cell phones, books, and other prohibited items** (using YOLOv4)  
✅ **Cheating Probability Score**: Real-time risk assessment (0-100%)  
✅ **Interactive Dashboard**: Live graphs + event logging  
✅ **Pause/Resume Controls**: Flexible analysis management  


## **Project Structure**  

📦 src  
 ┣ 📜 analyzer.py        # Core analysis (MediaPipe + YOLO)  
 ┣ 📜 ui.py              # Tkinter GUI with live graphs  
 ┣ 📜 main.py            # Application entry point  
 ┣ 📜 yolov4.cfg         # YOLO model configuration  
 ┣ 📜 yolov4.weights     # YOLO pretrained weights  
 ┗ 📜 coco.names         # Object class labels  


## 🛠️ **Installation**  

### 1. Clone & Setup  
git clone https://github.com/gsaikumar-123/Video_Proctoring_Analysis.git  
cd Video_Proctoring_Analysis/src

### 2. Install Dependencies  
pip install -r requirements.txt

> **Note**: YOLO requires OpenCV with DNN support. For GPU acceleration, install `opencv-python-headless` and CUDA-enabled OpenCV.


## 🎯 **Usage**  
python main.py

### **Workflow**  
1. **Upload** exam video (MP4/AVI/MOV)  
2. **Analyze**:  
   - Real-time facial tracking  
   - Prohibited object detection  
3. **Review**:  
   - Cheating probability graph  
   - Flagged events timeline  

## ⚙️ **Detection System**  

### **1. Facial Analysis (MediaPipe)**  
| Metric          | Suspicious Pattern                | Weight |
|-----------------|-----------------------------------|--------|
| Eye Movement    | Frequent rapid shifts             | 30%    |
| Head Position   | Sudden turns/looking down         | 30%    |
| Mouth Activity  | Excessive talking motions         | 20%    |

### **2. Object Detection (YOLOv4)**  
🚫 **Flagged Items**:  
- Cell phones    
- Secondary devices  

**Impact**: Immediate +90% probability boost when detected  

### **Risk Levels**  
| Probability | Status          | Response               |
|-------------|-----------------|------------------------|
| 0-30%       | ✅ Normal       | No action              |
| 30-60%      | ⚠️ Suspicious  | Review recommended     |
| 60-100%     | ❌ High Risk    | Strong cheating evidence|


Here are the official download links for the YOLO files you'll need:

## **YOLOv4 Files Download Links**

### **1. yolov4.weights** (Official Pre-trained Weights)
🔗 [Download from AlexeyAB's Darknet Repository](https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v3_optimal/yolov4.weights)  
*(~245 MB - Official COCO dataset weights)*

### **2. yolov4.cfg** (Configuration File)
🔗 [Raw GitHub Link](https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg)  
*(Right-click → "Save As" to download)*

### **3. coco.names** (Class Labels)
🔗 [Raw GitHub Link](https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names)  
*(Contains all 80 COCO class names)*

---

## **Alternative Mirrors (if GitHub is slow)**

### **yolov4.weights**
🔗 [Google Drive Mirror](https://drive.google.com/file/d/1cewMfusmPjYWbrnuJRuKhPMwRe_b9PaT/view?usp=sharing)

### **yolov4-tiny.weights** (Lighter/Faster Version)
🔗 [GitHub Release](https://github.com/AlexeyAB/darknet/releases/download/darknet_yolo_v4_pre/yolov4-tiny.weights)  
*(~23 MB - Lower accuracy but faster processing)*

---

## **📦 Where to Place the Files**
After downloading, place these files in your `src/` directory:
```
src/
├── yolov4.weights
├── yolov4.cfg
└── coco.names
```

---

## **⚠️ Important Notes**
1. **Git Ignored**: These files are in `.gitignore` by default (due to large size)
2. **Alternative Models**: For different YOLO versions:
   - [YOLOv7](https://github.com/WongKinYiu/yolov7/releases)
   - [YOLOv5](https://github.com/ultralytics/yolov5/releases)
3. **Verification**: Ensure MD5 checksums match:
   ```
   yolov4.weights: 4f1e8a7f9ecd7845b5e20b03a3a6a8d7
   yolov4.cfg: d80e0defb9f1a873cc4946a0e9b4113a
   ```

---

## **🚀 Quick Start with YOLO**
1. Download all 3 files using the links above
2. Place them in your project's `src` folder
3. Set `USE_YOLO=true` in `.env` file
4. Run `python main.py`

> 💡 *For first-time runs, YOLO may take 10-20 seconds to initialize the model.*


## 🔧 **Customization**  

### **YOLO Configuration**  
1. **To disable object detection**:  
   Create `.env` file with:  
   USE_YOLO=false

2. **Custom object classes**:  
   Modify `coco.names` to focus on specific items.  

3. **Model Selection**:  
   Replace `yolov4.weights` and `.cfg` with other YOLO versions (e.g., YOLOv7-tiny for faster processing).

### **Performance Tuning**  
| Parameter          | File           | Recommendation          |
|--------------------|----------------|-------------------------|
| `FRAME_SKIP`       | analyzer.py    | Higher = faster but less precise |
| Detection threshold| analyzer.py    | Adjust `confidence > 0.5` for sensitivity |


## 📌 **Notes**  
- YOLO files (`*.weights`, `*.cfg`) are **git-ignored** by default. Download them separately or use the `.env` config.  
- For **GPU acceleration**, install CUDA/cuDNN and compile OpenCV with DNN support.  


🚀 **Next Steps**:  
- Add multi-person support  
- Integrate audio analysis for voice detection  
- Export detailed PDF reports  

📄 *See `requirements.txt` for full dependency list*