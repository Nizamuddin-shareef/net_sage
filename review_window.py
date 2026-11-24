import json
import tkinter as tk
from tkinter import ttk, messagebox

from human_review import save_review


def show_review_window(parent, evidence, ai_diagnosis):

    window = tk.Toplevel(parent)
    window.title("NetSage AI - Human Review")
    window.geometry("850x750")
    window.minsize(700, 600)

    window.transient(parent)
    window.grab_set()  # keep focus on this window until it is closed

    # Main frame
    main = ttk.Frame(window, padding=12)
    main.pack(fill="both", expand=True)

    ttk.Label(
        main,
        text="NETSAGE AI - HUMAN REVIEW",
        font=("Arial", 16, "bold")
    ).pack(pady=(0, 10))

    # Evidence
    ttk.Label(
        main,
        text="Network Evidence:",
        font=("Arial", 10, "bold")
    ).pack(anchor="w")

    evidence_box = tk.Text(main, height=5, wrap="word")
    evidence_box.pack(fill="x", pady=5)
    evidence_box.insert("1.0", evidence)
    evidence_box.config(state="disabled")

    # Diagnosis editor
    ttk.Label(
        main,
        text="AI Diagnosis (editable JSON):",
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(10, 0))

    diagnosis_box = tk.Text(
        main,
        height=18,
        wrap="word",
        font=("Consolas", 10)
    )
    diagnosis_box.pack(fill="both", expand=True, pady=5)

    diagnosis_box.insert(
        "1.0",
        json.dumps(ai_diagnosis, indent=4)
    )

    # Notes
    ttk.Label(
        main,
        text="Reviewer Notes:",
        font=("Arial", 10, "bold")
    ).pack(anchor="w", pady=(10, 0))

    notes_box = tk.Text(main, height=4, wrap="word")
    notes_box.pack(fill="x", pady=5)

    past_tense = {
        "Accept": "accepted",
        "Edit": "saved as edited",
        "Reject": "rejected",
    }

    # Save review
    def record_review(decision):

        try:
            notes = notes_box.get("1.0", "end-1c").strip()

            if decision == "Accept":
                # Accept means the AI diagnosis was right as given,
                # even if the text box was changed by accident.
                human_diagnosis = ai_diagnosis

            elif decision == "Reject":
                human_diagnosis = {}

            else:  # Edit
                edited_text = diagnosis_box.get("1.0", "end-1c").strip()
                human_diagnosis = json.loads(edited_text)

                if not isinstance(human_diagnosis, dict):
                    raise ValueError(
                        "The diagnosis must be a JSON object { ... }."
                    )

                if human_diagnosis == ai_diagnosis:
                    raise ValueError(
                        "No changes were made. Edit the diagnosis first, "
                        "or use Accept."
                    )

            save_review(
                evidence=evidence,
                ai_diagnosis=ai_diagnosis,
                decision=decision,
                human_diagnosis=human_diagnosis,
                reviewer_notes=notes
            )

            messagebox.showinfo(
                "Review Saved",
                f"Diagnosis {past_tense[decision]}.",
                parent=window
            )

            window.destroy()

        except json.JSONDecodeError:
            messagebox.showerror(
                "Invalid JSON",
                "The diagnosis must contain valid JSON.",
                parent=window
            )

        except Exception as error:
            messagebox.showerror(
                "Review Error",
                str(error),
                parent=window
            )

    # Buttons
    button_frame = ttk.Frame(main)
    button_frame.pack(fill="x", pady=12)

    ttk.Button(
        button_frame,
        text="Accept",
        command=lambda: record_review("Accept")
    ).pack(side="left", padx=5)

    ttk.Button(
        button_frame,
        text="Save Edited Diagnosis",
        command=lambda: record_review("Edit")
    ).pack(side="left", padx=5)

    ttk.Button(
        button_frame,
        text="Reject",
        command=lambda: record_review("Reject")
    ).pack(side="left", padx=5)

    ttk.Button(
        button_frame,
        text="Close",
        command=window.destroy
    ).pack(side="right", padx=5)