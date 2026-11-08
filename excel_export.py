"""Genera la nota spese mensile partendo dall'Excel originale (assets/template.xlsx).

Il file originale viene caricato così com'è (logo, font, larghezze, intestazione, blocco finale
con totali/firme) e vengono rigenerate solo le righe dei giorni: una riga per ogni spesa, e una
riga gialla di separazione dopo ogni giorno. Il blocco finale scorre verso il basso in base al
numero di righe.
"""
import copy
import datetime as dt
import io
import os
from collections import OrderedDict

import openpyxl
from openpyxl.styles import Border, Side
from openpyxl.worksheet.properties import PageSetupProperties

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "template.xlsx")

MESI = ["GENNAIO", "FEBBRAIO", "MARZO", "APRILE", "MAGGIO", "GIUGNO", "LUGLIO",
        "AGOSTO", "SETTEMBRE", "OTTOBRE", "NOVEMBRE", "DICEMBRE"]

FIRST_ROW = 11          # prima riga dati nel template
DATA_STYLE_ROW = 13     # riga "pulita" da cui copiare lo stile delle spese
YELLOW_STYLE_ROW = 12   # riga gialla di separazione
FOOTER_FIRST, FOOTER_LAST = 54, 65
LAST_COL = 14           # A..N

THIN = Side(style="thin")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)

MONEY_FIELDS = ["parcheggi", "alloggio", "benzina", "pedaggi", "diaria", "varie"]  # colonne G..L


def nome_file(ym: str) -> str:
    y, m = int(ym[:4]), int(ym[5:7])
    return f"PDS_Nota_spese_{MESI[m - 1]}_{y}.xlsx"


def _num(v):
    try:
        return float(v or 0)
    except (TypeError, ValueError):
        return 0.0


def build_workbook(ym: str, expenses: list, anticipo: float = 0.0) -> bytes:
    y, m = int(ym[:4]), int(ym[5:7])
    wb = openpyxl.load_workbook(TEMPLATE)
    ws = wb.active

    # ---- 1. snapshot degli stili/valori del template -------------------------------------
    data_style = {c: copy.copy(ws.cell(DATA_STYLE_ROW, c)._style) for c in range(1, LAST_COL + 1)}
    yellow_style = {c: copy.copy(ws.cell(YELLOW_STYLE_ROW, c)._style) for c in range(1, LAST_COL + 1)}
    blank_style = copy.copy(ws.cell(1, 1)._style)
    footer = {}
    for r in range(FOOTER_FIRST, FOOTER_LAST + 1):
        for c in range(1, LAST_COL + 1):
            cell = ws.cell(r, c)
            footer[(r, c)] = (cell.value, copy.copy(cell._style))
    footer_heights = {r: ws.row_dimensions[r].height for r in range(FOOTER_FIRST, FOOTER_LAST + 1)}

    # ---- 2. pulizia del corpo e del blocco finale ----------------------------------------
    for rng in list(ws.merged_cells.ranges):
        if rng.min_row >= FIRST_ROW:
            ws.unmerge_cells(str(rng))
    for r in range(FIRST_ROW, FOOTER_LAST + 1):
        for c in range(1, LAST_COL + 1):
            cell = ws.cell(r, c)
            cell.value = None
            cell._style = copy.copy(blank_style)
        if r in ws.row_dimensions:
            ws.row_dimensions[r].height = None

    # ---- 3. intestazione: mese ---------------------------------------------------------
    ws["I2"].value = dt.date(y, m, 1)

    # ---- 4. righe delle spese, raggruppate per giorno -----------------------------------
    by_day = OrderedDict()
    for e in sorted(expenses, key=lambda e: (e["date"], e.get("created_at", ""))):
        by_day.setdefault(e["date"], []).append(e)
    if not by_day:  # mese senza spese: una riga vuota come nel modello
        by_day[f"{ym}-01"] = [None]

    r = FIRST_ROW
    for day, items in by_day.items():
        for e in items:
            for c in range(1, LAST_COL):
                ws.cell(r, c)._style = copy.copy(data_style[c])
                ws.cell(r, c).border = BOX
            if e is not None:
                km = _num(e.get("km"))
                ws.cell(r, 1, dt.date.fromisoformat(day)).number_format = "dd/mm/yyyy"
                ws.cell(r, 2, e.get("luogo") or None)
                ws.cell(r, 3, e.get("descrizione") or None)
                ws.cell(r, 4, km)
                if km != int(km):
                    ws.cell(r, 4).number_format = "#,##0.0"
                ws.cell(r, 5, _num(e.get("rate")))
                for i, f in enumerate(MONEY_FIELDS):
                    ws.cell(r, 7 + i, _num(e.get(f)))
            else:
                ws.cell(r, 5, 0.6107)
                for i in range(len(MONEY_FIELDS)):
                    ws.cell(r, 7 + i, 0)
                ws.cell(r, 4, 0)
            ws.cell(r, 6, f"=+D{r}*E{r}")
            ws.cell(r, 13, f"=SUM(F{r}:L{r})")
            r += 1
        # riga gialla di separazione tra un giorno e il successivo
        for c in range(1, LAST_COL):
            ws.cell(r, c)._style = copy.copy(yellow_style[c])
            ws.cell(r, c).border = BOX
        r += 1
    last_data = r - 1

    # ---- 5. blocco finale (totali, anticipo, firme) spostato sotto le righe -------------
    off = (last_data + 1) - FOOTER_FIRST
    for (fr, c), (val, sty) in footer.items():
        cell = ws.cell(fr + off, c)
        cell._style = copy.copy(sty)
        cell.value = val
    for fr, h in footer_heights.items():
        if h:
            ws.row_dimensions[fr + off].height = h

    tot = 56 + off
    ws.merge_cells(start_row=tot, start_column=1, end_row=tot, end_column=2)
    ws.merge_cells(start_row=62 + off, start_column=11, end_row=62 + off, end_column=12)
    first, last = FIRST_ROW, last_data
    ws.cell(tot, 4).value = f"=SUM(D{first}:D{last})"
    for c, col in zip(range(6, 14), "FGHIJKLM"):
        ws.cell(tot, c).value = f"=SUM({col}{first}:{col}{last})"
    ws.cell(58 + off, 13).value = anticipo if anticipo else None
    # NB: nel file originale M60 era =SUM(F56:M56) e quindi contava due volte i totali
    # (M56 è già la somma di F..L). Qui è corretto: il totale generale è il totale di colonna M.
    ws.cell(60 + off, 13).value = f"=M{tot}"
    ws.cell(62 + off, 13).value = f"=M{60 + off}-M{58 + off}"

    # ---- 6. stampa ----------------------------------------------------------------------
    ws.print_area = f"A1:M{FOOTER_LAST + off}"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr = PageSetupProperties(fitToPage=True)

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()
