TEXFLAGS = -shell-escape
PDFLATEX = pdflatex

.PHONY: kivy all doc dist clean cleanall

kivy: kivy.tex
	$(PDFLATEX) $(TEXFLAGS) kivy.tex

all: kivy

clean:
	@$(RM) *.aux *.log *.out *.toc *.fdb_latexmk *.ilg *.glo *.gls *.lol

cleanall: clean

