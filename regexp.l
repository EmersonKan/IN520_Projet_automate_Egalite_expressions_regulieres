%{
#include "regexp.tab.h"
%}

%%

"("             {printf("Lexer: PAR_O\n");return PAR_O;}
")"             {printf("Lexer: PAR_F\n");return PAR_F;}
"+"             {printf("Lexer: +\n");return PLUS;}
"*"             {printf("Lexer: *\n");return STAR;}
"."             {printf("Lexer: .\n");return DOT;}
"E"             {printf("Lexer: epsilon\n");return EPS;}
[a-c]           { yylval.str = strdup(yytext);printf("Lexer: CHAR(%s)\n", yytext); return CHAR; }
[ \t\r]+        ;        /* ignorer espaces et tabulations */
\n              { printf("Lexer: NEWLINE\n"); return '\n'; }  /* retourner le token newline */
.               { fprintf(stderr, "Caractère invalide: %s\n", yytext); exit(1); }

%%
