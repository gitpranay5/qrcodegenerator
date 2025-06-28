from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import pyodbc
import base64
import qrcode
import os
from io import BytesIO

# Loading Environment variable (Azure SQL Database Connection)
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

## Allowing CORS for local testing
#origins = [
#    "http://localhost:3000" in production I will assign a ingress ip
##]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # for testing purposes, allow all origins 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure SQL Connection Configuration
conn_str = (
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={os.getenv('AZURE_SQL_SERVER')};"
    f"DATABASE={os.getenv('AZURE_SQL_DB')};"
    f"UID={os.getenv('AZURE_SQL_USER')};"
    f"PWD={os.getenv('AZURE_SQL_PASSWORD')}"
)

class URLRequest(BaseModel):
    url: HttpUrl
@app.post("/generate-qr/")
async def generate_qr(url_request: URLRequest):
    url = url_request.url
    # Generate QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR Code to BytesIO object
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Step 3: Convert to Base64 for frontend display
    qr_base64 = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")

    try:
        # Connect to Azure SQL DB
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            
            # Create table if not exists (optional safeguard)
            cursor.execute("""
                IF NOT EXISTS (
                    SELECT * FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_NAME = 'QRCodeStorage'
                )
                CREATE TABLE QRCodeStorage (
                    id INT IDENTITY PRIMARY KEY,
                    url NVARCHAR(2083),
                    image VARBINARY(MAX)
                )
            """)
            conn.commit()

            # Insert the QR code and URL into the DB
            cursor.execute("""
                INSERT INTO QRCodeStorage (url, image)
                VALUES (?, ?)
            """, url, img_byte_arr.read())
            conn.commit()

        # Step 5: Return Base64 string to frontend
        return {
            "message": "QR code generated and saved successfully.",
            "qr_code_base64": qr_base64
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from prometheus_fastapi_instrumentator import Instrumentator

# Register instrumentation
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

    