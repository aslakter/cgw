#!/usr/bin/env python2
#
# A Part of speech tagger for cgw vocabulary files.
# - usage:
#   $0 -f <sentence file> -v <vocabulary grammar file>
# - example:
#   $0 -f examples.sen -v S1_Vocab.gr 
# - outputs sentences with tokens associated with their part of speech
# and all possible POS tag sequences (when words have multiple POS tags).
#
# author: gabi, yks
#
import re
from nltk.util import bigrams, trigrams
from optparse import OptionParser

def load_vocab(VocabFileName):
  """
  load the vocabulary file into a has table
  """
  vocab_hash = {}
  f = open(VocabFileName,"r")
  for line in f:
    line = line.strip()
    if line and (not line.startswith("#")):
      line_arr = re.split('\s',line,2)
      count = line_arr[0]
      pos_tag = line_arr[1]
      terminal = line_arr[2]
      if not vocab_hash.has_key(terminal): 
        vocab_hash[terminal] = []
      if vocab_hash[terminal].count(pos_tag) == 0:
        vocab_hash[terminal].append(pos_tag)
  return vocab_hash

def get_pos(vocab_hash, words_list):
  word_hash = {}
  for token in words_list:
      if type(token).__name__=='list' or  type(token).__name__=='tuple':
	  ngram = ' '.join(token)
      else:
	  ngram = token

      if vocab_hash.has_key(ngram):
	if not word_hash.has_key(ngram):
	  word_hash[ngram] = vocab_hash[ngram]
  return word_hash

def generate_all_paths(tags):
    if len(tags) == 1:
	return [tags[0]]
    else:
	sublists = generate_all_paths(tags[1:])
	lists = []
	for t in tags[0]:
	    for lst in sublists:
		lists.append([t] + lst)
	return lists
    
def pos_tags(vocab_hash,sentence):  
  sentence = sentence.split()
  unigram_hash = get_pos(vocab_hash,sentence)
  bigram_hash = get_pos(vocab_hash,bigrams(sentence))
  trigram_hash = get_pos(vocab_hash,trigrams(sentence))
  pos_tags = []
  ngram_to_tag = {}
  ngram_ordering = []
  for i in xrange(len(sentence)):
    word = sentence[i]
    if unigram_hash.has_key(word):
	tag = unigram_hash[word]
	pos_tags.append(tag)
	ngram_to_tag[word] = tag
	ngram_ordering.append(word)
    elif i < len(sentence)-1:
	bigram = sentence[i] + " " + sentence[i+1]
	if bigram_hash.has_key(bigram):
	    tag = bigram_hash[bigram]
	    pos_tags.append(tag)
	    ngram_to_tag[bigram] = tag
	    ngram_ordering.append(bigram)
	    i += 1
	elif (i < len(sentence)-2):
	    trigram = " ".join(sentence[i:i+2])
	    if trigram_hash.has_key(trigram):
		tag = trigram_hash[trigram]
		pos_tags.append(tag)
		ngram_to_tag[trigram] = tag
		ngram_ordering.append(trigram)
		i += 2
  return pos_tags, ngram_to_tag, ngram_ordering

def main():
  parser = OptionParser()
  parser.add_option("-f", "--file", dest="fileName",
		    help="sentences file name", metavar="file")
  parser.add_option("-v", "--vocab-file",
		    dest="vocabFileName",
		    help="vocabulary file name",metavar="file")
      
  (options, args) = parser.parse_args()

  if options.vocabFileName is None:
      parser.print_help()
      exit(1)

  if options.fileName is None:
    sents = ["Arthur is the king and Sir Lancelot is not ."]
  else:
    f = open(options.fileName,"r")
    sents = f.readlines()
    sents = [sent.strip() for sent in sents]
  
  vocab_hash = load_vocab(options.vocabFileName)
  for sent in sents:
    print "#" + "="*(len(sent)+12)
    print "# Sentence: ", sent
    tags, ngram_to_tags, ngram_ordering = pos_tags(vocab_hash, sent)
    candidates = generate_all_paths(tags)
    
    for ngram in ngram_ordering:
	print "# %s => %s" %(ngram, ngram_to_tags[ngram])
    i = 1
    for candidate in candidates:
	print "# POS[%d]: %s" %(i, " ".join(candidate))
	i += 1
    print "#" + "="*(len(sent)+12)	

if __name__ == '__main__': main()
