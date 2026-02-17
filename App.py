import streamlit as st
import requests
import chess
import chess.svg
import tempfile
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage
from io import BytesIO
from PIL import Image as PILImage

# -------------------------
# CONFIG
# -------------------------

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
# LICHESS API FETCH
# -------------------------

def fetch_puzzles(theme, level, limit):
    min_rating, max_rating = LEVEL_RANGES[level]
    puzzles = []

    while len(puzzles) < limit:
        url = "https://lichess.org/api/puzzle"
        params = {}

        if theme:
            params["theme"] = theme

        response = requests.get(url, params=params, headers={"Accept": "application/json"})
        data = response.json()

        rating = data["puzzle"]["rating"]

        if min_rating <= rating <= max_rating:
            puzzles.append({
                "fen": data["game"]["fen"],
                "rating": rating
            })

    return puzzles


# -------------------------
# BOARD IMAGE
# -------------------------

def generate_board_image(fen):
    board = chess.Board(fen)
    svg_data = chess.svg.board(board=board)

    temp_svg = tempfile.NamedTemporaryFile(delete=False, suffix=".svg")
    temp_svg.write(svg_data.encode())
    temp_svg.close()

    temp_png = temp_svg.name.replace(".svg", ".png")

    # SVG → PNG dönüşüm (Pillow ile)
    from cairosvg import svg2png
    svg2png(url=temp_svg.name, write_to=temp_png)

    os.remove(temp_svg.name)

    return temp_png


# -------------------------
# PDF CREATION
# -------------------------

def create_pdf(puzzles, theme_label, level):

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []
    styles = getSampleStyleSheet()

    # HEADER
    elements.append(Paragraph("SATRAÇ TESTİ", styles["Heading1"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"Konu: {theme_label}", styles["Normal"]))
    elements.append(Paragraph(f"Seviye: {level}", styles["Normal"]))
    elements.append(Paragraph("Hazırlayan: Ömer Can Uyduran", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    student_table = Table([
        ["Öğrenci Adı:", "__________________________"],
        ["Tarih:", "____ / ____ / ______"]
    ], colWidths=[2*inch, 3*inch])

    elements.append(student_table)
    elements.append(PageBreak())

    # QUESTIONS
    for i, puzzle in enumerate(puzzles, 1):

        image_path = generate_board_image(puzzle["fen"])

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
# STREAMLIT UI
# -------------------------

st.title("♟️ Canlı Lichess Satranç Testi Oluşturucu")

theme_label = st.selectbox("Konu Seç", list(THEME_MAP.keys()))
level = st.selectbox("Seviye", list(LEVEL_RANGES.keys()))
limit = st.selectbox("Soru Sayısı", [5, 10, 15, 20])

if st.button("PDF Oluştur"):
    theme = THEME_MAP[theme_label]

    with st.spinner("So
