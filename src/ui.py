import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import cv2
from analyzer import VideoAnalyzer
import os
from PIL import Image, ImageTk

class EnhancedVideoUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Video Proctoring System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        self.analyzer = VideoAnalyzer()
        self.analyzer.ui_callback = self.update_log
        self.setup_ui()
        
        self.update_id = None
        self.video_image = None

    def update_log(self, log_msg):
        self.log_text.insert(tk.END, log_msg)
        self.log_text.see(tk.END)
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.upload_btn = ttk.Button(control_frame, text="Upload Video", command=self.upload_video)
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        
        self.analyze_btn = ttk.Button(control_frame, text="Analyze", command=self.analyze_video, state="disabled")
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = ttk.Button(control_frame, text="Pause", command=self.toggle_pause, state="disabled")
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_analysis, state="disabled")
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.file_label = ttk.Label(control_frame, text="No file selected")
        self.file_label.pack(side=tk.LEFT, padx=20)
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        video_frame = ttk.LabelFrame(content_frame, text="Video Analysis")
        video_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.video_canvas = tk.Canvas(video_frame, bg="black")
        self.video_canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        graphs_frame = ttk.LabelFrame(content_frame, text="Real-time Metrics")
        graphs_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.log_text = tk.Text(graphs_frame, height=10, width=60)
        self.log_text.pack(fill=tk.BOTH, padx=5, pady=5)
            
        self.fig = Figure(figsize=(6, 8), dpi=100)
        self.fig.patch.set_facecolor('#f0f0f0')
        
        self.ax1 = self.fig.add_subplot(211)
        self.ax1.set_title("Movement Tracking")
        self.ax1.set_xlabel("Time (seconds)")
        self.ax1.set_ylabel("Movement Intensity")
        self.ax1.grid(True, linestyle='--', alpha=0.7)
        
        self.ax2 = self.fig.add_subplot(212)
        self.ax2.set_title("Cheating Probability")
        self.ax2.set_xlabel("Time (seconds)")
        self.ax2.set_ylabel("Probability (%)")
        self.ax2.set_ylim(0, 100)
        self.ax2.grid(True, linestyle='--', alpha=0.7)
        
        self.ax2.axhline(y=30, color='green', linestyle='-', alpha=0.3)
        self.ax2.axhline(y=60, color='red', linestyle='-', alpha=0.3)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=graphs_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(status_frame, variable=self.progress_var, length=100)
        self.progress.pack(fill=tk.X, side=tk.TOP)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.result_label = ttk.Label(status_frame, text="", font=("Arial", 10, "bold"))
        self.result_label.pack(side=tk.RIGHT, padx=5)
        
        self.fig.tight_layout()
    
    def upload_video(self):
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.mp4 *.avi *.mov *.mkv"), ("All Files", "*.*")]
        )
        if file_path:
            self.analyzer.video_path = file_path
            self.file_label.config(text=f"File: {os.path.basename(file_path)}")
            self.analyze_btn.config(state="normal")
            self.status_label.config(text="Video loaded. Ready to analyze.")
    
    def analyze_video(self):
        if not self.analyzer.video_path:
            messagebox.showerror("Error", "No video file selected!")
            return
        
        self.progress_var.set(0)
        self.status_label.config(text="Analyzing video...")
        self.result_label.config(text="")
        self.analyze_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.stop_btn.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        
        threading.Thread(
            target=self.analyzer.analyze_video, 
            args=(self.analyzer.video_path, self.update_video_frame, self.update_progress),
            daemon=True
        ).start()
        
        self.start_animation()
    
    def toggle_pause(self):
        if self.analyzer.is_analyzing:
            if self.analyzer.pause_analysis:
                self.analyzer.pause_analysis = False
                self.pause_btn.config(text="Pause")
                self.status_label.config(text="Analysis resumed")
            else:
                self.analyzer.pause_analysis = True
                self.pause_btn.config(text="Resume")
                self.status_label.config(text="Analysis paused")
    
    def stop_analysis(self):
        if self.analyzer.is_analyzing:
            self.analyzer.is_analyzing = False
            self.status_label.config(text="Analysis stopped")
            self.pause_btn.config(state="disabled")
            self.stop_btn.config(state="disabled")
            self.analyze_btn.config(state="normal")
            
            if self.update_id:
                self.root.after_cancel(self.update_id)
    
    def update_video_frame(self, frame):
        if frame is not None:
            canvas_width = self.video_canvas.winfo_width()
            canvas_height = self.video_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                frame_height, frame_width = frame.shape[:2]
                aspect_ratio = frame_width / frame_height
                
                if canvas_width / canvas_height > aspect_ratio:
                    new_height = canvas_height
                    new_width = int(new_height * aspect_ratio)
                else:
                    new_width = canvas_width
                    new_height = int(new_width / aspect_ratio)
                
                frame = cv2.resize(frame, (new_width, new_height))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                self.video_image = ImageTk.PhotoImage(image=img)
                
                self.video_canvas.delete("all")
                self.video_canvas.create_image(
                    canvas_width // 2, canvas_height // 2, 
                    image=self.video_image, anchor=tk.CENTER
                )
    
    def update_progress(self, progress):
        self.progress_var.set(progress)
        
        if progress >= 100:
            self.status_label.config(text="Analysis complete")
            self.result_label.config(text=f"Result: {self.analyzer.final_result}")
            self.pause_btn.config(state="disabled")
            self.stop_btn.config(state="disabled")
            self.analyze_btn.config(state="normal")
    
    def start_animation(self):
        self.update_graphs()
    
    def update_graphs(self):
        if not self.analyzer.is_analyzing and len(self.analyzer.time_data) == 0:
            self.update_id = self.root.after(100, self.update_graphs)
            return
        
        self.ax1.clear()
        self.ax2.clear()
        
        self.ax1.set_title("Movement Tracking")
        self.ax1.set_xlabel("Time (seconds)")
        self.ax1.set_ylabel("Movement Intensity")
        self.ax1.grid(True, linestyle='--', alpha=0.7)
        
        self.ax2.set_title("Cheating Probability")
        self.ax2.set_xlabel("Time (seconds)")
        self.ax2.set_ylabel("Probability (%)")
        self.ax2.set_ylim(0, 100)
        self.ax2.grid(True, linestyle='--', alpha=0.7)
        
        self.ax2.axhline(y=30, color='green', linestyle='-', alpha=0.3)
        self.ax2.axhline(y=60, color='red', linestyle='-', alpha=0.3)
        
        if len(self.analyzer.time_data) > 0:
            self.ax1.plot(self.analyzer.time_data, self.analyzer.eye_tracking_data, 
                         label="Eye Movement", color='cyan')
            self.ax1.plot(self.analyzer.time_data, self.analyzer.head_movement_data, 
                         label="Head Movement", color='lime')
            self.ax1.plot(self.analyzer.time_data, self.analyzer.mouth_movement_data, 
                         label="Mouth Movement", color='magenta')
            self.ax1.legend(loc='upper left')
            
            self.ax2.plot(self.analyzer.time_data, self.analyzer.cheating_probability_data, 
                         label="Cheating Probability", color='red', linewidth=2)
            
            self.ax2.axhspan(0, 30, alpha=0.2, color='green')
            self.ax2.axhspan(30, 60, alpha=0.2, color='yellow')
            self.ax2.axhspan(60, 100, alpha=0.2, color='red')
            
            if len(self.analyzer.time_data) > 0:
                self.ax2.scatter([self.analyzer.time_data[-1]], [self.analyzer.current_probability], 
                                color='blue', s=100, zorder=5)
        
        self.fig.tight_layout()
        self.canvas.draw()
        self.update_id = self.root.after(100, self.update_graphs)