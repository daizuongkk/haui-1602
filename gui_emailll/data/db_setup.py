"""
db_setup.py
-----------
Khoi tao co so du lieu SQL Server `dienbien_weather` cho Notification Service.

File `dienbien_weather_updated_modified.sql` di kem trong repo la T-SQL that
(SQL Server): tao database `dienbien_weather` neu chua co, DROP/CREATE bang
`nguoi_dan` va nap 29 dong du lieu mau bang IDENTITY_INSERT.

Script nay:
  1. Doc toan bo file .sql, tach theo tu khoa `GO` (dung chuan batch cua
     SQL Server) va thuc thi tuan tu tung batch qua pyodbc.
  2. Xoa va tao lai bang `notification_logs`.

Chay: python db_setup.py
"""
import os
import re
import sys

import pyodbc
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

SQL_CONNECTION_STRING = os.getenv("SQL_CONNECTION_STRING")
SQL_FILE_PATH = os.path.join(BASE_DIR, "dienbien_weather_updated_modified.sql")
DB_NAME = "dienbien_weather"


def get_connection_string_for(database: str) -> str:
    """Return the SQL_CONNECTION_STRING with DATABASE overridden."""
    if "DATABASE=" in SQL_CONNECTION_STRING:
        return re.sub(r"DATABASE=[^;]*", f"DATABASE={database}", SQL_CONNECTION_STRING)
    return SQL_CONNECTION_STRING.rstrip(";") + f";DATABASE={database};"


def split_batches(sql_text: str):
    """Split a T-SQL script into batches on standalone 'GO' lines.

    Block comments (/* ... */) are stripped first so a 'GO' written inside a
    commented-out section is not mistaken for a real batch separator.
    """
    sql_text = re.sub(r"/\*.*?\*/", "", sql_text, flags=re.S)
    batches = re.split(r"(?im)^\s*GO\s*$", sql_text)
    return [b.strip() for b in batches if b.strip()]


def run_sql_script(cur, path: str) -> None:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    for batch in split_batches(content):
        cur.execute(batch)
    print(f"[OK] Da thuc thi file '{os.path.basename(path)}'.")


def create_notification_logs_table(cur) -> None:
    cur.execute(
        "IF OBJECT_ID('dbo.notification_logs', 'U') IS NOT NULL DROP TABLE dbo.notification_logs"
    )
    cur.execute(
        """
        CREATE TABLE notification_logs (
            id INT IDENTITY(1,1) PRIMARY KEY,
            nguoi_dan_id INT NOT NULL,
            warning_id VARCHAR(100) NOT NULL,
            send_time DATETIME DEFAULT GETDATE(),
            status VARCHAR(20) NOT NULL,
            CONSTRAINT FK_notification_logs_nguoi_dan
                FOREIGN KEY (nguoi_dan_id) REFERENCES nguoi_dan(id)
        )
        """
    )
    print("[OK] Bang 'notification_logs' da duoc tao lai.")


def main() -> None:
    if not SQL_CONNECTION_STRING:
        print("[LOI] Thieu bien SQL_CONNECTION_STRING trong .env")
        sys.exit(1)

    # Batch dau tien (CREATE DATABASE) phai chay o che do autocommit va
    # ngoai pham vi database dich, vi CREATE DATABASE khong duoc phep trong
    # mot transaction/explicit user do SQL Server. Neu database dich chua
    # ton tai thi ket noi truc tiep se loi -> thu lai qua 'master'.
    try:
        conn = pyodbc.connect(SQL_CONNECTION_STRING, autocommit=True)
    except pyodbc.Error:
        conn = pyodbc.connect(get_connection_string_for("master"), autocommit=True)

    try:
        cur = conn.cursor()
        run_sql_script(cur, SQL_FILE_PATH)
        print(f"[OK] Database '{DB_NAME}', bang 'nguoi_dan' va du lieu mau da san sang.")

        create_notification_logs_table(cur)

        print("[XONG] Khoi tao co so du lieu 'dienbien_weather' thanh cong.")
    except Exception as exc:
        print(f"[LOI] Khoi tao that bai: {exc}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
