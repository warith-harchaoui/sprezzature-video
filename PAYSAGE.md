# Paysage

🇫🇷 PAYSAGE.md · [🇬🇧 LANDSCAPE.md](https://github.com/warith-harchaoui/sprezzature-video/blob/main/LANDSCAPE.md)

`sprezzature-video` est le vérificateur de films de la suite
[sprezzature](https://sprezzature.ai/), un ensemble de paquets Python pour
produire du contenu web de qualité publication. C'est le seul des dix paquets
qui ne fabrique pas quelque chose à regarder. Il contrôle quelque chose que
quelqu'un a déjà fabriqué, contre le code dont ce film parle.

## Le problème, avant toute comparaison

Un film sur un projet fait des revendications sur ce projet : combien de types
de graphiques, combien de règles, combien de tests. Puis il grave ces
revendications dans des pixels à trente images par seconde, et plus rien ne les
relit.

Une phrase de README se relit. Quelqu'un ouvre le fichier, quelqu'un le
cherche au grep, quelqu'un en recopie une ligne dans une présentation. Un
chiffre à l'intérieur d'une image clé n'est plus du texte. C'est l'image d'un
chiffre, et la seule chose qui remarquerait qu'il est devenu faux, c'est une
personne qui regarde le film avec le dépôt ouvert à côté.

Ce n'est pas une hypothèse. Les cinq films en ligne sur sprezzature.ai
annonçaient **« 127 types de graphiques »** pendant des mois après que le
catalogue fut passé à 167. Le chiffre était cuit dans dix compositions et cinq
MP4 rendus, donc rien de moins qu'un remontage ne pouvait le corriger, et rien
nulle part ne surveillait. Tout le paquet existe à cause de ce seul chiffre.

Ce n'est donc pas un moteur de rendu. Son centre est un vérificateur qui tient
les affirmations d'un film contre le code qu'elles décrivent, dans les deux
sens : `verify` contrôle les revendications que quelqu'un a déclarées, `scan`
lit la composition et signale chaque chiffre à l'écran qu'aucune revendication
ne couvre. À côté du vérificateur se trouve un registre des ressources qui
répond à une question par fichier, « ce film pourrait-il être refabriqué depuis
un clone », et un écrivain de sous-titres qui construit le WebVTT à partir du
script de narration et de la longueur mesurée de chaque fichier audio, pas
d'une transcription. Le moteur de rendu reste derrière une couture, parce que
l'outil qui attrape les images est la décision la moins intéressante de la
chaîne.

## Sa place dans l'écosystème

```
suite sprezzature
├── sprezzature-video     ← ce paquet (le vérificateur de films)
├── sprezzature-figures     (les graphiques qui apparaissent dans le cadre)
├── sprezzature-maps        (les planches cartographiques dans le cadre)
├── sprezzature-colors      (la palette dans laquelle le film est monté)
├── sprezzature-audio       (la voix de narration, et l'écrivain WebVTT)
├── sprezzature-publish     (la page depuis laquelle le film est servi)
└── video-helper            (les primitives ffmpeg, venues d'ai-helpers)
```

Ce qui vient avant : un storyboard, les figures et les planches de
`sprezzature-figures` et `sprezzature-maps`, et un script de narration. Ce qui
vient après : un moteur de rendu, par défaut
[HyperFrames](https://github.com/heygen-com/hyperframes), puis la page que
`sprezzature-publish` construit autour du fichier fini. Le paquet frère qui
fait le travail voisin est `sprezzature-audio` : il possède la voix et
l'unique écrivain WebVTT que la suite partage, tandis que ce paquet-ci
possède l'endroit où chaque ligne parlée atterrit sur la grille de temps du
film.

## Quand la choisir

- **Votre film annonce un décompte qui va bouger.** Un catalogue, une suite de
  tests, une liste de paquets. Une revendication déclarée nomme le fichier qui
  la décide, donc un catalogue qui grandit fait échouer le contrôle au lieu de
  vieillir le film en silence.
- **Le projet a changé et un film est déjà publié.** C'est le déclencheur
  silencieux, et celui qu'il faut retenir. Rien ne relit un MP4 rendu, donc le
  film est faux dès que le catalogue grandit, et le reste jusqu'à ce que
  quelqu'un regarde.
- **Vous allez refaire un rendu et l'arbre des ressources est gitignoré.**
  Fontes, figures, narration, musique. Le registre dit quels fichiers sont à
  une copie, lesquels relancent un script, et lesquels existent à exactement
  un endroit sur un seul disque. Un rendu qui meurt à mi-chemin est une plus
  mauvaise façon de l'apprendre.
- **Un film est monté en deux langues.** `calque` mesure si la seconde version
  a été écrite ou seulement traduite, par correspondance et non par le sens, et
  nomme les lignes qui se répondent position par position.

## Quand prendre autre chose

- **Vous avez besoin de vraie direction artistique en mouvement.** Systèmes de
  particules, trois dimensions, animation de personnages, tout ce dont le cadre
  est le travail. [Remotion](https://www.remotion.dev/),
  [Motion Canvas](https://motioncanvas.io/) et HyperFrames font cela bien mieux
  que quoi que ce soit ici, et ce paquet est content de les piloter. Il ne
  possède rien de cette étendue et n'y tient pas.
- **Votre film n'affirme rien.** Une pièce d'ambiance, un générique, une
  bande démo. Il n'y a aucune revendication à protéger, et tout l'appareil
  n'est que du poids.
- **Vous voulez enregistrer un écran et partager un lien.**
  [Loom](https://www.loom.com/) et [Screen Studio](https://screen.studio/) font
  cela en un geste, sans rien à installer dans une chaîne de construction et
  sans rien à déclarer. Un fichier de spécification est la mauvaise forme pour
  une démonstration de deux minutes.
- **Vous voulez un présentateur à l'écran qui lit votre texte.**
  [Synthesia](https://www.synthesia.io/) produit un avatar convaincant à partir
  d'un texte en quelques minutes, avec clonage de voix et une trentaine de
  langues. Rien ici ne dessine un visage.
- **Vos revendications vivent dans des exemples de code, pas dans des images.**
  Le `doctest` de Python, [Sybil](https://sybil.readthedocs.io/) et
  `cargo test --doc` font déjà tourner votre documentation comme un test, ils
  sont matures, et ils sont meilleurs à ce travail qu'un paquet vidéo ne le
  sera jamais.
- **Votre vraie question est « puis-je reconstruire cet artefact ».**
  [DVC](https://dvc.org/) et Nix y répondent pour un projet entier, avec
  stockage distant, fichiers de verrouillage et dix ans d'expérience
  opérationnelle derrière eux. Le registre d'ici répond pour l'arbre des
  ressources d'un film et rien d'autre.

## Les idées à prendre

Étudier un concurrent et n'en rapporter rien, c'est de la lecture perdue. Huit
choses trouvées en écrivant cette page, de la meilleure à la plus coûteuse,
dont deux refusées avec leur raison.

**[Chromatic](https://www.chromatic.com/) et [Percy](https://percy.io/) : une
référence acceptée est enregistrée, pas rediscutée.** Un relecteur approuve un
changement visuel une fois et l'outil cesse de poser la question. Ici,
`assets.audit` signale `DIVERGED` avec « décidez, ne devinez pas », ce qui est
le bon refus et n'a aucune mémoire : la même divergence est resignalée à chaque
passage jusqu'à ce que les gens apprennent à passer dessus, et un garde devant
lequel tout le monde passe a cessé de tourner. La réparation est un bloc
`accepted:` dans la spécification du film, portant l'empreinte que quelqu'un a
approuvée et la ligne qui dit pourquoi, consulté par `AssetLedger.audit` avant
qu'il n'émette `State.DIVERGED`. Une demi-journée, et le meilleur rendement des
huit, parce que cela protège un contrôle qui existe déjà contre l'oubli.

**[Nix](https://nixos.org/) et [Make](https://www.gnu.org/software/make/) :
« je ne trouve pas ton entrée » n'est pas la même panne que « ta sortie est
périmée ».** Les deux refusent en nommant le fichier absent, et aucun ne compte
cela comme du travail fait. `verify` ne fait pas cette distinction, et
l'omission retourne le paquet contre lui-même. Les chemins des revendications
d'une spécification sont relatifs au répertoire qui contient les clones, ce que
la spécification documente. Lancé un cran plus bas, le `films.yaml` de la suite
sort neuf lignes `FAIL could not verify: claim source is missing` et conclut
**`1/10 claims hold`**, avec le code de sortie 1. Lancé au bon endroit, le même
fichier donne `10/10`. L'ennui est que `1/10 claims hold` est exactement la
phrase que produirait un film massivement périmé : quelqu'un qui lit cela en
intégration continue va corriger des chiffres qui étaient justes. Une mesure
qui ne sait pas de quel côté elle se trompe, c'est la classe de défaut que ce
paquet existe pour attraper, retournée contre lui. La réparation est de compter
`FileNotFoundError` à part d'un écart de valeur, de le signaler sur sa propre
ligne, et de refuser net quand *toutes* les sources manquent, parce que c'est
une racine fausse et pas dix revendications mortes le même jour. Une
demi-journée : `Verdict` porte déjà un `detail`, il lui faut un état et non une
réécriture. Résoudre les chemins contre le fichier de spécification plutôt que
contre le répertoire courant est la seconde moitié tentante, et elle doit
attendre : la disposition des dépôts voisins est une propriété du checkout, pas
du document.

**[Sybil](https://sybil.readthedocs.io/en/latest/integration.html) et
[pytest-codeblocks](https://pytest-codeblock.readthedocs.io/en/latest/) : le
contrôle de la documentation est collecté par le lanceur de tests, pas par une
commande dont quelqu'un doit se souvenir.** Sybil enregistre un collecteur dans
`conftest.py`, donc un exemple périmé dans `README.md` fait échouer le `pytest`
ordinaire sans seconde commande nulle part. Ce paquet a cinq surfaces et aucune
n'est celle-là : `sprezzature-video verify film.yaml` doit être branché à la
main dans un fichier de workflow, ce qui est exactement le mode de défaillance
que cette suite ne cesse de retrouver. Un point d'entrée `pytest11` dans
`pyproject.toml`, plus un petit greffon qui collecte chaque `*.film.yaml` sous
le répertoire courant comme élément de test, suffirait à rendre `pytest`
suffisant. Un jour, aucune dépendance nouvelle.

**[Playwright](https://playwright.dev/docs/test-snapshots) :
`--update-snapshots` transforme un rapport en un diff qu'on commite.** Un test
visuel qui échoue est à un drapeau d'une référence à jour, donc tenir les
références honnêtes coûte assez peu pour que les gens le fassent. L'analogue
ici est `scan`, qui imprime les chiffres non déclarés et laisse le lecteur
taper à la main un bloc de revendication par trouvaille. Un drapeau
`--write-claims` qui écrirait une ébauche dans la spécification, avec un
`method:` laissé délibérément invalide pour que le contrôle continue d'échouer
tant qu'un humain n'a pas nommé le fichier décideur, ferait de la déclaration
d'une revendication une corvée de trente secondes. Une demi-journée, et
l'ébauche invalide par défaut est la partie qu'il ne faut pas sauter.

**[DVC](https://dvc.org/doc/command-reference/repro) : `dvc.lock` enregistre
l'empreinte de chaque entrée et de chaque sortie du passage qui a produit un
artefact.** C'est ainsi qu'un relecteur, six mois plus tard, sait de quelle
version des données vient un résultat. `AssetLedger.audit` compare une copie à
sa source *aujourd'hui*, et ne peut pas dire quel côté a bougé. Écrire un
`film.lock.yaml` au moment du rendu, une empreinte par ressource, transforme
`DIVERGED` de « ces deux-là diffèrent » en « le projet a régénéré cette figure
après la sortie du film » ou « quelqu'un a modifié la copie », deux problèmes
opposés aux réparations opposées. Un jour, et cela se marie naturellement avec
le bloc `accepted:` ci-dessus.

**[shields.io](https://shields.io/) : le chiffre n'est jamais cuit, donc il ne
peut jamais périmer.** Un badge est récupéré à chaque chargement de page et est
toujours à jour. La moitié est à prendre, l'autre est refusée. À prendre : un
attribut `data-claim="figures.count"` sur l'élément qui porte un chiffre, lu
par `_VisibleText.handle_starttag`, qui existe déjà et jette actuellement les
attributs. Cela supprime la liste `--ignore`, où chaque valeur exemptée vit
aujourd'hui sur une ligne de commande loin de l'image à laquelle elle
appartient. Refusé : substituer la valeur vivante dans la composition au moment
du rendu, ce qui ferait de ce paquet le propriétaire du format de composition
et casserait la couture du moteur de rendu, qui est toute l'architecture. Une
demi-journée pour l'attribut.

**[WhisperX](https://github.com/m-bain/whisperX) : alignement forcé contre une
transcription connue, ce qui est exactement la situation ici.** Le script est
sur le disque, l'audio en a été synthétisé, donc les minutages mot à mot sont
disponibles pour qui les demande, et `split_line` couperait un sous-titre à une
pause mesurée au lieu d'une virgule devinée. Refusé tel quel : WhisperX amène
torch, et ce paquet s'installe en quelques secondes aujourd'hui. Si cela se
fait un jour, cela appartient à `sprezzature-audio`, qui porte déjà une
compilation de whisper.cpp et possède déjà l'écrivain WebVTT, et cela arrive
ici comme une liste de durées mesurées, comme tout le reste.

**[Nix](https://nixos.org/) : épingler tout l'environnement de construction et
la sortie cesse de dépendre de la machine.** Refusé, et la raison est précise
plutôt qu'idéologique. La narration de la suite passe par un moteur de voix qui
échantillonne : la même phrase française a mesuré 7,520, 6,760 et 6,640
secondes sur trois passages de `speaker-helper` 0.13. Un environnement épinglé
ne peut pas rendre cela déterministe, donc l'épinglage achèterait l'apparence
de la reproductibilité et pas la chose. Le module `timeline` est la réponse qui
a été construite à la place, et il absorbe la variation au lieu de faire comme
si elle n'existait pas.

## Comment le domaine se découpe

Il n'y a presque aucun concurrent frontal, et le dire franchement est plus
utile que d'en inventer un. Le tableau ci-dessous tient donc ensemble deux
familles qui ne se rencontrent jamais, parce que le travail de ce paquet est
leur recouvrement.

**La première famille fabrique un film.** À l'intérieur, la vraie coupure est
qui écrit le mouvement. Les cadriciels orientés code (Remotion, Motion Canvas,
Revideo, HyperFrames, Manim) mettent la composition dans un fichier texte qu'un
relecteur peut lire en diff, rendent de façon déterministe, et tournent dans
une chaîne de construction. Les monteurs à ligne de temps (After Effects,
Descript) la mettent dans un document qu'une personne déplace à la souris, ce
qui achète du métier et coûte de la reproductibilité. Les enregistreurs (Loom,
Screen Studio) font de l'humain la source, donc il n'y a pas de composition du
tout. Les générateurs hébergés (Veed, Pictory, Synthesia) prennent un texte et
rendent un fichier fini, avec toute la chaîne sur la machine de quelqu'un
d'autre. Aucun d'entre eux, à aucun prix, ne lit le projet dont le film parle.

**La seconde famille tient une affirmation à jour**, et elle n'est presque
jamais pointée vers une vidéo. La documentation testée en est la forme mature :
`doctest`, Sybil, `pytest-codeblocks` et `cargo test --doc` font tourner les
exemples à l'intérieur de votre prose, donc un exemple périmé fait échouer la
construction. Les services de badge prennent l'autre route, en ne cuisant
jamais le chiffre, et c'est pourquoi personne n'a jamais vu un badge périmé.
Les outils d'instantané visuel (le `toHaveScreenshot` de Playwright, Percy,
Chromatic) comparent un rendu à une référence stockée, et la distinction compte
ici : ils attrapent un artefact qui *a changé*, et la panne pour laquelle ce
paquet existe est un artefact qui n'a **pas** changé pendant que le monde
autour de lui changeait. Les registres de ressources (DVC, Git LFS, Make, Nix)
répondent à la question de la reconstruction, chacun à son grain : empreintes
de contenu, fichiers pointeurs, dates de fichiers, un environnement entier
épinglé.

**Les sous-titres forment une troisième coupure, plus petite**, et elle est
nette. Tout ce qui est listé ici, sauf ce paquet, part de l'audio : WhisperX et
ses dérivés, Rev, Otter, la piste automatique de YouTube. C'est de la
reconnaissance automatique de la parole (ASR), et l'ASR devine des mots que
quelqu'un connaît déjà, puisque la narration a été synthétisée depuis un script
posé sur le disque. Partir du script rend le texte exact par construction et ne
laisse que le minutage à calculer, et le minutage est ici mesuré sur le fichier
audio plutôt que tapé. L'alignement forcé se tient entre les deux et c'est la
comparaison honnête ; un service de transcription hébergé est un autre produit.

## Le tableau

Chaque outil est noté de 1 à 5 sur chaque critère, plus c'est mieux (⭐ faible
à ⭐⭐⭐⭐⭐ le plus fort). Les notes relèvent d'un jugement argumenté, pas d'un
banc d'essai, et chaque colonne est orientée de sorte que plus d'étoiles veut
dire plus fort sur ce trait : pour le coût, plus d'étoiles veut dire moins cher
ou plus ouvert ; pour le poids d'installation, plus d'étoiles veut dire plus
léger. Un ⭐ signifie que l'outil ne fait pas ce que la colonne mesure, ce qui
sur une échelle de capacité vaut un. La source lisible par machine est
[`assets/paysage.csv`](assets/paysage.csv) : 29 outils sur 14 critères.

| Outil | Produit un film fini | Étendue de l'animation | Qualité visuelle du résultat | Vérifie les revendications déclarées contre le code | Attrape la dérive non déclarée | Sous-titres fidèles au script | Refabricable depuis un clone propre | Déterminisme du résultat | Local et hors ligne | Gratuit ou ouvert | Utilisable en intégration continue | Tourne sans intervention humaine | Installation légère | Maturité et écosystème |
| --- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| sprezzature-video | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| Remotion | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Motion Canvas | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Revideo | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| HyperFrames | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Manim | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| After Effects | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ |
| ffmpeg | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Descript | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Screen Studio | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Loom | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Veed | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Pictory | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Synthesia | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| doctest | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Sybil | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| pytest-codeblocks | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| cargo test --doc | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Playwright snapshots | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Percy | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Chromatic | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| shields.io | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| DVC | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Git LFS | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Make | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Nix | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| WhisperX | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| Rev | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| YouTube auto-captions | ⭐ | ⭐ | ⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## La carte

![Carte de positionnement de 29 outils sur deux axes issus d'une analyse en composantes principales. sprezzature-video est seul dans le coin en haut à droite, aux coordonnées 3,46 et 3,42, sans rien près de lui. Le long du bord haut, à la même hauteur mais tout à gauche, se trouvent les moteurs orientés code : HyperFrames, Manim, Revideo, Remotion et Motion Canvas. L'extrême gauche est tenue par After Effects, Descript et Screen Studio. Le bord bas porte les services hébergés : Rev tout en bas, puis les sous-titres automatiques de YouTube, Loom, Pictory, Synthesia et Veed. Entre ce paquet et les moteurs se trouvent les outils de documentation testée, doctest, cargo test --doc, Sybil et pytest-codeblocks, et juste en dessous les registres de ressources, Nix, DVC, Make et Git LFS. L'axe horizontal oppose fabriquer l'image à contrôler le fait ; l'axe vertical oppose un outil qu'on fait tourner soi-même et depuis lequel on peut reconstruire à un outil déjà là qui ne coûte rien à démarrer.](assets/paysage.svg)

La source est [`assets/paysage.csv`](assets/paysage.csv), la table en étoiles
ci-dessus et rien de plus, et la carte se régénère avec :

```sh
python scripts/landscape_to_csv.py ~/sprezzature-video/PAYSAGE.md \
    --out ~/sprezzature-video/assets/paysage.csv            # depuis ~/sprezzature
standpoint assets/paysage.csv --outdir assets --stem paysage --check
```

La géométrie est une analyse en composantes principales (ACP) sur corrélations,
et elle est **déterministe** : la même table donne la même carte à chaque
passage. Les quatre mots des bords viennent d'un modèle local, et ils sont plus
vagues que les charges qui les portent, donc les charges sont le contrôle.
`standpoint` place la première ligne en haut à droite et oriente tout le reste
autour d'elle ; c'est une convention de dessin, pas une prétention de qualité.

**Horizontal, nommé « Esthétique ↔ Fiabilité ».** Qualité visuelle du résultat
(−0,445), produit un film fini (−0,432) et étendue de l'animation (−0,388)
tirent à gauche ; vérifie les revendications déclarées contre le code (+0,302),
tourne sans intervention humaine (+0,274), utilisable en intégration continue
(+0,269) et gratuit ou ouvert (+0,264) tirent à droite. L'axe oppose
*fabriquer l'image* à *contrôler le fait*, qui est la division dont parle toute
cette page, et c'est l'axe dont ce paquet occupe l'extrémité droite par
construction.

**Vertical, nommé « Simplicité ↔ Autonomie ».** Local et hors ligne (+0,411),
refabricable depuis un clone propre (+0,385) et déterminisme du résultat
(+0,381) chargent ensemble vers le haut, avec gratuit ou ouvert (+0,270) et
utilisable en intégration continue (+0,269) derrière eux ; installation légère
(−0,362) et maturité et écosystème (−0,167) tirent vers le bas. Le pôle haut
est une seule chose cohérente, *un outil qu'on fait tourner soi-même et depuis
lequel on peut reconstruire*, et le bas en est l'opposé, *un outil déjà debout
qui ne coûte rien à démarrer*. Rev, les sous-titres automatiques de YouTube et
les générateurs vidéo hébergés longent le bord bas ; Nix, DVC et les moteurs de
rendu longent le bord haut.

**Deux axes portent 61,2 % de la table** (38,9 % et 22,3 %). Les 38,8 % qui
restent sont dans la table et pas sur cette page, et une part compte plus que
les autres : *attrape la dérive non déclarée* est le critère le plus faiblement
chargé sur les deux axes (+0,173 et +0,110), et c'est le critère qui sépare ce
paquet de tout le reste ici. La carte est une première orientation ; la colonne
qui justifie le paquet la déplace à peine.

Deux lectures méritent d'être faites. HyperFrames est exactement à la même
hauteur que ce paquet (3,42) et à l'autre bout de l'axe horizontal, ce qui est
la carte en train de remarquer que le moteur de rendu derrière la couture
partage tous les traits de reproductibilité et aucun des traits de contrôle. Et
ce paquet est seul dans son coin, ce qui n'est pas une victoire : les moteurs
de rendu se regroupent parce qu'ils sont en concours les uns avec les autres,
et personne dans ce groupe n'essaie de confronter un chiffre à un catalogue,
parce que ce n'est pas le métier d'un moteur de rendu.

`--check` confirme le leader en haut à droite et les étiquettes d'axes
visibles, et marque la figure **non lisible** : huit paires d'étiquettes
risquent de se chevaucher, dont Remotion avec Motion Canvas, Sybil avec
pytest-codeblocks et Percy avec Chromatic. Ce sont des outils dont les notes se
superposent vraiment, donc le chevauchement est la table qui dit la vérité
plutôt que la figure qui se trompe. Le SVG interactif les sépare au survol ; le
PNG non.

## Sources

- [Remotion](https://www.remotion.dev/), [Motion Canvas](https://motioncanvas.io/)
  et [Revideo](https://re.video/) comparés pour 2026 :
  [rendercomp](https://rendercomp.com/blog/best-programmatic-video-tools-2026/).
- [HyperFrames](https://github.com/heygen-com/hyperframes), passé en Apache 2.0
  en mai 2026, et
  [une revue qui le place face à Remotion](https://kompozy.io/reviews/heygen-hyperframes).
- [L'intégration de Sybil au lanceur de tests](https://sybil.readthedocs.io/en/latest/integration.html)
  et [pytest-codeblocks](https://pytest-codeblock.readthedocs.io/en/latest/) :
  les deux façons qu'a un projet Python de faire tourner sa prose comme un test.
- [Les comparaisons visuelles de Playwright](https://playwright.dev/docs/test-snapshots)
  et [Chromatic sur le test visuel](https://www.chromatic.com/blog/how-to-visual-test-ui-using-playwright/),
  pour ce qu'une référence stockée attrape et n'attrape pas.
- [DVC](https://dvc.org/doc/command-reference/repro) pour la question de la
  reconstruction posée à l'échelle d'un projet, et pour `dvc.lock`.
- [WhisperX](https://github.com/m-bain/whisperX) pour l'alignement forcé, et
  l'écart mesuré entre minutages alignés et minutages natifs de Whisper dans
  [Whisper Has an Internal Word Aligner](https://arxiv.org/pdf/2509.09987).
- [Les meilleurs générateurs vidéo testés pour 2026](https://pictory.ai/blog/best-ai-video-maker-2026),
  pour le bout hébergé de la première famille.

## À voir aussi

- [BOUNDARIES.md](BOUNDARIES.md) : quel paquet possède quoi, entre cette suite
  et ai-helpers.
- [sprezzature-figures](https://github.com/warith-harchaoui/sprezzature-figures)
  et [sprezzature-maps](https://github.com/warith-harchaoui/sprezzature-maps) :
  ce qui apparaît dans le cadre.
- [sprezzature-audio](https://github.com/warith-harchaoui/sprezzature-audio) :
  la voix, et l'unique écrivain WebVTT que la suite partage.
