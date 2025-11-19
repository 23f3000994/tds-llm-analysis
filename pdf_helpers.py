import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import pandas as pd


def extract_tables_sum_from_pdf(pdf_path, column_name="value", page_number=2):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_number <= len(pdf.pages):
                page = pdf.pages[page_number - 1]
                tables = page.extract_tables()

                for tbl in tables:
                    df = pd.DataFrame(tbl[1:], columns=tbl[0])
                    cols = [c.lower().strip() for c in df.columns]

                    if column_name.lower() in cols:
                        col_name = df.columns[cols.index(column_name.lower())]
                        df[col_name] = pd.to_numeric(df[col_name].str.replace(",", ""), errors="coerce")
                        s = df[col_name].sum()
                        return int(s) if s and s.is_integer() else s
        return None
    except:
        return None


def pdf_to_images_and_ocr(pdf_path):
    try:
        images = convert_from_path(pdf_path, dpi=200)
        out = []
        for img in images:
            txt = pytesseract.image_to_string(img)
            out.append(txt)
        return "\n".join(out)
    except Exception as e:
        return str(e)
