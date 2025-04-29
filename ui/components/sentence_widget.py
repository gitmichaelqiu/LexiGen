import tkinter as tk
from tkinter import ttk
from models.translations import get_translation, TRANSLATIONS
from tkinter import filedialog, simpledialog, messagebox
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import platform
from nltk import word_tokenize
import markdown
import re

# Add these keys to both English and Chinese translations
for language in TRANSLATIONS:
    if "regenerate_button" not in TRANSLATIONS[language]:
        TRANSLATIONS[language]["regenerate_button"] = "↻"
    if "menu_button" not in TRANSLATIONS[language]:
        TRANSLATIONS[language]["menu_button"] = "⋮" 
    if "checkmark" not in TRANSLATIONS[language]:
        TRANSLATIONS[language]["checkmark"] = "✓"
    if "progress_indicator" not in TRANSLATIONS[language]:
        TRANSLATIONS[language]["progress_indicator"] = "{0}/{1}"

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
        
        # Create a 3-column grid layout
        frame.columnconfigure(0, weight=0)  # Order number column fixed width
        frame.columnconfigure(1, weight=1)  # Text column stretches
        frame.columnconfigure(2, weight=0)  # Button column fixed width
        
        # Add order number
        order_number = len(self.sentence_widgets) + 1
        order_label = ttk.Label(frame, text=f"{order_number}.", width=4)
        order_label.grid(row=0, column=0, sticky=tk.W, padx=(5, 0))
        
        # Create masked sentence
        masked_sentence = self._create_masked_sentence(word, sentence)
        
        # Text widget in second column
        text_widget = tk.Text(frame, wrap=tk.WORD, cursor="arrow", height=1, width=50)
        text_widget.insert("1.0", masked_sentence)
        text_widget.configure(state="disabled", selectbackground=text_widget.cget("background"), 
                            selectforeground=text_widget.cget("foreground"), 
                            inactiveselectbackground=text_widget.cget("background"))
        text_widget.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
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
        
        # Create a frame for the buttons in the third column
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(row=0, column=2, sticky=tk.E)
        
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
            text=get_translation(self.language, "regenerate_button"),
            width=2,
            command=lambda w=original_word, f=frame: self._regenerate_sentence(w, f)
        )
        regen_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # Create menu button
        menu_btn = ttk.Button(
            buttons_frame,
            text=get_translation(self.language, "menu_button"),
            width=2,
            command=lambda f=frame: self._show_menu(f)
        )
        menu_btn.pack(side=tk.LEFT)
        
        # Store references
        text_widget.original_sentence = sentence
        text_widget.masked_sentence = masked_sentence
        text_widget.word_visible = False
        text_widget.show_button = show_btn
        text_widget.original_word = original_word  # Store original word
        frame.text_widget = text_widget
        frame.menu_btn = menu_btn  # Store menu button reference
        frame.order_label = order_label  # Store order label reference
        
        self.sentence_widgets.append(frame)
        self._update_buttons_state()
        
        # Notify about sentence change
        if self.on_sentences_changed:
            self.on_sentences_changed(len(self.sentence_widgets) > 0)
        
        return frame
    
    def _create_masked_sentence(self, word, sentence):
        """Create a masked sentence by identifying and masking the target word."""
        # Get the base form of the input word
        target_word = word.lower()
        
        # Tokenize the sentence
        words = word_tokenize(sentence)
        masked_words = {}
        
        # Process each word in the sentence
        for original_word in words:
            # Skip non-alphabetic words
            if not original_word.isalpha():
                continue
            
            # Check if the word matches the target word or its variations
            if self.word_processor.is_word_match(original_word, target_word):
                masked_word = original_word[0] + '_' * (len(original_word) - 1)
                masked_words[original_word] = masked_word
        
        # Create the masked sentence
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
        
        # Ask if user wants to include analysis
        include_analysis = messagebox.askyesno(
            get_translation(self.language, "include_analysis_title"),
            get_translation(self.language, "include_analysis_prompt")
        )
        
        # If including analysis, check for missing analyses
        if include_analysis:
            # Count sentences without analysis
            missing_analyses = [frame for frame in self.sentence_widgets 
                               if not hasattr(frame.text_widget, 'analysis') or not frame.text_widget.analysis]
            
            # If there are missing analyses, generate them
            if missing_analyses:
                if not self.api_service.server_connected:
                    messagebox.showwarning(
                        get_translation(self.language, "server_error_title"),
                        get_translation(self.language, "server_connection_guide")
                    )
                    # Continue without analyses
                    include_analysis = False
                else:
                    # Create progress dialog
                    progress_window = tk.Toplevel(self)
                    progress_window.title(get_translation(self.language, "generating_analyses"))
                    progress_window.geometry("400x100")
                    progress_window.transient(self)
                    progress_window.grab_set()
                    progress_window.resizable(False, False)
                    
                    # Create progress frame
                    progress_frame = ttk.Frame(progress_window, padding="10")
                    progress_frame.pack(fill=tk.BOTH, expand=True)
                    
                    # Labels
                    ttk.Label(progress_frame, text=get_translation(self.language, "generating_analyses")).pack(pady=(0, 5))
                    progress_label = ttk.Label(progress_frame, text=get_translation(self.language, "progress_indicator").format(0, len(missing_analyses)))
                    progress_label.pack(pady=(0, 5))
                    
                    # Progress bar
                    progress_var = tk.DoubleVar()
                    progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
                    progress_bar.pack(fill=tk.X, pady=(0, 10))
                    
                    # Update progress
                    progress_window.update()
                    
                    # Generate analyses for all sentences
                    prompt = """Analyze the grammatical usage of '{word}' in this sentence: '{sentence}'
Focus on:
1. Tense (e.g., Present Simple, Past Perfect)
2. Voice (Active/Passive)
3. Mood (Indicative/Subjunctive)
4. Function (e.g., Subject, Object, Modifier)

Keep the analysis concise and technical. Output in 1 line. Example format:
"Present Simple, Active Voice. Functions as the subject of the sentence." """
                    
                    # Generate analyses one by one
                    for i, frame in enumerate(missing_analyses):
                        word = frame.text_widget.original_word
                        sentence = frame.text_widget.original_sentence
                        
                        # Update progress
                        progress_var.set((i / len(missing_analyses)) * 100)
                        progress_label.configure(text=get_translation(self.language, "progress_indicator").format(i+1, len(missing_analyses)))
                        progress_window.update()
                        
                        # Generate analysis
                        formatted_prompt = prompt.format(word=word, sentence=sentence)
                        analysis = self.api_service.generate_sentence(word, formatted_prompt)
                        
                        # Store analysis
                        if analysis:
                            frame.text_widget.analysis = analysis
                        
                        # Update progress again
                        progress_var.set(((i+1) / len(missing_analyses)) * 100)
                        progress_label.configure(text=get_translation(self.language, "progress_indicator").format(i+1, len(missing_analyses)))
                        progress_window.update()
                    
                    # Close progress window
                    progress_window.destroy()
        
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
        
        # Extract and list all blanked words with analysis if available
        for i, frame in enumerate(self.sentence_widgets, 1):
            if frame.winfo_exists():
                text_widget = frame.text_widget
                
                # Extract the blanked words from the sentence
                original = text_widget.original_sentence
                masked = text_widget.masked_sentence
                
                # Find all blanks and their answers using improved algorithm
                words = self._extract_blanked_words_improved(original, masked)
                
                if words:
                    para = doc.add_paragraph()
                    para.add_run(f"{i}. ").bold = True
                    
                    # Add word and analysis if available
                    if include_analysis and hasattr(text_widget, 'analysis') and text_widget.analysis:
                        para.add_run(f"{words[0]}; [{text_widget.analysis}]")
                    else:
                        para.add_run(", ".join(words))
                else:
                    # Fallback to using the original word if no blanks found
                    if hasattr(text_widget, 'original_word'):
                        para = doc.add_paragraph()
                        para.add_run(f"{i}. ").bold = True
                        if include_analysis and hasattr(text_widget, 'analysis') and text_widget.analysis:
                            para.add_run(f"{text_widget.original_word}; [{text_widget.analysis}]")
                        else:
                            para.add_run(text_widget.original_word)
        
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

    def _extract_blanked_words_improved(self, original, masked):
        """
        Extract words that have been blanked out in the masked sentence.
        More accurate than the previous method.
        """
        blank_answers = []
        
        # If there's no underscore in the masked sentence, there are no blanks
        if '_' not in masked:
            return []
        
        # First, identify indices where blanks appear
        orig_words = original.split()
        mask_words = masked.split()
        
        # Make sure the sentences have the same word count
        if len(orig_words) != len(mask_words):
            # Different word count indicates mismatch, fall back to advanced parsing
            return self._extract_blanks_by_pattern(original, masked)
        
        # Compare words at the same positions
        for i, (orig_word, mask_word) in enumerate(zip(orig_words, mask_words)):
            clean_orig = orig_word.strip('.,!?;:"\'()')
            clean_mask = mask_word.strip('.,!?;:"\'()')
            
            # Check if this is a blanked word (has underscores)
            if '_' in clean_mask:
                # Extract the original word without punctuation
                if clean_orig not in blank_answers:
                    blank_answers.append(clean_orig)
        
        # If we didn't find any blanks with the direct approach, try advanced pattern matching
        if not blank_answers:
            return self._extract_blanks_by_pattern(original, masked)
        
        return blank_answers

    def _extract_blanks_by_pattern(self, original, masked):
        """Extract blanks using pattern matching for more complex cases."""
        blank_answers = []
        
        # Find all masks (patterns of first letter followed by underscores)
        mask_patterns = []
        for word in masked.split():
            clean_word = word.strip('.,!?;:"\'()')
            if len(clean_word) > 1 and '_' in clean_word:
                # Get the pattern of the masked word
                mask_patterns.append((clean_word, len(clean_word), clean_word[0].lower()))
        
        # For each mask pattern, find the corresponding word in the original
        for mask, length, first_letter in mask_patterns:
            for word in original.split():
                clean_word = word.strip('.,!?;:"\'()')
                if (len(clean_word) == length and
                    clean_word[0].lower() == first_letter and
                    clean_word.lower() not in [w.lower() for w in blank_answers]):
                    blank_answers.append(clean_word)
                    break
        
        return blank_answers

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
                child.configure(text=get_translation(self.language, "checkmark"))
                
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
        
        # Renumber remaining sentences
        for i, widget in enumerate(self.sentence_widgets):
            widget.order_label.configure(text=f"{i + 1}.")
        
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
        
        # Generate new sentence
        prompt = self.api_service.settings_service.get_settings("generate_prompt") if hasattr(self.api_service, 'settings_service') and self.api_service.settings_service else None
        new_sentence = self.api_service.generate_sentence(word, prompt)
        
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

    def _show_menu(self, frame):
        """Show the menu for a sentence frame."""
        # Create menu
        menu = tk.Menu(self, tearoff=0)
        
        # Add menu items
        menu.add_command(
            label=get_translation(self.language, "move_up"),
            command=lambda: self._move_sentence(frame, -1)
        )
        menu.add_command(
            label=get_translation(self.language, "move_down"),
            command=lambda: self._move_sentence(frame, 1)
        )
        menu.add_command(
            label=get_translation(self.language, "analyze"),
            command=lambda: self._show_analysis(frame)
        )
        menu.add_command(
            label=get_translation(self.language, "edit"),
            command=lambda: self._edit_sentence(frame)
        )
        menu.add_separator()
        menu.add_command(
            label=get_translation(self.language, "delete"),
            command=lambda: self._delete_sentence(frame)
        )
        
        # Get button position
        btn = frame.menu_btn
        x = btn.winfo_rootx()
        y = btn.winfo_rooty() + btn.winfo_height()
        
        # Show menu and bind to close on click outside
        menu.post(x, y)
        menu.bind("<Unmap>", lambda e: menu.destroy())
        
        # Bind to close on any click
        def close_menu(e):
            menu.destroy()
            self.unbind("<Button-1>")
        
        self.bind("<Button-1>", close_menu)

    def _move_sentence(self, frame, direction):
        index = self.sentence_widgets.index(frame)
        new_index = index + direction
        
        if 0 <= new_index < len(self.sentence_widgets):
            # Remove from current position
            self.sentence_widgets.pop(index)
            # Insert at new position
            self.sentence_widgets.insert(new_index, frame)
            
            # Update grid positions
            for i, widget in enumerate(self.sentence_widgets):
                widget.grid(row=i)
            
            # Update all order numbers
            for i, widget in enumerate(self.sentence_widgets):
                widget.order_label.configure(text=f"{i + 1}.")
            
            # Notify about sentence change
            if self.on_sentences_changed:
                self.on_sentences_changed(len(self.sentence_widgets) > 0)

    def _show_analysis(self, frame):
        """Show analysis window for the sentence."""
        text_widget = frame.text_widget
        word = text_widget.original_word
        sentence = text_widget.original_sentence
        
        # Create and show analysis window
        AnalysisWindow(self, word, sentence, self.api_service, self.language, text_widget)

    def _edit_sentence(self, frame):
        """Edit a sentence."""
        text_widget = frame.text_widget
        word = text_widget.original_word
        sentence = text_widget.original_sentence
        
        # Create and show edit window
        EditSentenceWindow(self, word, sentence, self.api_service, self.language, frame)

class AnalysisWindow(tk.Toplevel):
    def __init__(self, parent, word, sentence, api_service, language, text_widget):
        super().__init__(parent)
        self.title(get_translation(language, "word_analysis"))
        self.geometry("600x400")
        self.resizable(True, True)
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        # Store references
        self.api_service = api_service
        self.language = language
        self.word = word
        self.sentence = sentence
        self.text_widget = text_widget
        self.analysis = None
        self.editing = False
        
        # Bind to window close event
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Create main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Word and sentence display
        word_frame = ttk.Frame(main_frame)
        word_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(word_frame, text=f"{get_translation(language, 'word')}: {word}").pack(side=tk.LEFT)
        ttk.Label(word_frame, text=f"{get_translation(language, 'sentence')}: {sentence}").pack(side=tk.LEFT, padx=(20, 0))
        
        # Analysis text widget
        self.analysis_text = tk.Text(main_frame, wrap=tk.WORD, height=15, state="disabled")
        self.analysis_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        self.regenerate_btn = ttk.Button(
            buttons_frame,
            text=get_translation(language, "regenerate_analysis"),
            command=self._regenerate_analysis
        )
        self.regenerate_btn.pack(side=tk.LEFT)
        
        self.edit_btn = ttk.Button(
            buttons_frame,
            text=get_translation(language, "edit_analysis"),
            command=self._toggle_edit_mode
        )
        self.edit_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        close_btn = ttk.Button(
            buttons_frame,
            text=get_translation(language, "close"),
            command=self._on_close
        )
        close_btn.pack(side=tk.RIGHT)
        
        # Check for existing analysis
        if hasattr(text_widget, 'analysis') and text_widget.analysis:
            self.analysis = text_widget.analysis
            self._display_analysis()
        else:
            self._generate_analysis()
    
    def _toggle_edit_mode(self):
        """Toggle between view and edit modes for the analysis text."""
        if not self.editing:
            # Switch to edit mode
            self.analysis_text.configure(state="normal")
            self.edit_btn.configure(text=get_translation(self.language, "save_analysis"))
            self.editing = True
        else:
            # Switch back to view mode and save changes
            self.analysis = self.analysis_text.get("1.0", "end-1c").strip()
            self.analysis_text.configure(state="disabled")
            self.edit_btn.configure(text=get_translation(self.language, "edit_analysis"))
            self.editing = False
    
    def _display_analysis(self):
        """Display the analysis in the text widget with markdown formatting."""
        if not self.analysis:
            return
            
        # Display the text directly
        self.analysis_text.configure(state="normal")
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert("1.0", self.analysis)
        self.analysis_text.configure(state="disabled")
    
    def _generate_analysis(self):
        """Generate analysis for the word in the sentence."""
        if not self.api_service.server_connected:
            messagebox.showwarning(
                get_translation(self.language, "server_error_title"),
                get_translation(self.language, "server_connection_guide")
            )
            return
        
        # Get analysis prompt from settings
        prompt_template = self.api_service.settings_service.get_settings("analysis_prompt") if hasattr(self.api_service, 'settings_service') and self.api_service.settings_service else None
        if prompt_template:
            prompt = prompt_template.format(word=self.word, sentence=self.sentence)
        else:
            prompt = f"Analyze the grammatical usage of '{self.word}' in this sentence: '{self.sentence}'"
        self.analysis = self.api_service.generate_sentence(self.word, prompt)
        
        if self.analysis:
            self._display_analysis()
        else:
            messagebox.showerror(
                get_translation(self.language, "error_title"),
                get_translation(self.language, "analysis_generation_failed")
            )
    
    def _regenerate_analysis(self):
        """Regenerate the analysis."""
        self.regenerate_btn.configure(state="disabled")
        self.edit_btn.configure(state="disabled")
        
        # Reset to view mode if currently editing
        if self.editing:
            self.editing = False
            self.edit_btn.configure(text=get_translation(self.language, "edit_analysis"))
        
        self._generate_analysis()
        
        self.regenerate_btn.configure(state="normal")
        self.edit_btn.configure(state="normal")
    
    def _on_close(self):
        """Store analysis in text widget and close window."""
        # If in edit mode, save the current text
        if self.editing:
            self.analysis = self.analysis_text.get("1.0", "end-1c").strip()
        
        if self.analysis:
            self.text_widget.analysis = self.analysis
        self.destroy()

class EditSentenceWindow(tk.Toplevel):
    def __init__(self, parent, word, sentence, api_service, language, frame):
        super().__init__(parent)
        self.title(get_translation(language, "edit_sentence"))
        self.geometry("600x250")
        self.resizable(True, True)
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        # Bind to window close event
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        # Store references
        self.parent = parent
        self.api_service = api_service
        self.language = language
        self.word = word
        self.original_sentence = sentence
        self.frame = frame
        
        # Create main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Word display
        word_frame = ttk.Frame(main_frame)
        word_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(word_frame, text=f"{get_translation(language, 'word')}: {word}").pack(side=tk.LEFT)
        
        # Sentence editing
        sentence_frame = ttk.Frame(main_frame)
        sentence_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(sentence_frame, text=f"{get_translation(language, 'sentence')}:").pack(anchor=tk.W)
        
        # Sentence text widget
        self.sentence_text = tk.Text(sentence_frame, wrap=tk.WORD, height=5)
        self.sentence_text.insert("1.0", sentence)
        self.sentence_text.pack(fill=tk.X, expand=True, pady=(5, 0))
        
        # Label with warning
        warning_label = ttk.Label(main_frame, text=get_translation(language, "edit_warning"), foreground="red")
        warning_label.pack(pady=(0, 10))
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X)
        
        save_btn = ttk.Button(
            buttons_frame,
            text=get_translation(language, "save"),
            command=self._save_changes
        )
        save_btn.pack(side=tk.LEFT)
        
        cancel_btn = ttk.Button(
            buttons_frame,
            text=get_translation(language, "cancel"),
            command=self.destroy
        )
        cancel_btn.pack(side=tk.RIGHT)
    
    def _save_changes(self):
        """Save the edited sentence."""
        new_sentence = self.sentence_text.get("1.0", "end-1c").strip()
        
        # Don't do anything if the sentence is empty or unchanged
        if not new_sentence or new_sentence == self.original_sentence:
            self.destroy()
            return
        
        # Update the sentence in the frame
        text_widget = self.frame.text_widget
        
        # Update original sentence
        text_widget.original_sentence = new_sentence
        
        # Create new masked sentence
        text_widget.masked_sentence = self.parent._create_masked_sentence(self.word, new_sentence)
        
        # Update the display based on current visibility
        text_widget.configure(state="normal")
        text_widget.delete("1.0", tk.END)
        
        if hasattr(text_widget, 'word_visible') and text_widget.word_visible:
            text_widget.insert("1.0", new_sentence)
        else:
            text_widget.insert("1.0", text_widget.masked_sentence)
        
        # Remove analysis if it exists as the sentence has changed
        if hasattr(text_widget, 'analysis'):
            delattr(text_widget, 'analysis')
        
        # Adjust height
        text_widget.see("end")
        num_lines = text_widget.count("1.0", "end", "displaylines")[0]
        text_widget.configure(height=max(2, num_lines))
        text_widget.configure(state="disabled")
        
        self.destroy()