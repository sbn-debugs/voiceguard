# VoiceGuard

A lightweight, on-device detection system to protect everyday users from AI voice-clone emergency scams.

---

### Team Details
* **ideathon:** LOGIC LEAGUE
* **Track:** AI/ML & Cybersecurity
* **Team Name:** [hack smith]
* **Team Leader:** (syed soban warsi) (syedsoban011@gmail.com)  (@sbn-debugs)
* **Team Member:** (aryansh garg) (loopedaryansh@gmail.com) | (@alyansss)

---

## 1. Problem Statement
Voice cloning tools have made it scarily easy to recreate anyone's voice using just a 5-second audio clip from Instagram or a voicemail. 

In recent months, there has been a sharp rise in "distress scam calls". A scammer clones the voice of a student or child and calls the parents claiming: *"Mom, I had an accident, I am in the hospital, please send money immediately."* 

Because the voice sounds familiar, panic takes over, and victims transfer money before verifying the story. The victims are almost always non-technical everyday people, especially parents and elders, who don't have any tool to verify if the voice on the other end is real or synthesized.

## 2. Existing Solutions
* **Truecaller / Spam Call Blockers:** These identify reported spam numbers. But scammers use new numbers, spoofed IDs, or WhatsApp calls. They judge the phone number, not the actual voice.
* **Cloud-based Deepfake Detectors:** Uploading live call audio to a cloud server causes network delay (which doesn't work during a live phone call) and creates a massive privacy risk by listening to private family conversations.
* **Family Safe Words:** While good in theory, panicking parents forget to ask for safe words during what sounds like a life-threatening crisis.

## 3. Proposed Solution: VoiceGuard
VoiceGuard is our concept for an on-device call assistant that analyzes audio locally in real-time without uploading anything to the internet. 

Instead of relying on just one metric, VoiceGuard runs a **two-layer validation check**:
1. **Acoustic Check (Voice Nature):** Synthetic voices created by neural models tend to be unnaturally smooth and lack natural micro-variations like breathing tremors and pitch jitter. VoiceGuard checks these acoustic indicators.
2. **Contextual Urgency Check:** A lightweight local speech scanner listens for high-pressure distress keywords commonly used in scams (e.g., *"accident"*, *"hospital"*, *"send money"*, *"don't tell dad"*).

If both the acoustic analysis points to synthetic speech AND the caller is demanding emergency payments, VoiceGuard triggers an immediate on-screen alert advising the user to hang up and call back.

## 4. Key Features
* **100% Local & Private:** Runs entirely on-device. Audio is processed frame-by-frame in memory and immediately discarded. No audio is ever saved or sent to any server.
* **Dual-Signal Scoring:** Avoids false alarms on normal frantic family calls by requiring both synthetic voice indicators and distress language to trigger a warning.
* **Instant Actionable Alert:** Instead of technical percentages, it shows a clear warning: *"Potential AI-Generated Voice Detected. Do not transfer funds. Hang up and dial directly."*
* **Low Latency:** Designed to flag an issue within the first 2-3 seconds of speech.

## 5. Technical Approach & Architecture

### Pipeline Flow:
Incoming Audio (16 kHz) 
  --> Rolling Buffer (25ms frames)
  --> [Parallel Branch A]: FFT Analysis (Spectral Flatness & Centroid Variance)
  --> [Parallel Branch B]: Lightweight Keyword Matching on Transcribed Tokens
  --> Fusion Scorer (0.55 * Voice Artifacts + 0.45 * Distress Score)
  --> If Risk >= 55 -> Trigger Warning Alert

### How the Proof of Concept Works:
For this ideathon submission, we implemented a functional Python prototype (`voiceguard_demo.py`) that simulates the audio pipeline:
* It analyzes simulated audio signals to calculate spectral variance and flatness.
* It parses transcript lines for distress/fraud phrases.
* It calculates the combined risk score and exits with code `0` for clean calls and code `1` for detected scams.

## 6. Technology Stack
* **Prototyping & Logic:** Python 3, NumPy (Signal calculations)
* **Audio Analysis (Target):** Librosa / Fast Fourier Transform (FFT) for spectral feature extraction
* **Mobile Runtime (Target Architecture):** TensorFlow Lite / ONNX Runtime for on-device quantized inference
* **Frontend UI (Planned):** Flutter / Android Native (for call overlay permissions)

## 7. Expected Impact
* **Stops Panic Fraud:** Shifts defense to the exact moment of the scam rather than after money has already left the bank account.
* **Zero Privacy Trade-off:** By keeping all processing local, users don't have to sacrifice private conversation privacy to get protection.
* **Accessible Security:** Built specifically for non-technical users and elders who cannot manually spot voice deepfakes.

## 8. Future Scope
* **Indian Language & Dialect Support:** Expanding distress keyword libraries and acoustic training for Hindi, Hinglish, and regional languages.
* **Android Dialer Integration:** Packing the model into a native Android dialer plugin or accessibility overlay.
* **Trusted Contact Ping:** Automatically send a quiet SMS to another family member if an active call triggers a high-confidence scam alert.
