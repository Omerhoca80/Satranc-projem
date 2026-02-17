import streamlit as st
import requests
import random
from fpdf import FPDF
from datetime import date
from io import BytesIO

# --- AYARLAR ---
OGRETMEN_ADI = "Omer Can Uyduran"
SİTE_BASLIGI = "Omer Can Uyduran Satranc Akademisi"

st.set_page_config(page_title=SİTE_BASLIGI, page_icon="♟️")

# --- LICHESS TEMALARI ---
TEMALAR = {
    "1 Hamlede Mat": "mateIn1",
    "2 Hamlede Mat": "mateIn2",
    "3 Hamlede Mat": "mateIn3",
    "Açmaz (Pin)": "pin",
    "Çatal (Fork)": "fork",
    "Şiş (Skewers)": "skewer",
    "Feda (Sacrifice)": "sacrifice",
    "Oyun Sonu": "endgame"
}

# --- SORU ÜRETİCİ ---
def get_puzzles(count):
    # Lichess veya Chess.com üzerinden gerçek FEN örnekleri
    fens = [
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "4r1k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1",
        "r1bq1rk1/pppp1ppp/2n2n2/4p3/2B1P3/2P2N2/PPPP1PPP/RNBQ1RK1 w - - 0 1"
    ]
    return [{"fen": random.choice(fens)} for _ in range(count)]

# --- ARAYÜZ ---
st.title(f"♟️ {SİTE_BASLIGI}")

with st.sidebar:
    st.header("Ayarlar")
    konu = st.selectbox("Konu Seçin", list(TEMALAR.keys()))
    adet = st.number_input("Soru Sayısı", 1, 12, 4)

if st.button("Soruları Yenile"):
    st.session_state['sorular'] = get_puzzles(adet)
    st.session_state['konu'] = konu

if 'sorular' in st.session_state:
    cols = st.columns(2)
    for idx, s in enumerate(st.session_state['sorular']):
        with cols[idx % 2]:
            url = f"https://www.chess.com/diagram-editor/render?fen={s['fen']}&size=200"
            st.image(url, caption=f"Soru {idx+1}")

    # --- PDF BUTONU ---
    if st.button("📥 RESİMLİ PDF İNDİR (GARANTİLİ)"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        # Başlık
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=SİTE_BASLIGI, ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, txt=f"Konu: {st.session_state['konu']} | Hazirlayan: {OGRETMEN_ADI}", ln=True, align='C')
        pdf.ln(10)

        for i, soru in enumerate(st.session_state['sorular']):
            # Yüksek çözünürlüklü diyagram çekimi
            img_url = f"https://www.chess.com/diagram-editor/render?fen={soru['fen']}&size=400"
            
            try:
                # Resmi indiriyoruz
                img_res = requests.get(img_url, timeout=10)
                if img_res.status_code == 200:
                    img_bytes = BytesIO(img_res.content)
                    
                    # Sayfadaki yerini ayarla
                    pdf.set_font("Arial", 'B', 12)
                    pdf.cell(0, 10, txt=f"Soru {i+1}: En iyi hamleyi bulun.", ln=True)
                    
                    # Resmi PDF'e yaz (x, y koordinatlarını ve genişliği manuel veriyoruz)
                    current_y = pdf.get_y()
                    pdf.image(img_bytes, x=50, y=current_y, w=110)
                    
                    # Resimden sonraki boşluk
                    pdf.set_y(current_y + 120)
                else:
                    pdf.cell(0, 10, txt=f"Soru {i+1} (Resim Yuklenemedi)", ln=True)
            except Exception as e:
                pdf.cell(0, 10, txt=f"Soru {i+1} Hatasi: {str(e)}", ln=True)

            # Her 2 soruda bir yeni sayfa
            if (i + 1) % 2 == 0 and (i + 1) != len(st.session_state['sorular']):
                pdf.add_page()

        # PDF'i Bellekten Sun
        pdf_out = pdf.output(dest='S')
        if isinstance(pdf_out, str):
            pdf_out = pdf_out.encode('latin-1', 'replace')
            
        st.download_button(
            label="✅ PDF DOSYASINI KAYDET",
            data=pdf_out,
            file_name=f"test_{date.today()}.pdf",
            mime="application/pdf"
        )
