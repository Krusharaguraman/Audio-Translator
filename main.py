import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import pygame
import time
from pathlib import Path
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from tkinter import simpledialog, messagebox

# Global variables
dropped_file_path = ""
output_audio_path = Path("D:/objectdetection/output.mp3")  # Output path

# Initialize pygame mixer
pygame.mixer.init()

# --- GradientButton Class (Styled like .cssbuttons-io) ---
class GradientButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=180, height=50, font_size=14):
        super().__init__(master, width=width, height=height, bg="white", highlightthickness=0)

        self.command = command
        self.text = text
        self.font = ("Helvetica", font_size, "bold")
        self.gradient_colors = ("#8e2de2", "#4a00e0")
        self.radius = 20

        self.button_bg = self.create_rectangle(0, 0, width, height, outline="", fill=self.gradient_colors[0])
        self.button_text = self.create_text(width//2, height//2, text=text, fill="ghostwhite", font=self.font)

        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def on_hover(self, event):
        self.itemconfig(self.button_bg, fill=self.gradient_colors[1])

    def on_leave(self, event):
        self.itemconfig(self.button_bg, fill=self.gradient_colors[0])

    def on_click(self, event):
        if self.command:
            self.command()

# --- Main Logic ---
def process_audio(file_path, target_language):
    global output_audio_path
    recognizer = sr.Recognizer()
    translator = Translator()

    with sr.AudioFile(file_path) as source:
        print("Listening...")
        audio_data = recognizer.record(source)
        try:
            english_text = recognizer.recognize_google(audio_data)
            print("Recognized Text (English):", english_text)

            translated = translator.translate(english_text, dest=target_language)
            translated_text = translated.text
            print(f"Translated Text ({target_language}):", translated_text)

            tts = gTTS(text=translated_text, lang=target_language)
            tts.save(str(output_audio_path))
            print(f"✅ Audio saved to {output_audio_path}")

            root.destroy()
            play_audio_window()

        except sr.UnknownValueError:
            print("❌ Could not understand the audio.")
        except sr.RequestError as e:
            print(f"❌ Could not request results; {e}")

def on_drop(event):
    global dropped_file_path
    dropped_file_path = event.data
    filename = Path(dropped_file_path).name
    file_label.config(text=f"File: {filename}")
    enter_button.config(state=tk.NORMAL)

def ask_language():
    target_language = simpledialog.askstring("Target Language", "Enter target language code (e.g., 'hi' for Hindi, 'fr' for French):")
    if target_language:
        process_audio(dropped_file_path, target_language)
    else:
        messagebox.showwarning("Invalid Input", "Please enter a valid language code.")

def play_audio(audio_path):
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play(loops=0, start=0.0)

def pause_audio():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()

def play_audio_window():
    play_window = tk.Tk()
    play_window.title("Audio Playback")
    play_window.geometry("400x250")
    play_window.config(bg="#E3F2FD")

    label = tk.Label(play_window, text=f"Playing audio: {output_audio_path.name}", bg="#E3F2FD", font=("Helvetica", 14))
    label.pack(pady=30)

    # Play Button
    play_btn = GradientButton(play_window, text="▶ Play", command=lambda: play_audio(str(output_audio_path)))
    play_btn.pack(pady=10)

    # Pause Button
    pause_btn = GradientButton(play_window, text="⏸ Pause", command=pause_audio)
    pause_btn.pack(pady=10)

    play_window.mainloop()

# --- Main App Window ---
root = TkinterDnD.Tk()
root.title("Audio File Translator")
root.geometry("400x300")
root.config(bg="#BBDEFB")

# Labels
label = tk.Label(root, text="Drag and drop an audio file here", width=40, height=3, bg="#81D4FA", font=("Helvetica", 14))
label.pack(pady=20)

file_label = tk.Label(root, text="No file dropped", bg="#BBDEFB", font=("Helvetica", 12))
file_label.pack(pady=5)

# Custom Gradient "Enter" Button
enter_button = GradientButton(root, text="Translate Audio", command=ask_language)
enter_button.pack(pady=20)
enter_button.config(state=tk.DISABLED)

# Drag-and-drop support
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

root.mainloop()
