import os
import re
from supabase import create_client, Client

url = "https://eeizuypqyhepkczqmqky.supabase.co"
key = "sb_publishable_AiaNimVhNkL3cA0lkeTYRw_AgjBF73J"

raw_data = """
A101Standard400
A102Standard400
A103Standard400
A104Standard400
A105Standard400
A106Standard Twin500
A107Standard Twin500
A108Standard Twin500
A109Standard Twin500
A110Standard Twin500
A111Standard400
A201Standard400
A202Standard400
A203Standard400
A204Standard400
A205Standard400
A206Standard400
A207Standard400
A208Standard400
A209Standard400
A210Standard400
A211Standard400
B101Standard400
B102Standard400
B103Standard400
B104Standard400
B105Standard400
B106Standard400
B107Standard400
B108Standard400
B109Standard400
B110Standard400
B111Standard Twin500
B201Standard400
B202Standard400
B203Standard400
B204Standard400
B205Standard400
B206Standard400
B207Standard400
B208Standard400
B209Standard400
B210Standard400
B211Standard400
N1Standard Twin600
N2Standard500
N3Standard500
N4Standard Twin600
N5Standard Twin600
N6Standard Twin600
N7Standard500
"""

def parse_line(line):
    line = line.strip()
    if not line: return None
    # Use simpler regex: starts with LetterDigits, ends with Digits
    match = re.match(r'^([A-Z]\d+)(.*?)(\d+)$', line)
    if match:
        room_num = match.group(1)
        room_type = match.group(2).strip() or "Standard"
        price = int(match.group(3))
        return {
            "room_number": room_num,
            "room_type": room_type,
            "price_per_night": price,
            "status": "available"
        }
    return None

def main():
    try:
        supabase: Client = create_client(url, key)
        rooms = [parse_line(l) for l in raw_data.strip().split('\n') if parse_line(l)]
        
        print(f"เตรียมข้อมูล {len(rooms)} รายการ...")
        
        # Upsert data to table 'rooms'
        response = supabase.table("rooms").upsert(rooms, on_conflict="room_number").execute()
        
        print(f"สำเร็จ! นำเข้าข้อมูลห้องพัก {len(response.data)} ห้องเรียบร้อยแล้ว")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    main()