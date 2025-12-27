%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int yylex(void);
void yyerror(const char *s);

int cpt = 0;
int nb_lignes = 0;

FILE *out;

char *new_var() {
    char *s = malloc(16);
    sprintf(s, "a%d", cpt++);
    return s;
}
%}

%union { char *str; }

%token <str> CHAR
%token EPS
%token PAR_O PAR_F PLUS STAR DOT
%type <str> expr concat term atom

%left PLUS
%left DOT
%right STAR

%%

start:
    lignes
;

lignes:
    lignes ligne
  | ligne
;

ligne:
    expr '\n' {
        nb_lignes++;

        if (nb_lignes == 1) {
            fprintf(out, "res1 = tout_faire(%s)\n\n", $1);
        }
        else if (nb_lignes == 2) {
            fprintf(out, "res2 = tout_faire(%s)\n\n", $1);
            fprintf(out,
                "if egal(res1,res2):\n"
                "    print('EGAL')\n"
                "else:\n"
                "    print('NON EGAL')\n"
            );
        }
    }
;


expr:
    expr PLUS concat
    {
        char *v = new_var();
        fprintf(out, "%s = union(%s,%s)\n", v, $1, $3);
        $$ = v;
    }
  | expr concat
    {
        /* Concaténation implicite */
        char *v = new_var();
        fprintf(out, "%s = concatenation(%s,%s)\n", v, $1, $2);
        $$ = v;
    }
  | concat
;

concat:
    concat DOT term {
        char *v = new_var();
        fprintf(out, "%s = concatenation(%s,%s)\n", v, $1, $3);
        $$ = v;
    }
  | term { $$ = $1; }
;

term:
    atom STAR {
        char *v = new_var();
        fprintf(out, "%s = etoile(%s)\n", v, $1);
        $$ = v;
    }
  | atom { $$ = $1; }
;

atom:
    CHAR {
        char *v = new_var();
        fprintf(out, "%s = automate(\"%s\")\n", v, $1);
        $$ = v;
    }
  | EPS {
        char *v = new_var();
        fprintf(out, "%s = automate(\"E\")\n", v);
        $$ = v;
    }
  | PAR_O expr PAR_F { $$ = $2; }
;

%%

void yyerror(const char *s) {
    fprintf(stderr, "Erreur syntaxe: %s\n", s);
}

int main() {
    out = fopen("main.py","w");
    fprintf(out,"from automate import *\n\n");

    yyparse(); // lit toutes les lignes d'expressions

    fclose(out);
    return 0;
}
