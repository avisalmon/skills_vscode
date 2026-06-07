---
name: ffmpeg-automation
description: >
  Batch video/audio conversion, trimming, compression, thumbnail extraction,
  and subtitle embedding using ffmpeg from PowerShell and Python. TRIGGER:
  user says "ffmpeg", "convert video", "compress video", "extract audio",
  "trim video", "thumbnail from video", "batch convert", "transcode", or
  "mp4 to mp3".
---

  FFmpeg Automation — Video & Audio Processing

> **Purpose**: The Swiss army knife for media processing. Convert formats,
> compress video, extract audio, trim clips, capture thumbnails, burn
> subtitles, and batch-process entire folders — from PowerShell or Python.

---

   Table of Contents

1. [Quick Reference]( quick-reference)
2. [Installation]( installation)
3. [Core Concepts]( core-concepts)
4. [Audio Extraction]( audio-extraction)
5. [Video Conversion & Compression]( video-conversion--compression)
6. [Trimming & Cutting]( trimming--cutting)
7. [Thumbnails & Screenshots]( thumbnails--screenshots)
8. [Subtitles]( subtitles)
9. [Concatenation & Merging]( concatenation--merging)
10. [Batch Processing — PowerShell]( batch-processing--powershell)
11. [Python Wrapper (ffmpeg-python)]( python-wrapper-ffmpeg-python)
12. [Encoding Quality Reference]( encoding-quality-reference)
13. [Troubleshooting]( troubleshooting)
14. [Lessons Learned]( lessons-learned)

---

   Quick Reference

```powershell
  Extract audio as MP3
ffmpeg -i input.mp4 -q:a 0 -map a output.mp3

  Compress video (half file size, good quality)
ffmpeg -i input.mp4 -crf 28 -preset fast output.mp4

  Trim 30s clip starting at 1:05
ffmpeg -i input.mp4 -ss 00:01:05 -t 30 -c copy clip.mp4

  Thumbnail at 5 second mark
ffmpeg -i input.mp4 -ss 5 -frames:v 1 thumb.jpg

  Convert to GIF
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1" -loop 0 output.gif

  Get file info (no output)
ffmpeg -i input.mp4 -hide_banner
```

---

   Installation

    Windows
```powershell
  Via winget (recommended)
winget install Gyan.FFmpeg

  Via chocolatey
choco install ffmpeg

  Manual: download from https://ffmpeg.org/download.html
  Extract to C:\ffmpeg\ and add C:\ffmpeg\bin to PATH
```

    Verify
```powershell
ffmpeg -version
ffprobe -version
```

    corporate proxy for winget/choco
```powershell
$env:HTTP_PROXY = "http://proxy.example.com:8080"
$env:HTTPS_PROXY = "http://proxy.example.com:8080"
winget install Gyan.FFmpeg
```

---

   Core Concepts

| Flag | Meaning |
|------|---------|
| `-i input.mp4` | Input file |
| `-c copy` | Copy streams without re-encoding (fast, lossless) |
| `-c:v libx264` | Encode video with H.264 |
| `-c:a aac` | Encode audio with AAC |
| `-c:a mp3` | Encode audio as MP3 |
| `-crf 23` | Quality: 0=lossless, 23=default, 51=worst |
| `-preset fast` | Encoding speed: ultrafast/superfast/veryfast/faster/fast/medium/slow |
| `-ss 00:01:30` | Seek to position (before `-i` = fast seek) |
| `-t 60` | Duration in seconds |
| `-to 00:02:30` | End time |
| `-vf "scale=1280:-1"` | Video filter: resize width to 1280, height auto |
| `-af "volume=2.0"` | Audio filter: double volume |
| `-y` | Overwrite output without asking |
| `-hide_banner` | Suppress version header in output |

---

   Audio Extraction

```powershell
  MP3 (best variable quality)
ffmpeg -i input.mp4 -q:a 0 -map a output.mp3

  MP3 at fixed bitrate
ffmpeg -i input.mp4 -b:a 192k output.mp3

  AAC (smaller, same quality)
ffmpeg -i input.mp4 -c:a aac -b:a 128k output.aac

  WAV (uncompressed — large)
ffmpeg -i input.mp4 -c:a pcm_s16le output.wav

  FLAC (lossless compressed)
ffmpeg -i input.mp4 -c:a flac output.flac

  Extract audio from specific time range
ffmpeg -i input.mp4 -ss 00:00:30 -t 120 -q:a 0 -map a clip_audio.mp3

  Strip audio — keep video only
ffmpeg -i input.mp4 -c:v copy -an video_only.mp4

  Replace audio in video
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac -map 0:v -map 1:a output.mp4
```

---

   Video Conversion & Compression

    Format conversion
```powershell
  MP4 → MKV (no re-encode)
ffmpeg -i input.mp4 -c copy output.mkv

  AVI → MP4
ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4

  MOV → MP4 (iPhone video)
ffmpeg -i input.mov -c:v libx264 -c:a aac -movflags +faststart output.mp4
  Note: -movflags +faststart moves metadata to front for web streaming
```

    Compression (reduce file size)
```powershell
  Good quality, smaller file (CRF 28 ≈ 50% of original size)
ffmpeg -i input.mp4 -crf 28 -preset fast output.mp4

  Aggressive compression (CRF 35 ≈ 20% of original)
ffmpeg -i input.mp4 -crf 35 -preset veryfast output.mp4

  Target specific bitrate (2 Mbps)
ffmpeg -i input.mp4 -b:v 2M -maxrate 2M -bufsize 4M output.mp4

  Two-pass encoding (best quality at target size)
ffmpeg -i input.mp4 -c:v libx264 -b:v 1M -pass 1 -an -f null NUL
ffmpeg -i input.mp4 -c:v libx264 -b:v 1M -pass 2 -c:a aac output.mp4
```

    Resize / scale
```powershell
  Scale to 720p (keep aspect ratio)
ffmpeg -i input.mp4 -vf "scale=-1:720" output_720p.mp4

  Scale to 1080p wide
ffmpeg -i input.mp4 -vf "scale=1920:-1" output_1080p.mp4

  Scale to exact size (may stretch)
ffmpeg -i input.mp4 -vf "scale=1280:720" output.mp4

  Crop to 16:9 from center
ffmpeg -i input.mp4 -vf "crop=in_w:in_w*9/16" output_cropped.mp4
```

    Change frame rate
```powershell
ffmpeg -i input.mp4 -r 30 output_30fps.mp4
ffmpeg -i input.mp4 -r 60 output_60fps.mp4
```

---

   Trimming & Cutting

```powershell
  Trim — fast (no re-encode, may be slightly imprecise at GOP boundary)
ffmpeg -ss 00:01:00 -i input.mp4 -t 60 -c copy clip.mp4

  Trim — precise (re-encodes, frame-accurate)
ffmpeg -i input.mp4 -ss 00:01:00 -t 60 clip.mp4

  Trim from 1:30 to 3:45 (using -to instead of -t)
ffmpeg -i input.mp4 -ss 00:01:30 -to 00:03:45 -c copy clip.mp4

  Remove first 10 seconds
ffmpeg -ss 10 -i input.mp4 -c copy output.mp4

  Keep only the last 30 seconds (need duration first)
  Step 1: Get duration
ffprobe -v error -show_entries format=duration -of csv=p=0 input.mp4
  Step 2: Use (duration - 30) as -ss value
```

---

   Thumbnails & Screenshots

```powershell
  Single thumbnail at specific time
ffmpeg -i input.mp4 -ss 00:00:05 -frames:v 1 thumb.jpg

  High quality JPEG
ffmpeg -i input.mp4 -ss 10 -frames:v 1 -q:v 2 thumb.jpg

  PNG (lossless)
ffmpeg -i input.mp4 -ss 10 -frames:v 1 thumb.png

  One thumbnail every 30 seconds
ffmpeg -i input.mp4 -vf "fps=1/30" thumb_%04d.jpg

  Grid of thumbnails (contact sheet) — requires ffmpeg with tile filter
ffmpeg -i input.mp4 -vf "fps=1/60,scale=320:-1,tile=5x4" sheet.png

  GIF from video clip
ffmpeg -i input.mp4 -ss 5 -t 4 -vf "fps=15,scale=480:-1" -loop 0 clip.gif

  Optimized GIF (smaller file, better quality)
ffmpeg -i input.mp4 -ss 5 -t 4 -vf "fps=12,scale=480:-1,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" output.gif
```

---

   Subtitles

```powershell
  Burn subtitles into video (hardcoded — permanent)
ffmpeg -i input.mp4 -vf "subtitles=subs.srt" output.mp4

  Add subtitle as a soft track (selectable, no re-encode of video)
ffmpeg -i input.mp4 -i subs.srt -c copy -c:s mov_text output.mp4

  Extract embedded subtitle track
ffmpeg -i input.mp4 -map 0:s:0 subs_extracted.srt

  Convert SRT to ASS format (more styling options)
ffmpeg -i subs.srt subs.ass
```

---

   Concatenation & Merging

```powershell
  Concatenate files (same codec, fast)
  Create file list:
"file 'part1.mp4'`nfile 'part2.mp4'`nfile 'part3.mp4'" | Out-File -Encoding ascii filelist.txt

ffmpeg -f concat -safe 0 -i filelist.txt -c copy merged.mp4

  Concatenate with re-encode (different formats/codecs)
ffmpeg -i part1.mp4 -i part2.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" merged.mp4

  Stack videos side by side
ffmpeg -i left.mp4 -i right.mp4 -filter_complex "[0:v][1:v]hstack[v]" -map "[v]" side_by_side.mp4

  Stack videos vertically
ffmpeg -i top.mp4 -i bottom.mp4 -filter_complex "[0:v][1:v]vstack[v]" -map "[v]" stacked.mp4
```

---

   Batch Processing — PowerShell

    Convert all .avi files to .mp4
```powershell
Get-ChildItem "." -Filter "*.avi" | ForEach-Object {
    $out = $_.BaseName + ".mp4"
    Write-Host "Converting $($_.Name) -> $out"
    ffmpeg -i $_.FullName -c:v libx264 -c:a aac -y $out
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK]"
    } else {
        Write-Host "  [FAILED]" -ForegroundColor Red
    }
}
```

    Extract thumbnail from every video in folder
```powershell
$outDir = "thumbnails"
New-Item -ItemType Directory -Force $outDir | Out-Null

Get-ChildItem "." -Filter "*.mp4" | ForEach-Object {
    $thumb = Join-Path $outDir ($_.BaseName + ".jpg")
    ffmpeg -i $_.FullName -ss 5 -frames:v 1 -q:v 2 $thumb -y -hide_banner -loglevel error
    Write-Host "Thumbnail: $thumb"
}
```

    Compress all MP4s in folder (output to subfolder)
```powershell
$outDir = "compressed"
New-Item -ItemType Directory -Force $outDir | Out-Null

Get-ChildItem "." -Filter "*.mp4" | ForEach-Object {
    $out = Join-Path $outDir $_.Name
    $before = [math]::Round($_.Length / 1MB, 1)
    ffmpeg -i $_.FullName -crf 28 -preset fast $out -y -hide_banner -loglevel error
    $after = [math]::Round((Get-Item $out).Length / 1MB, 1)
    Write-Host "$($_.Name): ${before}MB -> ${after}MB"
}
```

    Get info for all videos in folder
```powershell
Get-ChildItem "." -Include "*.mp4","*.mkv","*.avi" -Recurse | ForEach-Object {
    $duration = ffprobe -v error -show_entries format=duration -of csv=p=0 $_.FullName
    $size = [math]::Round($_.Length / 1MB, 1)
    [PSCustomObject]@{
        Name     = $_.Name
        Size_MB  = $size
        Duration = [math]::Round([double]$duration, 0)
    }
} | Format-Table
```

---

   Python Wrapper (ffmpeg-python)

```bash
pip install ffmpeg-python
```

```python
import ffmpeg
import subprocess

  Convert
ffmpeg.input("input.mp4").output("output.mp3", q='0', map='a').run()

  Trim + compress
(
    ffmpeg
    .input("input.mp4", ss="00:01:00", t=60)
    .output("clip.mp4", crf=28, preset="fast", vcodec="libx264")
    .overwrite_output()
    .run()
)

  Thumbnail
(
    ffmpeg
    .input("input.mp4", ss=5)
    .output("thumb.jpg", vframes=1, **{"q:v": 2})
    .overwrite_output()
    .run(capture_stderr=True)
)

  Get video info
def get_video_info(path: str) -> dict:
    probe = ffmpeg.probe(path)
    video_stream = next(s for s in probe["streams"] if s["codec_type"] == "video")
    return {
        "duration": float(probe["format"]["duration"]),
        "width": video_stream["width"],
        "height": video_stream["height"],
        "fps": eval(video_stream["r_frame_rate"]),     "30/1" -> 30.0
        "codec": video_stream["codec_name"],
        "bitrate": int(probe["format"]["bit_rate"]) // 1000,    kbps
    }

info = get_video_info("input.mp4")
print(f"{info['width']}x{info['height']} @ {info['fps']}fps, {info['duration']:.1f}s")
```

---

   Encoding Quality Reference

    CRF (Constant Rate Factor) for H.264
| CRF | Quality | Use Case |
|-----|---------|----------|
| 0 | Lossless | Archiving (huge files) |
| 18 | Visually lossless | High-quality archive |
| 23 | Default | General purpose |
| 28 | Good | Web sharing, ~50% smaller |
| 35 | Acceptable | Small files, mobile |
| 51 | Worst | Tiny files only |

    Preset speed vs file size (same CRF)
| Preset | Encode speed | File size |
|--------|-------------|-----------|
| ultrafast | Very fast | Largest |
| fast | Fast | Medium |
| medium | Default | Default |
| slow | Slow | Smaller |
| veryslow | Very slow | Smallest |

**Rule of thumb**: Use `crf=28, preset=fast` for most batch jobs.

---

   Troubleshooting

    "Unknown encoder 'libx264'" on Windows
```powershell
  Download the full build (not "essentials") from gyan.dev
winget install Gyan.FFmpeg --version 7.0.0-full_build
```

    Sync issues (audio/video drift after trim)
```powershell
  Force re-encode instead of copy after trim
ffmpeg -i input.mp4 -ss 00:01:00 -t 60 output.mp4    no -c copy
```

    "Invalid data found when processing input"
- File may be corrupted. Try: `ffmpeg -i input.mp4 -c copy -y output.mp4` to fix container.

    Output has no audio
```powershell
  Check what streams the input has
ffprobe -v error -show_streams -select_streams a input.mp4
  Explicitly map audio
ffmpeg -i input.mp4 -map 0:v -map 0:a output.mp4
```

    Slow encode on CPU — use GPU (NVIDIA)
```powershell
ffmpeg -i input.mp4 -c:v h264_nvenc -crf 28 output.mp4
  AMD:  -c:v h264_amf
  Hardware acceleration example: -c:v h264_qsv
```

---

   Lessons Learned

- **`-ss` before `-i` = fast seek** (key-frame accurate, not frame-accurate).
  `-ss` after `-i` = slow but frame-accurate. Use fast seek for long files,
  re-encode for precise cuts.
- **`-c copy` is instant** — it just remuxes the container. Any filter or
  resize forces a full re-encode.
- **CRF 28 is the sweet spot** for most batch compression. Cuts file size ~50%
  with barely noticeable quality loss.
- **`-movflags +faststart`** is required for web-served MP4s — puts MOOV atom
  at the start so the browser can start playing before the full download.
- **Batch in PowerShell**: `ForEach-Object` with `$LASTEXITCODE` check is the
  most reliable pattern. Don't use `Start-Process` — it hides errors.
- **ffprobe** is your diagnostic tool — always check it before writing the
  conversion command.
- **GIF optimization**: The `palettegen/paletteuse` filter chain produces
  GIFs ~3x smaller than the naive `fps,scale` approach.
