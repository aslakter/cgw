#!/usr/bin/env python2
# 6.863 CGW Spring 2009 - Team 12 kuat/advay
# Created: Advay Mengle on Mar 6 2009
# Modified for CGW by yks

# Usage: python drawtrees.py [sentence ids] < parsedsentencefile
#  * sentence ids is an optional spaced list of sentence numbers
#    to display, indexed starting at 1.  When no list is specified
#    all sentences are drawn.
#  * parsedsentencefile is the bracketed parse tree output of ./parse
# 
# TYPICAL USAGE:
# 1. Generate a grammar file:
# ~> cat S1.gr S1_Vocab.gr S2.gr S2_Vocab.gr TopNo2.gr > GRAMMAR.gr
# 2. Parse the sentences into s-expressions.
# ~> cat examples.sen | ./parse -g GRAMMAR.gr > training_examples.txt
# 3. Draw the trees
# ~> python drawtrees.py < training_examples.txt

from nltk.draw.tree import draw_trees
from nltk.tree import Tree
import sys

args = sys.argv[1:len(sys.argv)]

tt = []
c = 0
for l in sys.stdin:
	c = c + 1
	if ((len(args) == 0) or (str(c) in args)):
		try:
			t = Tree.fromstring(l, remove_empty_top_bracketing=True)
			tt.append(t)
		except:
			print "encountered failure on sentence " + str(c)
	
apply(draw_trees,tt)
