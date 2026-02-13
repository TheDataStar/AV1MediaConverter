"""
Modern Video Converter - AV1 Hardware Encoding with CustomTkinter GUI
Requires: customtkinter, ffmpeg.exe in the same directory
"""

import os
import subprocess
import threading
import re
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk

# Set appearance mode and color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


def detect_subtitle_language(filename):
    """
    Detect language code from subtitle filename.
    Returns tuple: (language_code, language_title)
    """
    filename_lower = filename.lower()
    
    # Language patterns: (pattern, code, title)
    language_patterns = [
        # English variants
        (r'\beng\b', 'eng', 'English'),
        (r'\ben\b', 'eng', 'English'),
        (r'\benglish\b', 'eng', 'English'),
        
        # Spanish variants
        (r'\bspa\b', 'spa', 'Spanish'),
        (r'\bes\b', 'spa', 'Spanish'),
        (r'\bspanish\b', 'spa', 'Spanish'),
        (r'\bespañol\b', 'spa', 'Spanish'),
        
        # French variants
        (r'\bfre\b', 'fre', 'French'),
        (r'\bfra\b', 'fre', 'French'),
        (r'\bfr\b', 'fre', 'French'),
        (r'\bfrench\b', 'fre', 'French'),
        
        # German variants
        (r'\bger\b', 'ger', 'German'),
        (r'\bdeu\b', 'ger', 'German'),
        (r'\bde\b', 'ger', 'German'),
        (r'\bgerman\b', 'ger', 'German'),
        
        # Italian variants
        (r'\bita\b', 'ita', 'Italian'),
        (r'\bit\b', 'ita', 'Italian'),
        (r'\bitalian\b', 'ita', 'Italian'),
        
        # Portuguese variants
        (r'\bpor\b', 'por', 'Portuguese'),
        (r'\bpt\b', 'por', 'Portuguese'),
        (r'\bportuguese\b', 'por', 'Portuguese'),
        
        # Japanese variants
        (r'\bjpn\b', 'jpn', 'Japanese'),
        (r'\bja\b', 'jpn', 'Japanese'),
        (r'\bjapanese\b', 'jpn', 'Japanese'),
        
        # Chinese variants
        (r'\bchi\b', 'chi', 'Chinese'),
        (r'\bzh\b', 'chi', 'Chinese'),
        (r'\bchinese\b', 'chi', 'Chinese'),
        
        # Korean variants
        (r'\bkor\b', 'kor', 'Korean'),
        (r'\bko\b', 'kor', 'Korean'),
        (r'\bkorean\b', 'kor', 'Korean'),
        
        # Russian variants
        (r'\brus\b', 'rus', 'Russian'),
        (r'\bru\b', 'rus', 'Russian'),
        (r'\brussian\b', 'rus', 'Russian'),
        
        # Arabic variants
        (r'\bara\b', 'ara', 'Arabic'),
        (r'\bar\b', 'ara', 'Arabic'),
        (r'\barabic\b', 'ara', 'Arabic'),
    ]
    
    for pattern, code, title in language_patterns:
        if re.search(pattern, filename_lower):
            return (code, title)
    
    # Default to English if no language detected
    return ('eng', 'English')


class VideoConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("AV1 Video Converter")
        self.geometry("900x750")
        self.minsize(800, 650)
        
        # Variables
        self.queue = []
        self.is_converting = False
        self.current_process = None
        
        # Resolution mapping
        self.resolution_map = {
            "Original": None,
            "1080p": "1920:1080",
            "720p": "1280:720"
        }
        
        # Audio codec mapping
        self.audio_codec_map = {
            "AAC (Universal)": {"codec": "aac", "bitrate": "192k"},
            "Opus (Efficient)": {"codec": "libopus", "bitrate": "128k"}
        }
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(4, weight=1)
        
        # Top buttons frame
        top_frame = ctk.CTkFrame(self)
        top_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)
        
        self.select_file_btn = ctk.CTkButton(
            top_frame,
            text="Select File",
            command=self.select_file,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.select_file_btn.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        
        self.select_folder_btn = ctk.CTkButton(
            top_frame,
            text="Select Folder",
            command=self.select_folder,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.select_folder_btn.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="ew")
        
        # Queue section
        queue_label = ctk.CTkLabel(
            self,
            text="Conversion Queue",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        queue_label.grid(row=1, column=0, padx=20, pady=(10, 5), sticky="w")
        
        # Queue listbox with scrollbar
        queue_frame = ctk.CTkFrame(self)
        queue_frame.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")
        queue_frame.grid_columnconfigure(0, weight=1)
        queue_frame.grid_rowconfigure(0, weight=1)
        
        self.queue_textbox = ctk.CTkTextbox(
            queue_frame,
            font=ctk.CTkFont(size=12),
            wrap="none"
        )
        self.queue_textbox.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Settings frame
        settings_frame = ctk.CTkFrame(self)
        settings_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Resolution dropdown
        resolution_label = ctk.CTkLabel(
            settings_frame,
            text="Resolution:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        resolution_label.grid(row=0, column=0, padx=(20, 10), pady=10, sticky="w")
        
        self.resolution_var = ctk.StringVar(value="Original")
        self.resolution_dropdown = ctk.CTkOptionMenu(
            settings_frame,
            values=["Original", "1080p", "720p"],
            variable=self.resolution_var,
            font=ctk.CTkFont(size=13),
            width=150
        )
        self.resolution_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Audio codec dropdown (NEW)
        audio_label = ctk.CTkLabel(
            settings_frame,
            text="Audio Codec:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        audio_label.grid(row=1, column=0, padx=(20, 10), pady=10, sticky="w")
        
        self.audio_var = ctk.StringVar(value="AAC (Universal)")
        self.audio_dropdown = ctk.CTkOptionMenu(
            settings_frame,
            values=["AAC (Universal)", "Opus (Efficient)"],
            variable=self.audio_var,
            font=ctk.CTkFont(size=13),
            width=150
        )
        self.audio_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Quality slider (UPDATED: 25-45, default 34)
        quality_label = ctk.CTkLabel(
            settings_frame,
            text="RF/CQ Value:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        quality_label.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="w")
        
        slider_frame = ctk.CTkFrame(settings_frame)
        slider_frame.grid(row=2, column=1, padx=10, pady=10, sticky="ew")
        slider_frame.grid_columnconfigure(0, weight=1)
        
        self.quality_var = ctk.IntVar(value=34)
        self.quality_slider = ctk.CTkSlider(
            slider_frame,
            from_=25,
            to=45,
            number_of_steps=20,
            variable=self.quality_var,
            command=self.update_quality_label
        )
        self.quality_slider.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        
        self.quality_value_label = ctk.CTkLabel(
            slider_frame,
            text="34",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=40
        )
        self.quality_value_label.grid(row=0, column=1)
        
        # Custom output filename entry (NEW)
        output_label = ctk.CTkLabel(
            settings_frame,
            text="Output Filename (Optional):",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        output_label.grid(row=3, column=0, padx=(20, 10), pady=10, sticky="w")
        
        self.output_name_entry = ctk.CTkEntry(
            settings_frame,
            placeholder_text="Leave blank for default naming",
            font=ctk.CTkFont(size=13),
            width=300
        )
        self.output_name_entry.grid(row=3, column=1, padx=10, pady=10, sticky="ew")
        
        # Start conversion button and progress
        conversion_frame = ctk.CTkFrame(self)
        conversion_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")
        conversion_frame.grid_columnconfigure(0, weight=1)
        
        self.start_btn = ctk.CTkButton(
            conversion_frame,
            text="Start Conversion",
            command=self.start_conversion,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#1f6aa5",
            hover_color="#144870"
        )
        self.start_btn.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        
        # Progress bar
        progress_frame = ctk.CTkFrame(conversion_frame)
        progress_frame.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="0%",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=50
        )
        self.progress_label.grid(row=0, column=1)
        
        # Log window
        log_label = ctk.CTkLabel(
            conversion_frame,
            text="Log Output",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        log_label.grid(row=2, column=0, padx=20, pady=(10, 5), sticky="w")
        
        self.log_textbox = ctk.CTkTextbox(
            conversion_frame,
            font=ctk.CTkFont(size=11),
            height=150
        )
        self.log_textbox.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
    def update_quality_label(self, value):
        """Update quality value label when slider moves"""
        self.quality_value_label.configure(text=str(int(float(value))))
        
    def select_file(self):
        """Select a single video file"""
        filetypes = (
            ("Video files", "*.mp4 *.mkv *.avi *.mov *.flv *.wmv *.webm"),
            ("All files", "*.*")
        )
        filename = filedialog.askopenfilename(
            title="Select video file",
            filetypes=filetypes
        )
        if filename:
            self.add_to_queue(filename)
            
    def select_folder(self):
        """Select a folder and add all video files"""
        folder = filedialog.askdirectory(title="Select folder with videos")
        if folder:
            video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm'}
            folder_path = Path(folder)
            video_files = [
                str(f) for f in folder_path.iterdir()
                if f.is_file() and f.suffix.lower() in video_extensions
            ]
            if video_files:
                for video_file in video_files:
                    self.add_to_queue(video_file)
                self.log(f"Added {len(video_files)} video(s) from folder")
            else:
                messagebox.showinfo("No Videos", "No video files found in selected folder")
                
    def add_to_queue(self, filepath):
        """Add a file to the conversion queue"""
        if filepath not in self.queue:
            self.queue.append(filepath)
            self.update_queue_display()
            self.log(f"Added to queue: {os.path.basename(filepath)}")
        else:
            self.log(f"Already in queue: {os.path.basename(filepath)}")
            
    def update_queue_display(self):
        """Update the queue display"""
        self.queue_textbox.delete("1.0", "end")
        for i, filepath in enumerate(self.queue, 1):
            self.queue_textbox.insert("end", f"{i}. {filepath}\n")
            
    def log(self, message):
        """Add message to log window"""
        self.log_textbox.insert("end", f"{message}\n")
        self.log_textbox.see("end")
    
    def find_matching_subtitles(self, video_path):
        """
        Find all SRT files in the video's directory that match the current video.
        Returns list of tuples: [(srt_path, language_code, language_title), ...]
        """
        video_path = Path(video_path)
        video_dir = video_path.parent
        video_stem = video_path.stem.lower()
        
        # Find all SRT files in the directory
        all_srt_files = list(video_dir.glob("*.srt"))
        
        if not all_srt_files:
            return []
        
        # Find all video files in the directory
        video_extensions = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm'}
        all_video_files = [
            f for f in video_dir.iterdir()
            if f.is_file() and f.suffix.lower() in video_extensions
        ]
        
        matching_subtitles = []
        
        # Safeguard logic for batch processing
        if len(all_video_files) == 1:
            # Only one video in folder - grab all SRTs
            for srt_file in all_srt_files:
                lang_code, lang_title = detect_subtitle_language(srt_file.name)
                matching_subtitles.append((srt_file, lang_code, lang_title))
        else:
            # Multiple videos - only grab SRTs that match this video's filename
            for srt_file in all_srt_files:
                srt_stem = srt_file.stem.lower()
                # Check if SRT filename contains the video filename
                if video_stem in srt_stem:
                    lang_code, lang_title = detect_subtitle_language(srt_file.name)
                    matching_subtitles.append((srt_file, lang_code, lang_title))
        
        return matching_subtitles
        
    def start_conversion(self):
        """Start the conversion process in a separate thread"""
        if self.is_converting:
            messagebox.showwarning("Already Converting", "Conversion is already in progress")
            return
            
        if not self.queue:
            messagebox.showwarning("Empty Queue", "Please add files to the queue first")
            return
            
        # Check if ffmpeg exists
        ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg.exe')
        if not os.path.exists(ffmpeg_path):
            messagebox.showerror(
                "FFmpeg Not Found",
                f"ffmpeg.exe not found in:\n{os.getcwd()}\n\nPlease place ffmpeg.exe in the same directory as this script."
            )
            return
            
        self.is_converting = True
        self.start_btn.configure(state="disabled", text="Converting...")
        self.select_file_btn.configure(state="disabled")
        self.select_folder_btn.configure(state="disabled")
        
        # Start conversion in separate thread
        conversion_thread = threading.Thread(target=self.conversion_worker, daemon=True)
        conversion_thread.start()
        
    def conversion_worker(self):
        """Worker thread for conversion process"""
        total_files = len(self.queue)
        
        for index, filepath in enumerate(self.queue.copy(), 1):
            self.log(f"\n{'='*60}")
            self.log(f"Converting {index}/{total_files}: {os.path.basename(filepath)}")
            self.log(f"{'='*60}")
            
            try:
                self.convert_video(filepath)
                self.queue.remove(filepath)
                self.after(0, self.update_queue_display)
            except Exception as e:
                self.log(f"ERROR: {str(e)}")
                
        self.is_converting = False
        self.after(0, self.conversion_complete)
        
    def convert_video(self, input_file):
        """Convert a single video file"""
        input_path = Path(input_file)
        
        # Create output directory
        output_dir = input_path.parent / "Converted"
        output_dir.mkdir(exist_ok=True)
        
        # Determine output filename (UPDATED: custom or default)
        custom_name = self.output_name_entry.get().strip()
        if custom_name:
            # Use custom name, ensure .mkv extension
            if not custom_name.endswith('.mkv'):
                output_filename = f"{custom_name}.mkv"
            else:
                output_filename = custom_name
        else:
            # Use default naming
            output_filename = f"{input_path.stem}_AV1.mkv"
        
        output_path = output_dir / output_filename
        
        # Smart Subtitle Scanner - Find all matching SRT files
        matching_subtitles = self.find_matching_subtitles(input_file)
        
        if matching_subtitles:
            subtitle_names = [f"{srt.name} ({lang_title})" for srt, _, lang_title in matching_subtitles]
            self.log(f"Found {len(matching_subtitles)} subtitle file(s): {', '.join(subtitle_names)}")
        else:
            self.log("No subtitle files found")
        
        # Build ffmpeg command
        ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg.exe')
        
        cmd = [ffmpeg_path, '-i', str(input_path)]
        
        # Add all subtitle files as inputs
        for srt_file, _, _ in matching_subtitles:
            cmd.extend(['-i', str(srt_file)])
        
        # Video encoding settings
        cmd.extend([
            '-c:v', 'av1_nvenc',
            '-preset', 'p7',
            '-cq', str(self.quality_var.get())
        ])
        
        # Resolution scaling if not original
        resolution = self.resolution_var.get()
        if resolution != "Original":
            scale = self.resolution_map[resolution]
            cmd.extend(['-vf', f'scale={scale}:force_original_aspect_ratio=decrease'])
        
        # Audio encoding (UPDATED: AAC or Opus based on selection)
        audio_selection = self.audio_var.get()
        audio_settings = self.audio_codec_map[audio_selection]
        cmd.extend([
            '-c:a', audio_settings['codec'],
            '-b:a', audio_settings['bitrate']
        ])
        
        # Subtitle handling
        cmd.extend(['-c:s', 'copy'])
        
        # Map streams (CRITICAL: proper mapping for video, audio, and all subtitles)
        cmd.extend(['-map', '0:v'])  # Map video from first input
        cmd.extend(['-map', '0:a'])  # Map audio from first input
        
        # Map each subtitle file and set metadata
        for idx, (srt_file, lang_code, lang_title) in enumerate(matching_subtitles):
            input_index = idx + 1  # Subtitle inputs start at index 1
            subtitle_stream_index = idx  # Subtitle stream index in output
            
            cmd.extend(['-map', f'{input_index}:0'])  # Map subtitle from input
            cmd.extend(['-metadata:s:s:{}'.format(subtitle_stream_index), f'language={lang_code}'])
            cmd.extend(['-metadata:s:s:{}'.format(subtitle_stream_index), f'title={lang_title}'])
        
        # Output file
        cmd.extend(['-y', str(output_path)])
        
        self.log(f"Command: {' '.join(cmd)}")
        
        # Get video duration for progress calculation
        duration = self.get_video_duration(input_file)
        
        # Run ffmpeg
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        self.current_process = process
        
        # Parse output for progress
        for line in process.stdout:
            line = line.strip()
            if line:
                # Look for time progress
                time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
                if time_match and duration > 0:
                    hours, minutes, seconds = time_match.groups()
                    current_time = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
                    progress = min(current_time / duration, 1.0)
                    percentage = int(progress * 100)
                    
                    self.after(0, lambda p=progress, pct=percentage: self.update_progress(p, pct))
                
                # Log important lines
                if any(keyword in line.lower() for keyword in ['error', 'warning', 'frame=', 'speed=']):
                    self.log(line)
        
        process.wait()
        
        if process.returncode == 0:
            self.log(f"✓ Successfully converted: {output_filename}")
            self.after(0, lambda: self.update_progress(1.0, 100))
        else:
            raise Exception(f"FFmpeg exited with code {process.returncode}")
            
    def get_video_duration(self, input_file):
        """Get video duration in seconds using ffmpeg"""
        try:
            ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg.exe')
            cmd = [
                ffmpeg_path,
                '-i', input_file,
                '-f', 'null',
                '-'
            ]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Parse duration from output
            duration_match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', result.stdout)
            if duration_match:
                hours, minutes, seconds = duration_match.groups()
                return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        except:
            pass
        return 0
        
    def update_progress(self, progress, percentage):
        """Update progress bar and label"""
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"{percentage}%")
        
    def conversion_complete(self):
        """Called when all conversions are complete"""
        self.start_btn.configure(state="normal", text="Start Conversion")
        self.select_file_btn.configure(state="normal")
        self.select_folder_btn.configure(state="normal")
        self.progress_bar.set(0)
        self.progress_label.configure(text="0%")
        self.log("\n" + "="*60)
        self.log("All conversions complete!")
        self.log("="*60)
        messagebox.showinfo("Complete", "All video conversions completed successfully!")


if __name__ == "__main__":
    app = VideoConverterApp()
    app.mainloop()
