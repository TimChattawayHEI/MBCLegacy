"""beats.py file.mp3 bpm_lo bpm_hi: estimate tempo and first-beat offset (seconds) from the kick/snare onsets."""
import sys, subprocess, numpy as np
f, lo, hi = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', '11025', '-f', 's16le', '-'], capture_output=True).stdout
x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
hop, win = 110, 1024; n = (len(x) - win) // hop
spec = np.abs(np.fft.rfft(np.stack([x[i * hop:i * hop + win] * np.hanning(win) for i in range(n)]), axis=1))
low = spec[:, :60]   # lows: kicks
flux = np.maximum(0, np.diff(np.log1p(low * 10), axis=0)).sum(1); flux -= flux.mean()
fr = 11025 / hop; best = None
for bpm in np.arange(lo, hi, 0.01):
    per = 60 / bpm * fr; idx = np.arange(0, len(flux) - 1, per)
    for ph in np.arange(0, per, 1.0):
        s = flux[np.clip((idx + ph).astype(int), 0, len(flux) - 1)].sum()
        if best is None or s > best[0]: best = (s, bpm, ph / fr)
    pass
print('%.3f %.4f' % (best[1], best[2]))
