"""Contenuti iniziali del sito pubblico. Dopo il primo avvio si modificano dall'area riservata (Sito).

Fonti: Archiproducts (elenco prodotti), Domus, Disenia, Albatros, Matrix4design, Messaggero Veneto,
IlBagnoNews, Area, Fuorisalone, European Product Design Award.
"""
SEED_VERSION = 2

# (nome, azienda, categoria, descrizione)
D, AMA, GL, AL = "Disenia (IdeaGroup)", "Ama Luxury Shower", "Glass1989", "Albatros"
AZ, EG = "Azzurra Ceramica", "Ege Vitrifiye"
MP, VA, DO, SA, SN, AC = ("Minipiscine", "Vasche", "Docce e rubinetteria", "Saune e bagno turco",
                          "Sanitari", "Accessori e complementi")

CATALOG = [
    # --- Disenia · The Wellness Collection ---
    ("Aretusa", D, VA, "Vasca idromassaggio in Aquatek, con sistemi Airpool e Whirlpool e corona luminosa. Centro stanza o a parete. ADI Design Award 2024."),
    ("Domina", D, VA, "Vasca ovale centro stanza."),
    ("Fonte", D, VA, "Vasca wellness per interni, parte di The Wellness Collection."),
    ("Ellisse Plus", D, VA, "Vasca wellness per interni, parte di The Wellness Collection."),
    ("Dhelia", D, VA, "Vasca wellness per interni, parte di The Wellness Collection."),
    ("Helba 240 · fuori terra", D, MP, "Minipiscina rettangolare fuori terra, 4/5 posti. Linea Élite."),
    ("Helba 240 · da incasso", D, MP, "Minipiscina rettangolare da incasso, 4/5 posti. Linea Élite."),
    ("Helba 210 · fuori terra", D, MP, "Minipiscina rettangolare fuori terra, 3 posti. Linea Élite."),
    ("Helba 210 · da incasso", D, MP, "Minipiscina rettangolare da incasso, 3 posti. Linea Élite."),
    ("Gilium · fuori terra", D, MP, "Minipiscina quadrata fuori terra, 4 posti. Linea Élite."),
    ("Gilium · da incasso", D, MP, "Minipiscina quadrata da incasso, 4 posti. Linea Élite."),
    ("Linos", D, MP, "Minipiscina compatta per 2 o 4 persone, freestanding o da incasso, per interni ed esterni."),
    ("Kyra", D, MP, "Minipiscina compatta per 2 o 4 persone, freestanding o da incasso, per interni ed esterni."),
    ("Libeccio", D, DO, "Colonna doccia in acciaio inox 316. Premiata nel 2023."),
    ("Grecale", D, DO, "Colonna doccia in acciaio inox 316."),
    ("Baia", D, DO, "Piatto doccia in Aquatek."),
    ("Lumina", D, AC, "Braciere a legna o bioetanolo, per interni ed esterni."),
    ("Solaris", D, AC, "Lettino da giardino."),
    ("Atollo", D, AC, "Servomuto in metallo."),
    ("Lido", D, AC, "Servomuto in metallo."),
    ("Artico", D, AC, "Secchiello per ghiaccio."),
    ("Duna", D, AC, "Scaletta per piscina."),
    ("Riviera", D, AC, "Scaletta per piscina."),
    ("Porta asciugamani a barra", D, AC, "In metallo verniciato."),
    ("Vano portaoggetti", D, AC, "In metallo verniciato."),
    # --- Albatros ---
    ("Hammam Plus Home", AL, SA, "Bagno turco per la casa, con aromaterapia. ADI Design Index e European Product Design Award."),
    ("Hammam Plus Contract", AL, SA, "Bagno turco per hotel e centri benessere, con cromoterapia."),
    ("Modula S", AL, SA, "Sauna finlandese."),
    ("Modula S Combi", AL, SA, "Sauna finlandese con doccia."),
    ("Modula Pool", AL, MP, "Minipiscina a sfioro in Solid Surface, 4 posti, con Secret System. ADI Design Award 2019."),
    ("Ethos", AL, MP, "Minipiscina quadrata a 5 posti con cromoterapia."),
    ("Syraka", AL, VA, "Vasca o minipiscina centro stanza in Solid Surface, con mensola integrata e Secret System: nessun getto a vista."),
    ("Modula F", AL, VA, "Vasca con vani contenitori."),
    ("Modula F Combi", AL, VA, "Vasca centro stanza con seduta rettangolare."),
    ("Modula Wall", AL, VA, "Vasca in resina con cesto estraibile."),
    ("Soreha Wall", AL, VA, "Vasca rettangolare in resina."),
    ("Ethos Wall", AL, VA, "Vasca angolare ovale."),
    ("Graphic", AL, DO, "Colonna doccia con getti laterali e soffione."),
    # --- altri marchi ---
    ("Eden", GL, VA, "Vasca angolare con idromassaggio."),
    ("Link · lavabo", AMA, DO, "Miscelatore monocomando per lavabo in acciaio inox."),
    ("Link · doccia", AMA, DO, "Miscelatore per doccia in acciaio inox."),
    ("Class 05", AZ, SN, "Linea di sanitari. Best Bathroom Design 2006 e 2007."),
    ("Finikia", EG, SN, "Linea di sanitari. European Product Design Award."),
    ("Katamaran", EG, SN, "Linea di sanitari. European Product Design Award, argento 2018."),
]

BRAND_INFO = {
    AL: "Storica azienda wellness di Spilimbergo (PN). Claudio Papa collabora con Albatros dal 2000 e ne è art director dal 2018. Qui nasce il sistema brevettato Secret System.",
    D: "Marchio di IdeaGroup. The Wellness Collection, presentata a Cersaie 2023, è un sistema coordinato di minipiscine, vasche e accessori per interni ed esterni, interamente made in Italy.",
    AMA: "Rubinetteria e docce in acciaio inox.",
    GL: "Vasche e docce.",
    AZ: "Sanitari in ceramica.",
    EG: "Sanitari in ceramica (Turchia).",
}

NEWS = [
    dict(kind="Web", source="Matrix4design", title="Claudio Papa conquista l’ADI Ceramics & Bathroom Design Award 2024 con la vasca Aretusa", when="24 ottobre 2024",
         text="Il premio, categoria Arredo Bagno, è il secondo consecutivo con Disenia dopo quello del 2023 per la colonna doccia Libeccio.",
         url="https://www.matrix4design.com/it/design/claudio-papa-conquista-ladi-ceramics-bathroom-design-award-2024-con-la-vasca-idromassaggio-aretusa-di-disenia/"),
    dict(kind="Rivista", source="Domus", title="The Wellness Collection di Disenia by IdeaGroup", when="Giugno 2026",
         text="Minipiscine, vasche e accessori coordinati, interamente made in Italy: Claudio Papa è il designer che ha costruito la collezione.",
         url="https://www.domusweb.it/it/product-news/gallery/2026/06/18/the-wellness-collection-di-disenia-by-ideagroup.html"),
    dict(kind="Cersaie", source="Cersaie · Bologna", title="Cersaie 2025: nuove finiture per la linea Élite", when="Settembre 2025",
         text="Le minipiscine Élite di Disenia (Helba 240, Helba 210, Gilium) si arricchiscono di nuovi rivestimenti in gres porcellanato.",
         url="https://www.domusweb.it/it/product-news/gallery/2026/06/18/the-wellness-collection-di-disenia-by-ideagroup.html"),
    dict(kind="Cersaie", source="Cersaie · Bologna", title="Cersaie 2024: premio ADI alla vasca Aretusa", when="Settembre 2024",
         text="Al Cersaie l’ADI Ceramics & Bathroom Design Award 2024 va ad Aretusa, la vasca idromassaggio di The Wellness Collection.",
         url="https://www.matrix4design.com/it/design/claudio-papa-conquista-ladi-ceramics-bathroom-design-award-2024-con-la-vasca-idromassaggio-aretusa-di-disenia/"),
    dict(kind="Rivista", source="Domus", title="Gilium, la minipiscina disegnata per Disenia", when="Settembre 2024",
         text="Servizio di Domus sulla minipiscina Gilium, parte della linea Élite.",
         url="https://domusweb.it/en/product-news/gallery/2024/09/23/gilium-mini-pool-disenia.html"),
    dict(kind="Cersaie", source="Cersaie · Bologna", title="Cersaie 2023: nasce The Wellness Collection di Disenia", when="Settembre 2023",
         text="Prima presentazione della collezione di minipiscine, vasche e accessori disegnata da Claudio Papa. Nel 2023 premiata anche la colonna doccia Libeccio.", url=""),
    dict(kind="Evento", source="Fuorisalone · Milano", title="«I am (k)not ok» nella Design Guide del Fuorisalone", when="17–23 aprile 2023",
         text="Evento all’Insula delle Rose, Via Goito 3, Milano.",
         url="https://www.fuorisalone.it/en/designer/1589/Claudio-Papa-designer-ABA-Udine"),
    dict(kind="Web", source="IlBagnoNews", title="Syraka by Albatros, puro design per vasca o mini pool", when="10 marzo 2020",
         text="La forma tondeggiante, la mensola integrata e il Secret System che nasconde i getti idromassaggio.",
         url="https://www.ilbagnonews.it/syraka-albatros/"),
    dict(kind="Web", source="Albatros Wellness", title="Syraka selezionata per l’ADI Design Index 2020", when="2020",
         text="La vasca Syraka entra nella selezione ADI Design Index 2020.",
         url="https://albatroswellness.it/news-eventi/syraka-adi-design-index-2020/"),
    dict(kind="Stampa", source="Messaggero Veneto", title="Il progetto innovativo di Albatros premiato al Cersaie di Bologna", when="27 settembre 2019",
         text="L’ADI Ceramics & Bathroom Design Award, per innovazione e miglior progetto, va al Secret System usato in Syraka e Modula Pool.",
         url="https://www.messaggeroveneto.it/cronaca/il-progetto-innovativo-di-albatros-premiato-al-cersaie-di-bologna-ha0k85a9"),
    dict(kind="Rivista", source="Area", title="Claudio Papa designer: tre premi internazionali", when="Novembre 2019",
         text="Il racconto dell’Hammam Plus e del Secret System, i progetti per Albatros che hanno portato i riconoscimenti ADI ed European Product Design Award.",
         url="https://www.area-arch.it/claudio-papa-designer-tre-premi-internazionali/"),
    dict(kind="Rivista", source="Vista Casa", title="La rubrica di design", when="Dal 2013",
         text="Claudio Papa cura una rubrica di design sulla rivista.", url=""),
]

AWARDS = [
    ("2024", "ADI Ceramics & Bathroom Design Award, Arredo Bagno", "Vasca idromassaggio Aretusa (Disenia) · Cersaie"),
    ("2023", "Premio ADI Ceramics & Bathroom Design", "Colonna doccia Libeccio (Disenia)"),
    ("2020 · 2022", "Finalista Compasso d’Oro ADI", "Il più autorevole premio italiano di design"),
    ("2019", "ADI Ceramics & Bathroom Design Award, innovazione", "Secret System · Syraka e Modula Pool (Albatros) · Cersaie"),
    ("2019", "European Product Design Award", "Home Interiors Product · Hammam Plus (Albatros)"),
    ("2018", "ADI Ceramics & Bathroom Design Award", "Hammam Plus (Albatros) · poi selezionato per l’ADI Design Index 2019"),
    ("2017 · 2018", "European Product Design Award", "Finikia e Katamaran (Ege Vitrifiye)"),
    ("2006 · 2007", "Best Bathroom Design", "Class 05 (Azzurra Ceramica)"),
]

TIMELINE = [
    ("1964", "Nasce a Catania."),
    ("1990", "Si diploma in Industrial Design all’I.S.I.A. di Roma; la tesi, uno scooter, nasce in collaborazione con Piaggio."),
    ("Anni ’90", "Due anni al Centro Stile Piaggio Veicoli Europei. Parallelamente i primi progetti per arredo d’interni e arredo bagno; circa otto anni al fianco di Carlo Urbinati per Jacuzzi."),
    ("2000", "Inizia la collaborazione con Albatros."),
    ("2003", "Docente di tecnologie sperimentali e progettazione alla Sapienza di Roma."),
    ("2013", "Cura la rubrica di design sulla rivista Vista Casa."),
    ("2015", "Docente di design universale e interior design allo IED di Venezia."),
    ("2016", "Dirige il dipartimento di Progettazione ed Arti applicate dell’Accademia di Belle Arti di Udine e conduce una trasmissione radiofonica sul design."),
    ("2017", "Porta il design italiano in dieci università cinesi."),
    ("2018", "Diventa art director di Albatros."),
    ("2023", "Presenta a Cersaie The Wellness Collection di Disenia."),
    ("2024", "Secondo ADI Ceramics & Bathroom Design Award consecutivo con Disenia, per la vasca Aretusa."),
]


def seed_docs(only=None):
    docs = []
    if only in (None, "catalog"):
        for i, (n, b, c, t) in enumerate(CATALOG):
            docs.append(dict(type="catalog", order=i, title=n, brand=b, category=c, text=t, url=""))
    if only in (None, "news"):
        for i, n in enumerate(NEWS):
            docs.append(dict(type="news", order=i, **n))
    if only in (None, "award"):
        for i, (y, t, d) in enumerate(AWARDS):
            docs.append(dict(type="award", order=i, year=y, title=t, detail=d))
    if only in (None, "timeline"):
        for i, (y, t) in enumerate(TIMELINE):
            docs.append(dict(type="timeline", order=i, year=y, text=t))
    return docs
