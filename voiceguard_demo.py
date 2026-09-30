#!/usr/bin/env python3
"""VoiceGuard PoC: on-device voice-clone + distress scam detector (simulated stream).
Usage: python voiceguard_demo.py [safe|scam]    Exit code: 0 = safe call, 1 = flagged scam"""
import sys
import numpy as np

SR, FRAME, THRESHOLD = 16000, 512, 55.0
FLAT_REF, CENT_REF = 0.15, 300.0  # natural-speech reference levels (calibrated on simulated data)
DISTRESS = {"accident": 2, "hospital": 2, "emergency": 2, "arrested": 3, "bail": 3, "gift card": 3,
            "send money": 3, "wire": 3, "don't tell": 3, "right now": 1, "please help": 1}
CALLS = {"safe": ["Hey mom, running late for dinner.", "Can you save me a plate?", "Love you, see you soon."],
         "scam": ["Mom, it's me. I had an accident.", "I'm at the hospital, please help me.",
                  "Don't tell dad. Send money right now.", "Buy a gift card, it's an emergency."]}

def synth_stream(kind, secs=3.0, seed=7):
    """Simulated mic input. Natural voice = pitch jitter, formant motion, breath noise; clone = over-smooth."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(SR * secs)) / SR
    live = kind == "safe"
    f0 = 150 * (1 + 0.08 * np.sin(2 * np.pi * 0.6 * t) + (0.02 if live else 0.0015) * np.cumsum(rng.normal(size=t.size)) / 30)
    tilt = 1.0 + (0.9 * np.sin(2 * np.pi * 0.9 * t) if live else 0.0)
    x = sum(np.sin(k * 2 * np.pi * np.cumsum(f0) / SR) * k ** (-tilt) for k in range(1, 21))
    x = x / np.abs(x).max() * (0.6 + 0.4 * np.sin(2 * np.pi * 3.5 * t) if live else 1.0)
    return x + rng.normal(0, 0.05 if live else 0.002, t.size)

def acoustic_features(x):
    """FFT frames -> (mean spectral flatness, spectral-centroid variability in Hz)."""
    f = x[: len(x) // FRAME * FRAME].reshape(-1, FRAME) * np.hanning(FRAME)
    p = np.abs(np.fft.rfft(f, axis=1)) ** 2 + 1e-12
    flat = np.exp(np.log(p).mean(1)) / p.mean(1)
    cent = (p * np.fft.rfftfreq(FRAME, 1 / SR)).sum(1) / p.sum(1)
    return flat.mean(), cent.std()

def distress_score(lines):
    """On-device NLP stand-in: weighted urgency/payment keyword scan over ASR transcript lines."""
    total = 0
    for i, line in enumerate(lines, 1):
        hits = [(k, w) for k, w in DISTRESS.items() if k in line.lower()]
        total += sum(w for _, w in hits)
        tag = "[WARN]" if hits else "[ OK ]"
        print(f"  {tag} L{i}: \"{line}\"" + (f"  -> {', '.join(k for k, _ in hits)}" if hits else ""))
    return min(1.0, total / 8)

def main():
    kind = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in CALLS else "scam"
    x = synth_stream(kind)
    print(f"[*] VoiceGuard PoC | scenario={kind} | {SR} Hz | {len(x) // FRAME} frames | offline, no audio leaves device")
    flat, cvar = acoustic_features(x)
    print("\n--- Acoustic artifact inspection ---")
    a_flat, a_var = np.clip(1 - flat / FLAT_REF, 0, 1), np.clip(1 - cvar / CENT_REF, 0, 1)
    for name, val, sc, lim in [("Spectral flatness", flat, a_flat, "synthetic if low"),
                               ("Spectral-centroid variance", cvar, a_var, "synthetic if low")]:
        print(f"  {'[FAIL]' if sc > 0.5 else '[ OK ]'} {name:<27} = {val:9.4f}  ({lim})  artifact={sc:.2f}")
    print("\n--- Distress transcript inspection ---")
    d = distress_score(CALLS[kind])
    a = (a_flat + a_var) / 2
    risk = 100 * (0.55 * a + 0.45 * d)
    flagged = risk >= THRESHOLD
    print(f"\n[*] Synthetic-voice score: {a:.2f} | Distress score: {d:.2f}")
    print(f"[*] RISK SCORE: {risk:.0f}/100 (threshold {THRESHOLD:.0f})")
    print("[!] ALERT: likely AI-cloned distress scam. Hang up and call back on a known number." if flagged
          else "[+] PASS: no cloning artifacts or distress-scam pattern detected.")
    return int(flagged)

if __name__ == "__main__":
    sys.exit(main())
