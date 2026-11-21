"""
excel_report.py - read several sheets from an Excel workbook, summarise, and write a styled
multi-sheet Excel report with pandas + openpyxl.

Run:   python 02-python-for-data/code/excel_report.py
Output: 02-python-for-data/outputs/monthly_report.xlsx
"""
from pathlib import Path                                   # file paths that work on Windows/Mac/Linux

import pandas as pd                                        # tables
from openpyxl import load_workbook                         # open an .xlsx to change its look
from openpyxl.styles import Font, PatternFill              # bold text and coloured cell backgrounds

HERE = Path(__file__).resolve().parent                     # code/ folder
SOURCE = HERE.parent / "excel" / "practice-datasets.xlsx"  # the practice workbook
OUT = HERE.parent / "outputs" / "monthly_report.xlsx"      # where the report will be written

# --- 1. Read every sheet at once -----------------------------------------------------
sheets = pd.read_excel(SOURCE, sheet_name=None)            # dict: {"Sales": DataFrame, "Customers": ...}
print("sheets found:", list(sheets))                       # show the sheet names
sales = sheets["Sales"]                                    # pick out the tables we need
products = sheets["Products"]
customers = sheets["Customers"]

# --- 2. Prepare one combined table ---------------------------------------------------
sales["revenue"] = sales["quantity"] * sales["unit_price"] * (1 - sales["discount_pct"] / 100)  # money per order
sales["month"] = pd.to_datetime(sales["order_date"]).dt.strftime("%Y-%m")     # "2026-03" style month label
full = (sales.merge(products.drop(columns="unit_price"), on="product_id", how="left")  # add category
             .merge(customers, on="customer_id", how="left"))                         # add city, segment
full["city"] = full["city"].fillna("Unknown")              # orders from unknown customers

# --- 3. Build the summary tables -----------------------------------------------------
by_month = full.groupby("month").agg(orders=("order_id", "count"),       # one row per month
                                     revenue=("revenue", "sum")).round(0)
by_category = pd.pivot_table(full, index="category", columns="month",     # category x month grid
                             values="revenue", aggfunc="sum").round(0)
by_segment = full.groupby("segment").agg(customers=("customer_id", "nunique"),   # per customer segment
                                         revenue=("revenue", "sum")).round(0)

# --- 4. Write them into one workbook, one sheet each ----------------------------------
OUT.parent.mkdir(exist_ok=True)                            # create outputs/ if needed
with pd.ExcelWriter(OUT, engine="openpyxl") as writer:     # keeps the file open for several sheets
    by_month.to_excel(writer, sheet_name="By month")       # each call adds one sheet
    by_category.to_excel(writer, sheet_name="Category x month")
    by_segment.to_excel(writer, sheet_name="By segment")
print("written", OUT)

# --- 5. Make it look professional with openpyxl --------------------------------------
wb = load_workbook(OUT)                                    # open the file we just wrote
header_fill = PatternFill("solid", fgColor="1B263B")       # dark navy background
for ws in wb.worksheets:                                   # every sheet in the workbook
    for cell in ws[1]:                                     # row 1 is the header row
        cell.font = Font(bold=True, color="FFFFFF")        # bold white text
        cell.fill = header_fill                            # on navy
    ws.column_dimensions["A"].width = 16                   # make the label column wider
    for row in ws.iter_rows(min_row=2, min_col=2):         # every number cell below the header
        for cell in row:
            cell.number_format = "#,##0"                   # show 12345 as 12,345

ws = wb["By month"]                                        # add a live formula column to one sheet
ws["D1"] = "avg_order_value"                               # new header
ws["D1"].font = Font(bold=True, color="FFFFFF")
ws["D1"].fill = header_fill
for r in range(2, ws.max_row + 1):                         # one formula per month row
    ws[f"D{r}"] = f"=C{r}/B{r}"                            # revenue / orders, calculated by Excel
    ws[f"D{r}"].number_format = "#,##0.0"
wb.save(OUT)                                               # write the changes back to disk
print("styled and saved. Open it in Excel, LibreOffice or Google Sheets.")
