import streamlit as st
from deta import Deta
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

st.title("TRACCIATORE DI SPESE 2023")
categorie = ["Spesa", "Libri", "Salute", "Ristorazione", "Intrattenimento",
            "Animali", "Scuola", "Oggetti", "Gas", "Luce", "Internet",
            "Casa", "Tecnologia", "Trasporti", "Vacanze", "Abbigliamento",
            "Regali", "Bimbi", "Tasse", "Altro"     
            ]

now = datetime.now()

# Connessione al database tramite la Project Key di Deta
deta = Deta(st.secrets["deta_key"])

# Crea il database
db = deta.Base("spese-db")

@st.cache(suppress_st_warning=True)
def expenses():
    with st.form('form'):
        importo = st.number_input('Importo: ', value=0, step=10)
        categoria = st.selectbox('Categoria: ', categorie)
        descrizione = st.text_input('Descrizione: ')
        timestamp = now.strftime('%Y-%m-%d')
        submitted = st.form_submit_button('INVIA')

    if submitted:
        db.put({"importo": importo, "categoria": categoria, "descrizione": descrizione,
                "timestamp": timestamp})

    db_content = db.fetch().items

    df = pd.DataFrame(db_content)
    st.write("Ultimi record: ", df.tail())

    # Converti il campo timestamp in un oggetto datatime di pandas
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Filtra i record del 2023
    df_2023 = df[df["timestamp"].dt.year == 2023]

    # Raggruppa i dati per mese e somma le spese per ogni mese
    spese_mensili = df_2023.groupby(df_2023.timestamp.dt.month)['importo'].sum()

    # Raggruppa le spese per categoria
    spese_categoria = df_2023.groupby("categoria")["importo"].sum()

    # Crea due subplot per poter visualizzare due grafici diversi e ovviare alla deprecazione di st.pyplot()
    fig, axs = plt.subplots(2,1)
    plt.subplots_adjust(hspace=0.5)

    # Plotta il grafico delle spese suddivise per mese
    axs[0].bar(spese_mensili.index, spese_mensili.values)
    axs[0].set_xticks(spese_mensili.index)
    axs[0].set_ylabel("Importo")
    axs[0].set_title("Spese suddivise per mese")

    # Plotta il grafico delle spese suddivise per categoria
    axs[1].bar(spese_categoria.index, spese_categoria.values)
    axs[1].set_xticks(spese_categoria.index)
    axs[1].set_ylabel("Importo")
    axs[1].set_title("Spese suddivise per categoria")

    st.pyplot(fig)

    # Creare un bottone per effettuare il download di un file csv dell'intero db
    # Crea il csv a partire dal dataframe
    csv = df.to_csv(index=False).encode('utf-8')

    # Crea un bottone per scaricare il file csv
    st.download_button(
        "Clicca per scaricare il file csv",
        csv,
        "spese.csv",
        "text/csv",
        key='download-csv'
    )
    # Cliccando il bottone, scrive un file csv all'interno del browser




# Esempio di cancellazione di record che contengono la parola "prova" nella descrizione
# for entry in db_content:
#     if "Prova" in entry["descrizione"]:
#         db.delete(entry["key"])


expenses()

