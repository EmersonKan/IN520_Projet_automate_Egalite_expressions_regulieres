PROJET IN520 – ÉGALITÉ D’EXPRESSIONS RÉGULIÈRES
=============================================

OBJECTIF
--------
Le but du projet est de déterminer si deux expressions régulières reconnaissent
le même langage sur l’alphabet {a, b, c}.

Pour cela, on utilise les propriétés fondamentales de la théorie des langages :
- toute expression régulière peut être transformée en automate fini,
- deux expressions sont équivalentes si et seulement si leurs automates
  reconnaissent le même langage.

STRATÉGIE GÉNÉRALE
-----------------
1) Analyse syntaxique des expressions régulières (Flex + Bison)
2) Construction d’un automate NON déterministe (NFA) par construction de Thompson
3) Suppression des transitions epsilon
4) Déterminisation (subset construction)
5) Complétion
6) Minimisation
7) Comparaison des deux automates minimaux par produit

ÉTAPE 1 — PARSING
-----------------
Flex découpe l’entrée en tokens :
  a b c  +  *  .  ( )  E

Bison applique la grammaire avec les priorités :
  *  >  .  >  +

Chaque règle produit du code Python au lieu d’un arbre :
  - automate("a")
  - union(a1, a2)
  - concatenation(a1, a2)
  - etoile(a1)

Le parser génère automatiquement le fichier main.py.

ÉTAPE 2 — CONSTRUCTION DES AUTOMATES
------------------------------------
On utilise la construction de Thompson :
- concaténation : epsilon entre les automates
- union : nouveau départ + nouveau final
- étoile : boucles epsilon

Les automates sont représentés par :
- nombre d’états
- états finaux
- transitions (q, symbole) → liste d’états

ÉTAPE 3 — NORMALISATION
-----------------------
Pipeline tout_faire :
- suppression epsilon
- déterminisation
- complétion
- minimisation

ÉTAPE 4 — COMPARAISON
---------------------
On construit le produit des deux DFA complets.
Si on trouve une paire (q1, q2) telle que :
  q1 final et q2 non final (ou inversement)
alors les langages sont différents.

Sinon, ils sont égaux.

SORTIE
------
Le programme affiche :
  EGAL
ou
  NON EGAL

OUTILS
------
- Flex / Bison
- Python 3	
- Graphviz (pour les dessins d’automates)
