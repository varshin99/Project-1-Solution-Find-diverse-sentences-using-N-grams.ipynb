# -*- coding: utf-8 -*-
"""Project 1 Solution: Find diverse sentences using N-grams.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1MvbtZAOqojr0aoaiQcq1sJ2EoIDFLeou
"""

!pip install --quiet transformers==4.10.2
!pip install --quiet sentencepiece==0.1.96

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model = AutoModelForSeq2SeqLM.from_pretrained("ramsrigouthamg/t5-large-paraphraser-diverse-high-quality")
tokenizer = AutoTokenizer.from_pretrained("ramsrigouthamg/t5-large-paraphraser-diverse-high-quality")

"""## Short sentence Paraphraser"""

# Diverse Beam search

original = "Once, a group of frogs was roaming around the forest in search of water."
text = "paraphrase: "+original + " </s>"

encoding = tokenizer.encode_plus(text,max_length =128, padding=True, return_tensors="pt")
input_ids,attention_mask  = encoding["input_ids"], encoding["attention_mask"]

model.eval()
diverse_beam_outputs = model.generate(
    input_ids=input_ids,attention_mask=attention_mask,
    max_length=128,
    early_stopping=True,
    num_beams=5,
    num_beam_groups = 5,
    num_return_sequences=5,
    diversity_penalty = 0.70

)

print ("\n\n")
print ("Original: ",original)
paraphrases =[]
for beam_output in diverse_beam_outputs:
    sent = tokenizer.decode(beam_output, skip_special_tokens=True,clean_up_tokenization_spaces=True)
    if 'paraphrasedoutput:' in sent:
      modified_sent = sent.replace('paraphrasedoutput:','').strip()
      paraphrases.append(modified_sent)
    print (sent)

print (original)
# remove exact duplicates
paraphrases = list(set(paraphrases))
print ("**********")
for paraphrase in paraphrases:
  print (paraphrase)

"""**Order the paraphrased sentences from most diverse to least diverse when compared to original sentence**



Get an overlap score between original and each paraphrase.

Then the paraphrase with the lowest overlap score is the most diverse paraphrase.

Algorithm:

1) Get n-grams (1,2,3,4 grams) from the original and each of paraphrase sentence.

2) Calculate n-gram overlap, that is no of elements in list overlap between original and paraphrase and divide by the length of paraphrase.

3) Avg out the n-gram overlap score to get final score between original and paraphrase sentence. eg: 1/4(1-gram-overlap-score) + 1/4 (2-gram-overlap-score) + 1/4 (3-gram-overlap-score) + 1/4 (4-gram-overlap-score)

4) Sort from least score (most diverse) to highest score (least diverse)

## Solution : Find the most diverse paraphrase sentence when compared to the original sentence using n-grams count
"""

from nltk.tokenize import word_tokenize
from nltk.util import ngrams
import nltk
import string
nltk.download('punkt')

def get_ngrams(text, n ):
    n_grams = ngrams(word_tokenize(text), n)
    return [ ' '.join(grams) for grams in n_grams]

# get overlap between two lists
def get_match_score(orig,ref):
  overlap = set(orig).intersection(ref)
  return len(overlap)/len(ref)

def calculate_score(original,reference):
  original = original.translate(str.maketrans('', '', string.punctuation))
  reference = reference.translate(str.maketrans('', '', string.punctuation))

  unigrams_orig = get_ngrams(original,1)
  unigrams_reference = get_ngrams(reference,1)

  bigrams_orig = get_ngrams(original,2)
  bigrams_reference = get_ngrams(reference,2)

  trigrams_orig = get_ngrams(original,3)
  trigrams_reference = get_ngrams(reference,3)

  fourgrams_orig = get_ngrams(original,4)
  fourgrams_reference = get_ngrams(reference,4)

  unigram_score = get_match_score(unigrams_orig,unigrams_reference)
  bigram_score =  get_match_score(bigrams_orig,bigrams_reference)
  trigram_score = get_match_score(trigrams_orig,trigrams_reference)
  fourgrams_score = get_match_score(fourgrams_orig,fourgrams_reference)

  return (1/4)*unigram_score + (1/4)*bigram_score + (1/4)*trigram_score + (1/4)*fourgrams_score

outputs =[]
for paraphrase in paraphrases:
  score = calculate_score(original,paraphrase)
  outputs.append((paraphrase,score))
  
print (original)
sorted_list = sorted(outputs, key = lambda y:y[1])
for each in sorted_list:
  print (each)

"""The lower the score the more farther the sentence is from the original sentence. Hence it is the most diverse.

This is the basis of BLEU score in text generation to compare reference output to original.

https://towardsdatascience.com/bleu-bilingual-evaluation-understudy-2b4eab9bcfd1
"""