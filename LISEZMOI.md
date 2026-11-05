# sprezzature-video

🇫🇷 LISEZMOI.md · [🇬🇧 README.md](https://github.com/warith-harchaoui/sprezzature-video/blob/main/README.md)

Un film sur un projet **affirme** des choses sur ce projet : combien de types
de figures, combien de tests, combien de paquets. Il les cuit dans des pixels,
où plus rien ne les relit jamais. La prose d'un README se relit. Un nombre dans
une image clé, non.

Ce paquet n'est donc pas un moteur de rendu. Son centre est un vérificateur qui
confronte les affirmations d'un film au code qu'elles décrivent, dans les deux
sens. Le rendu reste hors du paquet, parce que l'outil qui saisit les images
est la décision la moins intéressante ici.

Fait partie de la suite [sprezzature](https://sprezzature.ai/).

---

## Comment ça marche

![Schéma de flux. En haut, une spécification de film et le code qu'elle décrit alimentent deux voies. La voie de gauche vérifie les nombres : chaque affirmation déclarée contre l'endroit du code qui la tranche, chaque nombre visible à l'écran contre les déclarations, et la possibilité de refabriquer le film depuis un clone. La voie de droite vérifie le récit : l'ordre de Kawasaki, et la moitié mécanique de la charte d'écriture. Les deux se rejoignent en un seul résultat, les parties d'un film qu'une fonction peut porter, les sous-titres calés sur l'audio mesuré, l'affiche cuite en image zéro, et le niveau sonore égalisé sur toute une série.](https://raw.githubusercontent.com/warith-harchaoui/sprezzature-video/main/assets/comment-ca-marche.svg)

## Pourquoi il existe

Les cinq films servis sur sprezzature.ai annonçaient **« 127 chart kinds »**.
Le catalogue en comptait 167 depuis septembre. Le nombre était cuit dans dix
compositions et cinq MP4 rendus : rien d'autre qu'un remontage ne le
corrigeait, et rien, nulle part, ne le surveillait. C'est tout le sujet de ce
paquet.

## Installation

```bash
pip install sprezzature-video
```

Une seule installation, toutes les surfaces. FastAPI, uvicorn, le serveur MCP,
`sprezzature-audio`, `audio-helper`, `video-helper` et `os-helper`
sont des dépendances de base. Le seul extra est `[dev]`, l'outillage de test
(pytest, ruff, mypy, httpx et httpx2).

Python 3.10 à 3.13. La commande `poster` et le module `post` demandent aussi le
binaire `ffmpeg` dans le `PATH`, tout comme `captions` quand une ligne de
narration désigne un fichier audio plutôt qu'une durée : il le mesure avec
ffprobe.

## Cinq surfaces

Les mêmes fonctions derrière cinq portes.

| Surface | Comment l'atteindre |
|---|---|
| Bibliothèque | `import sprezzature_video` |
| CLI (interface en ligne de commande) | `sprezzature-video` ou `make-film` : deux noms pour un seul groupe Click |
| API HTTP | `uvicorn sprezzature_video.api:app --port 8000` (routes HTTP seulement, pas de `/mcp`), ou `sprezzature-video-mcp`, ou `docker compose up` |
| Serveur MCP (Model Context Protocol) | `sprezzature-video-mcp`, point d'accès `/mcp` sur la même application FastAPI ; la ligne `uvicorn` ci-dessus ne le sert pas |
| Skill | `sprezzature-video/SKILL.md`, rangé dans le dépôt central [sprezzature](https://github.com/warith-harchaoui/sprezzature) |

### Ligne de commande

| Commande | Ce qu'elle fait | Sortie 1 quand |
|---|---|---|
| `verify SPEC [--root DIR]` | Vérifie chaque revendication déclarée contre le code. | une revendication échoue, ou la spécification n'en déclare aucune |
| `scan COMPOSITION [--spec SPEC] [--ignore 2026,...]` | Liste les nombres du texte visible d'une composition HTML qu'aucune revendication n'explique. | un nombre reste inexpliqué |
| `assets SPEC --tree DIR [--repo DIR] [--restore]` | Audite l'arbre d'actifs. `--restore` recopie d'abord les fichiers suivis absents, et rien d'autre. | un actif manque à l'appel |
| `captions SPEC --lang LANG [--out FILE] [--translated]` | Écrit le WebVTT depuis la narration de la spécification. `--translated` omet les balises de voix. | la langue n'est pas dans la spécification |
| `poster VIDEO --out FILE --at SECONDES` | Extrait une image en JPEG par ffmpeg. | |
| `prose FILE [--lang en\|fr] [--strict]` | Confronte chaque ligne d'un fichier texte à la charte d'écriture. | `--strict` et une alerte ferme |
| `pitch SPEC --duration SECONDES [--voice LANG]` | Vérifie les trois temps problème, solution, ingrédient secret. | une alerte |
| `calque SPEC [--from en] [--to fr]` | Signale une coupe en deuxième langue qui se lit comme une traduction de la première. | la coupe est soupçonnée |

La sortie 2 signale un appel faux : un fichier absent, une option obligatoire
manquante, ou, pour `poster`, pas de `ffmpeg` dans le `PATH`. La complétion
du shell et les codes de sortie sont affichés par `sprezzature-video --help`.

### HTTP et MCP

Chaque route déclare un `operation_id`, et ce nom est celui de l'outil MCP.

| Route | Outil MCP | Ce qu'il fait |
|---|---|---|
| `GET /health` | `health` | Sonde de vie : état, nom du service, version. |
| `GET /v1/methods` | `list_methods` | Les cinq façons de lire dans le code la vérité d'une revendication. |
| `POST /v1/scan` | `scan_composition` | Les nombres à l'écran qu'aucune revendication n'explique. Pur : tout est dans la requête. |
| `POST /v1/verify` | `verify_claims` | Les revendications déclarées contre des fichiers sous une racine **sur le serveur**. 400 sur une liste vide. |
| `POST /v1/captions` | `build_captions` | Du WebVTT depuis des lignes de narration. 400 quand une ligne n'a ni audio ni durée. |

L'audit d'actifs, l'affiche, `prose`, `pitch` et `calque` n'ont pas de route.
On les atteint par la CLI ou la bibliothèque.

`sprezzature-video-mcp` écoute sur `127.0.0.1:8000` par défaut. `--host` et
`--port` le changent, comme `SPREZZATURE_VIDEO_HOST` et
`SPREZZATURE_VIDEO_PORT`.

L'image Docker installe ffmpeg et lance `sprezzature-video-mcp` sur
`0.0.0.0:8000` : un seul conteneur sert les routes HTTP et le point d'accès MCP
`/mcp` sur le même port. Le fichier compose monte `./work` sur `/work`, et c'est là que `/v1/verify` doit trouver
le dépôt qu'il vérifie.

## La spécification de film

Un film est un fichier YAML. Chaque section est facultative.

```yaml
name: demo                     # par défaut, le nom du fichier sans extension
claims:                        # ce que le film affirme, et où c'est vérifié
  - text: "167 kinds, every one hand-authored."
    value: 167
    source: {path: sprezzature-figures/sprezzature_figures/catalog/figures.json, method: json_len}
assets:                        # ce dont il est rendu : suivi, dérivé ou unique
  - {rel: figures/sankey.svg, provenance: tracked, source: web/img/figures/sankey.svg}
  - {rel: music/track.mp3, provenance: sole, why: "piste sous licence, une seule copie"}
narration:                     # par langue : début, texte, et audio ou durée
  en:
    - {start: 0.0, text: "A film said 127.", audio: voice/en-01.wav}
scenes:                        # ce que chaque scène met à l'écran, et quand
  - {text: "A film said 127.", start: 0.0}
pitch:                         # nom du temps vers les indices de scène
  problem: [0]
```

La `method` d'une revendication est l'une de `json_len` (longueur d'un tableau
JSON de premier niveau), `json_key_len` (longueur de la valeur sous
`selector`), `regex_count` (correspondances de `selector`, en mode multiligne),
`line_count` (lignes non vides) et `literal` (le fichier contient `selector`
mot pour mot). Un sélecteur `regex_count` qui ne trouve rien est une erreur,
pas un compte de zéro. Un fichier source absent fait échouer la revendication ;
il n'est jamais sauté.

Un actif `sole` sans `why` est refusé au chargement. Un chemin `audio` se
résout depuis le répertoire de la spécification elle-même.

## Ce qu'il y a ici

| Module | Ce qu'il possède |
|---|---|
| `claims` | Une revendication est un couple déclaré : le texte à l'écran, et l'endroit du code qui décide s'il est vrai. `verify_all` vérifie que chaque revendication déclarée tient encore ; `undeclared_numbers` vérifie que chaque nombre *visible* est une revendication déclarée. Le texte de `style`, `script`, `template`, `head`, `title` et `meta` est ignoré. |
| `assets` | Ce film peut-il être rendu à nouveau depuis un clone ? Trois classes : `TRACKED` (copie d'un fichier suivi, **prouvée** égale à sa source par empreinte de contenu), `DERIVED` (sortie d'une recette, affichée et jamais exécutée), `SOLE` (existe à un seul endroit). Une divergence est signalée, jamais réparée en silence. |
| `captions` | Du WebVTT construit à partir du script de narration et de la durée **mesurée** de chaque fichier audio, ni transcrite, ni tapée. Un sous-titre est coupé à 42 caractères autant de fois qu'il le faut. Le fichier est écrit par `video_helper.subtitles`. |
| `post` | `poster` extrait une image. `bake_poster` fait de cette image fixe l'image 0, parce que Slack, X et Discord refabriquent leur vignette depuis la première image, quoi que dise un attribut `poster=`. `normalize_loudness` et `measured_loudness` égalisent une série à -16 LUFS (unités de sonie relatives à la pleine échelle), crête vraie à -1,5 dBTP. |
| `timeline` | `lay_out` place chaque ligne de narration au plus tard entre la scène pour laquelle elle est écrite et la fin de celle qui la précède. Un débordement décale et se signale ; seul un script trop long pour son film est un échec. |
| `pitch` | Vérifie les trois temps d'un pitch, depuis les scènes ou depuis la narration. |
| `calque` | La deuxième langue d'un film a-t-elle été écrite, ou seulement traduite ? Mesuré par la correspondance. |
| `charter` | La moitié mécanique des chartes d'écriture, en anglais et en français. |
| `spec` | Charge la spécification YAML dans un `FilmSpec`. |

### Les deux sens, et pourquoi le second compte

```python
from sprezzature_video import Claim, ClaimSource, verify, undeclared_numbers

claim = Claim(
    text="167 kinds, every one hand-authored.",
    value=167,
    source=ClaimSource(
        path="sprezzature-figures/sprezzature_figures/catalog/figures.json",
        method="json_len",
    ),
)
verify(claim, root).ok  # le code est-il toujours d'accord ?
undeclared_numbers(html, [claim])  # quelque chose d'inexpliqué à l'écran ?
```

Ne vérifier que les revendications déclarées protège les nombres qu'on a pensé
à déclarer. Cela ne protège jamais celui qu'on a tapé dans une image clé à
minuit et laissé vieillir.

## Le film explique-t-il quelque chose ?

Trois vérifications qui n'ont rien à voir avec le rendu, et tout à voir avec
une question : un spectateur qui n'a jamais entendu parler de votre paquet
peut-il dire à quoi il sert ?

### `pitch` : problème, solution, ingrédient secret

L'ordre de Guy KAWASAKI. Dire ce qui ne va pas, puis ce qu'on y fait, puis la
seule chose non évidente qui le rend possible. Le troisième temps est celui
qu'on rate : la magie sous-jacente est une idée, en langage simple, qu'un
concurrent n'a pas. Une liste de fonctionnalités n'en est pas une, une
démonstration non plus.

Les temps sont déclarés dans la spécification par indice de scène, si bien que
la vérification porte sur le film qui existe et non sur une description qui
peut dériver :

```yaml
pitch:
  problem:  [0, 1]
  solution: [2, 3]
  magic:    [4, 5]
```

```bash
sprezzature-video pitch film.yaml --duration 60
# colors: the secret sauce is 5 words ('Ten packages. Five surfaces each.').
# That is a label, not the insight.
# colors: the secret sauce is 4 of its 5 words a feature list (...). Kawasaki's
# warning applies: the underlying magic is the one non-obvious thing that makes
# the solution possible, not an inventory of what ships.
```

Il signale un temps absent, des temps dans le désordre, un problème qui arrive
après les premiers 22 % du film, et un ingrédient secret trop court (moins de
six mots), écrit en verbes de plaquette (`supports`, `propose`), ou fait pour
moitié ou plus d'un inventaire. Savoir si le problème est le *bon* reste une
question humaine.

**`--voice` lit la narration au lieu de l'écran.** Une minute de film met une
phrase par scène sous les yeux et en prononce huit. C'est la voix que le
spectateur reçoit, et un film peut porter les trois temps dans sa liste de
scènes en disant tout autre chose à haute voix.

```bash
sprezzature-video pitch film.yaml --duration 60 --voice fr
```

Une ligne prend le temps de la scène affichée quand elle commence. Une seule
déclaration, pas deux, donc la voix ne peut pas être rangée sous un temps que
l'image dément.

### `calque` : deux langues, ou une seule et son décalque

Un film tourné en deux langues, c'est deux films. La panne est silencieuse :
chaque phrase est correcte, chaque fait est juste, et la seconde coupe sonne
comme une traduction parce qu'elle en est une. Un relecteur qui ouvre le diff
de deux langues voit deux colonnes de mots sans rapport et ne peut rien en
dire.

```bash
sprezzature-video calque film.yaml --from en --to fr
# demo: the fr cut reads as a rendering of the en one (score 0.88, at or above
# 0.75). 7 of 8 positions have the same sentence count and the same numerals
# in the same order: line(s) 1, 2, 3, 4, 5, 6, 8. Two cuts written separately
# distribute their material differently; these do not. Read them side by side
# before shipping both.
```

Le sens n'est jamais inspecté. Ce qui se mesure, c'est la correspondance : une
traduction conserve la forme de ce qu'elle traduit, là où deux scripts écrits
séparément répartissent leur matière autrement. Le seuil de 0,75 a été calibré
des deux côtés : onze coupes traduites connues entre 0,75 et 0,89, les onze
mêmes réécrites entre 0,36 et 0,70. Un soupçon, nommé ligne par ligne, pas un
verdict.

### `prose` : la moitié mécanique des chartes d'écriture

Tirets cadratins et demi-cadratins, une virgule suivie de « and » ou « et »,
les phrases qui s'ouvrent sur une négation, et une liste de tournures
proscrites. Les deux langues, chacune avec sa liste : `mord` ne dit rien au
vérificateur anglais et `truly` ne dit rien au français.

```bash
sprezzature-video prose script.txt --lang fr --strict
```

Les modaux et l'antithèse réflexe sont **comptés, jamais sanctionnés**. Un
compte brut de modaux confond les sens, et « un tiers peut exiger ce contrôle »
garde son modal parce qu'il énonce une opposabilité. Le nombre indique où
relire.

Le jugement reste un jugement. Savoir si une phrase mérite sa place n'est pas
une chose que connaît une expression régulière, et une coche verte qui
tiendrait lieu de lecture serait pire que pas de vérification du tout.

D'autres exécutions, avec leur sortie, sont dans [EXAMPLES.md](EXAMPLES.md).
Le routage des agents est dans [TRIGGERS.md](TRIGGERS.md).

---

## Frontières

Qui possède quoi, entre cette suite et
[ai-helpers](https://deraison.ai/ai-helpers), est écrit dans
[BOUNDARIES.md](BOUNDARIES.md). En bref : **ai-helpers possède la primitive,
sprezzature possède l'opinion.** L'audio de narration est fabriqué par
`sprezzature-audio` ; ce paquet le mesure et ne synthétise rien. Les fichiers
de sous-titres et les primitives ffmpeg viennent de `video-helper`, les durées
d'`audio-helper`. Le rendu est fait par Hyperframes, hors de ce paquet.

## État

Alpha, avant 1.0. Le vérificateur, le registre d'actifs, les sous-titres,
l'après-rendu, le calage sur la grille, les vérifications pitch et calque, la
charte de prose, le chargeur de spécifications YAML et les cinq surfaces sont
écrits et testés. La CI fait tourner ruff, `ruff format --check`,
mypy et pytest sous Python 3.12, et un job plancher qui installe et importe le
paquet sous 3.10.

Il n'y a pas encore de module de rendu. Hyperframes est piloté directement, et
un paquet `renderers/` revient dans le commit qui lui donne un module.

## Licence

BSD-3-Clause.
