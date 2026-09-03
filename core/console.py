"""مساعد صغير: كونسول Windows الافتراضي (cp1252) ما يطبع عربي — نجبره UTF-8."""
import sys


def force_utf8_stdout():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
