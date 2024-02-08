
def role_to_string(role: int) -> str:
    role_map = {
        0: "system",
        1: "user",
        2: "assistant",
    }
    return role_map.get(role, "UNKNOWN")
