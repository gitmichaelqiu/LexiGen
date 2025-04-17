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
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('punkt', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
            
            wordnet.synsets('test')
            self.lemmatizer = WordNetLemmatizer()
            return True
        except (LookupError, ImportError, AttributeError) as e:
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

    def get_word_variations(self, word):
        """Get word variations using NLTK WordNet with part of speech analysis."""
        if not self.lemmatizer:
            return {word.lower()}
            
        word = word.lower()
        variations = {word}
        
        # Get part of speech
        pos = self.get_wordnet_pos(word)
        
        # Get base form (lemma) using correct part of speech
        base_form = self.lemmatizer.lemmatize(word, pos)
        if base_form:
            variations.add(base_form)
        
        # Get all synsets for the word with the correct part of speech
        all_synsets = wordnet.synsets(word, pos=pos)
        
        # Process each synset
        for synset in all_synsets:
            for lemma in synset.lemmas():
                if lemma.name().lower() == word:
                    variations.add(lemma.name().lower())
                    # Get all related forms
                    deriv_forms = lemma.derivationally_related_forms()
                    if deriv_forms:
                        variations.update(d.name().lower() for d in deriv_forms)
        
        # Handle specific word forms based on part of speech
        if pos == wordnet.NOUN:
            # Handle plural forms
            if not word.endswith('s'):
                variations.add(word + 's')
            if word.endswith('s'):
                variations.add(word[:-1])  # Remove 's' for singular
            if word.endswith('es'):
                variations.add(word[:-2])  # Remove 'es' for singular
            if word.endswith('ies'):
                variations.add(word[:-3] + 'y')  # Change 'ies' to 'y'
        
        elif pos == wordnet.VERB:
            # Handle verb forms
            base = base_form if base_form else word
            variations.update([
                base + 's',  # third person singular
                base + 'ing',  # present participle
                base + 'ed',  # past tense
                base + 'en'  # past participle
            ])
            
            # Handle special cases
            if base.endswith('e'):
                variations.add(base[:-1] + 'ing')
            if base.endswith('y'):
                variations.add(base[:-1] + 'ied')
            if base.endswith('c'):
                variations.add(base + 'ked')
        
        elif pos == wordnet.ADJ:
            # Handle adjective forms
            base = base_form if base_form else word
            variations.update([
                base + 'er',  # comparative
                base + 'est'  # superlative
            ])
            
            # Handle special cases
            if base.endswith('y'):
                variations.add(base[:-1] + 'ier')
                variations.add(base[:-1] + 'iest')
            if base.endswith('e'):
                variations.add(base + 'r')
                variations.add(base + 'st')
        
        # Add capitalized versions
        variations.update({v.capitalize() for v in variations})
        
        return {v for v in variations if v}