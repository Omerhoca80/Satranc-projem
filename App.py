import streamlit as st
import requests
import random
from fpdf import FPDF
from datetime import date
from io import BytesIO

# --- KİŞİSELLEŞTİRME ---
OGRETMEN_ADI = "Omer Can Uyduran"
SİTE_BASLIGI = "Omer Can Uyduran Satranc Akademisi"

st.set_page_config(page_title=SİTE_BASLIGI, page_icon="♟️")

# --- LICHESS VERİ TABANINA BAĞLANMA ---
def get_puzzles(count):
    puzzles = []
    # Test amaçlı sabit bir FEN havuzu (İleride Lichess API ile çeşitlendirilebilir)
    fen_list = [
        "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "r1bqk1nr/pppp1ppp/2n5/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
    ]
    for i in range(count):
        selected_fen = random.choice(fen_list)
        puzzles.append({"fen": selected_fen})
    return puzzles

# --- ARAYÜZ ---
st.title(f"♟️ {SİTE_BASLIGI}")
st.write(f"Hoş geldiniz, **{OGRETMEN_ADI}**.")

with st.sidebar:
    st.header("Soru Ayarları")
    adet = st.number_input("Soru Sayısı", 1, 10, 4) # Sayfa yapısı için şimdilik az tutalım

if st.button("Soruları Getir"):
    st.session_state['hazir_sorular'] = get_puzzles(adet)
    cols = st.columns(2)
    for idx, soru in enumerate(st.session_state['hazir_sorular']):
        with cols[idx % 2]:
            img_url = f"https://www.chess.com/diagram-editor/render?fen={soru['fen']}&size=200"
            st.image(img_url, caption=f"Soru {idx+1}")

# --- PDF OLUŞTURMA (RESİMLİ) ---
if 'hazir_sorular' in st.session_state:
    if st.button("Resimli PDF Oluştur"):
        pdf = FPDF()
        pdf.add_page()
        
        # Başlıklar
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=SİTE_BASLIGI, ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(200, 10, txt=f"Hazirlayan: {OGRETMEN_ADI} - Tarih: {date.today()}", ln=True, align='C')
        pdf.ln(10)

        for i, soru in enumerate(st.session_state['hazir_sorular']):
            # 1. Resmi İnternetten İndir
            img_url = f"https://www.chess.com/diagram-editor/render?fen={soru['fen']}&size=200"
            response = requests.get(img_url)
            
            if response.status_code == 200:
                img_data = BytesIO(response.content)
                # 2. Resmi PDF'e Ekle (Soru metni ile birlikte)
                pdf.set_font("Arial", 'B', 11)
                pdf.cell(0, 10, txt=f"Soru {i+1}: Beyaz oynar, en iyi hamleyi bul.", ln=True)
                
                # Resim konumu ayarı (Her sayfaya 2 soru sığacak şekilde basit yerleşim)
                pdf.image(img_data, x=10, y=pdf.get_y(), w=60)
                pdf.ln(70) # Bir sonraki soru için boşluk bırak

        pdf_output = pdf.output(dest='S')
        if isinstance(pdf_output, str):
            pdf_output = pdf_output.encode('latin-1', 'replace')
        
        st.download_button(label="📥 Resimli PDF'i İndir", data=pdf_output, file_name="satranc_testi.pdf", mime="application/pdf")
