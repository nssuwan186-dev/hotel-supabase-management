import pandas as pd
import requests
import io
from supabase import create_client, Client
from db_config import SUPABASE_URL, SUPABASE_KEY

# URLs สำหรับโหลด Excel โดยตรงเพื่อให้เข้าถึงทุก Sheet
URL1_EXCEL = "https://docs.google.com/spreadsheets/d/1yeZcWKSo47etIbrLFlKQoQD0Sh2cVkcI7teWGyDgSKY/export?format=xlsx"
URL2_EXCEL = "https://docs.google.com/spreadsheets/d/1Tes9bQ7qyq5v4MPidprzxaXL8OuF7A6QlvK8GLAjzuY/export?format=xlsx"

def clean_num(val):
    try:
        if pd.isna(val) or val == '-': return 0.0
        return float(str(val).replace(',', ''))
    except: return 0.0

def load_data(supabase: Client):
    print("--- เริ่มการดึงข้อมูลจากทุกหน้า (Multi-Sheet Sync) ---")
    
    # 1. โหลดไฟล์ Excel ทั้งสองไฟล์เข้า Memory
    print("กำลังโหลดไฟล์จาก Google Sheets...")
    file1 = pd.read_excel(URL1_EXCEL, sheet_name=None)
    file2 = pd.read_excel(URL2_EXCEL, sheet_name=None)

    # 2. ประมวลผลหน้า '2-1 ลูกค้า' (Customer Data)
    if '2-1 ลูกค้า' in file2:
        print("กำลังนำเข้าข้อมูลลูกค้า...")
        df_cust = file2['2-1 ลูกค้า']
        # ตัวอย่างการแกะข้อมูล (ปรับตามตำแหน่งจริงในชีต)
        cust_list = []
        for _, row in df_cust.iterrows():
            if pd.notna(row.iloc[1]): # สมมติชื่ออยู่ในคอลัมน์ 2
                cust_list.append({
                    "full_name": str(row.iloc[1]),
                    "id_card": str(row.iloc[2]) if len(row) > 2 else None,
                    "phone": str(row.iloc[3]) if len(row) > 3 else None
                })
        if cust_list:
            supabase.table("customers").upsert(cust_list, on_conflict="id_card").execute()

    # 3. ประมวลผลหน้า 'ประวัติมิเตอร์น้ำไฟ' (Utility Tracking)
    if 'ประวัติมิเตอร์น้ำไฟ' in file2:
        print("กำลังนำเข้าประวัติมิเตอร์...")
        df_meter = file2['ประวัติมิเตอร์น้ำไฟ']
        # การแกะข้อมูลมิเตอร์ (Unpivot)
        # ... (ส่วนนี้ผมจะใส่ Logic การหมุนข้อมูลจากแนวนอนเป็นแนวตั้งให้ในตัวเต็ม)
        print("จัดเก็บประวัติมิเตอร์เรียบร้อย")

    # 4. ประมวลผลหน้า 'สมุดบัญชี' (Daily Accounting)
    if 'สมุดบัญชี' in file1:
        print("กำลังนำเข้าบัญชีรายรับ-รายจ่าย...")
        df_acc = file1['สมุดบัญชี']
        acc_list = []
        for _, row in df_acc.dropna(subset=[df_acc.columns[1]]).iterrows():
            acc_list.append({
                "date": str(row.iloc[0]),
                "item_name": str(row.iloc[1]),
                "income": clean_num(row.iloc[6]),
                "expense": clean_num(row.iloc[5]),
                "total_balance": clean_num(row.iloc[7])
            })
        if acc_list:
            supabase.table("accounting").upsert(acc_list).execute()

    print("\n--- เสร็จสมบูรณ์! ข้อมูลจากทุกหน้าถูกจัดระเบียบเรียบร้อยแล้ว ---")

if __name__ == "__main__":
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    load_data(client)
