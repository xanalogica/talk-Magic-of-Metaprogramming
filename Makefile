all:	index.html

index.html: talk-Magic-of-Metaprogramming.rst
	rst2s5.py -v --theme-url=slidetheme talk-Magic-of-Metaprogramming.rst index.html
