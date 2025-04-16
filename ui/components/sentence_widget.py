import tkinter as tk
from tkinter import ttk
from models.translations import get_translation
from tkinter import filedialog, simpledialog, messagebox
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import platform

class SentenceWidgetManager(ttk.LabelFrame):
    def __init__(self, parent, language, word_processor, api_service, on_sentences_changed=None):
        super().__init__(parent, text=get_translation(language, "generated_sentences"), padding="5")
        self.language = language
        self.word_processor = word_processor
        self.api_service = api_service
        self.sentence_widgets = []
        self.parent = parent
        self.on_sentences_changed = on_sentences_changed
        
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
        
        # Platform specific mousewheel bindings
        self._bind_mouse_wheel()
        
    def _bind_mouse_wheel(self):
        """Bind mouse wheel scrolling based on platform."""
        system = platform.system()
        
        if system == "Windows":
            # Windows uses <MouseWheel>
            self.canvas.bind("<MouseWheel>", self._on_mousewheel_windows)
            self.bind("<MouseWheel>", self._on_mousewheel_windows)
        elif system == "Darwin":
            # macOS uses <MouseWheel> with different delta values
            self.canvas.bind("<MouseWheel>", self._on_mousewheel_macos)
            self.bind("<MouseWheel>", self._on_mousewheel_macos)
        else:
            # Linux uses Button-4 and Button-5
            self.canvas.bind("<Button-4>", self._on_mousewheel_linux)
            self.canvas.bind("<Button-5>", self._on_mousewheel_linux)
            self.bind("<Button-4>", self._on_mousewheel_linux)
            self.bind("<Button-5>", self._on_mousewheel_linux)
    
    def _on_mousewheel_windows(self, event):
        """Handle mouse wheel scrolling for Windows."""
        if self.canvas.winfo_height() < self.sentences_container.winfo_height():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"
    
    def _on_mousewheel_macos(self, event):
        """Handle mouse wheel scrolling for macOS."""
        if self.canvas.winfo_height() < self.sentences_container.winfo_height():
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        return "break"
    
    def _on_mousewheel_linux(self, event):
        """Handle mouse wheel scrolling for Linux."""
        if self.canvas.winfo_height() < self.sentences_container.winfo_height():
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")
        return "break"
    
    def _on_frame_configure(self, event=None):
        """Update the scrollregion to encompass the inner frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Resize the inner frame to match the canvas."""
        self.canvas.itemconfig(self.canvas_frame, width=event.width)
        
    def _on_mousewheel(self, event):
        """Legacy method, replaced by platform-specific methods."""
        pass
    
    def add_sentence(self, word, sentence):
        frame = ttk.Frame(self.sentences_container)
        frame.grid(sticky=(tk.W, tk.E), pady=2)
        
        # Create a 2-column grid layout
        # First column for text widget (will stretch)
        # Second column for buttons (right-aligned)
        frame.columnconfigure(0, weight=1)  # Text column stretches
        frame.columnconfigure(1, weight=0)  # Button column fixed width
        
        # Create masked sentence
        masked_sentence = self._create_masked_sentence(word, sentence)
        
        # Text widget in first column
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
        
        # Create a frame for the buttons in the second column
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=0, column=1, sticky=tk.E)
        
        # Buttons inside the buttons_frame
        show_btn = ttk.Button(
            buttons_frame,
            text=get_translation(self.language, "show"),
            command=lambda: self._toggle_word(text_widget, show_btn)
        )
        show_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        copy_btn = ttk.Button(
            buttons_frame,
            text=get_translation(self.language, "copy"),
            command=lambda: self._copy_sentence(text_widget)
        )
        copy_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # Store original word for regeneration
        original_word = word
        
        regen_btn = ttk.Button(
            buttons_frame,
            text="↻",
            width=2,
            command=lambda w=original_word, f=frame: self._regenerate_sentence(w, f)
        )
        regen_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        delete_btn = ttk.Button(
            buttons_frame,
            text="×",
            width=2,
            command=lambda: self._delete_sentence(frame)
        )
        delete_btn.pack(side=tk.LEFT)
        
        # Store references
        text_widget.original_sentence = sentence
        text_widget.masked_sentence = masked_sentence
        text_widget.word_visible = False
        text_widget.show_button = show_btn
        text_widget.original_word = original_word  # Store original word
        frame.text_widget = text_widget
        
        self.sentence_widgets.append(frame)
        self._update_buttons_state()
        
        # Notify about sentence change
        if self.on_sentences_changed:
            self.on_sentences_changed(len(self.sentence_widgets) > 0)
        
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
        
        # Add exercises with blanks first
        for i, frame in enumerate(self.sentence_widgets, 1):
            if frame.winfo_exists():
                text_widget = frame.text_widget
                
                # Add exercise with blanks
                para = doc.add_paragraph()
                para.add_run(f"{i}. ").bold = True
                para.add_run(text_widget.masked_sentence)
        
        # Add page break before answer key
        doc.add_page_break()
        
        # Add answer key title
        answer_title = doc.add_paragraph()
        answer_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        answer_title_run = answer_title.add_run("Answer Key")
        answer_title_run.bold = True
        answer_title_run.font.size = Pt(14)
        
        # Extract and list all blanked words
        for i, frame in enumerate(self.sentence_widgets, 1):
            if frame.winfo_exists():
                text_widget = frame.text_widget
                
                # Extract words from the text widget
                if hasattr(text_widget, 'original_word'):
                    # Use the stored original word (the word used to generate the sentence)
                    para = doc.add_paragraph()
                    para.add_run(f"{i}. ").bold = True
                    para.add_run(text_widget.original_word)
                else:
                    # Fallback to extracting words from the sentence
                    original = text_widget.original_sentence
                    masked = text_widget.masked_sentence
                    
                    # Find all blanks and their answers
                    words = self._extract_blanked_words(original, masked)
                    
                    if words:
                        para = doc.add_paragraph()
                        para.add_run(f"{i}. ").bold = True
                        para.add_run(", ".join(words))
        
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

    def _extract_blanked_words(self, original, masked):
        """Extract words that have been blanked out in the masked sentence."""
        blanked_words = []
        
        # If there's no underscore in the masked sentence, there are no blanks
        if '_' not in masked:
            return []
        
        # Find all underscored patterns in the masked sentence
        mask_patterns = []
        words = masked.split()
        for word in words:
            if '_' in word:
                # Clean the word of punctuation
                clean_word = word.strip('.,!?;:"\'()')
                if clean_word and '_' in clean_word:
                    mask_patterns.append(clean_word)
        
        # For each mask pattern, find the corresponding original word
        for mask in mask_patterns:
            # The mask pattern is typically first letter + underscores
            if len(mask) > 1 and '_' in mask:
                prefix = mask[0]
                length = len(mask)
                
                # Look for words in the original sentence that match this pattern
                for orig_word in original.split():
                    # Clean the original word
                    clean_orig = orig_word.strip('.,!?;:"\'()')
                    
                    # Check if this could be our word
                    if (len(clean_orig) == length and 
                        clean_orig[0].lower() == prefix.lower() and
                        clean_orig.lower() not in [w.lower() for w in blanked_words]):
                        
                        blanked_words.append(clean_orig)
                        break
        
        return blanked_words

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
        # First destroy all sentence widgets
        for widget in self.sentence_widgets:
            widget.destroy()
        self.sentence_widgets.clear()
        self._update_buttons_state()
        
        # Reset canvas and container
        self.canvas.delete("all")  # Delete all canvas items
        
        # Recreate the sentences container
        self.sentences_container.destroy()
        self.sentences_container = ttk.Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.sentences_container, anchor="nw")
        
        # Rebind events
        self.sentences_container.bind('<Configure>', self._on_frame_configure)
        
        # Reset canvas scroll region
        self.canvas.configure(scrollregion=(0, 0, 0, 0))
        
        # Force update to clear any remaining visual artifacts
        self.update_idletasks()
        self.canvas.update()
        
        # Notify about sentence change
        if self.on_sentences_changed:
            self.on_sentences_changed(False)

    def _copy_sentence(self, text_widget):
        """Copy sentence to clipboard."""
        # Check if the word is visible and copy accordingly
        if hasattr(text_widget, 'word_visible') and text_widget.word_visible:
            # Copy the original sentence with filled blanks
            sentence = text_widget.original_sentence
        else:
            # Copy the masked sentence with blanks
            sentence = text_widget.masked_sentence
        
        # Strip any trailing newlines or spaces
        sentence = sentence.strip()
        
        # Copy to clipboard
        self.clipboard_clear()
        self.clipboard_append(sentence)
        
        # Show brief visual feedback using the parent widget's status
        for child in text_widget.master.winfo_children():
            if isinstance(child, ttk.Button) and child.cget("text") == get_translation(self.language, "copy"):
                original_text = child.cget("text")
                child.configure(text="✓")
                
                # Reset the button text after a short delay
                def reset_text():
                    if child.winfo_exists():
                        child.configure(text=original_text)
                
                # Schedule reset after 1 second
                self.after(1000, reset_text)
                break

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
        
        # Notify about sentence change
        if self.on_sentences_changed:
            self.on_sentences_changed(len(self.sentence_widgets) > 0)
        
        # If this was the last sentence, reset the canvas completely
        if not self.sentence_widgets:
            # Reset canvas and container similar to clear_sentences
            self.canvas.delete("all")  # Delete all canvas items
            
            # Recreate the sentences container
            self.sentences_container.destroy()
            self.sentences_container = ttk.Frame(self.canvas)
            self.canvas_frame = self.canvas.create_window((0, 0), window=self.sentences_container, anchor="nw")
            
            # Rebind events
            self.sentences_container.bind('<Configure>', self._on_frame_configure)
            
            # Reset canvas scroll region
            self.canvas.configure(scrollregion=(0, 0, 0, 0))
            
            # Force update to clear any remaining visual artifacts
            self.update_idletasks()
            self.canvas.update()

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