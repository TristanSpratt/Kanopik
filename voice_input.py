import speech_recognition as sr

def listen_to_voice_command():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎤 Listening... Please ask your question.")

    with mic as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("🟢 Start speaking...")
        recognizer.pause_threshold = 2.5  # wait before stopping recording
        audio = recognizer.listen(source)

    print("🔄 Processing...")
    try:
        query = recognizer.recognize_google(audio)
        print(f"✅ You said: {query}")
        return query
    except sr.UnknownValueError:
        print("❌ Sorry, I couldn’t understand that.")
    except sr.RequestError as e:
        print(f"❌ Could not request results from Google Speech Recognition service; {e}")

    return None
