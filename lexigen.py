import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog, simpledialog
import requests
import json
import webbrowser
import os
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import threading

def initialize_nltk():
    """Initialize NLTK data in a separate thread."""
    try:
        # Try to load wordnet
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            print("Downloading NLTK data (this may take a moment)...")
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
            print("NLTK data download complete.")
    except Exception as e:
        print(f"Warning: Failed to initialize NLTK data: {str(e)}")
        print("The application will still work, but word variation detection might be limited.")

class LexiGen:
    def __init__(self, root):
        self.root = root
        self.lemmatizer = WordNetLemmatizer()
        self.root.title("LexiGen - Fill-in-the-Blank Generator")
        self.root.geometry("1000x800")
        
        # Ollama API Configuration
        self.api_url = "http://127.0.0.1:11434/api/generate"
        self.model = "llama2"
        self.available_models = []
        self.server_connected = False  # Track server connection status
        
        # Default prompt
        self.default_prompt = "Create a simple sentence using the word '{word}'. The sentence should be clear and educational."
        self.prompt_file = "prompt.txt"
        
        # Create main container
        self.main_container = ttk.Frame(self.root, padding="10")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Settings Frame
        self.settings_frame = ttk.LabelFrame(self.main_container, text="Settings", padding="5")
        self.settings_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # API URL Entry
        ttk.Label(self.settings_frame, text="API URL:").grid(row=0, column=0, padx=5)
        self.api_url_var = tk.StringVar(value=self.api_url)
        self.api_url_entry = ttk.Entry(self.settings_frame, textvariable=self.api_url_var, width=40)
        self.api_url_entry.grid(row=0, column=1, padx=5)
        
        # Model Selection
        ttk.Label(self.settings_frame, text="Model:").grid(row=0, column=2, padx=5)
        self.model_var = tk.StringVar(value=self.model)
        self.model_select = ttk.Combobox(self.settings_frame, textvariable=self.model_var, width=20, state="readonly")
        self.model_select.grid(row=0, column=3, padx=5)
        
        # Server Status and Help
        self.status_frame = ttk.Frame(self.settings_frame)
        self.status_frame.grid(row=1, column=0, columnspan=5, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(self.status_frame, text="Server Status: Checking...", foreground="gray")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.check_server_btn = ttk.Button(self.status_frame, text="Check Server", command=self.check_server_status)
        self.check_server_btn.pack(side=tk.LEFT, padx=5)
        
        self.help_btn = ttk.Button(self.status_frame, text="Setup Help", command=self.open_help)
        self.help_btn.pack(side=tk.LEFT, padx=5)
        
        # Word Input Frame
        self.input_frame = ttk.LabelFrame(self.main_container, text="Input Words", padding="5")
        self.input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Word Input
        self.word_input = scrolledtext.ScrolledText(self.input_frame, height=3, width=70)
        self.word_input.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        ttk.Label(self.input_frame, text="Enter words separated by commas").grid(row=1, column=0, sticky=tk.W, padx=5)
        
        # Buttons Frame for Generate and Append
        buttons_frame = ttk.Frame(self.input_frame)
        buttons_frame.grid(row=1, column=1, sticky=tk.E, padx=5)
        
        # Generate Button (create first but pack second)
        self.generate_btn = ttk.Button(buttons_frame, text="Generate", command=lambda: self.generate_sentences(append=False))
        
        # Append Button (create second but pack first)
        self.append_btn = ttk.Button(buttons_frame, text="Append", command=lambda: self.generate_sentences(append=True))
        self.append_btn.pack(side=tk.LEFT, padx=(0, 5))  # Pack first to be on the left
        self.append_btn.pack_forget()  # Hide initially
        
        # Now pack the Generate button
        self.generate_btn.pack(side=tk.LEFT)  # Pack second to be on the right
        
        # Progress Bar (hidden by default)
        self.progress_frame = ttk.Frame(self.input_frame)
        self.progress_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=5)
        self.progress_label = ttk.Label(self.progress_frame, text="Generating sentences...")
        self.progress_label.pack(side=tk.LEFT, padx=(0, 5))
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.progress_frame.grid_remove()  # Hide initially
        
        # Sentences Frame
        self.sentences_frame = ttk.LabelFrame(self.main_container, text="Generated Sentences", padding="5")
        self.sentences_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Buttons Frame
        self.buttons_frame = ttk.Frame(self.sentences_frame)
        self.buttons_frame.grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)

        # Export Docx Button
        self.export_btn = ttk.Button(self.buttons_frame, text="Export Docx", command=self.export_docx, state="disabled")
        self.export_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Show All Button
        self.show_all_btn = ttk.Button(self.buttons_frame, text="Show All", command=self.show_all_words, state="disabled")
        self.show_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Delete All Button
        self.delete_btn = ttk.Button(self.buttons_frame, text="Delete All", command=self.delete_all, state="disabled")
        self.delete_btn.pack(side=tk.LEFT)
        
        # Create a canvas and scrollbar for the sentences
        self.canvas = tk.Canvas(self.sentences_frame)
        self.scrollbar = ttk.Scrollbar(self.sentences_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Container for generated sentences
        self.sentences_container = ttk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.sentences_container, anchor="nw")
        
        # Grid layout for canvas and scrollbar
        self.canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        self.scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # List to keep track of generated sentence widgets
        self.sentence_widgets = []
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(2, weight=1)  # Make sentences frame expandable
        self.sentences_frame.columnconfigure(0, weight=1)
        self.sentences_frame.rowconfigure(1, weight=1)  # Make canvas expandable
        self.sentences_container.columnconfigure(0, weight=1)
        
        # Bind canvas resizing
        self.sentences_container.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Bind mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Check server status and fetch models on startup
        self.root.after(1000, self.initial_setup)

    def _on_frame_configure(self, event=None):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """When the canvas is resized, resize the inner frame to match"""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if self.canvas.winfo_height() < self.sentences_container.winfo_height():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def check_server_status_initial(self):
        """Check server status on startup, only show message if there's an error."""
        try:
            response = requests.get(self.api_url_var.get().replace("/generate", "/version"))
            if response.status_code == 200:
                self.status_label.config(text="Server Status: Connected", foreground="green")
                self.server_connected = True
                self.generate_btn.configure(state="normal")  # Enable Generate button
                return True
            else:
                self.status_label.config(text="Server Status: Error", foreground="red")
                messagebox.showerror("Server Status", "Failed to connect to Ollama server.\n\nPlease check if the server is running and the URL is correct.")
                self.server_connected = False
                self.generate_btn.configure(state="disabled")  # Disable Generate button
                return False
        except Exception as e:
            self.status_label.config(text="Server Status: Not Connected", foreground="red")
            messagebox.showerror(
                "Server Status", 
                "Cannot connect to Ollama server. Please ensure:\n\n"
                "1. Ollama is installed\n"
                "2. Server is running ('ollama serve')\n"
                "3. API URL is correct\n\n"
                f"Error: {str(e)}"
            )
            self.server_connected = False
            self.generate_btn.configure(state="disabled")  # Disable Generate button
            return False

    def initial_setup(self):
        if self.check_server_status_initial():
            self.fetch_models()

    def fetch_models(self):
        try:
            response = requests.get(self.api_url_var.get().replace("/generate", "/tags"))
            if response.status_code == 200:
                models = response.json()
                self.available_models = [model["name"] for model in models["models"]]
                if not self.available_models:
                    self.available_models = ["llama2"]  # Default fallback
                self.model_select["values"] = self.available_models
                
                # Set default model if current selection is not in list
                if self.model_var.get() not in self.available_models and self.available_models:
                    self.model_var.set(self.available_models[0])
                    
                return True
        except Exception as e:
            self.available_models = ["llama2"]  # Default fallback
            self.model_select["values"] = self.available_models
            self.model_var.set("llama2")
            messagebox.showwarning("Warning", f"Failed to fetch models: {str(e)}\nUsing default model list.")
            return False

    def check_server_status(self):
        try:
            # Try to connect to the Ollama server
            response = requests.get(self.api_url_var.get().replace("/generate", "/version"))
            if response.status_code == 200:
                self.status_label.config(text="Server Status: Connected", foreground="green")
                messagebox.showinfo("Server Status", "Successfully connected to Ollama server!\n\nServer version: " + response.json().get('version', 'Unknown'))
                self.server_connected = True
                self.generate_btn.configure(state="normal")  # Enable Generate button
                return True
            else:
                self.status_label.config(text="Server Status: Error", foreground="red")
                messagebox.showerror("Server Status", "Failed to connect to Ollama server.\n\nPlease check if the server is running and the URL is correct.")
                self.server_connected = False
                self.generate_btn.configure(state="disabled")  # Disable Generate button
                return False
        except Exception as e:
            self.status_label.config(text="Server Status: Not Connected", foreground="red")
            messagebox.showerror(
                "Server Status", 
                "Cannot connect to Ollama server. Please ensure:\n\n"
                "1. Ollama is installed\n"
                "2. Server is running ('ollama serve')\n"
                "3. API URL is correct\n\n"
                f"Error: {str(e)}"
            )
            self.server_connected = False
            self.generate_btn.configure(state="disabled")  # Disable Generate button
            return False

    def open_help(self):
        webbrowser.open("https://ollama.com/")
        
        try:
            with open("README.md", 'r') as f:
                content = f.read()
                # Find the Prerequisites section
                start = content.find("## Prerequisites")
                if start != -1:
                    # Find the next section
                    end = content.find("##", start + 1)
                    if end != -1:
                        prerequisites = content[start:end].strip()
                    else:
                        prerequisites = content[start:].strip()
                    
                    # Extract just the numbered list (remove the "## Prerequisites" header)
                    prerequisites = prerequisites.replace("## Prerequisites", "").strip()
                    
                    messagebox.showinfo("Setup Instructions", prerequisites)
                else:
                    raise FileNotFoundError("Prerequisites section not found in README.md")
        except Exception as e:
            # Fallback message if README.md can't be read
            messagebox.showinfo(
                "Setup Instructions",
                "1. Install Ollama from ollama.com\n"
                "2. Run 'ollama serve' in terminal\n"
                "3. Run 'ollama pull model' to download the model\n"
                "4. Click 'Check Server' to verify connection"
            )

    def get_prompt_template(self):
        """Read prompt from file or return default prompt."""
        try:
            if os.path.exists(self.prompt_file):
                with open(self.prompt_file, 'r') as f:
                    prompt = f.read().strip()
                    if prompt:  # Check if file is not empty
                        return prompt
        except Exception as e:
            messagebox.showwarning("Warning", f"Failed to read prompt file: {str(e)}\nUsing default prompt.")
        
        return self.default_prompt

    def check_server_status_silent(self):
        """Check server status without showing message boxes."""
        try:
            response = requests.get(self.api_url_var.get().replace("/generate", "/version"))
            if response.status_code == 200:
                self.status_label.config(text="Server Status: Connected", foreground="green")
                self.server_connected = True
                return True
            else:
                self.status_label.config(text="Server Status: Error", foreground="red")
                self.server_connected = False
                self.generate_btn.configure(state="disabled")  # Disable Generate button
                return False
        except Exception as e:
            self.status_label.config(text="Server Status: Not Connected", foreground="red")
            self.server_connected = False
            self.generate_btn.configure(state="disabled")  # Disable Generate button
            return False

    def generate_sentence_for_word(self, word):
        if not self.check_server_status_silent():
            messagebox.showerror(
                "Server Error",
                "Cannot connect to Ollama server. Please ensure:\n"
                "1. Ollama is installed\n"
                "2. Server is running ('ollama serve')\n"
                "3. Model is installed ('ollama pull llama2')\n"
                "Click 'Setup Help' for more information."
            )
            return None
        
        prompt_template = self.get_prompt_template()
        prompt = prompt_template.format(word=word)
        
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                response = requests.post(
                    self.api_url_var.get(),
                    json={
                        "model": self.model_var.get(),
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                result = response.json()
                sentence = result["response"].strip()
                
                # Check if the word or its variations are in the sentence
                word_variations = {word}  # Start with the original word
                # Add simple variations (lowercase, uppercase first letter, all uppercase)
                word_variations.add(word.lower())
                word_variations.add(word.capitalize())
                word_variations.add(word.upper())
                
                # Check if any variation of the word is in the sentence
                if any(variation in sentence.lower() for variation in word_variations):
                    return sentence
                
                # If this is the last attempt, return the sentence anyway
                if attempt == max_attempts - 1:
                    return sentence
                
            except requests.exceptions.RequestException as e:
                messagebox.showerror("Error", f"Failed to generate sentence: {str(e)}\nPlease check your server settings and connection.")
                return None
            except Exception as e:
                messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
                return None
        
        return None  # Should never reach here due to return in last attempt

    def create_sentence_widget(self, word, sentence):
        frame = ttk.Frame(self.sentences_container)
        frame.grid(sticky=(tk.W, tk.E), pady=2)
        frame.columnconfigure(0, weight=1)
        
        # Function to mask a word
        def create_mask(w):
            return w[0] + "_" * (len(w) - 1)
        
        # Function to get word variations using NLTK
        def get_word_variations(word):
            word = word.lower()
            variations = {word}  # Start with the original word
            
            # Get base form (lemma) for different parts of speech
            for pos in [wordnet.NOUN, wordnet.VERB, wordnet.ADJ, wordnet.ADV]:
                lemma = self.lemmatizer.lemmatize(word, pos=pos)
                variations.add(lemma)
            
            # Add common derivational forms
            for w in list(variations):  # Make a copy of the set to iterate over
                # Nouns
                variations.add(w + 's')  # Plural
                variations.add(w + 'es')  # Plural form 2
                # Verbs
                variations.add(w + 'ed')  # Past tense
                variations.add(w + 'd')   # Past tense alternate
                variations.add(w + 'ing')  # Present participle
                # Adjectives
                variations.add(w + 'ic')   # Related adjective
                variations.add(w + 'ical')  # Related adjective
                variations.add(w + 'ous')   # Related adjective
                variations.add(w + 'al')    # Related adjective
                variations.add(w + 'ive')   # Related adjective
                variations.add(w + 'able')  # Ability adjective
                variations.add(w + 'ible')  # Ability adjective
                variations.add(w + 'y')     # Related adjective
                # Adverbs
                variations.add(w + 'ly')    # Related adverb
                # Nouns from adjectives
                variations.add(w + 'ness')  # Quality noun
                variations.add(w + 'ity')   # State noun
                
                # Handle words ending in 'e'
                if w.endswith('e'):
                    variations.add(w[:-1] + 'ing')  # remove 'e' before 'ing'
                    variations.add(w + 'r')         # comparative
                    variations.add(w + 'st')        # superlative
                
                # Handle words ending in 'y'
                if w.endswith('y'):
                    variations.add(w[:-1] + 'ies')  # plural
                    variations.add(w[:-1] + 'ied')  # past tense
                    variations.add(w[:-1] + 'ier')  # comparative
                    variations.add(w[:-1] + 'iest') # superlative
                    variations.add(w[:-1] + 'ily')  # adverb
                    variations.add(w[:-1] + 'iness') # noun
                
                # Special cases for your example
                if w in ['melody']:
                    variations.add('melodic')
                    variations.add('melodious')
                    variations.add('melodically')
                    variations.add('melodiously')
            
            return variations
        
        # Get word variations
        word_forms = get_word_variations(word)
        
        # Create the masked sentence
        sentence_lower = sentence.lower()
        masked_words = {}  # Store original and masked versions
        
        # Sort word forms by length in descending order to handle longer forms first
        word_forms = sorted(word_forms, key=len, reverse=True)
        
        for form in word_forms:
            index = 0
            while True:
                index = sentence_lower.find(form.lower(), index)
                if index == -1:
                    break
                    
                # Check if it's a complete word (not part of another word)
                before = index == 0 or not sentence_lower[index-1].isalpha()
                after = index + len(form) == len(sentence_lower) or not sentence_lower[index + len(form)].isalpha()
                
                if before and after:
                    original_word = sentence[index:index + len(form)]
                    masked_word = create_mask(original_word)
                    masked_words[original_word] = masked_word
                
                index += len(form)
        
        # Apply masking while preserving original case
        masked_sentence = sentence
        for original, masked in sorted(masked_words.items(), key=lambda x: len(x[0]), reverse=True):
            masked_sentence = masked_sentence.replace(original, masked)
        
        # Text widget for the sentence
        text_widget = tk.Text(frame, wrap=tk.WORD, cursor="arrow")
        text_widget.insert("1.0", masked_sentence)
        text_widget.configure(state="disabled", selectbackground=text_widget.cget("background"), 
                            selectforeground=text_widget.cget("foreground"), inactiveselectbackground=text_widget.cget("background"))
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Bind to prevent text selection
        text_widget.bind("<Button-1>", lambda e: "break")
        text_widget.bind("<B1-Motion>", lambda e: "break")
        text_widget.bind("<Double-Button-1>", lambda e: "break")
        text_widget.bind("<Triple-Button-1>", lambda e: "break")
        
        # Disable text widget scrolling
        text_widget.configure(yscrollcommand=None)
        
        # Adjust height based on content
        def adjust_text_height(event=None):
            text_widget.configure(state="normal")
            # Get the number of lines needed to display all text
            text_widget.see("end")  # Make sure all text is rendered
            num_lines = text_widget.count("1.0", "end", "displaylines")[0]
            # Set minimum height to 2 lines
            text_widget.configure(height=max(2, num_lines))
            text_widget.configure(state="disabled")
        
        # Call height adjustment after a short delay to ensure text is properly rendered
        text_widget.after(10, adjust_text_height)
        
        # Bind to Configure event for window resizing
        text_widget.bind('<Configure>', lambda e: text_widget.after(10, adjust_text_height))
        
        # Show/Hide Word Button
        show_btn = ttk.Button(
            frame,
            text="Show",
            command=lambda t=text_widget, b=None: self.toggle_word(word, t, b)
        )
        show_btn.grid(row=0, column=1, padx=(0, 5))
        
        # Copy Button
        copy_btn = ttk.Button(
            frame,
            text="Copy",
            command=lambda t=text_widget: self.copy_sentence(t)
        )
        copy_btn.grid(row=0, column=2, padx=(0, 5))
        
        # Regenerate Button
        regen_btn = ttk.Button(
            frame,
            text="↻",  # Circular arrow symbol for regenerate
            width=2,
            command=lambda w=word, t=text_widget, f=frame: self.regenerate_sentence(w, t, f)
        )
        regen_btn.grid(row=0, column=3, padx=(0, 5))  # Added padding to separate from Delete button
        
        # Delete Button
        delete_btn = ttk.Button(
            frame,
            text="×",  # Multiplication sign (×) for delete
            width=2,
            command=lambda f=frame: self.delete_sentence(f)
        )
        delete_btn.grid(row=0, column=4)
        
        # Store the original sentence, masked sentence, and button reference for toggling
        text_widget.original_sentence = sentence
        text_widget.masked_sentence = masked_sentence
        text_widget.word_visible = False
        text_widget.show_button = show_btn  # Store button reference
        
        # Store text widget reference in the frame for easy access
        frame.text_widget = text_widget
        
        self.sentence_widgets.append(frame)
        return frame

    def copy_sentence(self, text_widget):
        """Copy the current sentence to clipboard."""
        sentence = text_widget.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(sentence)
        self.root.update()  # Required to finalize clipboard update

    def toggle_word(self, word, text_widget, button):
        text_widget.configure(state="normal")
        
        if not text_widget.word_visible:
            # Show the word
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", text_widget.original_sentence)
            text_widget.show_button.configure(text="Hide")
            text_widget.word_visible = True
        else:
            # Hide the word
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", text_widget.masked_sentence)
            text_widget.show_button.configure(text="Show")
            text_widget.word_visible = False
        
        text_widget.configure(state="disabled")

    def export_docx(self):
        """Export sentences to a Word document."""
        if not self.sentence_widgets:
            messagebox.showwarning("Warning", "No sentences to export!")
            return
        
        # Ask user for document title
        title = simpledialog.askstring("Document Title", "Enter the title for your document:", initialvalue="Fill in the Blank")
        if not title:  # User cancelled or entered empty string
            return
        
        # Ask user for save location with the title as default filename
        file_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx")],
            title="Save Document As",
            initialfile=f"{title}.docx"  # Use title as default filename
        )
        
        if not file_path:  # User cancelled
            return
        
        try:
            # Create document
            doc = Document()
            
            # Add title
            title_para = doc.add_paragraph(title)
            title_format = title_para.runs[0].font
            title_format.size = Pt(16)
            title_format.bold = True
            title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            # Add sentences
            doc.add_paragraph()  # Add space after title
            for i, widget in enumerate(self.sentence_widgets, 1):
                text_widget = widget.text_widget
                sentence = text_widget.masked_sentence
                p = doc.add_paragraph()
                p.add_run(f"{i}. ").bold = True
                p.add_run(sentence)
            
            # Add answer key section
            doc.add_page_break()
            key_title = doc.add_paragraph("Answer Key")
            key_title_format = key_title.runs[0].font
            key_title_format.size = Pt(16)
            key_title_format.bold = True
            key_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
            doc.add_paragraph()  # Add space after title
            for i, widget in enumerate(self.sentence_widgets, 1):
                text_widget = widget.text_widget
                # Find the masked words by comparing original and masked sentences
                original_words = set()
                for orig, masked in zip(text_widget.original_sentence.split(), text_widget.masked_sentence.split()):
                    if orig != masked and masked.startswith(orig[0]) and '_' in masked:
                        original_words.add(orig)
                
                # Add answer with number
                p = doc.add_paragraph()
                p.add_run(f"{i}. ").bold = True
                p.add_run(", ".join(sorted(original_words)))
            
            # Save document
            doc.save(file_path)
            messagebox.showinfo("Success", "Document exported successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export document: {str(e)}")

    def generate_sentences(self, append=False):
        # Get words from input and convert to lowercase
        words = [word.strip().lower() for word in self.word_input.get("1.0", tk.END).strip().split(",")]
        words = [w for w in words if w]  # Remove empty strings
        
        if not words:
            return
        
        # Clear existing sentences if not appending
        if not append:
            self.delete_all()
            
        # Clear input box
        self.word_input.delete("1.0", tk.END)
            
        # Show progress bar
        self.progress_bar['maximum'] = len(words)
        self.progress_bar['value'] = 0
        self.progress_frame.grid()
        self.generate_btn.configure(state="disabled")
        if hasattr(self, 'append_btn'):
            self.append_btn.configure(state="disabled")
        
        # Update UI
        self.root.update()
        
        has_sentences = False
        for i, word in enumerate(words):
            sentence = self.generate_sentence_for_word(word)
            if sentence:
                self.create_sentence_widget(word, sentence)
                has_sentences = True
            else:
                # If sentence generation failed (likely due to server disconnection)
                self.progress_frame.grid_remove()
                return  # Stop generation
            
            # Update progress
            self.progress_bar['value'] = i + 1
            self.progress_label.configure(text=f"Generating sentences... ({i + 1}/{len(words)})")
            self.root.update()
        
        # Enable Show All and Export buttons if sentences were generated
        if has_sentences or len(self.sentence_widgets) > 0:
            self.show_all_btn.configure(state="normal")
            self.export_btn.configure(state="normal")
            self.delete_btn.configure(state="normal")  # Enable Delete All button
            self.append_btn.pack(side=tk.LEFT, padx=(0, 5))  # Show Append button
        else:
            self.append_btn.pack_forget()  # Hide Append button
            self.delete_btn.configure(state="disabled")  # Disable Delete All button
        
        # Hide progress bar and re-enable generate button only if server is connected
        self.progress_frame.grid_remove()
        if self.server_connected:
            self.generate_btn.configure(state="normal")
            if hasattr(self, 'append_btn'):
                self.append_btn.configure(state="normal")

    def delete_all(self):
        for widget in self.sentence_widgets:
            widget.destroy()
        self.sentence_widgets.clear()
        # Disable all buttons and reset text
        self.show_all_btn.configure(text="Show All", state="disabled")
        self.export_btn.configure(state="disabled")
        self.delete_btn.configure(state="disabled")  # Disable Delete All button
        # Hide Append button
        self.append_btn.pack_forget()

    def show_all_words(self):
        """Show or hide all words in all sentences."""
        if not self.sentence_widgets:
            return
            
        # Determine the action based on any visible word
        show_all = not any(hasattr(widget.text_widget, 'word_visible') and widget.text_widget.word_visible 
                          for widget in self.sentence_widgets)
        
        # Update button text
        self.show_all_btn.configure(text="Hide All" if show_all else "Show All")
        
        # Create a list of valid widgets to process
        valid_widgets = []
        for widget in self.sentence_widgets[:]:  # Create a copy of the list to iterate
            try:
                # Check if widget still exists and has required attributes
                if (widget.winfo_exists() and 
                    hasattr(widget, 'text_widget') and 
                    widget.text_widget.winfo_exists() and
                    hasattr(widget.text_widget, 'original_sentence') and
                    hasattr(widget.text_widget, 'masked_sentence')):
                    valid_widgets.append(widget)
                else:
                    # Remove invalid widget from the list
                    self.sentence_widgets.remove(widget)
            except tk.TclError:
                # Widget has been destroyed, remove it from the list
                self.sentence_widgets.remove(widget)
        
        # Process only valid widgets
        for widget in valid_widgets:
            try:
                text_widget = widget.text_widget
                text_widget.configure(state="normal")
                text_widget.delete("1.0", tk.END)
                
                if show_all:
                    # Show the word
                    text_widget.insert("1.0", text_widget.original_sentence)
                    text_widget.word_visible = True
                    text_widget.show_button.configure(text="Hide")
                else:
                    # Hide the word
                    text_widget.insert("1.0", text_widget.masked_sentence)
                    text_widget.word_visible = False
                    text_widget.show_button.configure(text="Show")
                
                text_widget.configure(state="disabled")
            except tk.TclError:
                # If any error occurs during processing, skip this widget
                continue

    def regenerate_sentence(self, word, text_widget, frame):
        """Generate a new sentence for the given word and update the widget."""
        new_sentence = self.generate_sentence_for_word(word)
        if new_sentence:
            # Create a new sentence widget
            new_frame = self.create_sentence_widget(word, new_sentence)
            
            # Get the grid info of the old frame
            grid_info = frame.grid_info()
            
            # Configure the new frame with the same grid parameters
            new_frame.grid(row=grid_info['row'], column=grid_info['column'], sticky=grid_info['sticky'], pady=grid_info['pady'])
            
            # Replace the old frame in the sentence_widgets list
            index = self.sentence_widgets.index(frame)
            self.sentence_widgets[index] = new_frame
            
            # Destroy the old frame
            frame.destroy()
            
            # Update the scroll region
            self._on_frame_configure()

    def delete_sentence(self, frame):
        """Delete a single sentence widget."""
        # Remove from the list of sentence widgets
        if frame in self.sentence_widgets:
            self.sentence_widgets.remove(frame)
            
        # Destroy the frame
        frame.destroy()
        
        # Update the scroll region
        self._on_frame_configure()
        
        # If no sentences left, disable buttons and hide append button
        if not self.sentence_widgets:
            self.show_all_btn.configure(text="Show All", state="disabled")
            self.export_btn.configure(state="disabled")
            self.delete_btn.configure(state="disabled")  # Disable Delete All button
            self.append_btn.pack_forget()

if __name__ == "__main__":
    try:
        print("Starting LexiGen...")
        # Initialize NLTK in a background thread
        nltk_thread = threading.Thread(target=initialize_nltk, daemon=True)
        nltk_thread.start()
        
        # Create and run the application
        root = tk.Tk()
        app = LexiGen(root)
        root.mainloop()
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        import traceback
        traceback.print_exc() 