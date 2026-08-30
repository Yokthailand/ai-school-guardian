# วิธีเปิด AI School Guardian Demo

โปรเจกต์นี้ใส่วิดีโอตัวอย่างไว้แล้วที่ `backend/storage/videos/demo_school_guardian.mp4`

## 1) เปิด Backend

```bash
cd backend
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

macOS / Linux:

```bash
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend และหน้า Swagger จะอยู่ที่ <http://localhost:8000/docs>

## 2) เปิด Dashboard

เปิด Terminal อีกหน้าหนึ่ง:

```bash
cd frontend
npm install
npm run dev
```

เปิด <http://localhost:3000> แล้วกด **ANALYZE VIDEO** ระบบจะวาดกรอบบุคคล หมายเลขติดตาม และพื้นที่หวงห้าม ก่อนแสดงวิดีโอผลลัพธ์พร้อมสถิติ

## โหมด YOLOv8 + ByteTrack (แม่นยำกว่า)

ใน virtual environment ของ Backend ให้ติดตั้ง:

```bash
pip install -r requirements-ai.txt
```

จากนั้นเปิด Backend ใหม่ ระบบจะสลับจาก OpenCV fallback ไปใช้ YOLOv8 + ByteTrack โดยอัตโนมัติ การเปิดครั้งแรกอาจใช้เวลาสักครู่เพื่อดาวน์โหลดโมเดล `yolov8n.pt`

> ผลแจ้งเตือนเป็นข้อมูลช่วยคัดกรองและต้องมีผู้รับผิดชอบตรวจสอบ ไม่ควรใช้เพื่อตัดสินว่าบุคคลใดเป็นอันตรายโดยอัตโนมัติ
