import copy as cp
from collections import deque
import os
import shutil
import graphviz

# =============================================================================
# CONFIGURATION GRAPHVIZ (Linux / WSL)
# =============================================================================

def check_graphviz():
    """Vérifie si Graphviz (dot) est disponible"""
    return shutil.which("dot") is not None

GRAPHVIZ_AVAILABLE = True

try:
    from graphviz import Digraph
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    print("ATTENTION : modules Python manquants.")
    print("Installez avec : pip install graphviz fpdf2")

if not check_graphviz():
    GRAPHVIZ_AVAILABLE = False
    print("ATTENTION : Graphviz (dot) n'est pas installé ou introuvable.")
    print("Sous Ubuntu/WSL : sudo apt install graphviz")
    print("Sous Windows : https://graphviz.org/download/")

class automate:
    """
    classe de manipulation des automates
    l'alphabet est l'ensemble des caractères alphabétiques minuscules et "E" pour epsilon, 
    et "O" pour l'automate vide
    """
    
    def __init__(self, expr="O"):
        """
        construit un automate élémentaire pour une expression régulière expr 
            réduite à un caractère de l'alphabet, ou automate vide si "O"
        identifiant des états = entier de 0 à n-1 pour automate à n états
        état initial = état 0
        """
        
        # alphabet
        self.alphabet = list("abc")
        # l'expression doit contenir un et un seul caractère de l'alphabet
        if expr not in (self.alphabet + ["O", "E"]):
            raise ValueError("l'expression doit contenir un et un seul\
                           caractère de l'alphabet " + str(self.alphabet))
        # nombre d'états
        if expr == "O":
            # langage vide
            self.n = 1
        elif expr == "E":
            self.n = 1
        else:
            self.n = 2
        # états finals: liste d'états (entiers de 0 à n-1)
        if expr == "O":
            self.final = []
        elif expr == "E":
            self.final = [0]
        else:
            self.final = [1]
        # transitions: dico indicé par (état, caractère) qui donne la liste des états d'arrivée
        self.transition =  {} if (expr in ["O", "E"]) else {(0,expr): [1]}
        # nom de l'automate: obtenu par application des règles de construction
        self.name = "" if expr == "O" else "(" + expr + ")" 
        
    def __str__(self):
        """affichage de l'automate par fonction print"""
        res = "Automate " + self.name + "\n"
        res += "Nombre d'états " + str(self.n) + "\n"
        res += "Etats finals " + str(self.final) + "\n"
        res += "Transitions:\n"
        for k,v in self.transition.items():    
            res += str(k) + ": " + str(v) + "\n"
        res += "*********************************"
        return res
    
    def ajoute_transition(self, q0, a, qlist):
        """ ajoute la liste de transitions (q0, a, q1) pour tout q1 
            dans qlist à l'automate
            qlist est une liste d'états
        """
        if not isinstance(qlist, list):
            raise TypeError("Erreur de type: ajoute_transition requiert une liste à ajouter")
        if (q0, a) in self.transition:
            self.transition[(q0, a)] = self.transition[(q0, a)] + qlist
        else:
            self.transition.update({(q0, a): qlist})

    def to_graphviz(self, filename):
        """ Génère une image de l'automate via Graphviz """
        if not GRAPHVIZ_AVAILABLE:
            return None
        
        try:
            dot = Digraph(comment=self.name, format='png')
            dot.attr(rankdir='LR') # De gauche à droite
            
            # Point invisible pour pointer vers l'état initial (0)
            dot.node('start', style='invisible', shape='point')
            dot.edge('start', '0')

            # Création des noeuds
            for i in range(self.n):
                if i in self.final:
                    dot.node(str(i), shape='doublecircle') # Etat final
                else:
                    dot.node(str(i), shape='circle') # Etat normal

            # Création des arêtes (transitions)
            for (src, char), dests in self.transition.items():
                label = "ε" if char == "E" else char
                for dest in dests:
                    dot.edge(str(src), str(dest), label=label)
            
            # Rendu du fichier
            # Graphviz ajoute automatiquement l'extension .png au nom de fichier
            output_path = dot.render(filename, cleanup=True)
            return output_path
        except Exception as e:
            print(f"\n[ERREUR] Impossible de générer l'image pour {filename}.")
            print(f"Cause : {e}")
            print("Vérifiez que le chemin GRAPHVIZ_PATH ligne 9 est correct.")
            return None
    
    
def _clone_with_offset(a, offset):
    """Clone l'automate a en renumérotant chaque état q -> q+offset.
       Retourne un nouvel automate 'b' en tant qu'instance automatique (structure compatible)."""
    b = automate()  # initial temporaire, on va remplacer champs
    b = cp.deepcopy(b)
    b.name = a.name
    b.n = a.n + offset
    # finals
    b.final = [q + offset for q in a.final]
    # transitions
    b.transition = {}
    for (q, c), dests in a.transition.items():
        b.transition[(q + offset, c)] = [d + offset for d in dests]
    b.alphabet = list(a.alphabet)
    return b

def concatenation(a1, a2): 
    """Retourne l'automate qui reconnaît la concaténation des 
    langages reconnus par les automates a1 et a2"""
    # cas simples: si première est vide => vide
    if a1.final == []:
        return cp.deepcopy(a1)
    # si a2 est vide => vide
    if a2.final == []:
        return cp.deepcopy(a2)
    # clone a2 avec offset
    offset = a1.n
    b2 = _clone_with_offset(a2, offset)
    res = automate()
    res = cp.deepcopy(res)
    # nom
    res.name = "(" + a1.name + "." + a2.name + ")"
    # états totaux
    res.n = a1.n + a2.n
    # finals = finals de b2 renommé
    res.final = list(b2.final)
    # trans = union des transitions (copie)
    res.transition = {}
    for k,v in a1.transition.items():
        res.transition[k] = list(v)
    for k,v in b2.transition.items():
        res.transition[k] = list(v)
    # ajouter epsilon transitions des finals de a1 vers le start renommé (offset + 0)
    for f in a1.final:
        res.ajoute_transition(f, "E", [offset + 0])
    # alphabet (on garde a1.alphabet standard)
    res.alphabet = list(a1.alphabet)
    return res


def union(a1, a2):
    """Retourne l'automate qui reconnaît l'union des 
    langages reconnus par les automates a1 et a2""" 
    # si l'un est vide, retourner copie de l'autre mais en renommant pour garder la forme
    if a1.final == []:
        return cp.deepcopy(a2)
    if a2.final == []:
        return cp.deepcopy(a1)
    # renumérotation: on va créer un nouvel état 0 (start), puis a1 puis a2 puis état final
    offset1 = 1
    b1 = _clone_with_offset(a1, offset1)
    offset2 = offset1 + a1.n
    b2 = _clone_with_offset(a2, offset2)
    # nouvel automate
    res = automate()
    res = cp.deepcopy(res)
    res.name = "(" + a1.name + "+" + a2.name + ")"
    # nouvel état final
    final_index = offset2 + a2.n
    res.n = final_index + 1
    # transitions = union des transitions
    res.transition = {}
    for k,v in b1.transition.items():
        res.transition[k] = list(v)
    for k,v in b2.transition.items():
        res.transition[k] = list(v)
    # ajouter epsilon du nouvel état 0 vers starts de b1 et b2
    res.ajoute_transition(0, "E", [b1_index := 0 + offset1, b2_index := 0 + offset2])
    # epsilon des finals de b1 et b2 vers final_index
    for f in b1.final:
        res.ajoute_transition(f, "E", [final_index])
    for f in b2.final:
        res.ajoute_transition(f, "E", [final_index])
    res.final = [final_index]
    res.alphabet = list(a1.alphabet)
    return res


def etoile(a):
    """Retourne l'automate qui reconnaît l'étoile de Kleene du 
    langage reconnu par l'automate a""" 
    # cas particulier: O* = {epsilon}
    if a.final == []:
        # construire un automate qui accepte epsilon
        b = automate("E")
        return b
    # on crée nouvel état 0 (start) et état final f en fin
    offset = 1
    b = _clone_with_offset(a, offset)
    new_final = offset + a.n
    res = automate()
    res = cp.deepcopy(res)
    res.name = "(" + a.name + ")*"
    res.n = new_final + 1
    # copier transitions
    res.transition = {}
    for k,v in b.transition.items():
        res.transition[k] = list(v)
    # epsilon du nouvel état 0 vers le start de b et vers new_final
    res.ajoute_transition(0, "E", [offset + 0, new_final])
    # epsilon des finals de b vers start de b et vers new_final
    for f in b.final:
        res.ajoute_transition(f, "E", [offset + 0, new_final])
    res.final = [new_final]
    res.alphabet = list(a.alphabet)
    return res


def acces_epsilon(a):
    """ retourne la liste pour chaque état des états accessibles par epsilon
        transitions pour l'automate a
        res[i] est la liste des états accessible pour l'état i
    """
    # on initialise la liste résultat qui contient au moins l'état i pour chaque état i
    res = [[i] for i in range(a.n)]
    for i in range(a.n):
        candidats = list(range(i)) + list(range(i+1, a.n))
        new = [i]
        while True:
            # liste des epsilon voisins des états ajoutés en dernier:
            voisins_epsilon = []
            for e in new:
                if (e, "E") in a.transition.keys():
                    voisins_epsilon += [j for j in a.transition[(e, "E")]]
            # on calcule la liste des nouveaux états:
            new = list(set(voisins_epsilon) & set(candidats))
            # si la nouvelle liste est vide on arrête:
            if new == []:
                break
            # sinon on retire les nouveaux états ajoutés aux états candidats
            candidats = list(set(candidats) - set(new))
            res[i] += new 
    return res


def supression_epsilon_transitions(a):
    """ retourne l'automate équivalent sans epsilon transitions
    """
    # on copie pour éviter les effets de bord     
    a = cp.deepcopy(a)
    res = automate()
    res.name = a.name
    res.n = a.n
    res.final = a.final
    # pour chaque état on calcule les états auxquels il accède
    # par epsilon transitions.
    acces = acces_epsilon(a)
    # on retire toutes les epsilon transitions
    res.transition = {c: j for c, j in a.transition.items() if c[1] != "E"}
    for i in range(a.n):
        # on ajoute i dans les états finals si accès à un état final:
        if (set(acces[i]) & set(a.final)):
            if i not in res.final:
                res.final.append(i)
        # on ajoute les nouvelles transitions en parcourant toutes les transitions
        for c, v in a.transition.items():
            if c[1] != "E" and c[0] in acces[i]:
                res.ajoute_transition(i, c[1], v)
    return res
        
        
def determinisation(a):
    """ retourne l'automate équivalent déterministe
        la construction garantit que tous les états sont accessibles
        automate d'entrée sans epsilon-transitions
    """
    # mapping: frozenset(d'états NFA) -> état int dans DFA
    start_set = frozenset([0])  # état initial 0 dans la convention NFA (ici on suppose pas d'epsilons)
    # cependant si epsilon transitions existaient, supression_epsilon_transitions doit être appelée avant
    # on va quand même chercher l'ensemble initial comme {0}
    mapping = {start_set: 0}
    inv = [start_set]
    trans = {}
    finals = []
    queue = deque([start_set])
    while queue:
        S = queue.popleft()
        sid = mapping[S]
        trans.setdefault(sid, {})
        # pour chaque symbole de l'alphabet
        for c in a.alphabet:
            dest_set = set()
            for q in S:
                dests = a.transition.get((q, c), [])
                for d in dests:
                    dest_set.add(d)
            dest_fs = frozenset(dest_set)
            if dest_fs not in mapping:
                mapping[dest_fs] = len(inv)
                inv.append(dest_fs)
                queue.append(dest_fs)
            trans[sid][c] = mapping[dest_fs]
        # finals: si S contient un état final du NFA
        if any((q in a.final) for q in S):
            finals.append(sid)
    # construction du nouvel automate déterministe
    res = automate()
    res = cp.deepcopy(res)
    res.name = a.name
    res.n = len(inv)
    res.transition = {}
    for s, m in trans.items():
        for c, dest in m.items():
            # stockage sous la forme attendue: liste d'un élément
            res.transition[(s, c)] = [dest]
    res.final = list(set(finals))
    res.alphabet = list(a.alphabet)
    return res
    
    
def completion(a):
    """ retourne l'automate a complété
        l'automate en entrée doit être déterministe
    """
    res = cp.deepcopy(a)
    # vérifier chaque paire (q,c)
    sink = None
    for q in range(res.n):
        for c in res.alphabet:
            if (q, c) not in res.transition:
                if sink is None:
                    sink = res.n
                    # créer les transitions du sink vers lui-même
                    for cc in res.alphabet:
                        res.transition[(sink, cc)] = [sink]
                    # incrémenter le nombre d'états
                    res.n = sink + 1
                res.transition[(q, c)] = [sink]
    return res


def minimisation(a):
    """ retourne l'automate minimum
        a doit être déterministe complet
        algo par raffinement de partition (algo de Moore)
    """
    # on copie pour éviter les effets de bord     
    a = cp.deepcopy(a)
    res = automate()
    res.name = a.name
    
    # Étape 1 : partition initiale = finaux / non finaux
    part = [set(a.final), set(range(a.n)) - set(a.final)]
    # on retire les ensembles vides
    part = [e for e in part if e != set()]  
    
    # Étape 2 : raffinement jusqu’à stabilité
    modif = True
    while modif:
        modif = False
        new_part = []
        for e in part:
            # sous-ensembles à essayer de séparer
            classes = {}
            for q in e:
                # signature = tuple des indices des blocs atteints pour chaque lettre
                signature = []
                for c in a.alphabet:
                    for i, e2 in enumerate(part):
                        if a.transition[(q, c)][0] in e2:
                            signature.append(i)
                # on ajoute l'état q à la clef signature calculée
                classes.setdefault(tuple(signature), set()).add(q)
            if len(classes) > 1:
                # s'il y a >2 signatures différentes on a séparé des états dans e
                modif = True
                new_part.extend(classes.values())
            else:
                new_part.append(e)
        part = new_part
    # on réordonne la partition pour que le premier sous-ensemble soit celui qui contient l'état initial
    for i, e in enumerate(part):
        if 0 in e:
            part[0], part[i] = part[i], part[0]
            break
 
     
    # Étape 3 : on construit le nouvel automate minimal
    mapping = {}
    # on associe à chaque état q le nouvel état i
    # obtenu comme étant l'indice du sous-ensemble de part
    for i, e in enumerate(part):
        for q in e:
            mapping[q] = i

    res.n = len(part)
    res.final = list({mapping[q] for q in a.final if q in mapping})
    for i, e in enumerate(part):
        # on récupère un élément de e:
        representant = next(iter(e))
        for c in a.alphabet:
            q = a.transition[(representant, c)][0]
            res.transition[(i, c)] = [mapping[q]]
    return res

def tout_faire(a):
    a1 = supression_epsilon_transitions(a)
    a2 = determinisation(a1)
    a3 = completion(a2)
    a4 = minimisation(a3)
    return a4


def egal(a1, a2):
    """ retourne True si a1 et a2 reconnaissent le même langage
        On suppose a1 et a2 déterministes et complets (ou bien passer par tout_faire)
    """
    # s'assurer que même alphabet (on suppose ["a","b","c"])
    alpha = a1.alphabet
    # BFS sur le produit
    start = (0, 0)
    visited = set([start])
    stack = [start]
    while stack:
        q1, q2 = stack.pop()
        final1 = q1 in a1.final
        final2 = q2 in a2.final
        if final1 != final2:
            return False
        for c in alpha:
            t1 = a1.transition.get((q1, c), [None])[0]
            t2 = a2.transition.get((q2, c), [None])[0]
            # si transition manquante, on considère None (mais en pratique, should be completed)
            if t1 is None or t2 is None:
                # si l'un est None (non défini) mieux vaut appeler tout_faire avant egal
                # on considère qu'absence => langage différent potentiellement
                return False
            pair = (t1, t2)
            if pair not in visited:
                visited.add(pair)
                stack.append(pair)
    return True


# --- FONCTIONS POUR LE PDF ---

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 15)
        self.cell(0, 10, 'Rapport de Projet: Automates', border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Helvetica', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 6, title, border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='L', fill=True)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Helvetica', '', 12)
        self.multi_cell(0, 5, body)
        self.ln()

    def add_image(self, img_path, w=100):
        if img_path and os.path.exists(img_path):
            self.image(img_path, w=w)
            self.ln()
        else:
            self.set_text_color(255, 0, 0)
            self.cell(0, 10, "Image introuvable (Erreur Graphviz)", border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_text_color(0, 0, 0)


def generer_rapport_pdf():
    if not GRAPHVIZ_AVAILABLE:
        print("Impossible de générer le PDF sans graphviz et fpdf")
        return

    pdf = PDFReport()
    pdf.add_page()

    # Création des automates de test
    a = automate("a")
    b = automate("b")
    
    # 1. Concaténation
    cat = concatenation(a, b)
    cat_img = cat.to_graphviz("graph_concat")
    
    pdf.chapter_title("1. Test Concatenation (a.b)")
    pdf.chapter_body(f"Automate résultant de a.b :\n{cat}")
    pdf.add_image(cat_img)

    # 2. Union
    uni = union(a, b)
    uni_img = uni.to_graphviz("graph_union")
    
    pdf.chapter_title("2. Test Union (a+b)")
    pdf.chapter_body(f"Automate résultant de a+b :\n{uni}")
    pdf.add_image(uni_img)

    # 3. Etoile
    st = etoile(a)
    st_img = st.to_graphviz("graph_star")
    
    pdf.chapter_title("3. Test Etoile (a*)")
    pdf.chapter_body(f"Automate résultant de a* :\n{st}")
    pdf.add_image(st_img)

    # 4. Determinisation
    pdf.add_page()
    det = determinisation(union(a,concatenation(a,b)))   # a + ab
    det_img = det.to_graphviz("graph_star")
    
    pdf.chapter_title("3. Test Determinisation (a+b)*.c")
    pdf.chapter_body(f"Automate résultant de (a+b)*;c :\n{det}")
    pdf.add_image(det_img)


    # 5. Completion
    com = completion(etoile(a))  # a*
    com_img = com.to_graphviz("graph_star")
    
    pdf.chapter_title("3. Test Completion (a+b)*.c")
    pdf.chapter_body(f"Automate résultant de (a+b)*;c :\n{com}")
    pdf.add_image(com_img)

    # 6. Test Egalité
    pdf.add_page()
    pdf.chapter_title("6. Test d'Egalite")
    
    A = tout_faire(concatenation(etoile(union(a, b)), automate("c")))   # (a+b)* . c
    B = tout_faire(union(concatenation(etoile(a), automate("c")), concatenation(etoile(b), automate("c"))))  # a*.c + b*.c
    
    A_img = A.to_graphviz("graph_A")
    B_img = B.to_graphviz("graph_B")
    
    resultat = egal(A, B)
    
    pdf.chapter_body("Comparaison de A = (a+b)*.c et B = a*.c + b*.c")
    pdf.chapter_body("Automate A (minimisé) :")
    pdf.add_image(A_img)
    pdf.chapter_body("Automate B (minimisé) :")
    pdf.add_image(B_img)
    
    result_text = "EGAL" if resultat else "NON EGAL"
    if resultat:
        pdf.set_text_color(0, 100, 0)
    else:
        pdf.set_text_color(150, 0, 0)
    
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, f"RESULTAT: {result_text}", border=0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)

    # Sauvegarde
    pdf.output("rapport_projet.pdf")
    print("\n---------------------------------------------------------")
    print("PDF généré avec succès : rapport_projet.pdf")
    print("---------------------------------------------------------")
    
    # Nettoyage des fichiers temporaires (optionnel)
    # for f in ["graph_concat.png", "graph_union.png", "graph_star.png", "graph_no_eps.png", "graph_A.png", "graph_B.png"]:
    #    if os.path.exists(f): os.remove(f)


if __name__ == "__main__":
    print("=== Exécution des tests et génération du PDF ===")
    generer_rapport_pdf()
