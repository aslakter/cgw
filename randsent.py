#!/usr/bin/env python2

import argparse
import random

# Parse arguments.  You should not need to modify this.
parser = argparse.ArgumentParser()
parser.add_argument("grammar", help="path to grammar file")
parser.add_argument("count", type=int, help="number of sentences to generate", nargs='?', default=1)
parser.add_argument("-t", "--tree", action='store_true', help="pretty-print tree form instead of printing sentence")
parser.add_argument("--seed", type=int, default=0, help="RNG seed")
args = parser.parse_args()

# Create a random generator.
rng = random.Random(args.seed)

# Here's how to access the args.  (You won't print them in your actual program.)
#print 'path to grammar file:', args.grammar
#print 'count:', args.count
#print 'print tree?', args.tree
#print 'RNG seed:', args.seed

# Like the functions below from problems 1 and 2
# This kicks off the recursive calls to expandWithTree
# Returns the "tree" of the sentence as defined in the handout.
def makeTree(rules, rand):
  tree = "(START"
  chosenRule = chooseRuleWithProbability(rules, 'START', rand)
  firstExpansion = chosenRule
  tree += expandWithTree(rules, firstExpansion, rand)
  return tree

# Recursively expand the non-terminals probabilistically with weights and expansion
# rules as defined in the provided grammar file.
# Returns the tree structure string of the produced sentence.
def expandWithTree(rules, rule, rand):
  out = ""
  # print rule
  lastWasTerm = False
  for word in rule[0]:
    if not rules.has_key(word):
      out += " " + word
    else:
      chosenRule = chooseRuleWithProbability(rules, word, rand)
      nextRule = chosenRule # following is from part 1 rules[word][rand.randint(0, len(rules[word]) - 1)]
      # print nextRule
      out += " (" + word + expandWithTree (rules, nextRule, rand)
  out += ")"
  return out

### PROBLEM 1/2 CODE BELOW

# Kicks off the recursive calls to expand
def generate(rules, rand):
  sentence = ""
  #x = rand.randint(0, len(rules['START']))
  # print x
  chosenRule = chooseRuleWithProbability(rules, 'START', rand)
  firstExpansion = chosenRule
  # firstExpansion = rules['START'][rand.randint(0, len(rules['START']) - 1)]
  sentence = expand(rules, firstExpansion, rand)
  return sentence

# given the LHS of a rule (word), choose the RHS
# according to the relative probabilities of each RHS
# as defined in the grammar file
def chooseRuleWithProbability(rules, word, rand):
  cumulativeSum = 0
  print ("in choose: ", rules[word])
  for (rhs, prob) in rules[word]:
    cumulativeSum += float(prob)
  threshold = rand.uniform(0, 1)
  runningSum = 0

  # choose a random rule by sequentially summing
  # the relative probabilities of the rules and
  # comparing that sum to a randomly chosen threshold value
  # whichever rule adds the amount of probability that causes
  # the running sum to pass the threshold is the
  # chosen rule

  for (rhs, prob) in rules[word]:
    print (rhs, prob)
    runningSum += (float(prob) / float(cumulativeSum))
    print (runningSum, threshold)
    if runningSum > threshold:
      return (rhs, prob)

#Recurse through the rules expanding left to right
#randomly choosing which acceptable rule we expand to given the lefthand side
def expand(rules, rule, rand):
  out = ""
  # print rule
  for word in rule[0]:
    if not rules.has_key(word):
      if out == "":
        out += word
      else:
        out += " " + word
    else:
      chosenRule = chooseRuleWithProbability(rules, word, rand)
      nextRule = chosenRule # following is from part 1 rules[word][rand.randint(0, len(rules[word]) - 1)]
      if out == "":
        out += expand(rules, nextRule, rand)
      else:
        out += " " + expand (rules, nextRule, rand)
  return out


# Print out the grammar.  You'll replace the loop body.
with open(args.grammar, 'r') as grammar_file:
  rules = {}
  for line in grammar_file:
    words = line.split()
    if (len(words) > 0):
      #ignore the comments
      if (words[0] == "#" or words[0].startswith("#")):
        continue
      # given the formatting: weight, LHS, RHS
      # abstract the rules to a map where LHS is the key
      # and the value is a list of tuples where the tuple contains
      # the RHS (in list form) and the weight of that rule.
      else:
        # print words
        weight = words[0]
        key = words[1]
        #add a new non-terminal
        if not (rules.has_key(key)):
          rules[key] = []
        newRule = []
        for i in range(2, len(words)):
          #ignore inline comments
          if not (words[i] == "#" or words[i].startswith("#")):
            newRule.append(words[i])
          else:
            break

        newRule = (newRule, weight)
        rules[key].append(newRule)
  # print rules
  # print line

  #generates the requested number of sentences
  for i in range(args.count):
    if (args.tree):
      print makeTree(rules, rng)
    else:
      print generate(rules, rng)

