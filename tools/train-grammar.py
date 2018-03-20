#!/usr/bin/env python2
#
# A tool useful for estimating the weight (or probability) of grammar productions
# given a "treebank" (a collection of known parsed s-expressions.)
#
# For example, the s-expression for "man walked on the moon" look like this:
# (S (NP (N man)) (VP (VBD walked) (PP (IN on) (NP (Det "the") (NNP "Moon")))))
#
# This script outputs 100-normalized weights of rule productions 
# using the parse trees in the input tree-bank.  
#
# Example output:
#
# S -> NP VP   1
# NP -> N      1
# N -> "man"   1
# VP -> VBD PP 1
# ...
#
# Usage:
#    $0 -t <tree bank file> -i <input grammar file> -o <output grammar file>
#
# <input grammar file> and <output grammar file> are optional
# but if specified should both be of CGW format:
# i.e.  <weight><tab><LHS nonterminal><tab><RHS>
#
# If -i <input grammar file> is specified, then the program will attempt to annotate
# the input file with the learned 100-normed weights.  Note: this program does not check
# for duplicate rules.   If S -> NP VP occurs twice in your input grammar file, you may
# risk annotating the same weight twice, causing an incorrect rule assignment.
#
# If -o <output grammar file> is not specified, then <input grammar file>.tuned would be used
# as the output.
#
# Author: yks
#
import nltk
import sys
import re
from optparse import OptionParser

def tree_from_sexp(sexp):
    """
    parses an s-expression into a tree
    """
    return nltk.Tree.fromstring(sexp, remove_empty_top_bracketing=True)

def train(training):
    """
    Generate maximum likelihood estimates of
    productions from a training file of s-expression trees.
    """
    tfd = open(options.training)
    parses = tfd.readlines()
    parses = [parse.strip() for parse in parses]
    
    counts = {}
    for parse in parses:
	if parse != "failure":
	    tree = tree_from_sexp(parse)
	    productions = tree.productions()
	    for production in productions:
		if not counts.has_key(production):
		    counts[production] = 0
		counts[production] += 1

    lhs_map = {}
    for production in counts.keys():
	if not lhs_map.has_key(production.lhs()):
	    lhs_map[production.lhs()] = []
	lhs_map[production.lhs()].append(production)

    keys = lhs_map.keys()
    keys.sort()

    weights = {}
    for key, productions in lhs_map.items():
	total = 0;
	for production in productions:
	    total += counts[production]

	for production in productions:
	    weights[production] = max(1,
				      int(counts[production]/float(total)*100))
    regexp_hash = {}
    for key in keys:
	productions = lhs_map[key]
	for production in productions:
	    rhs_symbols = [str(nt) for nt in production.rhs()]
	    string_symbols = ' '.join(rhs_symbols)
	    string_symbols = re.escape(string_symbols)
	    regexp = "^\\d+\\s+%s\\s+%s$" %(production.lhs(), string_symbols)
					    
	    regexp_hash[regexp] = production
    return weights, regexp_hash, lhs_map

def replace_weights(regexp_hash, weights, input_file, output_file, normalize=False):
    if normalize:
	lines = normalize_grammar(input_file)
    else:
	ifd = open(input_file)
	lines = ifd.readlines()
	lines = [line.strip() for line in lines]
	ifd.close()

    ofd = open(output_file, "w")

    for line in lines:
	if re.match("^\s*#", line) or re.match("^\s*$", line):
	    ofd.write(line + "\n")
	else:
	    replaced = False
	    for regexp, production in regexp_hash.items():
		if re.match(regexp, line):
		    rhs_symbols = [str(nt) for nt in production.rhs()]
		    replacement = "%d\t%s\t%s" %(weights[production],
						   production.lhs(),
						   ' '.join(rhs_symbols))
		    ofd.write(replacement)
		    ofd.write("\n")
		    print "Replaced: [%s] with [%s]" %(line, replacement)
		    replaced = True
		    break

	    if not replaced:
		print "WARNING: missing training data for: %s" %(line)
		ofd.write(line)
		ofd.write("\n")
    ofd.close()
		
def print_weights(lhs_map, weights):
    keys = lhs_map.keys()
    keys.sort()
    for key in keys:
	productions = lhs_map[key]
	print "#"
	for production in productions:
	    rhs_symbols = [str(nt) for nt in production.rhs()]
	    print "%d\t%s\t%s" %(weights[production],
				      production.lhs(),
				      ' '.join(rhs_symbols))

def uniq(seq):
    # order preserving
    checked = []
    for e in seq:
	if e not in checked:
            checked.append(e)
    return checked

def normalize_grammar(grammar_file):
    """
    Method for taking a grammar
    finding all the rules, and outputting
    the rules as having weight of 1.
    """
    
    fd = open(grammar_file)
    lines = fd.readlines()
    lines = [line.strip() for line in lines]

    rules = []

    for line in lines:
	if re.match("^\s*#", line) or re.match("^\s*$", line):
	    continue

	parts = line.split("\t")
	if len(parts) < 3:
	    print "ERROR: improperly formatted line: %s" %(line)
	    continue

	score = parts[0]
	lhs = parts[1]
	rhs = parts[2]

	rules.append("%d\t%s\t%s" %(1, lhs, rhs))

    rules.sort()
    rules = uniq(rules)
    return rules

if __name__ == "__main__":

    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input",
		      help="input grammar filename", metavar="file")
    parser.add_option("-o", "--output", dest="output",
		      help="output grammar filename", metavar="file")
    parser.add_option("-t", "--training", dest="training",
		      help="s-expression training filename",metavar="file")
    parser.add_option("-n", "--normalize", dest="normalize",
		      help="normalize the input grammar before annotating", default=False,
		      metavar="False")
    (options, args) = parser.parse_args()

    if options.training is None:
	parser.print_help()
	exit(1)

    weights, regexp_hash, lhs_map = train(options.training)
    if options.input is None:
	print_weights(lhs_map, weights)
    else:
	if options.output is None:
	    options.output = options.input + ".tuned"
	print "reading grammar file: %s" %(options.input)
	print "outputting to file: %s" %(options.output)
	print "normalize: %s" %(options.normalize)
	replace_weights(regexp_hash, weights,
			options.input, options.output, options.normalize)	
