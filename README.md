![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Powered-green?style=for-the-badge&logo=ffmpeg&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)

# MediaConverter (NVENC + AV1)

GUI application built with Python and CustomTkinter. It leverages **NVIDIA NVENC** hardware acceleration to convert video libraries into **AV1 / MKV** files, preserving subtitles and ensuring compatibility.

## 🚀 Features

* **Hardware Acceleration:** Uses `av1_nvenc` (NVIDIA RTX 40-series optimized) for fast conversion.
* **Smart Compression:** Reduces file sizes by 30-50% while maintaining visual fidelity (App has customizable CQ Slider).
* **Subtitle Magic:** Automatically detects, scans, and muxes external `.srt` files into the final MKV container.
* **Audio Handling:** * 
    **AAC:** Universal compatibility
    * **Opus:** High-efficiency audio for modern clients.
* **Safety First:** Never overwrites originals; outputs to a `Converted` subfolder.

## 🛠️ Prerequisites

1.  **NVIDIA GPU:** RTX 40-series recommended (for AV1 encoding support).
2.  **FFmpeg:** You must have `ffmpeg.exe` installed or placed in the app directory.

## 📦 Installation (Running from Source)

1.  Clone the repository:
    ```bash
    git clone [https://github.com/YOUR_USERNAME/MediaConverter.git](https://github.com/YOUR_USERNAME/MediaConverter.git)
    cd MediaConverter
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Important:** Download [FFmpeg](https://ffmpeg.org/download.html) and place `ffmpeg.exe` in the root folder next to the script.
4.  Run the app:
    ```bash
    python video_converter.py
    ```

## 💿 Downloading the Exe (For non-coders)

Go to the **[Releases](link_to_your_releases_page)** tab on the right to download the standalone Windows Executable.
* *Note: You still need to place `ffmpeg.exe` next to the application for it to work.*

## 📄 License

[MIT License](LICENSE)