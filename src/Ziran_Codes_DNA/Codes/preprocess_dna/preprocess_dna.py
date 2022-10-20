#minimum reproducible code
#preprocessing dna data for cvec, tfidf algorithms
# !pip install fastaparser

import fastaparser
import random
import numpy as np 
import pandas as pd


def Kmers_funct(seq, k_low, k_high):
   return [seq[x:x+random.randint(k_low,k_high)].lower() for x in range(len(seq)-k_low + 1)]

def spacings(seq,k_low,k_high):
  words = Kmers_funct(seq, k_low, k_high)
  joined_sentence = ' '.join(words)
  return joined_sentence

def loadsequence(sequence_file, k_low, k_high):
  with open(sequence_file) as fasta_file:
        parser = fastaparser.Reader(fasta_file, parse_method='quick')
        corpus = []
        for seq in parser:
          s = seq.sequence
          corpus.append(spacings(s, k_low, k_high))
  return corpus


#sequence_file = 'PromoterSet.fa'
#k_low = 3
#k_high = 5

# print(len(loadsequence(sequence_file, k_low, k_high)))  # prints no of sequences in sequence_file
# print(loadsequence(sequence_file, k_low, k_high))[0:9]) # prints corpus of sentence generated by first 10 sequence of file

