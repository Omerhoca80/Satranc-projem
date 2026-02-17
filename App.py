import streamlit as st
import requests
import random
from datetime import date
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

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
    adet = st.number_input("Soru Sayisi (Max 4)", 1, 4, 4)

if st.button("Sorulari Getir"):
    st.session_state['sorular'] = get_puzzles(adet)
    st.session_state['konu'] = konu

if 'sorular' in st.session_state:
    cols = st.columns(2)
    for idx, s in enumerate(st.session_state['sorular']):
        url = f"https://www.chess.com/diagram-editor/render?fen={s['fen']}&size=200"
        cols[idx % 2].image(url, caption=f"Soru {idx+1}")

    if st.button("📥 GARANTİLİ PDF OLUŞTUR"):
        # 1. A4 Boyutunda (300 DPI) Beyaz Bir Resim Oluştur (2480x3508 piksel)
        a4_canvas = Image.new('RGB', (2480, 3508), color=(255, 255, 255))
        draw = ImageDraw.Draw(a4_canvas)
        
        # Baslik Yazilari
        # Not: Sunucuda font bulamazsa varsayilan fontu kullanir
        try:
            title_font = ImageFont.load_default()
        except:
            title_font = None

        draw.text((1240, 200), SİTE_BASLIGI, fill=(0,0,0), anchor="mm")
        draw.text((1240, 300), f"Hazirlayan: {OGRETMEN_ADI} - Konu: {st.session_state['konu']}", fill=(0,0,0), anchor="mm")

        # 2. Sorulari ve Resimleri Tuvale Yerlestir
        positions = [(200, 500), (1300, 500), (200, 1800), (1300, 1800)]
        
        for i, soru in enumerate(st.session_state['sorular']):
            if i >= 4: break # Simdilik 4 soru sığdıralım
            
            img_url = f"https://www.chess.com/diagram-editor/render?fen={soru['fen']}&size=400"
            res = requests.get(img_url)
            
            if res.status_code == 200:
                puzzle_img = Image.open(BytesIO(res.content)).convert("RGB")
                puzzle_img = puzzle_img.resize((900, 900)) # Resimleri büyüt
                
                # Resmi beyaz sayfaya yapistir
                a4_canvas.paste(puzzle_img, positions[i])
                draw.text((positions[i][0], positions[i][1] - 100), f"Soru {i+1}: Sira Beyazda", fill=(0,0,0))
                # Cevap çizgisi
                draw.line([positions[i][0], positions[i][1]+1000, positions[i][0]+900, positions[i][1]+1000], fill=(0,0,0), width=5)

        # 3. Sayfayi PDF Olarak Kaydet
        pdf_buffer = BytesIO()
        a4_canvas.save(pdf_buffer, format="PDF", resolution=300.0)
        
        st.download_button(
            label="✅ PDF'i Buradan İndirin",
            data=pdf_buffer.getvalue(),
            file_name=f"satranc_testi_{date.today()}.pdf",
            mime="application/pdf"
        )
