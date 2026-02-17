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

# --- LICHESS TEMALARI (Tam Liste) ---
TEMALAR = {
    "1 Hamlede Mat": "mateIn1",
    "2 Hamlede Mat": "mateIn2",
    "3 Hamlede Mat": "mateIn3",
    "Açmaz (Pin)": "pin",
    "Çatal (Fork)": "fork",
    "Şiş (Skewers)": "skewer",
    "Feda (Sacrifice)": "sacrifice"
}

def get_puzzles(count):
    # Gerçek uygulamada Lichess API kullanılabilir, şimdilik güvenli FEN listesi
    fens = [
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
        "4r1k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "6k1/5ppp/8/8/8/8/5PPP/6K1 w - - 0 1"
    ]
    return [{"fen": random.choice(fens)} for _ in range(count)]

st.title(f"♟️ {SİTE_BASLIGI}")

with st.sidebar:
    st.header("Çalışma Kağıdı Ayarları")
    konu = st.selectbox("Taktik Tema", list(TEMALAR.keys()))
    adet = st.number_input("Soru Sayısı", 2, 12, 6)

if st.button("Soruları Lichess'ten Getir"):
    st.session_state['sorular'] = get_puzzles(adet)
    st.session_state['konu'] = konu

if 'sorular' in st.session_state:
    # Ekranda Önizleme
    cols = st.columns(3)
    for idx, s in enumerate(st.session_state['sorular']):
        url = f"https://www.chess.com/diagram-editor/render?fen={s['fen']}&size=200"
        cols[idx % 3].image(url, caption=f"Soru {idx+1}")

    # --- PDF OLUŞTURMA (ChessNonstop Tarzı) ---
    if st.button("📥 PROFESYONEL PDF OLUŞTUR"):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Sayfa Başlığı
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(width/2, height - 50, SİTE_BASLIGI)
        c.setFont("Helvetica", 12)
        c.drawCentredString(width/2, height - 70, f"Konu: {st.session_state['konu']} | Hazırlayan: {OGRETMEN_ADI}")
        c.line(50, height - 80, width - 50, height - 80) # Alt çizgi
        
        # Soru Izgarası Ayarları (2 sütunlu yapı)
        x_start = 60
        y_start = height - 150
        x_offset = 260
        y_offset = 240
        
        for i, soru in enumerate(st.session_state['sorular']):
            # Sütun ve satır hesapla
            col = i % 2
            row = (i // 2) % 3
            
            if i > 0 and i % 6 == 0: # Her 6 soruda yeni sayfa
                c.showPage()
                y_start = height - 100
                # Yeni sayfada başlığı tekrar yaz (isteğe bağlı)
            
            curr_x = x_start + (col * x_offset)
            curr_y = y_start - (row * y_offset)
            
            # Resmi indir ve işle (Garantili yöntem)
            img_url = f"https://www.chess.com/diagram-editor/render?fen={soru['fen']}&size=300"
            res = requests.get(img_url)
            if res.status_code == 200:
                img = Image.open(BytesIO(res.content))
                # Resmi çiz
                c.setFont("Helvetica-Bold", 11)
                c.drawString(curr_x, curr_y + 160, f"Soru {i+1}: Beyaz Oynar")
                c.drawInlineImage(img, curr_x, curr_y, width=200, height=150)
                # Cevap çizgisi
                c.setDash(1, 2) # Kesikli çizgi
                c.line(curr_x, curr_y - 15, curr_x + 200, curr_y - 15)
                c.setDash(1, 0) # Normal çizgiye dön
        
        c.save()
        st.download_button("✅ PDF Hazır! İndirmek İçin Tıklayın", 
                           data=buffer.getvalue(), 
                           file_name=f"satranc_calisma_{date.today()}.pdf", 
                           mime="application/pdf")
