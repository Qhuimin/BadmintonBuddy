def is_prime_time(start_time_str: str) -> bool:
    """
    Checks if the game's start time falls between 7:00 PM and 11:00 PM (19:00 - 23:00).
    Handles dynamic squashed layout formats like '8', '730', '8pm', '7:30pm'.
    """
    if not start_time_str:
        return False
        
    try:
        time_clean = start_time_str.lower().replace(" ", "")
        
        hour = 0
        minute = 0
        
        # Strip out all non-digits except colons and periods
        digits_only = "".join([c for c in time_clean if c.isdigit() or c in (':', '.')])
        if not digits_only:
            return False

        digits_only = digits_only.replace('.', ':')

        if ":" in digits_only:
            parts = digits_only.split(":")
            hour = int(parts[0])
            minute = int(parts[1])
        else:
            val = int(digits_only)
            if val > 100:  # e.g., '730' or '2000'
                # If it's a 3-digit number like 730 or 830, parse out hours/minutes
                if val < 1200:
                    hour = val // 100
                    minute = val % 100
                else:  # Military time like 2000
                    hour = val // 100
                    minute = val % 100
            else:
                hour = val

        # --- SMART CONTEXTUAL PM DETECTION ---
        # 1. Explicit marker check
        is_pm = "pm" in time_clean
        is_am = "am" in time_clean
        
        # 2. Context fallback: If this token was stripped out of a block ending in PM 
        # (e.g., '730' parsed from '730-930pm'), assume PM if the hour is between 1 and 11,
        # BUT ONLY if it wasn't explicitly labeled as AM.
        if not is_pm and not is_am and hour < 12:
            is_pm = True 

        # Convert to 24-hour scale
        if is_pm and hour < 12:
            hour += 12
        elif not is_pm and hour == 12:  # 12am case
            hour = 0
            
        # Target Window Evaluation: 19:00 <= game_time <= 23:00
        # 7:00 PM is 19. A 6:30 PM (18:30) slot does not clear, but 7:00 PM onwards clears.
        return 19 <= hour <= 23
    except Exception:
        # Fallback to True so we don't accidentally miss a match due to text quirks
        return True