"""Contenuti iniziali della home pubblica. Dopo il primo avvio si modificano dall'area riservata (Sito)."""

PRODUCTS = [
    dict(icon="vapore", brand="Albatros · Spilimbergo (PN)", title="Wellness e bagno",
         text="Il lavoro come art director dal 2018, con il sistema brevettato Secret System.",
         items=["Hammam Plus | Home e Contract", "Modula Pool | minipiscina a sfioro", "Modula S e S Combi | saune",
                "Modula F e Wall | vasche", "Ethos | minipiscina e vasca", "Syraka · Graphic · Soreha Wall"],
         url="", urllabel=""),
    dict(icon="acqua", brand="Disenia · IdeaGroup", title="The Wellness Collection",
         text="Un sistema coordinato di minipiscine, vasche e accessori, per interni ed esterni. Tutto made in Italy.",
         items=["Élite: Helba 240, Helba 210, Gilium", "Linos e Kyra | minipiscine",
                "Aretusa · Fonte · Ellisse Plus · Dhelia | vasche", "Solaris · Atollo · Lido | accessori",
                "Libeccio e Grecale | docce outdoor", "Lumina | braciere"],
         url="https://www.cersaie.it/en/3880/disenia/p3411", urllabel="Disenia a Cersaie"),
    dict(icon="ceramica", brand="Azzurra Ceramica · Ege Vitrifiye", title="Sanitari e ceramica",
         text="Linee di sanitari premiate a livello europeo.",
         items=["Class 05 | Azzurra Ceramica", "Finikia | Ege Vitrifiye", "Katamaran | Ege Vitrifiye"], url="", urllabel=""),
    dict(icon="doccia", brand="Ama Luxury Shower · Glass1989", title="Rubinetteria e vasche",
         text="Dettagli in acciaio inox e idromassaggio.",
         items=["Link | miscelatori in acciaio inox", "Eden | vasca angolare idromassaggio"], url="", urllabel=""),
]

NEWS = [
    dict(kind="Rivista", source="Domus", title="The Wellness Collection di Disenia by IdeaGroup", when="Giugno 2026",
         text="Minipiscine, vasche e accessori coordinati, interamente made in Italy: Claudio Papa è il designer che ha costruito la collezione.",
         url="https://www.domusweb.it/it/product-news/gallery/2026/06/18/the-wellness-collection-di-disenia-by-ideagroup.html"),
    dict(kind="Cersaie", source="Cersaie · Bologna", title="Cersaie 2025: nuove finiture per la linea Élite", when="Settembre 2025",
         text="Le minipiscine Élite di Disenia (Helba 240, Helba 210, Gilium) si arricchiscono di nuovi rivestimenti in gres porcellanato.",
         url="https://www.domusweb.it/it/product-news/gallery/2026/06/18/the-wellness-collection-di-disenia-by-ideagroup.html"),
    dict(kind="Rivista", source="Domus", title="Gilium, la minipiscina disegnata per Disenia", when="Settembre 2024",
         text="Servizio di Domus sulla minipiscina Gilium, parte della linea Élite.",
         url="https://domusweb.it/en/product-news/gallery/2024/09/23/gilium-mini-pool-disenia.html"),
    dict(kind="Cersaie", source="Cersaie · Bologna", title="Cersaie 2023: la Wellness Collection di Disenia", when="Settembre 2023",
         text="Presentazione della collezione di minipiscine, vasche e accessori disegnata da Claudio Papa.", url=""),
    dict(kind="Evento", source="Fuorisalone · Milano", title="«I am (k)not ok» alla Design Guide", when="17–23 aprile 2023",
         text="Claudio Papa è nella Design Guide del Fuorisalone con l’evento all’Insula delle Rose, Via Goito 3, Milano.",
         url="https://www.fuorisalone.it/en/designer/1589/Claudio-Papa-designer-ABA-Udine"),
    dict(kind="Cersaie", source="Cersaie · Bologna", title="Cersaie 2019: ADI Ceramics & Bathroom Design Award", when="Settembre 2019",
         text="Premio per l’innovazione al sistema brevettato Secret System, applicato alla vasca Syraka e alla minipiscina Modula Pool (Albatros).",
         url="https://www.area-arch.it/claudio-papa-designer-tre-premi-internazionali/"),
    dict(kind="Rivista", source="Area", title="Claudio Papa designer: tre premi internazionali", when="Novembre 2019",
         text="Il racconto dell’Hammam Plus e del Secret System, i progetti per Albatros che hanno portato i riconoscimenti ADI ed European Product Design Award.",
         url="https://www.area-arch.it/claudio-papa-designer-tre-premi-internazionali/"),
    dict(kind="Rivista", source="Vista Casa", title="La rubrica di design", when="Dal 2013",
         text="Claudio Papa cura una rubrica di design sulla rivista.", url=""),
]

AWARDS = [
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
    ("2003", "Docente di tecnologie sperimentali e progettazione alla Sapienza di Roma."),
    ("2013", "Cura la rubrica di design sulla rivista Vista Casa."),
    ("2015", "Docente di design universale e interior design allo IED di Venezia."),
    ("2016", "Dirige il dipartimento di Progettazione ed Arti applicate dell’Accademia di Belle Arti di Udine e conduce una trasmissione radiofonica sul design."),
    ("2017", "Porta il design italiano in dieci università cinesi."),
    ("2018", "Diventa art director di Albatros, storica azienda wellness di Spilimbergo (PN)."),
    ("2023", "Presenta a Cersaie la Wellness Collection di Disenia."),
]


def seed_docs():
    docs = []
    for i, p in enumerate(PRODUCTS):
        docs.append(dict(type="product", order=i, **p))
    for i, n in enumerate(NEWS):
        docs.append(dict(type="news", order=i, **n))
    for i, (y, t, d) in enumerate(AWARDS):
        docs.append(dict(type="award", order=i, year=y, title=t, detail=d))
    for i, (y, t) in enumerate(TIMELINE):
        docs.append(dict(type="timeline", order=i, year=y, text=t))
    return docs
