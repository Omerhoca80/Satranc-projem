import streamlit as st
import pandas as pd
import chess
import chess.svg
import cairosvg
import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Table
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
        (df["Rating"] < max_rating)
    ]

    if theme:
        filtered = filtered[filtered["Themes"].str.contains(theme)]

    return filtered.sample(n=min(limit, len(filtered)))

# -------------------------
# BOARD IMAGE
# -------------------------

def generate_board_image(fen, filename):
    board = chess.Board(fen)
    svg = chess.svg.board(board=board)

    svg_file = filename.replace(".png", ".sv_
