# Video Converter Setup Instructions

## ⚠️ FFmpeg Required

This application requires **ffmpeg.exe** to be placed in the same directory as the Python script.

## 📥 How to Get FFmpeg

### Option 1: Download from Official Source (Recommended)

1. **Visit**: https://www.gyan.dev/ffmpeg/builds/
2. **Download**: Click on "ffmpeg-release-essentials.zip" (or "ffmpeg-git-essentials.zip")
3. **Extract**: Unzip the downloaded file
4. **Locate**: Open the extracted folder → go to the `bin` folder
5. **Copy**: Copy **`ffmpeg.exe`** from the bin folder
6. **Paste**: Place it in: `C:\Users\theda\PROJECTS\mediaformatconverter\`

### Option 2: Quick Download Link

Direct download: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.7z

### Option 3: Using Chocolatey (if installed)

```powershell
choco install ffmpeg
```

Then copy `ffmpeg.exe` from `C:\ProgramData\chocolatey\bin\` to your project folder.

## ✅ Verify Installation

After placing ffmpeg.exe in the folder, you should have:

```
C:\Users\theda\PROJECTS\mediaformatconverter\
├── ffmpeg.exe          ← This file is required!
├── video_converter.py
└── SETUP_INSTRUCTIONS.md
```

## 🚀 Running the Application

Once ffmpeg.exe is in place:

1. Install Python dependencies:
   ```powershell
   pip install customtkinter
   ```

2. Run the application:
   ```powershell
   python video_converter.py
   ```

## 🎯 Features

- **Hardware Encoding**: Uses NVIDIA GPU (av1_nvenc)
- **Batch Processing**: Convert multiple files at once
- **Quality Control**: Adjustable RF/CQ value (20-40)
- **Resolution Options**: Original, 1080p, or 720p
- **Audio**: Converts to Opus @ 128k
- **Subtitles**: Preserves internal subs and auto-detects .srt files
- **Output**: Saves to "Converted" subfolder as `[filename]_AV1.mkv`

## ❓ Troubleshooting

**Error: "FFmpeg Not Found"**
- Ensure `ffmpeg.exe` is in the same folder as `video_converter.py`
- Check the file is named exactly `ffmpeg.exe` (not `ffmpeg` or `ffmpeg.exe.exe`)

**Error: "NVIDIA GPU not found"**
- Your system needs an NVIDIA GPU with AV1 encoding support
- Alternatively, modify the script to use software encoding (CPU-based)
