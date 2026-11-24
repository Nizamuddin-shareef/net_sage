import tkinter as tk
from tkinter import ttk, messagebox
from human_review import get_review_statistics, REVIEW_FILE


def show_review_stats(parent=None):

    # Read the statistics first so a bad review file shows a clear message
    # instead of a crash or an empty window.
    try:
        stats = get_review_statistics()
    except Exception as error:
        messagebox.showerror(
            "Statistics Error",
            f"Could not read {REVIEW_FILE.name}:\n{error}",
            parent=parent
        )
        return

    window = tk.Toplevel(parent) if parent is not None else tk.Tk()
    window.title("NetSage AI - Review Statistics")
    window.minsize(500, 380)
    window.resizable(False, False)

    if parent is not None:
        window.transient(parent)

    main = ttk.Frame(window, padding=20)
    main.pack(fill="both", expand=True)

    ttk.Label(
        main,
        text="HUMAN REVIEW STATISTICS",
        font=("Arial", 16, "bold")
    ).pack(pady=15)

    items = [
        ("Total Reviews", stats["total"]),
        ("Accepted", stats["accepted"]),
        ("Edited / Corrected", stats["edited"]),
        ("Rejected", stats["rejected"]),
    ]

    for label, value in items:

        frame = ttk.Frame(main)
        frame.pack(fill="x", pady=8)

        ttk.Label(
            frame,
            text=label,
            font=("Arial", 11)
        ).pack(side="left")

        ttk.Label(
            frame,
            text=str(value),
            font=("Arial", 11, "bold")
        ).pack(side="right")

    ttk.Separator(main).pack(fill="x", pady=15)

    ttk.Label(
        main,
        text=f"Review data is stored in data/{REVIEW_FILE.name}",
        font=("Arial", 9)
    ).pack()

    ttk.Button(
        main,
        text="Close",
        command=window.destroy
    ).pack(pady=20)

    if parent is None:
        window.mainloop()


if __name__ == "__main__":
    show_review_stats()