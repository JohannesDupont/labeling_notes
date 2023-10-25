import csv
import re
import tkinter as tk
from tkinter import ttk
import os
result_filename = 'app/finished_labeling/external_results_labeled_notes.csv'
note_filename = 'app/notes_to_label/external_validation_cohort_note_text.csv'
# Regular expressions for highlighting and labeling
REGEX_PATTERNS = {
    "Mallory-Weiss Tear": r"\b(Mallory[-\s]Weiss(?:\sTear)?|esophageal tear|mwt|gastroesophageal tear|stomach tear)\b",
    "Esophagitis": r"\b(esophagitis|inflammation of the esophagus|esophageal inflammation)\b",
    "Esophageal Varices": r"\b(esophageal varices|varices|varix|dilated veins in esophagus)\b",
    "Ulcer": r"\b(ulcer|ulceration|peptic ulcer|gastric ulcer|duodenal ulcer|esophageal ulcer|stomach ulcer)\b",
    "Ulcer with stigmata": r"(?:\b(?:\w+\W+){0,5}(stigmata|stigmata of recent hemorrhage|signs of recent bleeding|bleeding|active bleeding|visible vessel|spurting vessel|oozing vessel)(?:\W+\w+){0,5}\bulcer\b)|(?:\bulcer(?:\W+\w+){0,5}\W+(stigmata|stigmata of recent hemorrhage|signs of recent bleeding|active bleeding|visible vessel|spurting vessel|oozing vessel)(?:\W+\w+){0,5}\b)",
    "Erosions": r"\b(erosions|eroded areas?|erosive disease|erosion|erosive|esophageal erosions|gastric erosions|duodenal erosions)\b",
    "Malignancy": r"\b(malignancy|malignant|cancer|mass|carcinoma|gist|sarcoma|metastasis|metast|lymphoma|leukemia|metastatic|neoplastic|tumour|tumor|oncology|neoplasia|carcinogenesis|adenocarcinoma|carcinogen|neoplasm|cancerous|cancerous cells)\b",
    "Major stigmata of recent hemorrhage": r"\b(major\s+stigmata\s+of\s+recent\s+hemorrhage|msrh|major\s+stigmata(?:\s+of)?\s+hemorrhage?|blood|bleeding|active\s+bleeding|fresh\s+blood|old\s+blood|recent\s+hemorrhage|blood\s+clots)\b",
    "No Lesion Identified, normal endoscopy": r"\b(no lesions? identified|normal endoscopy|no abnormalities found|no abnormal findings|endoscopy normal|normal esophagogastroduodenoscopy|normal EGD|no significant findings)\b",

    "Negation Terms": r"\b(no(?: evidence of| signs of)?|without|not|negative|absent|none|neither|nor)\b",

}

class LabelingApp:


    def __init__(self, root):
        self.root = root
        self.current_index = 0
        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=20)
        self.labels = {key: tk.BooleanVar() for key in REGEX_PATTERNS.keys()}
        self.text_widget = tk.Text(root, wrap=tk.WORD)
        self.text_widget.tag_configure("Negation Terms", foreground="red")
        self.text_widget.pack(padx=10, pady=10)
        self.update_progress()
        
        for pattern_name, pattern in REGEX_PATTERNS.items():
            self.text_widget.tag_configure(pattern_name, background="yellow")
        
        self.text_widget.config(state=tk.DISABLED)
        
        for label_name, var in self.labels.items():
            chk = ttk.Checkbutton(root, text=label_name, variable=var)
            chk.pack(anchor=tk.W, padx=10)

        prev_btn = ttk.Button(root, text="Previous", command=self.previous)
        prev_btn.pack(side=tk.LEFT, padx=10, pady=20)

        submit_btn = ttk.Button(root, text="Submit", command=self.submit)
        submit_btn.pack(side=tk.RIGHT, padx=10, pady=20)
        


    def submit(self):
        self.update_results()
        self.write_results_to_file()   # Write to file after updating results
        self.current_index += 1
        self.update_progress()
        if self.current_index < len(notes):
            self.show_note()
        else:
            self.root.destroy()
    
    def write_results_to_file(self):
        with open(result_filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['PAT_ENC_CSN_ID'] + list(REGEX_PATTERNS.keys()))
            for row in results:
                if row:  # Check if the row is not None
                    writer.writerow([row[0]] + ['True' if label else 'False' for label in row[1]])  # Change here
    
    def update_progress(self):
        self.progress['value'] = (self.current_index / len(notes)) * 100
        self.root.title(f"Labeling Notes ({self.current_index+1}/{len(notes)})")

    def update_results(self):
        note_entry = notes[self.current_index]
        if len(note_entry) != 2:  # Check if the entry has an unexpected number of values
            print(f"Warning: Unexpected entry format at index {self.current_index}: {note_entry}")
            return
        note_id, _ = note_entry
        labels = self.get_labels()
        results[self.current_index] = (note_id, labels)

    def previous(self):
        self.update_results()
        self.current_index -= 1
        self.show_note()
        self.update_progress()

    def show_note(self):
        self.note_text = notes[self.current_index][1]
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, self.note_text)

        for pattern_name, pattern in REGEX_PATTERNS.items():
            self.text_widget.tag_remove(pattern_name, 1.0, tk.END)
            for match in re.finditer(pattern, self.note_text, flags=re.IGNORECASE):
                self.text_widget.tag_add(pattern_name, "1.0 + {} chars".format(match.start()), "1.0 + {} chars".format(match.end()))

        self.text_widget.config(state=tk.DISABLED)

        # Reset checkboxes
        for var in self.labels.values():
            var.set(False)

        # If we have previous results, set the checkboxes accordingly
        if results[self.current_index]:
            _, previous_labels = results[self.current_index]
            for var, prev_value in zip(self.labels.values(), previous_labels):
                var.set(prev_value)

    def get_labels(self):
        return [self.labels[key].get() for key in REGEX_PATTERNS.keys()]


def on_closing():
    app.update_results()
    with open(result_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['PAT_ENC_CSN_ID'] + list(REGEX_PATTERNS.keys()))
        for row in results:
            if row:  # Check if the row is not None
                writer.writerow([row[0]] + ['True' if label else 'False' for label in row[1]])  # Change here
    root.destroy()


def create_empty_results_csv(filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['PAT_ENC_CSN_ID'] + list(REGEX_PATTERNS.keys()))

def load_existing_results(filename):
    results = [None] * len(notes)
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            index = [note[0] for note in notes].index(row[0])
            labels = [label_value == 'True' for label_value in row[1:]]  # Change here
            results[index] = (row[0], labels)

    return results, index


if __name__ == '__main__':
    notes = []

    # Load notes from the CSV
    print('starting programm')
    with open(note_filename, 'r', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        notes = [(row['PAT_ENC_CSN_ID'], row['ORDER_RESULT_COMPONENT_COMMENTS']) for row in reader]

        # Check if results file exists
        if os.path.exists(result_filename):
            print('result file exists, continuing where left off', flush=True)
            results, last_labeled_index= load_existing_results(result_filename)
            # Find the last labeled note (the first None in results) and set current_index accordingly
            try:
                last_labeled_index = results.index(None)
            except ValueError:  # All notes have been labeled
                last_labeled_index = len(notes) - 1
        else:
            results = [None] * len(notes)
            create_empty_results_csv(result_filename)
            last_labeled_index = 0
    


    root = tk.Tk()
    app = LabelingApp(root)
    
    #app.current_index = last_labeled_index 
    print('last_labeled_index', last_labeled_index)
    app.current_index = last_labeled_index if 'last_labeled_index' in locals() else 0
    app.show_note()
    print('app ready', flush=True)
    root.protocol("WM_DELETE_WINDOW", on_closing)  # Handle the window closing event
    root.mainloop()
