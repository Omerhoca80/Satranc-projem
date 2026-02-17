import streamlit as st
import pandas as pd
import chess
import chess.svg
import tempfile
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table
from reportlab.platypus import Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from io import BytesIO

# -------------------------
# CONFIG
# -------------------------

CSV_PATH = "lichess_db_puzzle.csv"

LEVEL_RANGES = {
    "Kolay": (0, 1400),
    "Orta": (1400, 1900),
    "Zor": (1900, 3000)
}

THEME_MAP = {
    "1 Hamlede Mat": "mateIn1",
    "2 Hamlede Mat": "mateIn2",
    "3 Hamlede Mat": "mateIn3",
    "4 Hamlede Mat": "mateIn4",
    "Çatal": "fork",
    "Şiş": "skewer",
    "Açmaz": "pin",
    "Savunmanın Kaldırılması": "removalOfDefender",
    "Saptırma": "deflection",
    "Piyon Oyunsonu": "pawnEndgame",
    "Vezir Oyunsonu": "queenEndgame",
    "Kale Oyunsonu": "rookEndgame",
    "Açılış": "opening",
    "Oyun Ortası": "middlegame",
    "Karışık": None
}

# -------------------------
# LOAD DATA
# -------------------------

@st.cache_data
def load_data():
    return pd.read_csv(CSV_PATH)

def filter_puzzles(df, theme, level, limit):
    min_rating, max_rating = LEVEL_RANGES[level]

    filtered = df[
        (df["Rating"] >= min_rating) &
        (df["Rating"] <= max_rating)
    ]

    if theme:
        filtered = filtered[filtered["Themes"].str.contains(theme)]

    return filtered.sample(n=min(limit, len(filtered)))

# -------------------------
# BOARD DRAW (CAIRO YOK)
# -------------------------

def generate_board_image(fen):
    board = chess.Board(fen)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    file_path = temp_file.name
    temp_file.close()

    # PNG üretimi (SVG kullanmadan)
    from reportlab.graphics import renderPM
    from svglib.svglib import svg2rlg

    svg_data = chess.svg.board(board=board)
    svg_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
    svg_temp.write(svg_data.encode())
    svg_temp.close()

    drawing = svg2rlg(svg_temp.name)
    renderPM.drawToFile(drawing, file_path, fmt="PNG")

    os.remove(svg_temp.name)

    return file_path

# -------------------------
# PDF
# -------------------------

def create_pdf(puzzles, theme_label, level):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("SATRANC TESTI", styles["Heading1"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Konu: {theme_label}", styles["Normal"]))
    elements.append(Paragraph(f"Seviye: {level}", styles["Normal"]))
    elements.append(Paragraph("Hazirlayan: Omer Can Uyduran", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    student_table = Table([
        ["Ogrenci Adi:", "__________________________"],
        ["Tarih:", "____ / ____ / ______"]
    ], colWidths=[2*inch, 3*inch])

    elements.append(student_table)
    elements.append(PageBreak())

    for i, (_, row) in enumerate(puzzles.iterrows(), 1):

        image_path = generate_board_image(row["FEN"])

        elements.append(Paragraph(f"Soru {i}", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * inch))
        elements.append(RLImage(image_path, width=4*inch, height=4*inch))
        elements.append(Spacer(1, 0.5 * inch))

        os.remove(image_path)

        if i % 2 == 0:
            elements.append(PageBreak())

    doc.build(elements)
    buffer.seek(0)
    return buffer

# -------------------------
# UI
# -------------------------

st.title("♟️ Ogrenciye Ozel Satranc Testi")

df = load_data()

theme_label = st.selectbox("Konu Sec", list(THEME_MAP.keys()))
level = st.selectbox("Seviye", list(LEVEL_RANGES.keys()))
limit = st.selectbox("Soru Sayisi", [5, 10, 15, 20])

if st.button("PDF Olustur"):

    theme = THEME_MAP[theme_label]
    puzzles = filter_puzzles(df, theme, level, limit)

    if len(puzzles) == 0:
        st.error("Uygun puzzle bulunamadi.")
    else:
        pdf = create_pdf(puzzles, theme_label, level)

        st.success("PDF hazir!")

        st.download_button(
            label="PDF Indir",
            data=pdf,
            file_name=f"{theme_label}_{level}_test.pdf",
            mime="application/pdf"
        )
