import tkinter as tk
from ui import EnhancedVideoUI

def main():
    root = tk.Tk()
    app = EnhancedVideoUI(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
