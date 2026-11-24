import tkinter as tk

from review_window import show_review_window


root = tk.Tk()
root.title("NetSage AI Test")
root.geometry("400x200")

sample_evidence = """
PC cannot access the internet.
Gateway configured: 192.168.1.254
Expected gateway: 192.168.1.1
"""

sample_diagnosis = {
    "case_id": "NS002",
    "problem_summary": "PC cannot reach remote network",
    "probable_root_cause": "Incorrect default gateway",
    "confidence": 95,
    "evidence": [
        "Configured gateway differs from expected gateway"
    ],
    "next_command": "show ip interface brief",
    "recommended_fix": "Correct the PC default gateway",
    "human_approval_required": True,
    "diagnosis_status": "Awaiting human review"
}


def open_review():
    show_review_window(
        root,
        sample_evidence,
        sample_diagnosis
    )


tk.Button(
    root,
    text="Open Human Review",
    command=open_review
).pack(pady=50)

root.mainloop()