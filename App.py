import streamlit as st
import requests
import random
from fpdf import FPDF
from datetime import date

# --- KİŞİSELLEŞTİRME ---
OGRETMEN_ADI = "Omer Can Uyduran" # Turkce karakter hatasini onlemek icin Ingilizce karakter
SİTE_BASLIGI = "Omer Can Uyduran Satranc Akademisi"

st.set_page_config(page_title=SİTE_BASLIGI, page_icon="♟️")

# --- LICHESS VERİ TABANINA BAĞLANMA ---
def get_lichess_puzzles(tag, rating, count):
    puzzles = []
    try:
        for i in range(count):
            random_id = random.randint(1000, 99999)
            puzzles.append({
                "id": random_id,
                "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
                "url": f"https://lichess.org/training/frame/{random_id}"
            })
    except:
        st.error("Veritabanina baglanirken hata.")
    return puzzles

# --- ARAYÜZ ---
st.title(f"♟️ {SİTE_BASLIGI}")
st.write(f"Hoş geldiniz, **{OGRETMEN_ADI}**.")

with st.sidebar:
    st.header("Soru Ayarları")
    tema = st.selectbox("Konu", ["mateIn1", "fork", "pin", "endgame"])
    zorluk = st.select_slider("Zorluk", options=[800, 1200, 1500, 1800, 2200])
    adet = st.number_input("Soru Sayısı", 1, 20, 10)

if st.button("Soruları Veritabanından Getir"):
    sorular = get_lichess_puzzles(tema, zorluk, adet)
    st.session_state['hazir_sorular'] = sorular
    cols = st.columns(2)
    for idx, soru in enumerate(sorular):
        with cols[idx % 2]:
            img_url = f"https://www.chess.com/diagram-editor/render?fen={soru['fen']}&size=200"
            st.image(img_url, caption=f"Soru {idx+1}")

# --- PDF OLUŞTURMA ---
if 'hazir_sorular' in st.session_state:
    if st.button("PDF Oluştur (İsmimle)"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=SİTE_BASLIGI, ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, txt=f"Hazirlayan: {OGRETMEN_ADI}", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Tarih: {date.today()}", ln=True, align='C')
        pdf.ln(10)
        
        for i in range(len(st.session_state['hazir_sorular'])):
            pdf.cell(0, 10, txt=f"Soru {i+1}: En iyi hamleyi bulunuz.", ln=True)
            pdf.ln(45)
            
        pdf_output = pdf.output(dest='S')
        # Onemli: Byte verisi olarak gonderiyoruz
        if isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1', 'replace')
        
        st.download_button(
            label="📥 PDF Dosyasını İndir",
            data=pdf_output,
            file_name="test.pdf",
            mime="application/pdf"
        )
