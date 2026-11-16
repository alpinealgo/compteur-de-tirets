# Le compteur de tirets longs

Un petit programme qui relit un document fini et compte deux fautes : le tiret long (le tiret cadratin, ce trait qu'on glisse au milieu d'une phrase) et les mots écrits tout en capitales, sigles mis à part.

Je l'ai fait parce que ma consigne à l'IA interdisait le tiret long, et qu'il est sorti quand même dans un document. Toute l'histoire est dans l'article [Ma consigne interdisait le tiret long. Il est sorti quand même](https://alpinealgo.ch/articles/ecrire-sans-sonner-ia.html).

## Ce qu'il lit

Word (.docx), PowerPoint (.pptx), Excel (.xlsx), PDF, pages web (.html), Markdown et texte brut.

## Comment le lancer

Il faut Python 3. Pour les PDF, il faut aussi `pdftotext`, qui vient avec le paquet poppler.

```bash
python3 compteur.py mon-document.docx
```

Il rend une ligne par faute, avec le passage autour, puis un total par fichier. S'il reste une seule faute, il se termine en échec (code de sortie 1) : du coup, on peut s'en servir comme barrière avant d'envoyer un document.

## Un sigle signalé à tort

C'est presque toujours un sigle qu'il ne connaît pas. Pour une fois, ajoutez-le avec `--allow` :

```bash
python3 compteur.py rapport.pdf --allow ZKB,SIX
```

Pour de bon, ajoutez-le à la liste des sigles, au début du programme. Ne coupez jamais le contrôle pour faire passer un fichier.

## Un essai

`exemple/texte-d-essai.md` contient deux tirets longs et un mot en capitales. Le programme doit trouver trois fautes, et ce fichier échoue exprès.

```bash
python3 compteur.py exemple/texte-d-essai.md
```

## Licence

MIT : vous pouvez le reprendre, le modifier et le partager, en gardant la mention de licence.
