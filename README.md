# Le compteur de tirets longs : fini les textes qui sonnent IA

Votre IA glisse des tirets longs partout et écrit des titres en capitales ? Ce petit programme relit vos documents finis et compte ces deux fautes, avant que vous les envoyiez. Word, PDF, Excel, PowerPoint, pages web, texte : il lit tout.

Je l'ai écrit parce que ma consigne à l'IA interdisait le tiret long, et qu'il est sorti quand même dans un document. Ce programme tourne depuis sur chaque document que Claude me livre. Toute l'histoire : [Ma consigne interdisait le tiret long. Il est sorti quand même](https://alpinealgo.ch/articles/ecrire-sans-sonner-ia.html).

## En une ligne

```bash
python3 compteur.py mon-document.docx
```

Il rend une ligne par faute, avec le passage autour, puis un total par fichier (passages coupés ici) :

```
texte-d-essai.md:5  tiret long  | Le rapport du trimestre (...)
texte-d-essai.md:7  tiret long  | Le RÉSUMÉ suit (...)
texte-d-essai.md:7  capitales : RÉSUMÉ  | Le RÉSUMÉ suit (...)
texte-d-essai.md     2 tiret(s) long(s),  1 mot(s) en capitales
Total : 3 faute(s)
```

S'il reste une seule faute, il se termine en échec (code de sortie 1). Du coup, on peut s'en servir comme barrière avant d'envoyer un document, à la main ou dans un programme.

## Ce qu'il lit

Word (.docx), PowerPoint (.pptx), Excel (.xlsx), PDF, pages web (.html), Markdown et texte brut. Il faut Python 3, et pour les PDF, `pdftotext` (paquet poppler).

## Un sigle signalé à tort

C'est presque toujours un sigle qu'il ne connaît pas. Pour une fois, ajoutez-le avec `--allow` :

```bash
python3 compteur.py rapport.pdf --allow ZKB,SIX
```

Pour de bon, ajoutez-le à la liste des sigles, au début du programme. Ne coupez jamais le contrôle pour faire passer un fichier.

## Un essai avant de lui faire confiance

`exemple/texte-d-essai.md` contient exprès deux tirets longs et un mot en capitales. Le programme doit trouver trois fautes :

```bash
python3 compteur.py exemple/texte-d-essai.md
```

## Licence

MIT : vous pouvez le reprendre, le modifier et le partager, en gardant la mention de licence.
