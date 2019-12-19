# utilities/time.py


def format_seconds_to_minutes_seconds(seconds):
    return f"{seconds // 60:02d}:{seconds % 60:02d}"
