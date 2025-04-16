import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from tkinter import messagebox

class WordProcessor:
    def __init__(self):
        self.lemmatizer = None
        self.initialize_nltk()

    def initialize_nltk(self):
        """Initialize NLTK data."""
        try:
            wordnet.synsets('test')
            self.lemmatizer = WordNetLemmatizer()
            return True
        except (LookupError, ImportError, AttributeError) as e:
            messagebox.showerror(
                "Error",
                "Failed to initialize word variation detection.\nThis may affect some functionality."
            )
            return False

    def get_word_variations(self, word):
        """Get word variations using NLTK WordNet."""
        if not self.lemmatizer:
            return {word.lower()}
            
        word = word.lower()
        variations = {word}
        
        # Get base form
        base_form = wordnet.morphy(word)
        if base_form:
            variations.add(base_form)
        else:
            base_form = word
        
        # Get all synsets for the word
        all_synsets = wordnet.synsets(word)
        
        # Process each synset
        for synset in all_synsets:
            for lemma in synset.lemmas():
                if lemma.name().lower() == word:
                    variations.add(lemma.name().lower())
                    deriv_forms = lemma.derivationally_related_forms()
                    if deriv_forms:
                        variations.update(d.name().lower() for d in deriv_forms)
        
        # Try to find verb forms
        verb_base = wordnet.morphy(word, 'v')
        if verb_base and verb_base == word:
            variations.update([
                word + 'ing',
                word + 's',
                word + 'ed'
            ])
            
            if word.endswith('e'):
                variations.add(word[:-1] + 'ing')
            
            verb_synsets = wordnet.synsets(word, pos='v')
            for synset in verb_synsets:
                for lemma in synset.lemmas():
                    if lemma.name().lower() == word:
                        for form in lemma.derivationally_related_forms():
                            variations.add(form.name().lower())
        
        # Check common adjective forms
        adj_forms = [word + 'ic', word + 'ical', word + 'ous']
        for adj in adj_forms:
            if wordnet.synsets(adj):
                variations.add(adj)
        
        return {v for v in variations if v}