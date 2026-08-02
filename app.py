import streamlit as st
import yfinance as yf
from google import genai

st.set_page_config(page_title="Investiční Analytik", page_icon="📈")
st.title("📈 Osobní investiční asistent")

try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except:
    st.error("API klíč nebyl nalezen v Secrets.")
    st.stop()

ticker = st.sidebar.text_input("Zadej Ticker (např. MSFT)", value="MSFT").upper()
period = st.sidebar.selectbox("Období", ["1mo", "3mo", "6mo", "1y"])

def analyzuj_akcii(ticker_symbol, period):
    t = yf.Ticker(ticker_symbol)
    hist = t.history(period=period)
    if hist.empty: return "Data nebyla nalezena."
    data_summary = hist[['Close', 'Volume']].tail(10).to_string()
    prompt = f"Analyzuj akcii {ticker_symbol} za {period}. Data: {data_summary}. Co si o tom myslíš?"
    response = client.models.generate_content(model="gemini-3.5-flash", contents=prompt)
    return response.text

if st.button("Analyzovat"):
    with st.spinner('Analyzuji data a trh...'):
        vysledek = analyzuj_akcii(ticker, period)
        st.subheader(f"Analýza pro {ticker}")
        st.write(vysledek)

# --- ČÁST PRO CHAT ---

# 1. Inicializace historie zpráv (aby se po každém kliku nesmazala)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Zobrazení dosavadní historie zpráv
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Vstupní řádek pro chat
if prompt := st.chat_input("Chceš se na něco zeptat k této akcii?"):
    # Zobrazíme zprávu uživatele
    with st.chat_message("user"):
        st.markdown(prompt)
    # Uložíme zprávu do historie
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Odpověď od modelu (tady voláš své Gemini)
    # Předpokládám, že máš 'client' vytvořený někde výše v kódu
    response = client.models.generate_content(
        model="gemini-1.5-flash", 
        contents=prompt
    )
    
    # Zobrazení odpovědi
    with st.chat_message("assistant"):
        st.markdown(response.text)
    # Uložení odpovědi do historie
    st.session_state.messages.append({"role": "assistant", "content": response.text})
