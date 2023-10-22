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
    "Ulcer with stigmata": r"(?:\b(?:\w+\W+){0,5}(stigmata|stigmata of recent hemorrhage|signs of recent bleeding|active bleeding|visible vessel|spurting vessel|oozing vessel)(?:\W+\w+){0,5}\bulcer\b)|(?:\bulcer(?:\W+\w+){0,5}\W+(stigmata|stigmata of recent hemorrhage|signs of recent bleeding|active bleeding|visible vessel|spurting vessel|oozing vessel)(?:\W+\w+){0,5}\b)",
    "Erosions": r"\b(erosions|eroded areas?|erosive disease|esophageal erosions|gastric erosions|duodenal erosions)\b",
    "Malignancy": r"\b(malignancy|malignant|cancer|carcinoma|sarcoma|lymphoma|leukemia|metastatic|neoplastic|tumour|tumor|oncology|neoplasia|carcinogenesis|adenocarcinoma|carcinogen|neoplasm|cancerous|cancerous cells)\b",
    "No Lesion Identified, normal endoscopy": r"\b(no lesions? identified|normal endoscopy|no abnormalities found|no abnormal findings|endoscopy normal|normal esophagogastroduodenoscopy|normal EGD|no significant findings)\b"
}

class LabelingApp:


    def __init__(self, root):
        self.root = root
        self.current_index = 0
        self.progress = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(pady=20)
        self.labels = {key: tk.BooleanVar() for key in REGEX_PATTERNS.keys()}
        self.text_widget = tk.Text(root, wrap=tk.WORD)
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
                    writer.writerow([row[0]] + row[1])
    
    def update_progress(self):
        self.progress['value'] = (self.current_index / len(notes)) * 100
        self.root.title(f"Labeling Notes ({self.current_index+1}/{len(notes)})")

    def update_results(self):
        note_id, _ = notes[self.current_index]
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
    app.update_results()  # Save the results of the current note
    with open(result_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['PAT_ENC_CSN_ID'] + list(REGEX_PATTERNS.keys()))
        for row in results:
            if row:  # Check if the row is not None
                writer.writerow([row[0]] + row[1])
    root.destroy()

def create_empty_results_csv(filename):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['PAT_ENC_CSN_ID'] + list(REGEX_PATTERNS.keys()))

if __name__ == '__main__':
    notes = []

    with open(note_filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            note_id = row['PAT_ENC_CSN_ID']
            note_text = row['ORDER_RESULT_COMPONENT_COMMENTS']
            notes.append((note_id, note_text))

    results = [None] * len(notes)

    if not os.path.exists(result_filename):
        create_empty_results_csv(result_filename)

    root = tk.Tk()
    app = LabelingApp(root)
    app.current_index = 0
    app.show_note()
    root.protocol("WM_DELETE_WINDOW", on_closing)  # Handle the window closing event
    root.mainloop()
