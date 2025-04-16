import tkinter as tk
from tkinter import ttk
from models.translations import get_translation
from tkinter import filedialog, simpledialog, messagebox
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

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
        
        # Store original word for regeneration
        original_word = word
        
        regen_btn = ttk.Button(
            frame,
            text="↻",
            width=2,
            command=lambda w=original_word, f=frame: self._regenerate_sentence(w, f)
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
        text_widget.original_word = original_word  # Store original word
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
        if not self.sentence_widgets:
            messagebox.showwarning(
                get_translation(self.language, "warning_title"),
                get_translation(self.language, "no_sentences_warning")
            )
            return
        
        # Get document title from user
        title = simpledialog.askstring(
            get_translation(self.language, "document_title_prompt"),
            get_translation(self.language, "document_title_prompt"),
            initialvalue="Fill in the Blank"
        )
        if not title:
            return
        
        # Ask for save location
        file_path = filedialog.asksaveasfilename(
            defaultextension=".docx",
            filetypes=[("Word Document", "*.docx")],
            title=get_translation(self.language, "save_document_title"),
            initialfile=f"{title}.docx"
        )
        
        if not file_path:
            return
        
        # Create document
        doc = Document()
        
        # Add title
        title_paragraph = doc.add_paragraph()
        title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title_paragraph.add_run(title)
        title_run.bold = True
        title_run.font.size = Pt(16)
        
        # Add sentences
        for i, frame in enumerate(self.sentence_widgets, 1):
            if frame.winfo_exists():
                text_widget = frame.text_widget
                
                # Original sentence for reference (shown)
                para = doc.add_paragraph()
                para.add_run(f"{i}. ").bold = True
                para.add_run(text_widget.original_sentence)
                
                # Masked sentence (with blanks for exercise)
                para = doc.add_paragraph()
                para.add_run(f"{i}. ").bold = True
                para.add_run(text_widget.masked_sentence)
                
                # Add a space between sentence pairs
                doc.add_paragraph()
        
        # Save the document
        try:
            doc.save(file_path)
            messagebox.showinfo(
                get_translation(self.language, "export_success_title"),
                get_translation(self.language, "export_success_msg")
            )
        except Exception as e:
            messagebox.showerror(
                get_translation(self.language, "error_title"),
                get_translation(self.language, "unexpected_error_msg").format(error=str(e))
            )

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
        
        # Reset canvas scroll region
        self.canvas.configure(scrollregion=(0, 0, 0, 0))
        
        # Clear any background that might remain
        self.update_idletasks()  # Ensure all pending drawing operations are completed
        self.canvas.update()

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
        if not self.api_service.server_connected:
            messagebox.showwarning(
                get_translation(self.language, "server_error_title"),
                get_translation(self.language, "server_connection_guide")
            )
            return
        
        # Get prompt from main application config
        from models.config import DEFAULT_CONFIG
        
        # Generate new sentence
        new_sentence = self.api_service.generate_sentence(word, DEFAULT_CONFIG["default_prompt"])
        
        if new_sentence:
            # Create masked sentence
            masked_sentence = self._create_masked_sentence(word, new_sentence)
            
            # Update text widget
            text_widget = frame.text_widget
            text_widget.configure(state="normal")
            text_widget.delete("1.0", tk.END)
            
            # Set the appropriate sentence based on visibility state
            if text_widget.word_visible:
                text_widget.insert("1.0", new_sentence)
            else:
                text_widget.insert("1.0", masked_sentence)
            
            # Update stored sentences
            text_widget.original_sentence = new_sentence
            text_widget.masked_sentence = masked_sentence
            
            # Readjust height
            text_widget.see("end")
            num_lines = text_widget.count("1.0", "end", "displaylines")[0]
            text_widget.configure(height=max(2, num_lines))
            
            text_widget.configure(state="disabled")

    def update_texts(self, language):
        """Update all texts in the widget after language change."""
        self.language = language
        
        # Update the frame title
        self.configure(text=get_translation(language, "generated_sentences"))
        
        # Update control buttons
        self.export_btn.configure(text=get_translation(language, "export_docx"))
        
        # Update show/hide all button based on its current state
        if hasattr(self, 'show_all_btn'):
            current_text = self.show_all_btn.cget("text")
            if current_text == get_translation(self.language, "hide_all") or "hide" in current_text.lower() or "隐藏" in current_text:
                self.show_all_btn.configure(text=get_translation(language, "hide_all"))
            else:
                self.show_all_btn.configure(text=get_translation(language, "show_all"))
        
        # Update delete button
        self.delete_btn.configure(text=get_translation(language, "delete_all"))
        
        # Update individual sentence widgets
        for frame in self.sentence_widgets:
            if frame.winfo_exists():
                # Update show/hide button for each sentence
                if hasattr(frame.text_widget, 'show_button'):
                    if frame.text_widget.word_visible:
                        frame.text_widget.show_button.configure(text=get_translation(language, "hide"))
                    else:
                        frame.text_widget.show_button.configure(text=get_translation(language, "show"))
                
                # Update other buttons in each sentence frame
                for child in frame.winfo_children():
                    if isinstance(child, ttk.Button):
                        current_text = child.cget("text")
                        if current_text in ["Copy", "复制", get_translation(self.language, "copy")]:
                            child.configure(text=get_translation(language, "copy"))