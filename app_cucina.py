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

# --- CONFIGURAZIONE GRAFICA CALDA E ACCOGLIENTE (EFFETTO RICETTARIO) ---
def imposta_stile_grafico():
    stile_css = """
    <style>
    /* Sfondo generale del sito color carta pergamena/sabbia calda */
    .stApp {
        background-color: #F4EEDC !important;
    }
    
    /* Nasconde la barra laterale di Streamlit */
    [data-testid="stSidebar"], [data-testid="collapsedControl"] {
        display: none;
    }
    
    /* Contenitore principale con sfondo crema caldo e bordo sfumato */
    div.block-container {
        background-color: #FAF6ED;
        padding: 30px;
        border-radius: 24px;
        border: 3px solid #D9C5A0;
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: 0 10px 25px rgba(140, 74, 25, 0.1);
    }
    
    /* Dimensione testo base leggibile */
    html, body, [class*="st-"] {
        font-size: 1.1rem !important;
        color: #2C3E50 !important;
    }

    /* Sfondo colorato e caldo per i box delle ricette (Expander) */
    div[data-testid="stExpander"] {
        background-color: #FFFDF9 !important;
        border-radius: 14px !important;
        border: 2px solid #D9C5A0 !important;
        margin-bottom: 14px;
        box-shadow: 0 3px 8px rgba(0,0,0,0.03);
    }

    /* TITOLI FISSI E SCURI (Anti Modalità Scura dei cellulari) */
    .streamlit-expanderHeader p, 
    .streamlit-expanderHeader span, 
    div[data-testid="stExpander"] summary p, 
    div[data-testid="stExpander"] summary span {
        font-weight: bold !important;
        font-size: 1.15rem !important;
        color: #8C4A19 !important;
        opacity: 1 !important;
    }

    /* Testo interno alle ricette */
    div[data-testid="stExpander"] p, 
    div[data-testid="stExpander"] li, 
    div[data-testid="stExpander"] div {
        color: #2C3E50 !important;
        line-height: 1.6;
    }

    /* Immagini ricette ben centrate con cornice coordinata */
    div[data-testid="stImage"] img {
        max-height: 380px !important;
        width: auto !important;
        max-width: 100% !important;
        object-fit: contain !important;
        border-radius: 14px !important;
        display: block;
        margin-left: auto;
        margin-right: auto;
        background-color: #FFFDF9;
        padding: 6px;
        border: 2px solid #D9C5A0;
    }

    /* Pulsanti caldi color terracotta chiaro con effetto al passaggio del mouse */
    .stButton button {
        opacity: 1 !important;
        background-color: #F3E5D8 !important;
        color: #8C4A19 !important;
        border: 2px solid #C89F73 !important;
        font-weight: bold !important;
        border-radius: 12px !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease-in-out;
    }
    
    .stButton button:hover {
        background-color: #C05621 !important;
        color: #FFFFFF !important;
        border-color: #C05621 !important;
        transform: translateY(-2px);
    }
    </style>
    """
    st.markdown(stile_css, unsafe_allow_html=True)

imposta_stile_grafico()

# Intitolazione pulita e unica della pagina principale
st.markdown("<h1 style='text-align: center; color: #8C4A19;'>🍳 Il Mio Ricettario di Casa 📖</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #5C6B73; font-style: italic; margin-bottom: 30px;'>I piatti della tradizione e i sapori di una volta, sempre a portata di mano.</p>", unsafe_allow_html=True)

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

# --- FUNZIONE GENERICA PER MOSTRARE LE CATEGORIE CON GRIGLIA A 2 COLONNE ---
def mostra_categoria(nome_categoria):
    col_titolo, col_home = st.columns([4, 1])
    with col_titolo:
        st.header(f"📖 Raccolta: {nome_categoria}")
    with col_home:
        if st.button("🏠 Torna alla Home", key=f"btn_home_top_{nome_categoria}", use_container_width=True):
            st.session_state.pagina_corrente = "🏠 Home"
            st.session_state.mostra_login_inline = False
            st.rerun()

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, titolo, ingredienti, procedimento, curiosita, fonte_url, immagine FROM ricette WHERE categoria = ? ORDER BY id DESC", (nome_categoria,))
    ricette = c.fetchall()
    conn.close()

    if ricette:
        titles = [r[1] for r in ricette]
        scelta_ricetta = st.selectbox(f"Scegli una ricetta specifica in {nome_categoria}:", ["Visualizza Tutti"] + titles, key=f"sb_main_{nome_categoria}")
        
        st.markdown("<br>", unsafe_allow_html=True)

        if scelta_ricetta == "Visualizza Tutti":
            # Ciclo a blocchi di 2 che gestisce perfettamente sia numeri pari che dispari di ricette
            for i in range(0, len(ricette), 2):
                col_a, col_b = st.columns(2)
                
                # Prima ricetta (colonna sinistra)
                item_id_a, titolo_a, ingredienti_a, procedimento_a, curiosita_a, fonte_url_a, img_path_a = ricette[i]
                with col_a:
                    with st.expander(f"{titolo_a}", key=f"exp_{item_id_a}"):
                        if img_path_a:
                            nome_file_a = os.path.basename(img_path_a)
                            full_path_a = os.path.join(MEDIA_DIR, nome_file_a)
                            if os.path.exists(full_path_a):
                                st.image(full_path_a, use_container_width=True)
                        
                        st.markdown("### 🛒 Ingredienti")
                        st.text(ingredienti_a)
                        
                        st.markdown("### 👩‍🍳 Procedimento")
                        st.text(procedimento_a)
                        
                        if curiosita_a:
                            st.markdown(f"💡 **Curiosità / Segreto dello Chef:**\n> {curiosita_a}")
                        
                        if fonte_url_a:
                            st.markdown(f"🔗 **Fonte originale:** [{fonte_url_a}]({fonte_url_a})")
                
                # Seconda ricetta (colonna destra - se esiste un elemento successivo)
                if i + 1 < len(ricette):
                    item_id_b, titolo_b, ingredienti_b, procedimento_b, curiosita_b, fonte_url_b, img_path_b = ricette[i + 1]
                    with col_b:
                        with st.expander(f"{titolo_b}", key=f"exp_{item_id_b}"):
                            if img_path_b:
                                nome_file_b = os.path.basename(img_path_b)
                                full_path_b = os.path.join(MEDIA_DIR, nome_file_b)
                                if os.path.exists(full_path_b):
                                    st.image(full_path_b, use_container_width=True)
                            
                            st.markdown("### 🛒 Ingredienti")
                            st.text(ingredienti_b)
                            
                            st.markdown("### 👩‍🍳 Procedimento")
                            st.text(procedimento_b)
                            
                            if curiosita_b:
                                st.markdown(f"💡 **Curiosità / Segreto dello Chef:**\n> {curiosita_b}")
                            
                            if fonte_url_b:
                                st.markdown(f"🔗 **Fonte originale:** [{fonte_url_b}]({fonte_url_b})")
        else:
            for item_id, titolo, ingredienti, procedimento, curiosita, fonte_url, img_path in ricette:
                if titolo == scelta_ricetta:
                    st.subheader(titolo)
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
        if st.button("🏠 Torna alla Home", key=f"btn_home_bottom_{nome_categoria}", use_container_width=True):
            st.session_state.pagina_corrente = "🏠 Home"
            st.session_state.mostra_login_inline = False
            st.rerun()

    else:
        st.info(f"Nessuna ricetta inserita in '{nome_categoria}' al momento.")
        if st.button("🏠 Torna alla Home", key=f"btn_home_empty_{nome_categoria}", use_container_width=True):
            st.session_state.pagina_corrente = "🏠 Home"
            st.session_state.mostra_login_inline = False
            st.rerun()

# --- GESTIONE PAGINE PRINCIPALI ---
if st.session_state.pagina_corrente == "🏠 Home":
    # --- TASTO / BOX ACCESSO GESTIONE NELLA HOME ---
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
                        if password_inserita == "1234":
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
                <div style="background-color: rgba(230, 248, 230, 0.98); padding: 15px; border-radius: 10px; border: 1px solid #28a745; text-align: center; margin-bottom: 10px;">
                    <h4 style="margin:0; color: #28a745;">✅ Area Amministrativa Attiva</h4>
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
            <div style="border: 2px solid #C89F73; background-color: #FFFDF9; padding: 20px; border-radius: 12px; text-align: center; height: 130px; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
                <h4 style="margin:0; color: #222; font-size: 1.15rem;">🥗 Antipasti</h4>
                <p style="font-size: 1.3rem; font-weight: bold; color: #28a745; margin: 12px 0 0 0;">{num_ant} inseriti</p>
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
            <div style="border: 2px solid #C89F73; background-color: #FFFDF9; padding: 20px; border-radius: 12px; text-align: center; height: 130px; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
                <h4 style="margin:0; color: #222; font-size: 1.15rem;">🍝 Primi</h4>
                <p style="font-size: 1.3rem; font-weight: bold; color: #17a2b8; margin: 12px 0 0 0;">{num_pri} inseriti</p>
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
            <div style="border: 2px solid #C89F73; background-color: #FFFDF9; padding: 20px; border-radius: 12px; text-align: center; height: 130px; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
                <h4 style="margin:0; color: #222; font-size: 1.15rem;">🥩 Secondi</h4>
                <p style="font-size: 1.3rem; font-weight: bold; color: #dc3545; margin: 12px 0 0 0;">{num_sec} inseriti</p>
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
            <div style="border: 2px solid #C89F73; background-color: #FFFDF9; padding: 20px; border-radius: 12px; text-align: center; height: 130px; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
                <h4 style="margin:0; color: #222; font-size: 1.15rem;">🍰 Dolci</h4>
                <p style="font-size: 1.3rem; font-weight: bold; color: #d69e2e; margin: 12px 0 0 0;">{num_dol} inseriti</p>
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
            <div style="border: 2px solid #C89F73; background-color: #FFFDF9; padding: 20px; border-radius: 12px; text-align: center; height: 130px; margin-bottom: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.03);">
                <h4 style="margin:0; color: #222; font-size: 1.15rem;">🍹 Altro</h4>
                <p style="font-size: 1.3rem; font-weight: bold; color: #6f42c1; margin: 12px 0 0 0;">{num_alt} inseriti</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("👉 Apri Altro", use_container_width=True, key="btn_alt"):
            st.session_state.pagina_corrente = "🍹 Altro"
            st.rerun()

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
                                  (nuovo_titolo, nuova_categoria, nuovi_ingredienti, nuovo_procedimento, nueva_curiosita if 'nueva_curiosita' in locals() else nuova_curiosita, nuovo_url, img_path, item_id))
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
