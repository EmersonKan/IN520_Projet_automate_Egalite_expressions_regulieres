LEX = flex
YACC = bison
CC = gcc

all: regexp

regexp: regexp.l regexp.y
	$(LEX) regexp.l
	$(YACC) -d regexp.y
	$(CC) lex.yy.c regexp.tab.c -lfl -o regexp

run:
	./regexp < test.1
	python3 main.py

clean:
	rm -f lex.yy.c regexp.tab.c regexp.tab.h regexp main.py

zip:
	zip IN520_Projet_Python.zip *.py *.l *.y Makefile test.1 README.txt
