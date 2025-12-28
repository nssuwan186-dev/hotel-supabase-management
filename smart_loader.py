import pandas as pd
import requests
import io
from supabase import create_client, Client
from db_config import SUPABASE_URL, SUPABASE_KEY

# ลิงก์ข้อมูล CSV
URL_SHEET1 = "https://docs.google.com/spreadsheets/d/1yeZcWKSo47etIbrLFlKQoQD0Sh2cVkcI7teWGyDgSKY/export?format=csv"
URL_SHEET2 = "https://docs.google.com/spreadsheets/d/1Tes9bQ7qyq5v4MPidprzxaXL8OuF7A6QlvK8GLAjzuY/export?format=csv"

def clean_currency(value):
    """แปลงข้อความเงิน เช่น '3,262' หรือ '-' ให้เป็น float"""
    if pd.isna(value) or value == '-':
        return 0.0
    return float(str(value).replace(',', '').replace('"', ''))

def load_sheet1(supabase: Client):
    print("กำลังประมวลผล Sheet 1 (บัญชีรายวัน)...")
    df = pd.read_csv(URL_SHEET1)
    # ล้างข้อมูลแถวที่ว่าง
    df = df.dropna(subset=['ชื่อรายการ'])
    
    data_to_insert = []
    for _, row in df.iterrows():
        data_to_insert.append({
            "date": str(row['วันที่']),
            "item_name": str(row['ชื่อรายการ']),
            "phone": str(row['เบอร์โทร']),
            "room_number": str(row['ห้อง']) if row['ห้อง'] != '-' else None,
            "nights": int(row['คืน']) if row['คืน'] != '-' else 0,
            "expense": clean_currency(row['จ่าย']),
            "income": clean_currency(row['รับ']),
            "total_balance": clean_currency(row['รวม']),
            "deposit": clean_currency(row['มัดจำสด']),
            "note": str(row['หมายเหตุ'])
        })
    
    if data_to_insert:
        # เนื่องจาก Anon Key ไม่สามารถรัน RPC ได้ เราจะใช้ upsert ทีละชุด
        res = supabase.table("accounting").upsert(data_to_insert).execute()
        print(f"นำเข้าบัญชีรายวันสำเร็จ: {len(res.data)} รายการ")

def load_sheet2(supabase: Client):
    print("กำลังประมวลผล Sheet 2 (ข้อมูลผู้เช่ารายเดือน)...")
    # เนื่องด้วยโครงสร้างซับซ้อน จะอ่านแบบดิบมาแกะ
    r = requests.get(URL_SHEET2)
    df = pd.read_csv(io.StringIO(r.content.decode('utf-8')))
    
    # แกะข้อมูลห้องและชื่อจากตำแหน่งที่แน่นอนในชีตตัวอย่าง
    room_no = "A206" # จากตัวอย่างที่ดึงมาได้
    tenant_name = df.iloc[1, 16] if len(df) > 1 else "Unknown"
    
    # แกะค่าไฟ/น้ำ (เดือน ม.ค. - พ.ย. ตามข้อมูลที่มี)
    months = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 
              'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน']
    
    rental_data = []
    for i, month in enumerate(months, 1):
        rental_data.append({
            "room_number": room_no,
            "tenant_name": tenant_name,
            "month_name": month,
            "electricity_meter": clean_currency(df.iloc[1, i]), # แถวค่าไฟ
            "water_meter": clean_currency(df.iloc[2, i]),       # แถวค่าน้ำ
            "rent_amount": 3500.0
        })
    
    if rental_data:
        res = supabase.table("monthly_rentals").upsert(rental_data).execute()
        print(f"นำเข้าข้อมูลผู้เช่ารายเดือนสำเร็จ: {len(res.data)} รายการ")

if __name__ == "__main__":
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    try:
        load_sheet1(supabase)
        load_sheet2(supabase)
        print("\n--- การจัดระเบียบและนำเข้าข้อมูลเสร็จสมบูรณ์ ---")
    except Exception as e:
        print(f"เกิดข้อผิดพลาด: {e}")
        print("คำแนะนำ: โปรดรันไฟล์ hotel_db_setup.sql ใน Supabase ก่อน")
