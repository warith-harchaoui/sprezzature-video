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

Précoce. Le vérificateur, le registre d'actifs, les sous-titres et l'après-rendu
sont écrits et testés ; la couture du moteur de rendu, le chargeur de
spécifications YAML et les cinq surfaces (CLI argparse, CLI Click, API HTTP,
MCP, skill) ne sont pas encore là.

## Licence

BSD-3-Clause.
