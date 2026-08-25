class VoiceCommands:
    def __init__(self, enabled=False):
        self.enabled = enabled
        self.engine = None
        if enabled:
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer(); self.microphone = sr.Microphone()
            except Exception:
                self.enabled = False
    def listen(self):
        if not self.enabled: return None
        import speech_recognition as sr
        try:
            with self.microphone as source: audio = self.recognizer.listen(source, timeout=0.2, phrase_time_limit=2)
            return self.recognizer.recognize_google(audio).lower()
        except (sr.WaitTimeoutError, sr.UnknownValueError, sr.RequestError): return None
