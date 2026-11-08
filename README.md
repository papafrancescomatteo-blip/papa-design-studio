# Papa Design Studio · Note spese

Sito privato (Flask + MongoDB) per registrare le spese e ottenere a fine mese l'Excel identico al modello.

## Messa online su Render
1. Carica questa cartella su un repository GitHub.
2. Su Render: **New → Web Service** (oppure Blueprint con `render.yaml`), runtime Python.
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app --workers 1 --threads 4 --timeout 60 --bind 0.0.0.0:$PORT`
3. In **Environment** imposta le variabili di `.env.example`
   (`MONGODB_URI`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `SECRET_KEY`, `CRON_TOKEN`, `SMTP_*`, `MAIL_TO`).
4. MongoDB Atlas: in *Network Access* consenti l'accesso da Render (0.0.0.0/0 va bene sul piano gratuito).
5. Email: con Gmail attiva la verifica in due passaggi e crea una "password per le app" da usare come `SMTP_PASS`.

## Chiusura mese a mezzanotte
Il server controlla ogni 30 secondi; allo scoccare del nuovo mese (ora di Roma) crea la notifica nel sito
e invia l'email con l'Excel. Sul piano gratuito Render il servizio va in pausa: per farlo scattare
puntualmente a mezzanotte crea su https://cron-job.org un job ogni 10 minuti che chiama
`https://TUO-SITO.onrender.com/api/cron/tick?token=IL_TUO_CRON_TOKEN`.
Se il servizio dormiva, la chiusura viene comunque recuperata al primo accesso o al primo ping.

## Modello Excel
`assets/template.xlsx` è il file originale: logo, intestazione e blocco firme vengono da lì.
