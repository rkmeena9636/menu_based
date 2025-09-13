# Speak module for text-to-speech functionality
import pyttsx3
import threading

def speak(text):
    """
    Convert text to speech using pyttsx3
    """
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)
        
        # Run in a separate thread to avoid blocking
        def speak_text():
            engine.say(text)
            engine.runAndWait()
        
        thread = threading.Thread(target=speak_text)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        print(f"Text: {text}")

def speak_sync(text):
    """
    Synchronous version of speak function
    """
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 0.9)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in text-to-speech: {e}")
        print(f"Text: {text}")
