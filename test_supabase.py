import os
from supabase import create_client, Client

url = "https://eeizuypqyhepkczqmqky.supabase.co"
key = "sb_publishable_AiaNimVhNkL3cA0lkeTYRw_AgjBF73J"

try:
    print("กำลังพยายามเชื่อมต่อกับ Supabase...")
    supabase: Client = create_client(url, key)
    
    # ลองดึงข้อมูลจากตาราง 'profiles' (ตามที่ระบบแนะนำ)
    print("กำลังลองดึงข้อมูลจากตาราง 'profiles'...")
    response = supabase.table("profiles").select("*").limit(5).execute()
    
    if response.data:
        print("เชื่อมต่อสำเร็จ! ข้อมูลที่พบในตาราง 'profiles':")
        for item in response.data:
            print(f"- {item}")
    else:
        print("เชื่อมต่อสำเร็จ แต่ไม่พบข้อมูลในตาราง 'profiles'")

except Exception as e:
    print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
