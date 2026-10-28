# sprezzature-video

🇫🇷 LISEZMOI.md · [🇬🇧 README.md](https://github.com/warith-harchaoui/sprezzature-video/blob/main/README.md)

Un film sur un projet **affirme** des choses sur ce projet — combien de types
de figures, combien de tests, combien de paquets — et les cuit dans des pixels,
où plus rien ne les relit jamais. La prose d'un README se relit. Un nombre dans
une image clé, non.

Ce paquet n'est donc pas un moteur de rendu. Son centre est un vérificateur qui
confronte les affirmations d'un film au code qu'elles décrivent, dans les deux
sens, et le moteur de rendu reste derrière une couture parce que l'outil qui
saisit les images est la décision la moins intéressante ici.

Fait partie de la suite [sprezzature](https://sprezzature.ai/).

---

## Comment ça marche

![Schéma de flux. En haut, une spécification de film et le code qu'elle décrit alimentent deux voies. La voie de gauche vérifie les nombres : chaque affirmation déclarée contre l'endroit du code qui la tranche, chaque nombre visible à l'écran contre les déclarations, et la possibilité de refabriquer le film depuis un clone. La voie de droite vérifie le récit : l'ordre de Kawasaki, et la moitié mécanique de la charte d'écriture. Les deux se rejoignent en un seul résultat, les parties d'un film qu'une fonction peut porter, les sous-titres calés sur l'audio mesuré, l'affiche cuite en image zéro, et le niveau sonore égalisé sur toute une série.](https://raw.githubusercontent.com/warith-harchaoui/sprezzature-video/main/assets/comment-ca-marche.svg)

## Pourquoi il existe

Les cinq films servis sur sprezzature.ai annonçaient **« 127 chart kinds »**.
Le catalogue en comptait 167 depuis septembre. Le nombre était cuit dans dix
compositions et cinq MP4 rendus : rien d'autre qu'un remontage ne le corrigeait
— et rien, nulle part, ne le surveillait. C'est tout le sujet de ce paquet.

## Ce qu'il y a ici

| Module | Ce qu'il possède |
|---|---|
| `claims` | Une revendication est un couple déclaré : le texte à l'écran, et l'endroit du code qui décide s'il est vrai. `verify_all` vérifie que chaque revendication déclarée tient encore ; `undeclared_numbers` vérifie que chaque nombre *visible* est une revendication déclarée. |
| `assets` | Ce film peut-il être rendu à nouveau depuis un clone ? Trois classes : `TRACKED` (copie d'un fichier suivi, **prouvée** égale à sa source), `DERIVED` (sortie d'un outil encore présent), `SOLE` (existe à un seul endroit). Une divergence est signalée, jamais réparée en silence. |
| `captions` | Du WebVTT construit à partir du script de narration et de la durée **mesurée** de chaque fichier audio — ni transcrite, ni tapée. |
| `post` | L'affiche cuite en image 0, parce que Slack, X et Discord refabriquent leur vignette côté serveur depuis la première image, quoi que dise un attribut `poster=`. Plus la normalisation de loudness sur une série. |
| `timeline` | Le moment où chaque ligne de narration tombe, une fois le moteur passé. Une ligne démarre au plus tard entre la scène pour laquelle elle est écrite et la fin de celle qui la précède. Un débordement décale et se signale ; seul un script trop long pour son film est un échec. |
| `calque` | La deuxième langue d'un film a-t-elle été écrite, ou seulement traduite ? Jamais le sens — la **correspondance** : la part des positions où les deux coupes portent le même nombre de phrases et les mêmes chiffres dans le même ordre. |

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
à déclarer — jamais celui qu'on a tapé dans une image clé à minuit et laissé
vieillir.

### Le pitch se lit aussi dans la voix

Une minute de film met une phrase par scène sous les yeux et en prononce huit.
C'est la voix que le spectateur reçoit, et un film peut porter les trois temps
de KAWASAKI dans sa liste de scènes en disant tout autre chose à haute voix.

```bash
sprezzature-video pitch film.yaml --duration 60 --voice fr
```

Une ligne prend le temps de la scène affichée quand elle commence : une seule
déclaration, pas deux, donc la voix ne peut pas être rangée sous un temps que
l'image dément.

### Deux langues, ou une seule et son décalque

Un film tourné en deux langues, c'est deux films. La panne est silencieuse :
chaque phrase est correcte, chaque fait est juste, et la seconde coupe sonne
comme une traduction parce qu'elle en est une. Un relecteur qui ouvre le diff
de deux langues voit deux colonnes de mots sans rapport et ne peut rien en
dire.

```bash
sprezzature-video calque film.yaml --from en --to fr
```

Le sens n'est jamais inspecté. Ce qui se mesure, c'est la correspondance : une
traduction conserve la forme de ce qu'elle traduit, là où deux scripts écrits
séparément répartissent leur matière autrement. Le seuil a été calibré des
deux côtés — onze coupes traduites connues entre 0,75 et 0,89, les onze mêmes
réécrites entre 0,36 et 0,70. Un soupçon, nommé ligne par ligne, pas un verdict.

## Installation

```bash
pip install sprezzature-video                    # le vérificateur et le registre
pip install 'sprezzature-video[voice,post]'      # plus la narration et le travail ffmpeg
```

## Frontières

Qui possède quoi, entre cette suite et
[ai-helpers](https://deraison.ai/ai-helpers), est écrit dans
[BOUNDARIES.md](BOUNDARIES.md). En bref : **ai-helpers possède la primitive,
sprezzature possède l'opinion.** La voix arrive par
`sprezzature-audio[narrate]`, ffmpeg par `video-helper`, et le rendu par
Hyperframes derrière une couture.

## État

0.3.0. Le vérificateur, le registre d'actifs, les sous-titres, l'après-rendu, le
calage sur la grille, la mesure de calque, le chargeur de spécifications YAML
et les cinq surfaces sont écrits et testés — 94 tests, CI sur 3.10/3.11/3.12. La couture du moteur de rendu reste hors
bande : Hyperframes est piloté directement, et `renderers/` revient dans le
commit qui lui donne un module.

## Licence

BSD-3-Clause.
