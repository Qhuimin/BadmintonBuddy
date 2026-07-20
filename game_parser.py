import re
from game import Game

def parse_style_a(text: str) -> list[Game] | None:
    if not (re.search(r"Date:", text, re.I) and (re.search(r"Time:", text, re.I) or re.search(r"Location:", text, re.I))):
        return None
    games_list = []
    global_level = "Unknown"
    global_level_match = re.search(r"Level:\s*([^\n\r]+)", text, re.I)
    if global_level_match:
        global_level = global_level_match.group(1).strip()

    raw_segments = re.split(r"Date:", text, flags=re.I)
    for segment in raw_segments[1:]:
        full_segment = "Date: " + segment
        date_match = re.search(r"Date:\s*([^\n\r]+)", full_segment, re.I)
        venue_match = re.search(r"(?:Location|Venue):\s*([^\n\r]+)", full_segment, re.I)
        level_match = re.search(r"Level:\s*([^\n\r]+)", full_segment, re.I)
        time_match = re.search(r"Time:\s*([^\n\r]+)", full_segment, re.I)

        if date_match and (venue_match or time_match):
            line_time = time_match.group(1).strip() if time_match else ""
            
            # Fix: Split by comma or semicolon to handle multiple slots on one line (e.g. 11am-1pm, 5-8pm)
            raw_slots = [s.strip() for s in re.split(r'[,;]', line_time) if s.strip()]
            if not raw_slots:
                raw_slots = [""]

            for slot_item in raw_slots:
                # Clean each individual sub-slot structure safely
                clean_time_match = re.search(r"^([0-9\s\:\.]+(?:AM|PM|am|pm|nn)?\s*(?:-|to)\s*[0-9\s\:\.]+(?:AM|PM|am|pm|nn)?)", slot_item, re.I)
                raw_time = clean_time_match.group(1).strip() if clean_time_match else slot_item

                start_time, end_time = "", ""
                separator = "to" if "to" in raw_time.lower() else "-"
                if separator in raw_time.lower():
                    parts = re.split(r"-|to", raw_time, flags=re.I)
                    start_time = parts[0].strip()
                    end_time = parts[1].strip() if len(parts) > 1 else ""
                else:
                    start_time = raw_time

                level = level_match.group(1).strip() if level_match else global_level
                venue = venue_match.group(1).strip() if venue_match else "Unknown"

                game = Game(
                    date=date_match.group(1).strip(),
                    venue=venue,
                    level=level,
                    start_time=start_time,
                    end_time=end_time,
                    original_message=text
                )
                games_list.append(game)
                
    return games_list if games_list else None

def parse_style_c(text: str) -> list[Game] | None:
    if not (re.search(r"📅", text) and re.search(r"🏸", text) and re.search(r"⏱️", text)):
        return None
    level = "Unknown"
    level_match = re.search(r"(?:friendly players|level|level:)\s*([^\n,]+)", text, re.I)
    if level_match:
        level = level_match.group(1).strip()

    games_list = []
    current_date = None
    current_venue = None

    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        date_match = re.search(r"📅\s*[:\-]?\s*([^\n]+)", line)
        venue_match = re.search(r"🏸\s*[:\-]?\s*([^\n]+)", line)
        time_match = re.search(r"⏱️\s*[:\-]?\s*([^\n]+)", line)

        if date_match:
            current_date = date_match.group(1).strip()
        elif venue_match:
            current_venue = venue_match.group(1).strip()
        elif time_match and current_date and current_venue:
            raw_time = time_match.group(1).strip()
            time_slots = [t.strip() for t in re.split(r",", raw_time) if t.strip()]
            for slot in time_slots:
                start_time, end_time = "", ""
                if "-" in slot:
                    parts = slot.split("-")
                    start_time = parts[0].strip()
                    end_time = parts[1].strip()
                else:
                    start_time = slot
                game = Game(
                    date=current_date,
                    venue=current_venue,
                    level=level,
                    start_time=start_time,
                    end_time=end_time,
                    original_message=text
                )
                games_list.append(game)
    return games_list if games_list else None

def parse_style_d(text: str) -> list[Game] | None:
    if not re.search(r"^\s*\*\s+", text, re.MULTILINE):
        return None
    games_list = []
    current_date = None
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        date_match = re.search(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\d+\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", line, re.I)
        if date_match:
            current_date = line
            continue
        if line.startswith("*") and current_date:
            content = line[1:].strip()
            level = "Unknown"
            level_match = re.search(r"\[([^\]]+)\]", content)
            if level_match:
                level = level_match.group(1).strip()
                content = content.replace(level_match.group(0), "").strip()

            time_match = re.search(r"(\d+(?:\:\d+)?\s*-\s*\d+(?:\:\d+)?(?:am|pm))", content, re.I)
            if time_match:
                raw_time = time_match.group(1).strip()
                venue = content[:time_match.start()].strip()
                start_time, end_time = "", ""
                if "-" in raw_time:
                    parts = raw_time.split("-")
                    start_time = parts[0].strip()
                    end_time = parts[1].strip()
                else:
                    start_time = raw_time
                game = Game(
                    date=current_date,
                    venue=venue,
                    level=level,
                    start_time=start_time,
                    end_time=end_time,
                    original_message=text
                )
                games_list.append(game)
    return games_list if games_list else None

def parse_style_f(text: str) -> list[Game] | None:
    if not (re.search(r"📅", text) and re.search(r"📍", text)):
        return None
    level = "Unknown"
    level_match = re.search(r"([L|M|H]B\s*-\s*[L|M|H]B)", text, re.I)
    if level_match:
        level = level_match.group(1).strip()

    games_list = []
    raw_segments = re.split(r"📅", text)
    for segment in raw_segments[1:]:
        full_segment = "📅" + segment
        date_match = re.search(r"📅\s*([^\n\r]+)", full_segment)
        time_match = re.search(r"🕰️?\s*([^\n\r]+)", full_segment)
        venue_match = re.search(r"📍\s*([^\n\r]+)", full_segment)
        price_match = re.search(r"💰\s*([^\n\r]+)", full_segment)

        if date_match and time_match and venue_match:
            raw_time = time_match.group(1).strip()
            start_time, end_time = "", ""
            if "-" in raw_time:
                parts = raw_time.split("-")
                start_time = parts[0].strip()
                end_time = parts[1].strip()
            else:
                start_time = raw_time
            price = price_match.group(1).strip() if price_match else None
            game = Game(
                date=date_match.group(1).strip(),
                venue=venue_match.group(1).strip(),
                level=level,
                start_time=start_time,
                end_time=end_time,
                price=price,
                original_message=text
            )
            games_list.append(game)
    return games_list if games_list else None

def parse_style_e(text: str) -> list[Game] | None:
    if not (re.search(r"(?:📅|🗓️|🗓)", text) and (re.search(r"(?:⏰|Time:)", text) or re.search(r"(?:📍|Location:)", text))):
        return None
    level = "Unknown"
    level_match = re.search(r"Level:\s*([^\n]+)", text, re.I)
    if not level_match:
        level_match = re.search(r"⚡\s*Level:\s*([^\n]+)", text, re.I)
    if level_match:
        level = level_match.group(1).strip()

    games_list = []
    segments = re.split(r"📅|🗓️|🗓", text)
    for segment in segments[1:]:
        date_match = re.search(r"^(?:\s*Date:\s*)?([^\n\r]+)", segment, re.I)
        venue_match = re.search(r"(?:📍|Location|Venue):\s*([^\n\r]+)", segment, re.I)
        time_match = re.search(r"(?:⏰|Time):\s*([^\n\r]+)", segment, re.I)
        price_match = re.search(r"(?:💵|Fee|Price):\s*([^\n\r]+)", segment, re.I)
        
        seg_level = level
        seg_level_match = re.search(r"⚡\s*Level:\s*([^\n]+)", segment, re.I)
        if seg_level_match:
            seg_level = seg_level_match.group(1).strip()

        if date_match and (venue_match or time_match):
            raw_time = time_match.group(1).strip() if time_match else ""
            clean_time_match = re.search(r"^([0-9\s\:\.]+(?:AM|PM|am|pm|nn)\s*(?:-|to)\s*[0-9\s\:\.]+(?:AM|PM|am|pm|nn))", raw_time, re.I)
            if clean_time_match:
                raw_time = clean_time_match.group(1).strip()
            
            time_slots = re.split(r"\n(?=\s*(?:⏰|\d))", raw_time) if "\n" in raw_time else [raw_time]
            for slot in time_slots:
                clean_slot = re.sub(r"🏸|⚡", "", slot).strip()
                if not clean_slot:
                    continue
                slot_time_match = re.search(r"([0-9\s\:\.]+(?:AM|PM|am|pm|nn)?\s*(?:-|to)\s*[0-9\s\:\.]+(?:AM|PM|am|pm|nn)?)", clean_slot, re.I)
                slot_time = slot_time_match.group(1).strip() if slot_time_match else clean_slot
                
                start_time, end_time = "", ""
                if "-" in slot_time:
                    parts = slot_time.split("-")
                    start_time = parts[0].strip()
                    end_time = parts[1].strip()
                elif "to" in slot_time.lower():
                    parts = re.split(r"to", slot_time, flags=re.I)
                    start_time = parts[0].strip()
                    end_time = parts[1].strip()
                else:
                    start_time = slot_time

                venue = venue_match.group(1).strip() if venue_match else "Unknown"
                price = price_match.group(1).strip() if price_match else None

                game = Game(
                    date=date_match.group(1).strip().strip("*"),
                    venue=venue,
                    level=seg_level,
                    start_time=start_time,
                    end_time=end_time,
                    price=price,
                    original_message=text
                )
                games_list.append(game)
    return games_list if games_list else None

def parse_style_g(text: str) -> list[Game] | None:
    if not (re.search(r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b", text, re.I) and 
            re.search(r"\d+\s*(?:am|pm|am|pm|\d+)\s*-\s*\d+", text, re.I)):
        return None

    games_list = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    i = 0
    while i < len(lines) - 2:
        is_date = re.search(r"\b\d+\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)|(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun|Tue,)\b", lines[i], re.I)
        is_time = re.search(r"(\d+(?:\:\d+)?\s*(?:am|pm)?\s*(?:-|to)\s*\d+(?:\:\d+)?\s*(?:am|pm)?)", lines[i+2], re.I)
        
        if is_date and is_time:
            date_str = lines[i]
            venue_str = lines[i+1]
            time_str = is_time.group(1).strip()
            
            start_time, end_time = "", ""
            if "-" in time_str:
                parts = time_str.split("-")
                start_time = parts[0].strip()
                end_time = parts[1].strip()
            elif "to" in time_str.lower():
                parts = re.split(r"to", time_str, flags=re.I)
                start_time = parts[0].strip()
                end_time = parts[1].strip()
            else:
                start_time = time_str

            game = Game(
                date=date_str,
                venue=venue_str,
                level="Unknown",
                start_time=start_time,
                end_time=end_time,
                original_message=text
            )
            games_list.append(game)
            i += 3
        else:
            i += 1
    return games_list if games_list else None

def parse_style_h(text: str) -> list[Game] | None:
    venue_match = re.search(r"(?:Venue|📍+)\s*[\*]?(?:Location:)?\s*([^\*📁🏸\n]+)", text, re.I)
    if not venue_match:
        return None
    
    venue = venue_match.group(1).strip().strip("*").strip()
    
    level = "Unknown"
    level_match = re.search(r"[\*📁]?\s*([L|M|H]B\s*-\s*[L|M|H]B|[L|M|H]B\s+to\s+[L|M|H]B)\s*[\*]?", text, re.I)
    if level_match:
        level = level_match.group(1).strip()

    games_list = []
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        time_match = re.search(r"(\d+(?:\:\d+)?\s*(?:am|pm|nn)?\s*-\s*\d+(?:\:\d+)?\s*(?:am|pm|nn)?)", line, re.I)
        if time_match:
            date_part = line[:time_match.start()].replace("🏸", "").strip()
            if not date_part: 
                continue 
            
            raw_time = time_match.group(1).strip()
            start_time, end_time = "", ""
            if "-" in raw_time:
                parts = raw_time.split("-")
                start_time = parts[0].strip()
                end_time = parts[1].strip()
            else:
                start_time = raw_time

            game = Game(
                date=date_part,
                venue=venue,
                level=level,
                start_time=start_time,
                end_time=end_time,
                original_message=text
            )
            games_list.append(game)
            
    return games_list if games_list else None

def parse_style_i(text: str) -> list[Game] | None:
    if not re.search(r"-\s+(?:TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY|MONDAY)", text, re.I):
        return None
        
    games_list = []
    segments = re.split(r"-\s+(?=TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY|MONDAY)", text, flags=re.I)
    
    for seg in segments[1:]:
        lines = [l.strip() for l in seg.splitlines() if l.strip()]
        if len(lines) >= 2:
            date_line = lines[0]
            date_part = re.split(r":", date_line)[0].strip()
            
            time_venue_line = lines[1]
            time_match = re.search(r"(\d+(?:\:\d+)?\s*-\s*\d+(?:\:\d+)?\s*(?:am|pm)?)", time_venue_line, re.I)
            if time_match:
                raw_time = time_match.group(1).strip()
                venue_part = time_venue_line[time_match.end():].strip().strip(",").strip()
                
                start_time, end_time = "", ""
                if "-" in raw_time:
                    parts = raw_time.split("-")
                    start_time = parts[0].strip()
                    end_time = parts[1].strip()
                else:
                    start_time = raw_time
                    
                game = Game(
                    date=date_part,
                    venue=venue_part if venue_part else "Unknown",
                    level="Unknown",
                    start_time=start_time,
                    end_time=end_time,
                    original_message=text
                )
                games_list.append(game)
    return games_list if games_list else None

def parse_style_j(text: str) -> list[Game] | None:
    if not (re.search(r"🎯", text) and re.search(r"🍟", text) and re.search(r"📌", text)):
        return None

    games_list = []
    current_date = "Unknown"
    current_venue = "Unknown"
    
    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("🎯"):
            current_date = line.replace("🎯", "").strip()
        elif line.startswith("🍟"):
            current_venue = line.replace("🍟", "").strip()
        elif line.startswith("📌"):
            time_block = line.replace("📌", "").strip()
            
            slots = re.split(r"/|~", time_block)
            for slot in slots:
                time_match = re.search(r"(\d+(?:\.\d+)?(?:\:\d+)?\s*(?:am|pm|nn)?\s*-\s*\d+(?:\.\d+)?(?:\:\d+)?\s*(?:am|pm|nn)?)", slot, re.I)
                if time_match:
                    raw_time = time_match.group(1).strip()
                    level_part = slot[time_match.end():].strip().strip("~")
                    
                    start_time, end_time = "", ""
                    if "-" in raw_time:
                        parts = raw_time.split("-")
                        start_time = parts[0].strip()
                        end_time = parts[1].strip()
                    else:
                        start_time = raw_time
                        
                    game = Game(
                        date=current_date,
                        venue=current_venue,
                        level=level_part if level_part else "Unknown",
                        start_time=start_time,
                        end_time=end_time,
                        original_message=text
                    )
                    games_list.append(game)
                    
    return games_list if games_list else None

# =====================================================================
# THE MASTER ROUTING SYSTEM
# =====================================================================

PARSER_STRATEGIES = [
    parse_style_a,
    parse_style_c,
    parse_style_d,
    parse_style_f,
    parse_style_e,
    parse_style_g,
    parse_style_h,
    parse_style_i,
    parse_style_j,
]

def parse_message(text: str) -> list[Game]:
    if not text:
        return []

    for strategy in PARSER_STRATEGIES:
        try:
            parsed_games = strategy(text)
            if parsed_games is not None:
                return parsed_games
        except Exception:
            continue

    text_lower = text.lower()
    
    has_prime_time_keyword = any(k in text_lower for k in [
        "7pm", "8pm", "9pm", "10pm", "11pm", 
        "7-9", "8-10", "7.30", "7:30", "6.30", "6:30",
        "19:00", "20:00", "21:00", "22:00"
    ])
    
    has_badminton_keyword = any(k in text_lower for k in [
        "safra", "cc", "sh", "hall", "sports", "arena", "hub", "primary", "secondary",
        "rsl", "supreme", "ultimate", "shuttlecock", "badminton", "court", "pax", "level"
    ])

    if has_prime_time_keyword and has_badminton_keyword:
        print(f"⚠️ [Safety Net] Unstructured prime-time message detected. Bypassing parser constraints.")
        fallback_game = Game(
            date="Review Original Message",
            venue="Unknown / Unstructured Venue",
            level="Unknown",
            start_time="7:00 PM",
            end_time="11:00 PM",
            original_message=text
        )
        return [fallback_game]

    return []