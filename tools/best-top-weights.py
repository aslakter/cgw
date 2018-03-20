#!/usr/bin/env python2
# A program for approximating optimal weights between the S1 and S2
# subgrammars by minimizing the cross-entropy of a test set against the
# combined grammar.
#
# Jeffrey Bosboom <jbosboom@csail.mit.edu>, Spring 2018
# inspired by a similar program from 2012 by Yuan K. Shen (yks)

import argparse, os, sys, re
try:
  import subprocess32 as subprocess
except ImportError:
  import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('sentencefile', type=str)
parser.add_argument('--granularity', type=int, default=100)
args = parser.parse_args()

if not os.path.isfile(args.sentencefile):
  print args.sentencefile, 'does not exist or is not a regular file'
  sys.exit(1)

grammar = ""
for file in ('S1.gr', 'S1_Vocab.gr', 'S2.gr', 'S2_Vocab.gr'):
  with open(file, 'r') as f:
    grammar += f.read()

def experiment(s1, s2):
  p = subprocess.Popen(['parse', '-i', args.sentencefile, '-n', '-C'], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=None, bufsize=-1)
  p.stdin.write(grammar)
  p.stdin.write('{} START S1\n'.format(str(s1)));
  p.stdin.write('{} START S2\n'.format(str(s2)));
  _, stderr = p.communicate()
  m = re.search(r'cross-entropy = (\S+) bits', stderr)
  if not m:
    print 'error: unable to parse cross-entropy'
    sys.exit(1)
  crossent = float(m.group(1))
  return crossent

best_crossent = float('inf')
best_s1 = None
for i in xrange(1, args.granularity):
  crossent = experiment(i, args.granularity-i)
  if crossent < best_crossent:
    best_crossent = crossent
    best_s1 = i

print 'best S1 weight is {}, S2 is {}, obtained cross-entropy {}'.format(str(best_s1), str(args.granularity-best_s1), str(best_crossent))
