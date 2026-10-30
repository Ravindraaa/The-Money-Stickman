from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"output"
voice,sr=sf.read(OUT/"pilot_voice.wav",dtype="float32")
if voice.ndim>1: voice=voice.mean(axis=1)
n=len(voice); t=np.arange(n)/sr
# Adaptive original electronic pulse: builds into the reveal, ducked beneath narration.
music=np.zeros(n,dtype=np.float32)
for freq,amp in [(110,.018),(164.81,.012),(220,.01),(329.63,.008)]:
    music += amp*np.sin(2*np.pi*freq*t + .18*np.sin(2*np.pi*.7*t))
env=np.clip(t/0.7,0,1)*np.clip((5-t)/.5,0,1)
music*=env
# Soft whoosh accents around the quick camera moves.
for center in (.85,2.45,3.75):
    x=t-center
    whoosh=np.exp(-((x)/.12)**2)*np.sin(2*np.pi*(180+90*np.maximum(x,0))*x)*.045
    music += whoosh.astype(np.float32)
mix=voice*.94+music
peak=np.max(np.abs(mix))
if peak>.97: mix*=.97/peak
sf.write(OUT/"pilot_mix.wav",mix,sr)
