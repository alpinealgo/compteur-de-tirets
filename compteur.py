#!/usr/bin/env python3
"""Compte deux fautes dans un document fini : le tiret long (tiret cadratin) et les mots
écrits tout en capitales, sigles mis à part.

Formats : .docx .pptx .xlsx (texte lu dans le fichier) ; .pdf (avec pdftotext) ;
.html .md .txt (texte brut).

Usage :
  python3 compteur.py fichier [fichier...] [--allow SIGLE,SIGLE] [--quiet]

Sortie : une ligne par faute avec le passage autour, puis un total par fichier.
Code de sortie 1 s'il reste au moins une faute : utilisable comme barrière avant d'envoyer.
"""
import re
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path

TIRET_LONG = "\u2014"  # le tiret cadratin, écrit par son code pour que ce fichier ne le contienne pas

# Sigles permis : ils ne comptent pas comme du texte en capitales. Ajoutez les vôtres ici.
SIGLES = {
    # Informatique et IA
    "IA", "LLM", "GPT", "API", "CLI", "MCP", "URL", "HTML", "CSS", "XML", "JSON", "CSV", "TSV",
    "PDF", "SVG", "SQL", "SQLITE", "HTTP", "HTTPS", "DNS", "SSH", "SSL", "TLS", "VPN", "CPU",
    "GPU", "RAM", "SSD", "DOM", "CDN", "SMS", "FAQ", "UTC",
    # Finance et monnaies
    "USD", "EUR", "CHF", "GBP", "JPY", "ETF", "NAV", "DCF", "EBITDA", "EPS", "ISIN", "YTD", "MTD",
    "ESG", "IFRS", "GAAP", "NYSE", "NASDAQ", "SMI", "SPI", "CAC", "DAX", "STOXX",
    # Suisse et France
    "TVA", "PME", "SARL", "RGPD", "LPD", "FINMA", "LSFIN",
    # Divers
    "CO2", "MIT", "III", "VII", "VIII", "XII",
}

# Un mot d'au moins trois signes, tout en capitales.
CAPITALES = re.compile(r"\b[A-ZÀ-ÖØ-Þ][A-ZÀ-ÖØ-Þ0-9''\-]{2,}\b")


def texte_office(chemin: Path, balises) -> str:
    """Texte d'un fichier Word, PowerPoint ou Excel : les nœuds texte du fichier dézippé."""
    morceaux = []
    motif = re.compile(r"<(?:%s)[^>]*>(.*?)</(?:%s)>" % ("|".join(balises), "|".join(balises)), re.S)
    with zipfile.ZipFile(chemin) as z:
        for nom in z.namelist():
            if not nom.endswith(".xml") or not nom.startswith(("word/", "ppt/", "xl/")):
                continue
            brut = z.read(nom).decode("utf-8", "replace")
            for m in motif.finditer(brut):
                bout = re.sub(r"<[^>]+>", "", m.group(1))
                if bout.strip():
                    morceaux.append(bout)
    return "\n".join(morceaux)


def lire(chemin: Path) -> str:
    ext = chemin.suffix.lower()
    if ext in (".docx", ".dotx"):
        return texte_office(chemin, ["w:t"])
    if ext in (".pptx", ".potx"):
        return texte_office(chemin, ["a:t"])
    if ext in (".xlsx", ".xltx", ".xlsm"):
        return texte_office(chemin, ["t"])
    if ext == ".pdf":
        r = subprocess.run(["pdftotext", "-layout", str(chemin), "-"], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("pdftotext a échoué sur %s : %s" % (chemin, r.stderr.strip()))
        return r.stdout
    return chemin.read_text(encoding="utf-8", errors="replace")


def sans_accent(mot: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", mot) if not unicodedata.combining(c))


# Dans une page web, le code (script, style), les commentaires et les balises ne sont pas du
# texte lu : on les vide pour les capitales, en gardant les sauts de ligne et les attributs
# qu'un lecteur voit (alt, title, placeholder, aria-label, content). Le tiret long reste compté partout.
BLOC_CODE = re.compile(r"(<(script|style)\b[^>]*>)(.*?)(</\2\s*>)", re.I | re.S)
COMMENTAIRE = re.compile(r"<!--.*?-->", re.S)
BALISE = re.compile(r"<[!/A-Za-z?][^>]*>", re.S)
ATTRIBUT_VU = re.compile(r"""\b(?:alt|title|placeholder|aria-label|content)\s*=\s*(?:"([^"]*)"|'([^']*)')""", re.I)


def _lignes(s: str) -> str:
    return "\n" * s.count("\n")


def _balise(m) -> str:
    vu = " ".join(a or b for a, b in ATTRIBUT_VU.findall(m.group(0)))
    return " " + vu + " " + _lignes(m.group(0))


def masquer_code(texte: str) -> str:
    texte = BLOC_CODE.sub(lambda m: m.group(1) + _lignes(m.group(3)) + m.group(4), texte)
    texte = COMMENTAIRE.sub(lambda m: _lignes(m.group(0)), texte)
    return BALISE.sub(_balise, texte)


def compter(chemin: Path, permis: set, discret: bool) -> int:
    texte = lire(chemin)
    texte_caps = masquer_code(texte) if chemin.suffix.lower() in (".html", ".htm") else texte
    fautes = []
    for n, (ligne, ligne_caps) in enumerate(zip(texte.splitlines(), texte_caps.splitlines()), 1):
        for _ in range(ligne.count(TIRET_LONG)):
            fautes.append((n, "tiret long", ligne.strip()[:120]))
        for m in CAPITALES.finditer(ligne_caps):
            mot = m.group(0)
            base = sans_accent(mot).replace("-", "").replace("'", "").replace("’", "")
            if base in permis or base.rstrip("S") in permis or base.isdigit():
                continue
            # « L'IA » : un article élidé devant un sigle permis ne fait pas un mot en capitales.
            sigle = sans_accent(mot).replace("’", "'").rsplit("'", 1)[-1].replace("-", "")
            if "'" in mot.replace("’", "'") and (sigle in permis or sigle.rstrip("S") in permis):
                continue
            fautes.append((n, "capitales : %s" % mot, ligne.strip()[:120]))
    if not discret:
        for n, sorte, passage in fautes:
            print("  %s:%d  %s  | %s" % (chemin.name, n, sorte, passage))
    tirets = sum(1 for f in fautes if f[1] == "tiret long")
    print("%-40s %2d tiret(s) long(s), %2d mot(s) en capitales" % (chemin.name, tirets, len(fautes) - tirets))
    return len(fautes)


def main():
    args = sys.argv[1:]
    permis, discret, fichiers = set(SIGLES), False, []
    i = 0
    while i < len(args):
        if args[i] == "--allow" and i + 1 < len(args):
            permis |= {x.strip().upper() for x in args[i + 1].split(",") if x.strip()}
            i += 2
        elif args[i] == "--quiet":
            discret = True
            i += 1
        else:
            fichiers.append(Path(args[i]))
            i += 1
    if not fichiers:
        raise SystemExit(__doc__)
    total = sum(compter(f, permis, discret) for f in fichiers)
    print("Total : %d faute(s)" % total)
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
