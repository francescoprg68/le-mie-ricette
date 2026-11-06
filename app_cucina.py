# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import os
import base64
from PIL import Image

# Ottiene automaticamente il percorso della cartella in cui si trova questo script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurazione pagina Streamlit (layout wide a tutto schermo)
st.set_page_config(page_title="Il Mio Ricettario", page_icon="🍳", layout="wide")

# Percorsi salvataggi all'interno della cartella
MEDIA_DIR = os.path.join(BASE_DIR, "media_cucina")
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

DB_PATH = os.path.join(BASE_DIR, "ricettario.db")

# --- FUNZIONE UNIVERSALE PER SALVARE E CONVERTIRE QUALSIASI IMMAGINE (ANCHE JFIF) ---
def save_uploaded_image(immagine_file):
    if immagine_file is not None:
        img_name = immagine_file.name
        if img_name.lower().endswith('.jfif'):
            img_name = os.path.splitext(img_name)[0] + ".jpg"
            
        img_path = os.path.join(MEDIA_DIR, img_name)
        
        try:
            img = Image.open(immagine_file)
            
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")
                
            max_size = (1000, 1000)
            img.thumbnail(max_size)
            
            img.save(img_path, "JPEG", optimize=True, quality=85)
            return f"media_cucina/{img_name}"
        except Exception as e:
            st.error(f"Errore nel caricamento dell'immagine: {e}")
            return ""
    return ""

# --- CONFIGURAZIONE GRAFICA ROSSO TENUE E CALDO ---
def imposta_stile_grafico():
    stile_css = """
    <style>
    /* Sfondo generale carta da cucina rosata tenue */
    .stApp {
        background-color: #FDF6F0 !important;
        background-image: radial-gradient(#EAD5CE 0.75px, transparent 0.75px);
        background-size: 15px 15px;
    }
    
    /* Nasconde la barra laterale di Streamlit */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none;
    }
    
    /* Contenitore principale in rosso cipria tenue (zero bianco freddo) */
    div.block-container {
        background-color: #FDF2F0;
        padding: 35px;
        border-radius: 20px;
        border: 2px solid #D98880;
        margin-top: 20px;
        margin-bottom: 30px;
        box-shadow: 0 12px 30px rgba(192, 57, 43, 0.08);
    }
    
    /* Tipografia elegante per titoli (rosso bordeaux) */
    h1, h2, h3, h4 {
        font-family: 'Georgia', serif !important;
        color: #900C3F !important;
    }

    /* Dimensione testo base leggibile */
    html, body, [class*="st-"] {
        font-size: 1.1rem !important;
        color: #2C3E50 !important;
    }

    /* Immagini ricette con cornice coordinata */
    div[data-testid="stImage"] img {
        max-height: 400px !important;
        width: auto !important;
        max-width: 100% !important;
        object-fit: contain !important;
        border-radius: 12px !important;
        display: block;
        margin-left: auto;
        margin-right: auto;
        background-color: #FDF2F0;
        padding: 8px;
        border: 2px solid #D98880;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    /* Pulsanti rossi/terracotta coordinati */
    .stButton button {
        opacity: 1 !important;
        background-color: #FADBD8 !important;
        color: #900C3F !important;
        border: 2px solid #D98880 !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        width: 100%;
    }
    
    .stButton button:hover {
        background-color: #C0392B !important;
        color: #FFFFFF !important;
        border-color: #C0392B !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(192, 57, 43, 0.2);
    }
    </style>
    """
    st.markdown(stile_css, unsafe_allow_html=True)

imposta_stile_grafico()

# --- FUNZIONE AUSILIARIA PER CONVERTIRE GLI STEMMI IN BASE64 ---
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return ""

stemma_sx_path = os.path.join(BASE_DIR, "stemma_sinistra.png")
stemma_dx_path = os.path.join(BASE_DIR, "stemma_destra.png")

stemma_sx_base64 = get_base64_image(stemma_sx_path)
stemma_dx_base64 = get_base64_image(stemma_dx_path)

if stemma_sx_base64:
    stemma_sx_html = f'<img src="data:image/png;base64,{stemma_sx_base64}" style="height: 60px; width: auto; vertical-align: middle; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">'
else:
    stemma_sx_html = '🛡️'

if stemma_dx_base64:
    stemma_dx_html = f'<img src="data:image/png;base64,{stemma_dx_base64}" style="height: 60px; width: auto; vertical-align: middle; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.15);">'
else:
    stemma_dx_html = '🛡️'

# Intitolazione con i due stemmi indipendenti ai lati
st.markdown(f"""
    <div style="text-align: center; margin-top: 20px; margin-bottom: 5px; display: flex; align-items: center; justify-content: center; flex-wrap: wrap; gap: 20px;">
        {stemma_sx_html}
        <span style="font-family: Georgia, serif; color: #900C3F; font-size: 3rem; font-weight: bold; letter-spacing: 1px;">Il Mio Ricettario di Casa</span>
        {stemma_dx_html}
    </div>
""", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7B7D7D; font-style: italic; font-size: 1.2rem; margin-bottom: 35px;'>I piatti della tradizione e i sapori di una volta, sempre a portata di mano.</p>", unsafe_allow_html=True)

# --- INIZIALIZZAZIONE DATABASE SQLITE ---
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS ricette 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 titolo TEXT, 
                 categoria TEXT, 
                 ingredienti TEXT, 
                 procedimento TEXT, 
                 curiosita TEXT,
                 fonte_url TEXT, 
                 immagine TEXT)''')
    
    c.execute("PRAGMA table_info(ricette)")
    columns = [column[1] for column in c.fetchall()]
    if "curiosita" not in columns:
        c.execute("ALTER TABLE ricette ADD COLUMN curiosita TEXT")

    conn.commit()
    conn.close()

init_db()

# --- GESTIONE STATO SESSIONE (NAVIGAZIONE E LOGIN) ---
if "pagina_corrente" not in st.session_state:
    st.session_state.pagina_corrente = "🏠 Home"

if "autenticato" not in st.session_state:
    st.session_state.autenticato = False

if "mostra_login_inline" not in st.session_state:
    st.session_state.mostra_login_inline = False

# --- GESTIONE VISUALIZZAZIONE SINGOLA RICETTA SELEZIONATA ---
if "ricetta_selezionata" not in st.session_state:
    st.session_state.ricetta_selezionata = None

# --- FUNZIONE GENERICA PER MOSTRARE LE CATEGORIE CON PULSANTI A GRIGLIA PULITI ---
def mostra_categoria(nome_categoria):
    col_titolo, col_home = st.columns([4, 1])
    with col_titolo:
        st.header(f"📖 Raccolta: {nome_categoria}")
    with col_home:
        if st.button("🏠 Torna alla Home", key=f"btn_home_top_{nome_categoria}", use_container_width=True):
            st.session_state.pagina_corrente = "🏠 Home"
            st.session_state.ricetta_selezionata = None
            st.session_state.mostra_login_inline = False
            st.rerun()

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, titolo, ingredienti, procedimento, curiosita, fonte_url, immagine FROM ricette WHERE categoria = ? ORDER BY id DESC", (nome_categoria,))
    ricette = c.fetchall()
    conn.close()

    if ricette:
        if st.session_state.ricetta_selezionata is not None:
            r_selezionata = next((r for r in ricette if r[0] == st.session_state.ricetta_selezionata), None)
            if r_selezionata:
                _, titolo, ingredienti, procedimento, curiosita, fonte_url, img_path = r_selezionata
                
                if st.button("⬅️ Torna alla lista ricette", key="btn_torna_lista"):
                    st.session_state.ricetta_selezionata = None
                    st.rerun()
                
                # TITOLO DELLA RICETTA IN UN ELEGANTE CARTONCINO IN EVIDENZA
                st.markdown(f"""
                    <div style="background-color: #FDF2F0; padding: 25px; border-radius: 16px; border: 2px solid #D98880; text-align: center; margin: 25px 0; box-shadow: 0 4px 12px rgba(192,57,43,0.06);">
                        <span style="font-family: Georgia, serif; color: #900C3F; font-size: 3.2rem; font-weight: bold; letter-spacing: 1px; display: block;">{titolo}</span>
                    </div>
                """, unsafe_allow_html=True)
                
                if img_path:
                    nome_file_img = os.path.basename(img_path)
                    full_img_path = os.path.join(MEDIA_DIR, nome_file_img)
                    if os.path.exists(full_img_path):
                        st.image(full_img_path, use_container_width=True)
                
                st.markdown("### 🛒 Ingredienti")
                st.text(ingredienti)
                
                st.markdown("### 👩‍🍳 Procedimento")
                st.text(procedimento)
                
                if curiosita:
                    st.markdown(f"💡 **Curiosità / Segreto dello Chef:**\n> {curiosita}")
                
                if fonte_url:
                    st.markdown(f"🔗 **Fonte originale:** [{fonte_url}]({fonte_url})")
                
                st.markdown("---")
                if st.button("⬅️ Torna alla lista ricette", key="btn_torna_lista_bottom"):
                    st.session_state.ricetta_selezionata = None
                    st.rerun()
                return

        st.markdown("<p style='color: #7B7D7D; font-style: italic;'>Clicca su una ricetta per leggerla:</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        for i in range(0, len(ricette), 2):
            col_a, col_b = st.columns(2)
            
            item_id_a, titolo_a, _, _, _, _, _ = ricette[i]
            with col_a:
                if st.button(f"📖 {titolo_a}", key=f"btn_ricetta_{item_id_a}", use_container_width=True):
                    st.session_state.ricetta_selezionata = item_id_a
                    st.rerun()
            
            if i + 1 < len(ricette):
                item_id_b, titolo_b, _, _, _, _, _ = ricette[i + 1]
                with col_b:
                    if st.button(f"📖 {titolo_b}", key=f"btn_ricetta_{item_id_b}", use_container_width=True):
                        st.session_state.ricetta_selezionata = item_id_b
                        st.rerun()

        st.markdown("---")
        if st.button("🏠 Torna alla Home", key=f"btn_home_bottom_{nome_categoria}", use_container_width=True):
            st.session_state.pagina_corrente = "🏠 Home"
            st.session_state.ricetta_selezionata = None
            st.session_state.mostra_login_inline = False
            st.rerun()

    else:
        st.info(f"Nessuna ricetta inserita in '{nome_categoria}' al momento.")
        if st.button("🏠 Torna alla Home", key=f"btn_home_empty_{nome_categoria}", use_container_width=True):
            st.session_state.pagina_corrente = "🏠 Home"
            st.session_state.ricetta_selezionata = None
            st.session_state.mostra_login_inline = False
            st.rerun()

# --- GESTIONE PAGINE PRINCIPALI ---
if st.session_state.pagina_corrente == "🏠 Home":
    st.session_state.ricetta_selezionata = None
    
    col_h1, col_h2, col_h3 = st.columns([1, 2, 1])
    with col_h2:
        if not st.session_state.autenticato:
            if not st.session_state.mostra_login_inline:
                if st.button("⚙️ Area Gestione & Inserisci Ricette", use_container_width=True, key="btn_apri_login"):
                    st.session_state.mostra_login_inline = True
                    st.rerun()
            else:
                with st.form("form_login_inline_home"):
                    password_inserita = st.text_input("Password", type="password", key="pwd_inline", label_visibility="collapsed", placeholder="")
                    col_f1, col_f2 = st.columns(2)
                    submit_inline = col_f1.form_submit_button("Accedi", use_container_width=True)
                    chiudi_inline = col_f2.form_submit_button("Chiudi", use_container_width=True)
                    
                    if submit_inline:
                        if password_inserita == st.secrets["password_amministratore"]:
                            st.session_state.autenticato = True
                            st.session_state.mostra_login_inline = False
                            st.success("Accesso effettuato!")
                            st.rerun()
                        else:
                            st.error("Password errata.")
                    if chiudi_inline:
                        st.session_state.mostra_login_inline = False
                        st.rerun()
        else:
            st.markdown(
                """
                <div style="background-color: rgba(230, 248, 230, 0.98); padding: 15px; border-radius: 12px; border: 1px solid #28a745; text-align: center; margin-bottom: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);">
                    <h4 style="margin:0; color: #28a745; font-family: Georgia, serif;">✅ Area Amministrativa Attiva</h4>
                </div>
                """,
                unsafe_allow_html=True
            )
            col_lg1, col_lg2 = st.columns(2)
            if col_lg1.button("➕ Gestisci / Inserisci", use_container_width=True, key="btn_vai_gestione_attiva"):
                st.session_state.pagina_corrente = "⚙️ Gestione Ricette"
                st.rerun()
            if col_lg2.button("🚪 Logout", use_container_width=True, key="btn_logout_home"):
                st.session_state.autenticato = False
                st.session_state.mostra_login_inline = False
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM ricette WHERE categoria = 'Antipasti'")
    res_ant = c.fetchone()
    num_ant = res_ant[0] if res_ant else 0

    c.execute("SELECT COUNT(*) FROM ricette WHERE categoria = 'Primi'")
    res_pri = c.fetchone()
    num_pri = res_pri[0] if res_pri else 0

    c.execute("SELECT COUNT(*) FROM ricette WHERE categoria = 'Secondi'")
    res_sec = c.fetchone()
    num_sec = res_sec[0] if res_sec else 0

    c.execute("SELECT COUNT(*) FROM ricette WHERE categoria = 'Dolci'")
    res_dol = c.fetchone()
    num_dol = res_dol[0] if res_dol else 0

    c.execute("SELECT COUNT(*) FROM ricette WHERE categoria = 'Altro'")
    res_alt = c.fetchone()
    num_alt = res_alt[0] if res_alt else 0

    conn.close()

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f"""
            <div style="border: 2px solid #D98880; background: #FDF2F0; padding: 22px; border-radius: 16px; text-align: center; height: 135px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(192,57,43,0.04);">
                <h4 style="margin:0; color: #900C3F; font-size: 1.15rem; font-family: Georgia, serif;">🥗 Antipasti</h4>
                <p style="font-size: 1.3rem; font-weight: bold; color: #2e7d32; margin: 14px 0 0 0;">{num_ant} inseriti</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("👉 Apri Antipasti", use_container_width=True, key="btn_ant"):
            st.session_state.pagina_corrente = "🥗 Antipasti"
            st.rerun()

    with col2:
        st.markdown(
            f"""
            <div style="border: 2px solid #D98880; background: #FDF2F0; padding: 22px; border-radius: 16px; text-align: center; height: 135px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(192,57,43,0.04);">
                <h4 style="margin:0; color: #900C3F; font-size: 1.15rem; font-family: Georgia, serif;">🍝 Primi</h4>
                <p style="font-size: 1.3rem; font-weight: bold; color: #00838f; margin: 14px 0 0 0;">{num_pri} inseriti</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("👉 Apri Primi", use_container_width=True, key="btn_pri"):
            st.session_state.pagina_corrente = "🍝 Primi"
            st.rerun()

    with col3:
        st.markdown(
            f"""
            <div style="border: 2px solid #D98880; background: #FDF2F0; padding: 22px; border-radius: 16px; text-align: center; height: 135px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(192,57,43,0.04);">
                <h4 style="margin:0; color: #900C3F; font-size: 1.15rem; font-family: Georgia, serif;">🥩 Secondi</h4>
                <p style="font-size: 1.3rem; font-weight: bold; color: #c62828; margin: 14px 0 0 0;">{num_sec} inseriti</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("👉 Apri Secondi", use_container_width=True, key="btn_sec"):
            st.session_state.pagina_corrente = "🥩 Secondi"
            st.rerun()

    with col4:
        st.markdown(
            f"""
            <div style="border: 2px solid #D98880; background: #FDF2F0; padding: 22px; border-radius: 16px; text-align: center; height: 135px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(192,57,43,0.04);">
                <h4 style="margin:0; color: #900C3F; font-size: 1.15rem; font-family: Georgia, serif;">🍰 Dolci</h4>
                <p style="font-size: 1.3rem; font-weight: bold; color: #f57f17; margin: 14px 0 0 0;">{num_dol} inseriti</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("👉 Apri Dolci", use_container_width=True, key="btn_dol"):
            st.session_state.pagina_corrente = "🍰 Dolci"
            st.rerun()

    with col5:
        st.markdown(
            f"""
            <div style="border: 2px solid #D98880; background: #FDF2F0; padding: 22px; border-radius: 16px; text-align: center; height: 135px; margin-bottom: 10px; box-shadow: 0 4px 12px rgba(192,57,43,0.04);">
                <h4 style="margin:0; color: #900C3F; font-size: 1.15rem; font-family: Georgia, serif;">🍹 Altro</h4>
                <p style="font-size: 1.3rem; font-weight: bold; color: #6a1b9a; margin: 14px 0 0 0;">{num_alt} inseriti</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("👉 Apri Altro", use_container_width=True, key="btn_alt"):
            st.session_state.pagina_corrente = "🍹 Altro"
            st.rerun()

    # --- FASCIA DECORATIVA IN BASSO (Rosso terracotta coordinato) ---
    st.markdown("""
        <div style="
            background-color: #FADBD8; 
            padding: 16px; 
            border-radius: 14px; 
            text-align: center; 
            margin-top: 30px; 
            margin-bottom: 20px;
            border: 2px dashed #C0392B;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 22px;
            flex-wrap: wrap;
        ">
            <!-- Posate -->
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#900C3F" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>
            <!-- Cappello Chef -->
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#C0392B" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 13.8a4.5 4.5 0 1 1 2.6-8.3 4.5 4.5 0 0 1 6.8 0 4.5 4.5 0 1 1 2.6 8.3"/><path d="M6 17h12"/><path d="M6 21h12"/></svg>
            <!-- Calice Vino -->
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#78281F" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 22h8"/><path d="M12 15v7"/><path d="M12 15a5 5 0 0 0 5-5V3H7v7a5 5 0 0 0 5 5Z"/></svg>
            <!-- Formaggio -->
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#B7950B" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11 11 3l10 8"/><path d="M3 11v9a1 1 0 0 0 1 1h16a1 1 0 0 0 1-1v-9"/><circle cx="9" cy="15" r="1"/><circle cx="15" cy="16" r="1.5"/></svg>
            <!-- Frutta -->
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1E8449" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20.94c1.5 0 2.75 1.06 4 1.06 3 0 6-8 6-12.22A4.91 4.91 0 0 0 17 5c-2.22 0-4 1.44-5 2-1-.56-2.78-2-5-2a4.91 4.91 0 0 0-5 4.78C2 14 5 22 8 22c1.25 0 2.5-1.06 4-1.06Z"/><path d="M10 2c1 .5 2 2 2 5"/></svg>
            <!-- Pizza -->
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#BA4A00" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 11h.01"/><path d="M11 15h.01"/><path d="M16 16h.01"/><path d="m2 16 20 6-6-20L2 16z"/><path d="M5.71 17.11a17.04 17.04 0 0 1 11.4-11.4"/></svg>
            <!-- Calice Vino -->
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#78281F" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 22h8"/><path d="M12 15v7"/><path d="M12 15a5 5 0 0 0 5-5V3H7v7a5 5 0 0 0 5 5Z"/></svg>
            <!-- Posate -->
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#900C3F" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 2v7c0 1.1.9 2 2 2h4a2 2 0 0 0 2-2V2"/><path d="M7 2v20"/><path d="M21 15V2v0a5 5 0 0 0-5 5v6c0 1.1.9 2 2 2h3Zm0 0v7"/></svg>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.pagina_corrente == "🥗 Antipasti":
    mostra_categoria("Antipasti")

elif st.session_state.pagina_corrente == "🍝 Primi":
    mostra_categoria("Primi")

elif st.session_state.pagina_corrente == "🥩 Secondi":
    mostra_categoria("Secondi")

elif st.session_state.pagina_corrente == "🍰 Dolci":
    mostra_categoria("Dolci")

elif st.session_state.pagina_corrente == "🍹 Altro":
    mostra_categoria("Altro")

elif st.session_state.pagina_corrente == "⚙️ Gestione Ricette":
    col_t, col_h = st.columns([4, 1])
    with col_t:
        st.header("⚙️ Gestione Ricettario e Area Riservata")
    with col_h:
        if st.button("🏠 Torna alla Home", use_container_width=True, key="btn_home_gestione"):
            st.session_state.pagina_corrente = "🏠 Home"
            st.rerun()
    
    if not st.session_state.autenticato:
        st.warning("🔒 Effettua prima l'accesso dalla Home.")
        if st.button("Torna alla Home per accedere", use_container_width=True):
            st.session_state.pagina_corrente = "🏠 Home"
            st.rerun()
    else:
        col_status, col_logout = st.columns([4, 1])
        with col_status:
            st.success("✅ Accesso amministrativo attivo.")
        with col_logout:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.autenticato = False
                st.session_state.pagina_corrente = "🏠 Home"
                st.rerun()
                
        st.markdown("---")
        
        modo_gestione = st.radio("Seleziona operazione:", ["➕ Incolla / Inserisci Nuova Ricetta", "✏️ Modifica o Elimina Esistente"])

        # INSERISCI NUOVA
        if modo_gestione == "➕ Incolla / Inserisci Nuova Ricetta":
            with st.form("form_nuova_ricetta"):
                st.markdown("### 📝 Incolla i dettagli della ricetta")
                titolo = st.text_input("Titolo della Ricetta (es. Liquore al limone, Pesto, ecc.)")
                categoria = st.selectbox("Categoria", ["Antipasti", "Primi", "Secondi", "Dolci", "Altro"])
                
                ingredienti = st.text_area("Incolla qui gli Ingredienti (copiati dal web)")
                procedimento = st.text_area("Incolla qui il Procedimento (copiato dal web)")
                curiosita = st.text_area("Curiosità o Segreto dello Chef (opzionale)")
                
                fonte_url = st.text_input("Link del sito web di origine (opzionale)")
                immagine_file = st.file_uploader("Carica la foto della ricetta", type=["jpg", "jpeg", "png", "webp", "jfif"])
                
                submit = st.form_submit_button("Salva Ricetta nel Database")

                if submit and titolo and ingredienti and procedimento:
                    img_path = save_uploaded_image(immagine_file)
                    conn = get_connection()
                    c = conn.cursor()
                    c.execute("INSERT INTO ricette (titolo, categoria, ingredienti, procedimento, curiosita, fonte_url, immagine) VALUES (?, ?, ?, ?, ?, ?, ?)",
                              (titolo, categoria, ingredienti, procedimento, curiosita, fonte_url, img_path))
                    conn.commit()
                    conn.close()
                    st.success("Ricetta salvata con successo sul tuo ricettario portatile!")

        # MODIFICA O ELIMINA
        elif modo_gestione == "✏️ Modifica o Elimina Esistente":
            cat_mod = st.selectbox("Seleziona categoria da modificare:", ["Antipasti", "Primi", "Secondi", "Dolci", "Altro"])
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT id, titolo, categoria, ingredienti, procedimento, curiosita, fonte_url, immagine FROM ricette WHERE categoria = ?", (cat_mod,))
            elementi = c.fetchall()
            conn.close()

            if elementi:
                mapping = {f"[ID: {elem[0]}] {elem[1]}": elem for elem in elementi}
                scelta_etichetta = st.selectbox("Scegli quale ricetta modificare o eliminare:", list(mapping.keys()))
                item_id, current_title, current_cat, current_ing, current_proc, current_cur, current_url, current_img = mapping[scelta_etichetta]

                with st.form("form_modifica_ricetta"):
                    nuovo_titolo = st.text_input("Modifica Titolo", value=current_title)
                    nuova_categoria = st.selectbox("Modifica Categoria", ["Antipasti", "Primi", "Secondi", "Dolci", "Altro"], index=["Antipasti", "Primi", "Secondi", "Dolci", "Altro"].index(current_cat))
                    nuovi_ingredienti = st.text_area("Modifica Ingredienti", value=current_ing)
                    nuovo_procedimento = st.text_area("Modifica Procedimento", value=current_proc)
                    nuova_curiosita = st.text_area("Modifica Curiosità / Segreto", value=current_cur if current_cur else "")
                    nuovo_url = st.text_input("Link Fonte", value=current_url if current_url else "")
                    
                    if current_img:
                        nome_file_img = os.path.basename(current_img)
                        full_img_path = os.path.join(MEDIA_DIR, nome_file_img)
                        if os.path.exists(full_img_path):
                            st.image(full_img_path, width=150)
                    
                    nuova_immagine_file = st.file_uploader("Sostituisci foto (lascia vuoto per non cambiare)", type=["jpg", "jpeg", "png", "webp", "jfif"])
                    rimuovi_img = st.checkbox("Elimina foto esistente")

                    col1, col2 = st.columns(2)
                    salva_modifiche = col1.form_submit_button("Salva Modifiche")
                    elimina_item = col2.form_submit_button("Elimina Ricetta")

                    conn = get_connection()
                    c = conn.cursor()
                    if salva_modifiche:
                        img_path = current_img
                        if rimuovi_img:
                            img_path = ""
                        elif nuova_immagine_file is not None:
                            img_path = save_uploaded_image(nuova_immagine_file)

                        c.execute("UPDATE ricette SET titolo = ?, categoria = ?, ingredienti = ?, procedimento = ?, curiosita = ?, fonte_url = ?, immagine = ? WHERE id = ?", 
                                  (nuovo_titolo, nuova_categoria, nuovi_ingredienti, nuovo_procedimento, nuova_curiosita, nuovo_url, img_path, item_id))
                        conn.commit()
                        conn.close()
                        st.success("Ricetta aggiornata con successo! Ricarica la pagina.")
                    elif elimina_item:
                        c.execute("DELETE FROM ricette WHERE id = ?", (item_id,))
                        conn.commit()
                        conn.close()
                        st.success("Ricetta eliminata con successo! Ricarica la pagina.")
            else:
                st.info("Nessuna ricetta disponibile in questa categoria per la modifica.")