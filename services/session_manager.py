# services/session_manager.py
import time
import threading

class SessionManager:
    def __init__(self, expiration_time=86400):
        self.sessions = {}
        self.expiration_time = expiration_time
        self.lock = threading.Lock()
        self.cleanup_thread = threading.Thread(target=self.cleanup_sessions, daemon=True)
        self.cleanup_thread.start()

    def set_session(self, key, value):
        with self.lock:
            self.sessions[key] = (value, time.time())

    def get_session(self, key):
        with self.lock:
            session = self.sessions.get(key)
            if session and time.time() - session[1] < self.expiration_time:
                return session[0]
            elif session:
                del self.sessions[key]
        return None

    def cleanup_sessions(self):
        while True:
            time.sleep(3600)  # Run cleanup every hour
            with self.lock:
                current_time = time.time()
                keys_to_delete = [key for key, (_, timestamp) in self.sessions.items() if current_time - timestamp >= self.expiration_time]
                for key in keys_to_delete:
                    del self.sessions[key]

session_manager = SessionManager()