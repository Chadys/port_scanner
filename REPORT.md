## Recherches préliminaires
Ne connaissant pas du tout l'outil `nmap`, la première chose à faire était de me renseigner dessus.
Pour cela, j'ai lu en grande partie l'édition en ligne gratuite de [*Nmap Network Scanning*](https://nmap.org/book/toc.html).
Le temps que j'ai passé dessus est important, et j'aurais pu me contenter du chapitre 15 (*Nmap Reference Guide*), 
mais j'aime aller en profondeur lorsque je suis amené à utiliser un nouvel outil, et `nmap` m'a paru être suffisamment utile et pratique pour mériter ce temps consacré.

De plus, cette exploration de la doc m'a permis de découvrir d'autre outils comme [`ncrack`](https://nmap.org/ncrack/)
et une bonne manière d'en découvrir encore d'autre avec [*SecTools*](https://sectools.org/)

À la fin de ma lecture, et après quelques tests sur terminal, j'ai pu avoir une bonne estimation des options que j'allais être amenée à utiliser pour mon script.

### Notes :
Lors de mes recherches préliminaires, je suis bien sûr tombée sur [python-nmap](http://xael.org/norman/python/python-nmap/) et [python3-nmap](https://github.com/wangoloj/python3-nmap).
Je ne suis volontairement pas allée consulter le code source de ces paquets.

## Respect des spécifications

### Arguments
Les arguments devant être acceptés comme cibles sont de manière commode les mêmes qui sont accepté par `nmap`.
En revanche, l'option `-iL` doit être passée lorsque la liste de cible provient d'un fichier.
Une validation des arguments sera donc faite en amont pour différencier ces deux types, en utilisant la bibliothèque standard `argparse`.
Elle permettra également d'éviter la valeur spéciale `-` en tant que nom de fichier dont `nmap` se sert
pour lui indiquer d'utiliser l'input standard plutôt qu'un fichier, comportement dont nous ne voulons pas.

### Affichage de la progression et du résumé
Sans option, `map` affiche un certains nombre de résultats pertinents au fur et à mesure qu'il les obtient (détection de ports ouverts notamment).
L'option verbose `-v` permet d'afficher encore plus d'information, comme l'estimation du temps restant, qui me parait très important à fournir.
Le retour de `map` me paraissant bien, j'ai choisi de simplement procéder à une redirection de sa sortie sur celle du script Python.

### Production du HTML
`map` permet d'obtenir directement une sortie en XML.
- `--webxml` or `--stylesheet` (%D used in filename to add date)
Run the XML file through an XSLT processor such as xsltproc to produce an HTML file

### Performance vs Informations
Le script demandé étant très générique, il m'a été difficile de choisir un bon compromis entre vitesse d'exécution et information récoltée.
Voici les options que j'ai retenues, bien que j'ai conscience que chacune pourrait être soumise à débat :
- `-A` (équivalent à `-sV -sC -O --traceroute` (version detection, Nmap Scripting Engine with the default set of scripts, remote OS detection, and traceroute))

  Option classique, elle permet de recueillir un maximum d'information lorsque l'on s'intéresse à la découverte de vulnérabilités (ce qui est notre cas ici)
  en identifiant la présence de versions insécures d'un service ou OS, TODO scripts.
  
- `--osscan-limit`
  
  Cette option permet de limiter le temps supplémentaire causé par l'option `-O` en ne cherchant à identifier l'OS que sur les cibles qui semble prometteuse pour cette identification.

- `--min-hostgroup 256` 
  
  Cette option est normalement [dynamique](https://nmap.org/book/performance-timing-templates.html#tbl-performance-timing-template-values)
  pour permettre un compromis entre rapidité et retour utilisateur.
  J'ai choisi de mettre un minimum élevé car la rapidité d'exécution me paraissait plus primordiale, et que l'option `-v` permet d'avoir quand même un peu de retour en attendant.

- J'ai hésité à ajouté l'option `--open` dans un soucis de concision, puisque les spécifications demandées n'avait l'air de s'intéresser à la détection de port ouvert uniquement.
  Mais cette option aurait également filtré les machines ne contenant aucun port ouvert, hors les spécification données demandent demande d'afficher les "machines détectée online", ce qu'elles peuvents très bien être avec des ports fermés uniquement.

- Pas d'option sur la résolution de reverse DNS, pour garder le comportement par défaut
  qui est de procéder à la résolution sur tous les hosts détectés en ligne, qui me paraisser être une information pertinente bien qu'elle ralentisse le scan.

- `-T aggressive`
  
  Les contrôles de timings bas-niveau sont très difficile à choisir sans informations sur les cibles potentielles,
  et je ne considère pas avoir les connaissance suffisantes pour choisir des valeurs saines.
  J'ai donc préférée m'abtenir et m'en tenir au options de plus haut-niveau.
  J'ai choisi celle-ci car il s'agit de l'option recommandée dans le livre lorsque l'on peut faire à peu près confiance dans la rapidité et la fiabilité de la connexion avec les cibles
  et qu'on ne cherche pas à être furtif.
  Cette option va elle-même [influencer les options de plus bas-niveau](https://nmap.org/book/performance-timing-templates.html#tbl-performance-timing-template-values)
  et elle me paraissait être un bon compromis pour rester le plus générique possible sans trop sacrifier les performances.
  
- --resolve-all
  
  Permet de scanner toutes les adresses IP correspondant à un hostname, plutôt que simplement la première.
  J'ai choisi d'inclure cette option au cas où, à défaut de connaître le comportement désiré.

#### Choix du type de scan et des ports
C'est le choix d'option pour lequel j'ai eu le plus d'hésitation.
Il paraissait évident de faire un scan SYN, car les port TCP sont les plus courant et le scan SYN est celui qui permet de détecter le plus grand nombre d'entre eux en un minimum de temps.
Mais il me semblait important de procéder également à des scans UDP, bien qu'il ne soit [pas conseillé de faire les deux à la fois](https://nmap.org/book/reduce-scantime.html#performance-udp), les options d'optimisation pertinentes n'étant pas les mêmes pour chacun.
Procéder à deux scans séparés aurait été possible mais aurait grandement complexifié le script en ajoutant le besoin de fusionner les deux résultats à la fin.
J'ai essayé de trouver un compromis, avec les options `-sSU -pT:-,U:631,161,137,123,138,1434,445,135,67,53,139,500,68,520,1900,4500,514,49152,162,69`.
Ces options indiquent de procéder à un scan SYN sur tous les ports de 1 à 65535 et UDP sur les [20 ports UDP les plus populaires](https://nmap.org/book/port-scanning.html#most-popular-ports).
Ça me permet de limiter l'impact des scans UDP, beaucoup plus lents, mais de garder un [taux d'efficacité supérieur à 20%](https://nmap.org/book/performance-port-selection.html#tbl-performance-top-ports-effectiveness).
Le port 0 a été exclu volontairement car il s'agit normalement d'un port invalide et son scan n'est pertinent que dans des cas très spécifiques (détection d'une backdoor installée dessus par exemple).
`nmap` ne permet malheureusement pas de se servir des options `-F` ou `--top-ports` pour un protocole seulement, sinon je les aurait utilisées pour réduire le nombre de port TCP scannés et pour ne pas avoir à écrire en dur les port UDP voulus.
J'ai tout de même préféré ajouter une possibilité d'accélérer l'opération en utilisant à la place les options `-sS -F`.

#### Choix des *probes*
Afin de détecter les machines en ligne et de ne scanner que celles-ci, des *probes* (=sondes) sont exécutés.
Bien qu'il puisse être utile d'effectuer les scans sur toutes les IP sans check préalable lorsque l'on veut faire une vérification plus poussée du réseau cible (l'option `Pn` peut être utilisée dans ce cas),
cela ne me paraissait pas pertinent pour un programme de détection de port plus générique.
Il faut donc choisir un liste de *probes* avec là aussi un compromis à faire entre le nombre d'IP correctement détectées en utilisation et le temps pris par cette vérification.
En m'appuyant sur les [résultats obtenus selon différentes combinaisons](https://nmap.org/book/host-discovery-strategies.html#host-discovery-tbl-best-combinations),
j'ai choisi une liste un peu plus étoffée de celle utilisée par défaut : `-PE -PP -PS80,443 -PA3389 -PU40125`

### Mise en production

## Difficultés rencontrées

### Compatibilité Python 2
Python 2 n'étant officiellement plus supporté depuis le 1er janvier 2020, et Python 3 étant la norme depuis maintenant pas mal d'années,
fait que dans mes années de développement je n'ai jamais codé que sous Python 3.
L'exigence de compatibilité avec les deux versions m'a demandé un travail supplémentaire non négligeable d'ajustement.

### Arguments
Il aurait été compliqué de faire une méthode de validation qui puisse distinguer de manière fiable un hostname d'un fichier.
J'ai donc fait le choix de ne pas pouvoir passer à mon script un fichier de manière indifférencié des autres types d'argument, mais d'en faire une option à part.
De cette manière, j'ai également pu procéder à la validation de manière plus propre, en profitant de `argparse.FileType`, mais que j'ai dû surcharger légèrement pour ne pas prendre en charge la valeur spéciale `'-'`.
Pour la validation de hostname / ipv4 / ipv6 / cidr, plutôt que de partir dans l'écriture de regex complexe, j'ai préféré me servir de solutions éprouvées.
Je suis d'abord parti voir le module standard `ipaddress`, qui permet de valider les ipv4-6 et la notation CIDR, mais pas les hostname.
J'ai ensuite trouvé le paquet `validators` qui a l'air correctement maintenu et est compatible Python 2.7+, qui permet de valider hostname et ipv4-6, mais pas la notation CIDR.
Un mélange des deux m'a permis d'obtenir ce que je voulais, après un test de performance effectué avec timeit pour choisir lequel s'occuperait des ipv4-6.

### Exécution avec les droits root
Afin de permettre à `nmap` certaines opérations, comme les scans SYN ou la détection d'OS, `nmap` doit être lancé avec les droits root sous Unix, 
Windows user without Npcap installed 
Windows administrator account recommended but can work if WinPcap loaded in the OS
Sans cela, `nmap` utilisera des contournement lorsqu'il le peut (comme d'utiliser un `connect` complet à la place du scan SYN),
mais les performances, la furtivité et la complétude des informations sera impacté.
TODO

## Temps passé

## Pistes d'amélioration
-6
todo spoof, decoy etc cover trace see https://nmap.org/book/man-bypass-firewalls-ids.html