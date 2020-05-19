## Recherches préliminaires
Ne connaissant pas du tout l'outil `nmap`, la première chose à faire était de me renseigner dessus.
Pour cela, j'ai lu en grande partie l'édition en ligne gratuite de [*Nmap Network Scanning*](https://nmap.org/book/toc.html).
Le temps que j'ai passé dessus est important, et j'aurais pu me contenter du chapitre 15 (*Nmap Reference Guide*), 
mais j'aime aller en profondeur lorsque je suis amené à utiliser un nouvel outil, et `nmap` m'a paru être suffisamment utile et pratique pour mériter ce temps consacré.

De plus, cette exploration de la doc m'a permis de découvrir d'autre outils comme [`ncrack`](https://nmap.org/ncrack/)
et une bonne manière d'en découvrir encore d'autres avec [*SecTools*](https://sectools.org/)

À la fin de ma lecture, et après quelques tests sur terminal, j'ai pu avoir une bonne estimation des options que j'allais être amenée à utiliser pour mon script.

#### Notes :
Lors de mes recherches préliminaires, je suis bien sûr tombée sur [python-nmap](http://xael.org/norman/python/python-nmap/) et [python3-nmap](https://github.com/wangoloj/python3-nmap).
Je ne suis volontairement pas allée consulter le code source de ces paquets.

## Respect des spécifications

### Utilisation de `nmap`
L'utilisation du module `subprocess` me paraît adapté.

### Arguments
Les arguments devant être acceptés comme cibles sont, de manière commode, les mêmes qui sont acceptés par `nmap`.
En revanche, l'option `-iL` doit être passée lorsque la liste de cibles provient d'un fichier.
Une validation des arguments sera donc faite en amont pour différencier ces deux types, en utilisant la bibliothèque standard `argparse`.
Et tant qu'à faire, la validité des arguments qui ne sont pas un fichier sera également vérifiée pour pouvoir les passer à `subprocess` de manière plus sécurisée.
Cette validation permettra également d'éviter de pouvoir passer à `nmap` la nom de fichier spécial `-`, qui indique l'input standard,
puisque c'est un comportement dont nous ne voulons pas dans un premier temps pour ne pas complexifier le programme.

### Affichage de la progression et du résumé
Sans option, `nmap` affiche un certains nombre de résultats pertinents au fur et à mesure qu'il les obtient.
L'option verbose `-v` permet d'afficher encore plus d'informations en temps réel, comme l'estimation du temps restant, qui me parait très important comme retour à avoir.
Le désavantage et que ça ajoute aussi des informations moins utiles comme les machines détectée hors ligne.
Le retour de `nmap` me paraissant globalement bien, j'ai choisi de simplement l'afficher directement en le faisant hériter du `stdout` et `stderr` du process Python.

### Production du HTML
`nmap` permet d'obtenir directement une sortie en `XML` et fourni également une feuille de style `XLS`.
Plutôt que de devoir écrire un générateur de `html`, j'ai choisi de profiter du travail qui a déjà été fait.
Un exemple de commande pour produire ce fameux `html` nous est même [donné](https://nmap.org/book/output-formats-output-to-html.html#output-formats-html-permanent).
J'ai comparé différent processeurs `XSLT` utilisables et voilà ce que j'ai trouvé :
- `xsltproc`, installé de base sur la plupart des système Unix, binaire à lancer en ligne de commande
- `libxslt`, bindings Python pour `xsltproc`, dépend de `libxml2`, instruction d'installation peu claires, nécessite à priori d'installer d'autre binaires
- `lxml`, surcouche sur `libxslt` et `libxml2` mais fourni à priori un paquet `pip` qui les intégre et utilise bien leurs dernières versions, bien maintenu. Python 2.7 ou 3.4+.

J'ai d'abord voulu tester `lxml`, qui offre l'avantage de pouvoir être indiqué en dépendance par le système de paquet Python.
Mais les exemples pour s'en servir demandent d'indiquer le chemin du fichier `XLS` séparemment (alors que l'attribut `xml-stylesheet` du `XML` est rempli)
et nécessite, je trouve, trop de lignes de code comparé à la simplicité de la commande `xsltproc` équivalente.
Mais peut-être y'a-t-il une solution plus compacte que j'ai raté.
Dans un souci d'économie de temps, j'ai tout de même fait le choix de me servir à nouveau de `subprocess`, pour appeler simplement `xsltproc`.


### Performance vs Informations
Le script demandé étant très générique, il m'a été difficile de choisir un bon compromis entre vitesse d'exécution et informations récoltées.
Voici les options que j'ai retenues, bien que j'ai conscience que chacune d'entre elles pourrait être soumise à débat :
- `-A` (équivalent à `-sV -sC -O --traceroute` (version detection, Nmap Scripting Engine with the default set of scripts, remote OS detection, and traceroute))

  Option classique, elle permet de recueillir un maximum d'informations lorsque l'on s'intéresse entre autre à la découverte de vulnérabilités (ce qui est notre cas ici),
  en identifiant la présence de versions insécures d'un service ou OS par exemple.
  D'autres types de vulnérabilités (login anonyme à un serveur FTP, ...) et des informations supplémentaires selon les services détectés,
  sont ajoutées grâce aux scripts NSE de la catégorie `default` qui sont également lancés par cette option.
  Ces scripts doivent répondre à certains critères, notamment de rapidité, ce qui rend pertinent leur exécution ici.
  
- `--osscan-limit`
  
  Cette option permet de limiter le temps supplémentaire causé par l'option `-O` en ne cherchant à identifier l'OS que sur les cibles qui semble prometteuse pour cette identification.

- `--min-hostgroup 256` 
  
  Cette option est normalement [dynamique](https://nmap.org/book/performance-timing-templates.html#tbl-performance-timing-template-values)
  pour permettre un compromis entre rapidité et retour utilisateur.
  J'ai choisi de mettre un minimum élevé car la rapidité d'exécution me paraissait plus primordiale que la rapidité de retour visuel,
  et que l'option `-v` permet d'avoir quand même des informations sur la progression en attendant.

- J'ai hésité à ajouter l'option `--open` dans un soucis de concision, puisque les spécifications demandées n'avait l'air de s'intéresser à la détection de port ouvert uniquement.
  Mais cette option aurait également filtré les machines ne contenant aucun port ouvert, hors les spécification données demandent d'afficher les "machines détectée online", ce qu'elles peuvents très bien être avec des ports fermés uniquement.

- Aucune option sur la résolution de reverse DNS n'a été mise, afin de garder le comportement par défaut
  qui est de procéder à la résolution sur tous les hosts détectés en ligne, qui m'a paru être une information pertinente à garder bien qu'elle ralentisse le scan.

- `-T aggressive`
  
  Les contrôles de timings bas-niveau sont très difficile à choisir sans plus d'informations sur les cibles potentielles,
  et je ne considère pas avoir les connaissance suffisantes pour choisir des valeurs génériques saines.
  J'ai donc préféré m'abtenir et m'en tenir au options de plus haut-niveau.
  J'ai choisi celle-ci car il s'agit de l'option recommandée dans le livre lorsque l'on suppose pouvoir faire à peu près confiance 
  à la rapidité et la fiabilité de notre connexion avec les cibles et qu'on ne cherche pas à être particulièrement furtif.
  Cette option va elle-même [influencer les options de plus bas-niveau](https://nmap.org/book/performance-timing-templates.html#tbl-performance-timing-template-values)
  et elle me paraissait être un bon compromis pour rester le plus générique possible sans trop sacrifier les performances.
  
- `--resolve-all`
  
  Permet de scanner toutes les adresses IP correspondant à un hostname, plutôt que simplement la première.
  J'ai choisi d'inclure cette option au cas où, à défaut de connaître le comportement désiré.

#### Choix du type de scan et des ports
C'est le choix d'options pour lequel j'ai eu le plus d'hésitation.
Il paraissait évident de faire un scan SYN, car les ports TCP sont les plus courant et le scan SYN est celui qui permet de détecter le plus grand nombre d'entre eux en un minimum de temps.
Mais il me semblait important de procéder également à des scans UDP, bien qu'il ne soit [pas conseillé de faire les deux à la fois](https://nmap.org/book/reduce-scantime.html#performance-udp), 
les options d'optimisation pertinentes n'étant pas les mêmes pour chacun.
Procéder à deux scans séparés aurait été possible mais aurait grandement complexifié le script en ajoutant entre autres le besoin de fusionner ensuite les deux résultats dans un seul rendu HTML.
J'ai essayé de trouver un compromis, avec les options `-sSU -pT:-,U:631,161,137,123,138,1434,445,135,67,53,139,500,68,520,1900,4500,514,49152,162,69`.
Ces options indiquent de procéder à un scan SYN sur tous les ports de 1 à 65535 et UDP sur les [20 ports UDP les plus populaires](https://nmap.org/book/port-scanning.html#most-popular-ports).
Ça me permet de limiter l'impact des scans UDP, beaucoup plus lents, mais de garder un [taux d'efficacité supérieur à 20%](https://nmap.org/book/performance-port-selection.html#tbl-performance-top-ports-effectiveness).
Le port 0 a été exclu volontairement car il s'agit normalement d'un port invalide et son scan n'est pertinent que dans des cas très spécifiques (détection d'une backdoor installée dessus par exemple).
`nmap` ne permet malheureusement pas de se servir des options `-F` ou `--top-ports` pour un protocole seulement, sinon je les aurais utilisées pour réduire le nombre de ports TCP scannés et pour ne pas avoir à écrire en dur les ports UDP voulus.
J'ai tout de même préféré ajouter une possibilité d'accélérer l'opération en utilisant à la place les options `-sS -F` si un argument optionnel est ajouté au script python (`--fast`).

#### Choix des *probes*
Afin de détecter les machines en ligne et de ne scanner que celles-ci, des *probes* (=sondes) sont exécutés.
Bien qu'il puisse être utile d'effectuer les scans sur toutes les IPs sans check préalable lorsque l'on veut faire une vérification plus poussée du réseau cible (l'option `-Pn` peut être utilisée dans ce cas),
cela ne me paraissait pas pertinent pour un programme de détection de port générique.
Il faut donc choisir un liste de *probes* avec là aussi un compromis à faire entre le nombre d'IPs correctement détectées en ligne et le temps pris par cette vérification.
En m'appuyant sur les [résultats obtenus selon différentes combinaisons](https://nmap.org/book/host-discovery-strategies.html#host-discovery-tbl-best-combinations),
j'ai choisi une liste un peu plus étoffée de celle utilisée par défaut : `-PE -PP -PS80,443 -PA3389 -PU40125`.

#### Scripts supplémentaires
Afin d'identifier des CVE potentielles, deux scripts NSE ont été ajoutés : `nmap-vulners` et `vulscan`.
`nmap-vulners` a l'air d'être déjà présent dans les scripts fourni avec `nmap` sous le nom de `vulners` mais la version du github a l'air plus complète que celle installée par défaut.
Ces deux scripts détecte des CVE en fonction de bases de données, statiques dans le cas de `vulscan`, récupérées dynamiquement au début d'un scan pour `nmap-vulners`.


### Mise en production
Le projet a été réalisé en suivant la structure de projet Python classique, avec de quoi tester le package 
et un fichier de setup afin de pouvoir éventuellement déployer le paquet sur PyPI.
J'ai pensé à faire un container Docker, mais le fait de devoir passer des arguments différents à chaque fois n'aurait pas rendu cela pratique.

## Difficultés rencontrées

### Compatibilité Python 2
Python 2 n'étant officiellement plus supporté depuis le 1er janvier 2020, et Python 3 étant la norme depuis maintenant pas mal d'années,
a fait que dans mes années de développement je n'ai jamais codé que sous Python 3.
L'exigence de compatibilité avec les deux versions m'a demandé un travail supplémentaire non négligeable d'ajustement.
De plus, la fin du support récent a entrainé des mises à jour dans certains des outils que j'utilise (`pip` et `brew` notamment)
avec parfois pour effet de casser des choses qui permettait précédemment de gérer la rétrocompatibilité.

### Arguments
Il aurait été compliqué de faire une méthode de validation qui puisse distinguer de manière fiable un hostname d'un nom de fichier.
J'ai donc fait le choix de ne pas pouvoir passer à mon script un fichier de manière indifférencié des autres types d'argument, mais d'en faire une option à part.
De cette manière, j'ai également pu procéder à la validation de manière plus propre, en profitant de `argparse.FileType`, mais que j'ai dû surcharger légèrement pour ne pas prendre en charge la valeur spéciale `'-'`.
Pour la validation de hostname / ipv4 / ipv6 / cidr, plutôt que de partir dans l'écriture de regex complexes, j'ai préféré me servir de solutions éprouvées.
Je suis d'abord parti voir le module standard `ipaddress`, qui permet de valider les ipv4-6 et la notation CIDR, mais pas les hostname.
J'ai ensuite trouvé le paquet `validators` qui a l'air correctement maintenu et est compatible Python 2.7+, qui permet de valider hostname et ipv4-6, mais pas la notation CIDR.
Un mélange des deux m'a permis d'obtenir ce que je voulais, après un test de performance effectué avec `timeit` pour choisir lequel s'occuperait des ipv4-6
(réponse : ça dépend de s'il s'agit d'une ipv6 ou ipv4, mais `ipaddress` était en moyenne plus rapide et surtout plus rapide avec les ipv4 qui reste le type d'IP le plus courant).

### Exécution avec les droits root
Afin de permettre à `nmap` certaines opérations, comme les scans SYN ou la détection d'OS, celui-ci doit être lancé avec les droits root sous Unix
et doit sous Windows être lancé en tant qu'administrateur excepté si `Npcap` ou `WinPcap` a été installé et chargé par l'OS.
Sans cela, `nmap` utilisera des contournements lorsqu'il le peut (comme d'utiliser un `connect` complet à la place du scan SYN),
mais les performances, la furtivité et la complétude des informations seront impactés.
De plus, le fait d'avoir indiqué en dur le type de scan à faire (`-sS`) empêche `nmap` de choisir une alternative, ce qui me parait être un comportement sain.
J'ai fait quelques recherches qui permettrait à l'utilisateur de lancer le script sans devoir indiquer en dur un niveau de permission,
mais je n'ai pas trouvé de solution satisfaisante.
J'ai exploré quelques pistes, notamment le bit `setuid`, mais cette solution, en plus de ne pas pouvoir fonctionner directement avec un script, n'est pas portable.
J'ai préféré laisser l'utilisateur exécuter lui-même le script avec les droits nécessaires, selon la version de son système.


## Temps passé et performance
#### Lecture du livre de `nmap`
Environ 7h
#### Développement
10-15h, incluant l'apprentissage de tox, de l'architecture correct d'un module,
la révision de comment utiliser `subprocess` et `argparse`, les recherches de bibliothèques pertinentes,
les galères avec la compatibilité Python 2 et l'écriture de tests et documentation.

#### Étapes de développement
- parsing des arguments
- appel à `nmap`
- choix des options
- production du html
- correction compatibilité py27, setup et readme

#### Vitesses d'exécution mesurées sur ma machine
- Version classique sur scanme.nmap.org -> 197.59 seconds
- Version accélérée sur scanme.nmap.org -> 23.97 seconds

## Pistes d'évolution
- La compatibilité sous Windows n'a pas été testée
- La compatibilité des versions de Python autre que 2.7 et 3.7 n'a pas été testée
- Le test fait par `tox` de la version Python 2.7 ne fonctionne pas à cause de l'impossibilité d'installer `ipaddress`,
  les problème devrait bientôt [être corrigé](https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1869247).
  Beaucoup de choses ont été cassé en Python 2 depuis la fin de son support officiel.
- faire un pipe sur le `stdin` de `nmap` pour gérer la valeur spécial de fichier `-`
- [L'option `-6`](https://nmap.org/book/port-scanning-ipv6.html) laisse penser qu'un traitement différent doit préférablement être fait selon le type d'ip que l'on analyse.
  Plus de recherche est nécessaire.
- Ce script ne s'occupe pas du tout des problématiques de discrétion, de couvrir ses traces.
  Il serait intéressant de se renseigner sur les technique de [spoof, decoy](https://nmap.org/book/man-bypass-firewalls-ids.html), [etc](https://nmap.org/book/firewalls.html).
