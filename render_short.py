from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PLAN = json.loads((ROOT / "assets/short_001.json").read_text(encoding="utf-8"))
W, H = PLAN["canvas"]["width"], PLAN["canvas"]["height"]
FPS = int(PLAN["canvas"]["fps"])
DURATION = max(s["end"] for s in PLAN["scenes"])
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
RAW = OUT / "silent.mp4"
FINAL = OUT / "first_1000_short.mp4"
AUDIO = OUT / "voice.wav"

BG = (13, 18, 32)
WHITE = (248, 249, 255)
YELLOW = (255, 211, 77)
CYAN = (70, 219, 238)
PINK = (255, 105, 145)
GREEN = (102, 233, 161)
MUTED = (157, 172, 197)

def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

F_TITLE = font(72, True)
F_HOOK = font(49, True)
F_BODY = font(36, True)
F_SMALL = font(26, True)

def rounded(draw: ImageDraw.ImageDraw, box, radius: int, fill, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def center_text(draw, text, y, f, fill=WHITE, stroke=0, stroke_fill=BG):
    box = draw.textbbox((0, 0), text, font=f, stroke_width=stroke)
    x = (W - (box[2] - box[0])) // 2
    draw.text((x, y), text, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)

def wrap_words(text: str, max_chars: int = 26) -> list[str]:
    words, lines, line = text.split(), [], ""
    for word in words:
        candidate = (line + " " + word).strip()
        if len(candidate) > max_chars and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines

def stickman(draw, x, y, scale=1.0, pose="idle", color=WHITE, phase=0.0):
    # Consistent character silhouette with animated limbs and expressive pose.
    s = scale
    head_r = int(42*s)
    bob = math.sin(phase*2.8)*9*s
    cy = y - int(185*s) + int(bob)
    draw.ellipse((x-head_r, cy-head_r, x+head_r, cy+head_r), outline=color, width=max(5,int(9*s)))
    # eyes and mouth
    eye_y = cy - int(4*s)
    draw.ellipse((x-int(15*s), eye_y-int(5*s), x-int(7*s), eye_y+int(4*s)), fill=color)
    draw.ellipse((x+int(7*s), eye_y-int(5*s), x+int(15*s), eye_y+int(4*s)), fill=color)
    mouth_w = int((17 if pose in ("shock","expense") else 12)*s)
    draw.arc((x-mouth_w, cy+int(10*s), x+mouth_w, cy+int(28*s)), 5, 175, fill=color, width=max(3,int(5*s)))
    shoulder = (x, cy+head_r+int(12*s))
    hip = (x, y-int(35*s))
    draw.line((shoulder, hip), fill=color, width=max(6,int(11*s)))
    swing = math.sin(phase*4.2)*int(42*s)
    if pose in ("shock","expense"):
        left_hand=(x-int(105*s),cy+int(25*s))
        right_hand=(x+int(105*s),cy+int(25*s))
    elif pose in ("work","save"):
        left_hand=(x-int(100*s),cy+int(90*s)+int(swing))
        right_hand=(x+int(95*s),cy+int(80*s)-int(swing))
    else:
        left_hand=(x-int(95*s),cy+int(90*s)+int(swing))
        right_hand=(x+int(95*s),cy+int(90*s)-int(swing))
    draw.line((shoulder,left_hand),fill=color,width=max(6,int(10*s)))
    draw.line((shoulder,right_hand),fill=color,width=max(6,int(10*s)))
    leg_swing=math.sin(phase*4.2)*int(35*s)
    draw.line((hip,(x-int(63*s)+int(leg_swing),y+int(115*s))),fill=color,width=max(6,int(11*s)))
    draw.line((hip,(x+int(63*s)-int(leg_swing),y+int(115*s))),fill=color,width=max(6,int(11*s)))
    draw.line((x-int(63*s)+int(leg_swing),y+int(115*s),x-int(105*s)+int(leg_swing),y+int(120*s)),fill=color,width=max(5,int(9*s)))
    draw.line((x+int(63*s)-int(leg_swing),y+int(115*s),x+int(105*s)-int(leg_swing),y+int(120*s)),fill=color,width=max(5,int(9*s)))

def draw_dollar(draw, x, y, r, color=GREEN, rotation=0):
    draw.ellipse((x-r,y-r,x+r,y+r), fill=(22,51,55), outline=color, width=5)
    draw.text((x-r//2,y-r), "$", font=font(r+8,True), fill=color)

def draw_scene(t: float) -> Image.Image:
    scene = next((s for s in PLAN["scenes"] if s["start"] <= t < s["end"]), PLAN["scenes"][-1])
    local = t - scene["start"]
    duration = scene["end"] - scene["start"]
    p = local / duration
    pulse = 1 + 0.045 * math.sin(local*5)
    img = Image.new("RGB",(W,H),BG)
    d = ImageDraw.Draw(img)

    # moving atmospheric accents / kinetic streaks
    for i in range(10):
        xx = int((i*137 + t*155*(1+i%3)) % W)
        yy = int((i*211 + t*82*(1+i%2)) % H)
        rr = 4 + (i%3)*3
        d.ellipse((xx-rr,yy-rr,xx+rr,yy+rr),fill=(27,42,62))
    d.rectangle((0,0,W,18),fill=CYAN)
    rounded(d,(48,52,W-48,112),24,(23,34,54))
    d.text((76,67),"THE MONEY STICKMAN",font=F_SMALL,fill=CYAN)
    d.text((W-230,67),"MONEY 101",font=F_SMALL,fill=YELLOW)

    center_text(d,scene["headline"],190,F_HOOK,YELLOW,stroke=1)
    pose = {"payday_zero":"shock","payday":"happy","bill_attack":"shock","expense":"expense","auto_save":"save","growth":"happy"}.get(scene["visual"],"idle")
    base_x=int(W*0.5 + math.sin(t*1.5)*24)
    base_y=1180
    if scene["visual"] == "payday_zero":
        rounded(d,(115,430,965,760),42,(24,42,63),outline=CYAN,width=5)
        center_text(d,"BANK BALANCE",490,F_BODY,MUTED)
        center_text(d,"$0",560,F_TITLE,PINK)
        stickman(d,base_x,base_y,1.15,"shock",phase=t)
        for i in range(4):
            draw_dollar(d,170+i*220,850+int(math.sin(t*3+i)*18),34,YELLOW)
    elif scene["visual"] == "payday":
        rounded(d,(100,420,980,760),42,(24,42,63),outline=GREEN,width=5)
        center_text(d,"PAYDAY DEPOSIT",485,F_BODY,MUTED)
        center_text(d,"+$2,400",560,F_TITLE,GREEN)
        stickman(d,base_x,base_y,1.16,"happy",phase=t)
        for i in range(6):
            draw_dollar(d,110+i*165,820+int(math.sin(t*4+i)*28),29,GREEN)
    elif scene["visual"] == "bill_attack":
        stickman(d,base_x,base_y,1.0,"shock",phase=t)
        labels=["RENT","GROCERIES","PHONE","SUBSCRIPTIONS"]
        for i,lab in enumerate(labels):
            x=55+(i%2)*520
            y=490+(i//2)*235+int(math.sin(t*4+i)*18)
            rounded(d,(x,y,x+450,y+135),24,(60,35,53),outline=PINK,width=4)
            d.text((x+28,y+40),lab,font=F_BODY,fill=WHITE)
            d.text((x+310,y+40),"DUE",font=F_SMALL,fill=YELLOW)
    elif scene["visual"] == "expense":
        rounded(d,(105,440,975,740),35,(56,35,47),outline=PINK,width=5)
        center_text(d,"CAR REPAIR",490,F_BODY,MUTED)
        center_text(d,"-$240",555,F_TITLE,PINK)
        stickman(d,base_x,base_y,1.15,"expense",phase=t)
        d.line((180,835,900,835),fill=PINK,width=6)
        for i in range(5):
            x=230+i*150
            d.line((x,805,x+55,865),fill=YELLOW,width=8)
    elif scene["visual"] == "auto_save":
        rounded(d,(95,425,985,755),42,(24,48,52),outline=GREEN,width=5)
        center_text(d,"AUTOMATIC TRANSFER",485,F_BODY,MUTED)
        center_text(d,"$20 → SAVINGS",555,F_TITLE,GREEN)
        stickman(d,base_x,base_y,1.12,"save",phase=t)
        draw_dollar(d,825,900,55,GREEN)
        d.arc((620,800,930,1100),190,510,fill=CYAN,width=9)
    else:
        stickman(d,base_x,base_y,1.2,"happy",phase=t)
        for i,val in enumerate(["$20","$200","$500","$1,000"]):
            x=100+i*225
            h=120+i*85
            rounded(d,(x,1070-h,x+145,1070),18,(25,55,57),outline=GREEN,width=4)
            center_text(d,val,1070-h-58,F_SMALL,GREEN)

    # bottom caption panel - scene text appears in short readable chunks
    voice_words = scene["voice"].split()
    words_per = max(1, math.ceil(len(voice_words) / max(1, math.ceil(duration/1.35))))
    idx = min(len(voice_words)-1, int(local/1.35)*words_per)
    chunk = " ".join(voice_words[idx:idx+words_per+3])
    rounded(d,(48,1450,W-48,1778),36,(23,33,52),outline=(54,75,101),width=3)
    lines=wrap_words(chunk.upper(),max_chars=30)[:3]
    for j,line in enumerate(lines):
        center_text(d,line,1515+j*82,F_BODY,WHITE)
    # progress bar and scene marker
    d.rounded_rectangle((65,1812,W-65,1830),radius=8,fill=(48,61,82))
    d.rounded_rectangle((65,1812,65+int((t/DURATION)*(W-130)),1830),radius=8,fill=CYAN)
    d.text((70,1852),"REAL LIFE. REAL MONEY. SMALL STEPS.",font=F_SMALL,fill=MUTED)
    return img

def make_video():
    cmd=["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",str(RAW)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        total_frames=int(DURATION*FPS)
        for frame in range(total_frames):
            t=frame/FPS
            img=draw_scene(t)
            assert proc.stdin is not None
            proc.stdin.write(np.asarray(img,dtype=np.uint8).tobytes())
    finally:
        if proc.stdin: proc.stdin.close()
    code=proc.wait()
    if code: raise RuntimeError(f"FFmpeg video render failed: {code}")

def mux_audio():
    if not AUDIO.exists():
        raise FileNotFoundError("Narration missing. Run: python scripts/generate_voice.py")
    cmd=["ffmpeg","-y","-i",str(RAW),"-i",str(AUDIO),"-filter_complex","[1:a]loudnorm=I=-16:TP=-1.5:LRA=11[a]","-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(FINAL)]
    subprocess.run(cmd,check=True)
    print(f"Rendered: {FINAL}")

if __name__=="__main__":
    make_video()
    mux_audio()
