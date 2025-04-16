import tkinter as tk
from tkinter import ttk
from models.translations import get_translation

class SentenceWidgetManager(ttk.LabelFrame):
    def __init__(self, parent, language, word_processor, api_service):
        super().__init__(parent, text=get_translation(language, "generated_sentences"), padding="5")
        self.language = language
        self.word_processor = word_processor
        self.api_service = api_service
        self.sentence_widgets = []
        
        # Buttons Frame
        self.buttons_frame = ttk.Frame(self)
        self.buttons_frame.grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)

        self.export_btn = ttk.Button(self.buttons_frame, text=get_translation(language, "export_docx"), 
                                   command=self.export_docx, state="disabled")
        self.export_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.show_all_btn = ttk.Button(self.buttons_frame, text=get_translation(language, "show_all"), 
                                     command=self.show_all_words, state="disabled")
        self.show_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_btn = ttk.Button(self.buttons_frame, text=get_translation(language, "delete_all"), 
                                   command=self.clear_sentences, state="disabled")
        self.delete_btn.pack(side=tk.LEFT)
        
        # Canvas and scrollbar
        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.sentences_container = ttk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.sentences_container, anchor="nw")
        
        self.canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        self.scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        self.sentences_container.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
    
    def _on_mousewheel(self, event):
        if self.canvas.winfo_height() < self.sentences_container.winfo_height():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def add_sentence(self, word, sentence):
        frame = ttk.Frame(self.sentences_container)
        frame.grid(sticky=(tk.W, tk.E), pady=2)
        frame.columnconfigure(0, weight=1)
        
        # Create masked sentence
        masked_sentence = self._create_masked_sentence(word, sentence)
        
        # Text widget
        text_widget = tk.Text(frame, wrap=tk.WORD, cursor="arrow", height=1, width=50)
        text_widget.insert("1.0", masked_sentence)
        text_widget.configure(state="disabled", selectbackground=text_widget.cget("background"), 
                            selectforeground=text_widget.cget("foreground"), 
                            inactiveselectbackground=text_widget.cget("background"))
        text_widget.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Bind to prevent text selection
        for seq in ["<Button-1>", "<B1-Motion>", "<Double-Button-1>", "<Triple-Button-1>"]:
            text_widget.bind(seq, lambda e: "break")
        
        # Adjust height
        def adjust_text_height():
            text_widget.configure(state="normal")
            text_widget.see("end")
            num_lines = text_widget.count("1.0", "end", "displaylines")[0]
            text_widget.configure(height=max(2, num_lines))
            text_widget.configure(state="disabled")
        
        text_widget.after(10, adjust_text_height)
        text_widget.bind('<Configure>', lambda e: text_widget.after(10, adjust_text_height))
        
        # Buttons
        show_btn = ttk.Button(
            frame,
            text=get_translation(self.language, "show"),
            command=lambda: self._toggle_word(text_widget, show_btn)
        )
        show_btn.grid(row=0, column=1, padx=(0, 5))
        
        copy_btn = ttk.Button(
            frame,
            text=get_translation(self.language, "copy"),
            command=lambda: self._copy_sentence(text_widget)
        )
        copy_btn.grid(row=0, column=2, padx=(0, 5))
        
        regen_btn = ttk.Button(
            frame,
            text="↻",
            width=2,
            command=lambda: self._regenerate_sentence(word, frame)
        )
        regen_btn.grid(row=0, column=3, padx=(0, 5))
        
        delete_btn = ttk.Button(
            frame,
            text="×",
            width=2,
            command=lambda: self._delete_sentence(frame)
        )
        delete_btn.grid(row=0, column=4)
        
        # Store references
        text_widget.original_sentence = sentence
        text_widget.masked_sentence = masked_sentence
        text_widget.word_visible = False
        text_widget.show_button = show_btn
        frame.text_widget = text_widget
        
        self.sentence_widgets.append(frame)
        self._update_buttons_state()
        
        return frame
    
    def _create_masked_sentence(self, word, sentence):
        def create_mask(w):
            return w[0] + "_" * (len(w) - 1)
        
        word_forms = {w.lower() for w in self.word_processor.get_word_variations(word)}
        sentence_lower = sentence.lower()
        masked_words = {}
        
        for form in sorted(word_forms, key=len, reverse=True):
            index = 0
            while True:
                index = sentence_lower.find(form, index)
                if index == -1:
                    break
                    
                before = index == 0 or not sentence_lower[index-1].isalpha()
                after = index + len(form) == len(sentence_lower) or not sentence_lower[index + len(form)].isalpha()
                
                if before and after:
                    original_word = sentence[index:index + len(form)]
                    masked_word = create_mask(original_word)
                    masked_words[original_word] = masked_word
                
                index += len(form)
        
        masked_sentence = sentence
        for original, masked in sorted(masked_words.items(), key=lambda x: len(x[0]), reverse=True):
            masked_sentence = masked_sentence.replace(original, masked)
        
        return masked_sentence
    
    def _toggle_word(self, text_widget, button):
        text_widget.configure(state="normal")
        
        if not text_widget.word_visible:
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", text_widget.original_sentence)
            button.configure(text=get_translation(self.language, "hide"))
            text_widget.word_visible = True
        else:
            text_widget.delete("1.0", tk.END)
            text_widget.insert("1.0", text_widget.masked_sentence)
            button.configure(text=get_translation(self.language, "show"))
            text_widget.word_visible = False
    
    def export_docx(self):
        """Export sentences to a Word document."""
        # Implement document export logic here
        pass

    def show_all_words(self):
        """Show or hide all words in all sentences."""
        if not self.sentence_widgets:
            return
            
        # Determine the action based on any visible word
        show_all = not any(hasattr(widget.text_widget, 'word_visible') and 
                          widget.text_widget.word_visible 
                          for widget in self.sentence_widgets)
        
        # Update button text
        self.show_all_btn.configure(
            text=get_translation(self.language, "hide_all" if show_all else "show_all")
        )
        
        for widget in self.sentence_widgets:
            if widget.winfo_exists():
                text_widget = widget.text_widget
                text_widget.configure(state="normal")
                
                if show_all:
                    text_widget.delete("1.0", tk.END)
                    text_widget.insert("1.0", text_widget.original_sentence)
                    text_widget.show_button.configure(
                        text=get_translation(self.language, "hide")
                    )
                    text_widget.word_visible = True
                else:
                    text_widget.delete("1.0", tk.END)
                    text_widget.insert("1.0", text_widget.masked_sentence)
                    text_widget.show_button.configure(
                        text=get_translation(self.language, "show")
                    )
                    text_widget.word_visible = False
                
                text_widget.configure(state="disabled")

    def clear_sentences(self):
        """Delete all sentences."""
        for widget in self.sentence_widgets:
            widget.destroy()
        self.sentence_widgets.clear()
        self._update_buttons_state()

    def _copy_sentence(self, text_widget):
        """Copy sentence to clipboard."""
        sentence = text_widget.get("1.0", tk.END).strip()
        self.clipboard_clear()
        self.clipboard_append(sentence)

    def _update_buttons_state(self):
        """Update the state of control buttons."""
        state = "normal" if self.sentence_widgets else "disabled"
        self.show_all_btn.configure(state=state)
        self.export_btn.configure(state=state)
        self.delete_btn.configure(state=state)

    def _delete_sentence(self, frame):
        """Delete a single sentence widget."""
        if frame in self.sentence_widgets:
            self.sentence_widgets.remove(frame)
        frame.destroy()
        self._update_buttons_state()

    def _regenerate_sentence(self, word, frame):
        """Regenerate sentence for a word."""
        # Implement sentence regeneration logic here
        pass