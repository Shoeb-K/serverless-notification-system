import datetime

def _format_log(level: str, message: str) -> str:
    timestamp = datetime.datetime.utcnow().isoformat()
    return f"[{timestamp}] {level}: {message}"

def log_info(message: str):
    print(_format_log("INFO", message))

def log_error(message: str):
    print(_format_log("ERROR", message))
