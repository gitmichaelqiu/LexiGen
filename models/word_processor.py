import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from tkinter import messagebox
from models.translations import get_translation

class WordProcessor:
    def __init__(self, language="English"):
        self.lemmatizer = None
        self.language = language
        self.initialize_nltk()

    def initialize_nltk(self):
        """Initialize NLTK data."""
        try:
            # Download required NLTK data
            self.lemmatizer = WordNetLemmatizer()
            return True
        except Exception as e:
            try:
                nltk.download('averaged_perceptron_tagger', quiet=True)
                nltk.download('punkt', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('omw-1.4', quiet=True)
                return True
            except Exception as e:
                messagebox.showerror(
                    get_translation(self.language, "error_title"),
                    get_translation(self.language, "unexpected_error_msg").format(error="Failed to initialize word variation detection")
                )
                return False

    def get_wordnet_pos(self, word):
        """Map POS tag to first character used by WordNetLemmatizer."""
        tag = pos_tag([word])[0][1][0].upper()
        tag_dict = {"J": wordnet.ADJ,
                   "N": wordnet.NOUN,
                   "V": wordnet.VERB,
                   "R": wordnet.ADV}
        return tag_dict.get(tag, wordnet.NOUN)
    
    def get_word_derivatives(self, word):
        """Get a word's all derivatives by giving different POS to lemmatizer"""
        derivatives = []
        tag_dict = [wordnet.ADJ, wordnet.NOUN, wordnet.VERB, wordnet.ADV]

        for tag in tag_dict:
            derivatives.append(self.lemmatizer.lemmatize(word, tag))

        return derivatives
    
    def get_word_stem(self, word):
        """Use Lancaster Stemmer to get the word stem"""
        stemmer = nltk.stem.lancaster.LancasterStemmer()
        word_stem = stemmer.stem(word)
        return word_stem

    # def restore_word(self, word):
    #     """Restore a word to its base form using NLTK's lemmatizer with POS information."""
    #     if not self.lemmatizer:
    #         return word.lower()
            
    #     word = word.lower()
    #     pos = self.get_wordnet_pos(word)
        
    #     # First try lemmatization
    #     lemma = self.lemmatizer.lemmatize(word, pos)
        
    #     return lemma

    def is_word_match(self, word1, word2):
        """Check if two words match, considering their base forms and word families."""
        # if not self.lemmatizer:
        #     return word1.lower() == word2.lower()
            
        word1 = word1.lower()
        word2 = word2.lower()
        
        # # Direct match
        # if word1 == word2:
        #     return True
            
        # # Get base forms
        # base1 = self.restore_word(word1)
        # base2 = self.restore_word(word2)
        
        # # Check base form match
        # if base1 == base2:
        #     return True
            
        # # Check for morphological variations
        # if word1.endswith('ic') and word2 == word1[:-2] + 'y':
        #     return True
        # if word2.endswith('ic') and word1 == word2[:-2] + 'y':
        #     return True
        # if word1.endswith('ious') and word2 == word1[:-4] + 'y':
        #     return True
        # if word2.endswith('ious') and word1 == word2[:-4] + 'y':
        #     return True
        # if word1.endswith('al') and word2 == word1[:-2]:
        #     return True
        # if word2.endswith('al') and word1 == word2[:-2]:
        #     return True
        
        # Use derivative list

        derivatives1 = self.get_word_derivatives(word1)
        derivatives2 = self.get_word_derivatives(word2)
        common_derivatives = set(derivatives1) & set(derivatives2)

        if common_derivatives:
            return True

        stem1 = []
        stem2 = []

        for der in derivatives1:
            stem1.append(self.get_word_stem(der))
        for der in derivatives2:
            stem2.append(self.get_word_stem(der))

        common_stem = set(stem1) & set(stem2)

        if common_stem:
            return True
            
        return False
