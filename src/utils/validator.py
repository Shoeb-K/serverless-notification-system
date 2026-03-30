def validate_notification_request(data: dict) -> tuple[bool, str]:
    if not isinstance(data, dict):
        return False, "Invalid request format. Expected JSON object."
    
    if "email" not in data or not data["email"].strip():
        return False, "Missing or empty field: 'email'."
        
    if "message" not in data or not data["message"].strip():
        return False, "Missing or empty field: 'message'."
        
    return True, ""
