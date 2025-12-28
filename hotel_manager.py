import os
from supabase import create_client, Client
from db_config import SUPABASE_URL, SUPABASE_KEY

class HotelManager:
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def get_all_rooms(self):
        """ดึงรายชื่อห้องพักทั้งหมด"""
        try:
            res = self.supabase.table("rooms").select("*").order("room_number").execute()
            return res.data
        except Exception as e:
            return f"Error: {e}"

    def get_available_rooms(self):
        """ดึงรายชื่อห้องพักที่ว่าง"""
        try:
            res = self.supabase.table("rooms").select("*").eq("status", "available").execute()
            return res.data
        except Exception as e:
            return f"Error: {e}"

    def update_room_status(self, room_number, new_status):
        """เปลี่ยนสถานะห้องพัก (เช่น available -> booked)"""
        try:
            res = self.supabase.table("rooms").update({"status": new_status}).eq("room_number", room_number).execute()
            return res.data
        except Exception as e:
            return f"Error: {e}"

if __name__ == "__main__":
    manager = HotelManager()
    print("--- ระบบจัดการโรงแรมกำลังทำงาน ---")
    rooms = manager.get_all_rooms()
    if isinstance(rooms, list):
        print(f"พบห้องพักทั้งหมด {len(rooms)} ห้อง")
        if len(rooms) > 0:
            print("ตัวอย่างห้องพัก 3 ห้องแรก:")
            for r in rooms[:3]:
                print(f"  - ห้อง {r['room_number']} ({r['room_type']}) ราคา {r['price_per_night']} บาท")
    else:
        print(rooms)
