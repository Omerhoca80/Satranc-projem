import streamlit as st
import requests
import random
from datetime import date
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image

# --- AYARLAR ---
OGRETMEN_ADI = "Omer Can Uyduran"
SİTE_BASLIGI = "Omer Can Uyduran Satranc Akademisi"

st.set_page_config(page_title=SİTE_BASLIGI, page_icon="♟️")

# --- LICHESS TEMALARI ---
TEMALAR = {
    "1 Hamlede Mat": "mateIn1",
    "2 Hamlede Mat": "mateIn2",
    "3 Hamlede Mat": "mateIn3",
    "Acmaz (Pin)": "pin",
    "Catal (Fork)": "fork",
    "Sis (Skewers)": "skewer"
}

def get_puzzles(count):
    fens = [
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
        "4r1k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1",
        "k7/8/K7/8/8/8/8/R7 w - - 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2"
    ]
    return [{"fen": random.choice(fens)} for _ in range(count)]

st.title(f"♟️ {SİTE_BASLIGI}")

with st.sidebar:
    konu = st.selectbox("Konu Secin", list(TEMALAR.keys()))
    adet = st.number_input("Soru Sayisi", 1, 10, 4)

if st.button("Sorulari Getir"):
    st.session_state['sorular'] = get_puzzles(adet)
    st.session_state['konu'] = konu

if 'sorular' in st.session_state:
    cols = st.columns(2)
    for idx, s in enumerate(st.session_state['sorular']):
        url = f"https://www.chess.com/diagram-editor/render?fen={s['fen']}&size=200"
        cols[idx % 2].image(url, caption=f"Soru {idx+1}")

    if st.button("✅ RESIMLI PDF INDIR (KESIN COZUM)"):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Baslik
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height - 50, SİTE_BASLIGI)
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height - 70, f"Hazirlayan: {OGRETMEN_ADI} - {date.today()}")
        
        y_position = height - 120
        
        for i, soru in enumerate(st.session_state['sorular']):
            img_url = f"https://www.chess.com/diagram-editor/render?fen={soru['fen']}&size=300"
            res = requests.get(img_url)
            
            if res.status_code == 200:
                img = Image.open(BytesIO(res.content))
                # Resmi PDF formatina uygun hale getiriyoruz
                img_buffer = BytesIO()
                img.save(img_buffer, format="PNG")
                img_buffer.seek(0)
                
                # Yeni Sayfa Kontrolu
                if y_position < 250:
                    c.showPage()
                    y_position = height - 100
                
                c.setFont("Helvetica-Bold", 12)
                c.drawString(100, y_position, f"Soru {i+1}: En iyi hamleyi bulunuz.")
                y_position -= 210
                # Resmi ciz
                c.drawInlineImage(img, 150, y_position, width=250, height=200)
                y_position -= 40

        c.save()
        pdf_data = buffer.getvalue()
        st.download_button("📥 PDF'i Kaydet", data=pdf_data, file_name="satranc_testi.pdf", mime="application/pdf")
