
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import subprocess
import platform
import os
import json
import csv
from pathlib import Path
from datetime import datetime

from diagnostic_engine import analyze_network_evidence
from ai_engine import diagnose_with_ai
from review_window import show_review_window


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

EVIDENCE_FILE = DATA_DIR / "evidence.txt"
DIAGNOSIS_LOG = DATA_DIR / "diagnosis_log.txt"
REVIEW_LOG = DATA_DIR / "review_log.csv"
DATASET_FILE = DATA_DIR / "network_dataset.csv"

BG = "#0b1120"
PANEL = "#111827"
PANEL2 = "#172033"
FG = "#e5e7eb"
MUTED = "#9ca3af"
ACCENT = "#38bdf8"
GREEN = "#22c55e"
ORANGE = "#f59e0b"
RED = "#ef4444"


# ============================================================
# MAIN APPLICATION
# ============================================================

class NetSageApp:

    def __init__(self, root):
        self.root = root
        self.root.title("NetSage AI | Network Intelligence Dashboard")
        self.root.geometry("1200x760")
        self.root.minsize(950, 650)
        self.root.configure(bg=BG)

        self.status_var = tk.StringVar(value="SYSTEM READY")
        self.mode_var = tk.StringVar(value="ENGINE: READY")
        self.current_evidence = ""

        self.setup_style()
        self.build_ui()

    # --------------------------------------------------------
    # STYLING
    # --------------------------------------------------------

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=PANEL,
            foreground=FG,
            fieldbackground=PANEL,
            rowheight=28
        )

        style.configure(
            "Treeview.Heading",
            background=PANEL2,
            foreground=FG,
            font=("Segoe UI", 10, "bold")
        )

        style.map(
            "Treeview",
            background=[("selected", "#1e40af")],
            foreground=[("selected", "white")]
        )

    # --------------------------------------------------------
    # UI
    # --------------------------------------------------------

    def build_ui(self):

        # HEADER
        header = tk.Frame(self.root, bg=BG)
        header.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(
            header,
            text="NETSAGE AI",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 22, "bold")
        ).pack(side="left")

        tk.Label(
            header,
            text="NETWORK TROUBLESHOOTING INTELLIGENCE",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(side="left", padx=18, pady=10)

        tk.Label(
            header,
            textvariable=self.mode_var,
            bg=BG,
            fg=GREEN,
            font=("Segoe UI", 10, "bold")
        ).pack(side="right", padx=10)

        # STATUS
        status_bar = tk.Frame(self.root, bg=PANEL2)
        status_bar.pack(fill="x", padx=20, pady=5)

        tk.Label(
            status_bar,
            textvariable=self.status_var,
            bg=PANEL2,
            fg=GREEN,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=12, pady=8)

        # MAIN LAYOUT
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=20, pady=10)

        sidebar = tk.Frame(main, bg=PANEL, width=220)
        sidebar.pack(side="left", fill="y", padx=(0, 12))
        sidebar.pack_propagate(False)

        content = tk.Frame(main, bg=BG)
        content.pack(side="left", fill="both", expand=True)

        # SIDEBAR
        tk.Label(
            sidebar,
            text="OPERATIONS",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", padx=15, pady=(20, 10))

        self.create_button(sidebar, "AI Diagnosis", self.open_evidence_window)
        self.create_button(sidebar, "Local Diagnosis", self.open_local_evidence_window)
        self.create_button(sidebar, "Load Dataset Case", self.load_dataset_case)
        self.create_button(sidebar, "View All Dataset", self.view_dataset)
        self.create_button(sidebar, "IP Configuration", self.run_ipconfig)
        self.create_button(sidebar, "Ping Test", self.open_ping_window)
        self.create_button(sidebar, "Diagnosis History", self.view_history)
        self.create_button(sidebar, "Review Statistics", self.view_review_stats)

        tk.Label(
            sidebar,
            text="NETSAGE AI\nRule Engine + Gemini\nHuman-in-the-loop",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9),
            justify="left"
        ).pack(anchor="w", padx=15, pady=20)

        # MAIN CONTENT HEADER
        tk.Label(
            content,
            text="NETWORK COMMAND CENTER",
            bg=BG,
            fg=FG,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", pady=(0, 10))

        # DASHBOARD CARDS
        cards = tk.Frame(content, bg=BG)
        cards.pack(fill="x", pady=5)

        self.create_card(cards, "AI ENGINE", "Gemini API", ACCENT)
        self.create_card(cards, "LOCAL ENGINE", "Rule-based", GREEN)
        self.create_card(cards, "HUMAN REVIEW", "Enabled", ORANGE)
        self.create_card(cards, "SYSTEM", "Operational", GREEN)

        # NETWORK OVERVIEW
        topology = tk.Frame(content, bg=PANEL, padx=15, pady=15)
        topology.pack(fill="x", pady=10)

        tk.Label(
            topology,
            text="NETWORK OVERVIEW",
            bg=PANEL,
            fg=FG,
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        tk.Label(
            topology,
            text="PC / CLIENT  ─────  SWITCH  ─────  ROUTER  ─────  NETWORK",
            bg=PANEL,
            fg=ACCENT,
            font=("Consolas", 12)
        ).pack(anchor="center", pady=18)

        tk.Label(
            topology,
            text="Use diagnostic evidence to identify connectivity, addressing, "
                 "routing and configuration issues.",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        # CONSOLE
        console_frame = tk.Frame(content, bg=PANEL)
        console_frame.pack(fill="both", expand=True, pady=10)

        tk.Label(
            console_frame,
            text="SYSTEM CONSOLE",
            bg=PANEL,
            fg=FG,
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w", padx=10, pady=8)

        self.console = scrolledtext.ScrolledText(
            console_frame,
            bg="#050914",
            fg="#a7f3d0",
            insertbackground=FG,
            font=("Consolas", 10),
            wrap="word",
            height=14,
            relief="flat"
        )
        self.console.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.log("NetSage AI initialized.")
        self.log("Rule-based diagnostic engine loaded.")
        self.log("Gemini API integration loaded.")
        self.log("Human review workflow available.")
        self.log("Ready for network evidence.")

    # --------------------------------------------------------
    # UI HELPERS
    # --------------------------------------------------------

    def create_button(self, parent, text, command):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=PANEL2,
            fg=FG,
            activebackground="#263449",
            activeforeground="white",
            font=("Segoe UI", 10),
            relief="flat",
            padx=10,
            pady=10,
            anchor="w"
        )

        button.pack(fill="x", padx=10, pady=4)
        return button

    def create_card(self, parent, heading, value, color):

        card = tk.Frame(parent, bg=PANEL, padx=15, pady=12)
        card.pack(side="left", fill="x", expand=True, padx=5)

        tk.Label(
            card,
            text=heading,
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w")

        tk.Label(
            card,
            text=value,
            bg=PANEL,
            fg=color,
            font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=5)

    def log(self, message):

        timestamp = datetime.now().strftime("%H:%M:%S")

        self.console.insert(
            "end",
            f"[{timestamp}] {message}\n"
        )

        self.console.see("end")

    def set_status(self, message, color=GREEN):

        self.status_var.set(message)

    # --------------------------------------------------------
    # EVIDENCE WINDOW
    # --------------------------------------------------------

    def open_evidence_window(self):

        self.create_evidence_window(use_ai=True)

    def open_local_evidence_window(self):

        self.create_evidence_window(use_ai=False)

    def create_evidence_window(self, use_ai):

        window = tk.Toplevel(self.root)
        window.title("Network Evidence")
        window.geometry("700x520")
        window.configure(bg=BG)

        heading = (
            "GEMINI AI DIAGNOSIS"
            if use_ai
            else "LOCAL RULE-BASED DIAGNOSIS"
        )

        tk.Label(
            window,
            text=heading,
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 15, "bold")
        ).pack(pady=10)

        tk.Label(
            window,
            text="Enter network evidence, command outputs, "
                 "errors or configuration details:",
            bg=BG,
            fg=FG
        ).pack(anchor="w", padx=15)

        evidence_box = scrolledtext.ScrolledText(
            window,
            bg=PANEL,
            fg=FG,
            insertbackground=FG,
            font=("Consolas", 10),
            wrap="word",
            height=16
        )
        evidence_box.pack(fill="both", expand=True, padx=15, pady=10)

        # Load previous evidence if available
        if EVIDENCE_FILE.exists():
            try:
                evidence_box.insert(
                    "1.0",
                    EVIDENCE_FILE.read_text(encoding="utf-8")
                )
            except Exception:
                pass

        buttons = tk.Frame(window, bg=BG)
        buttons.pack(fill="x", padx=15, pady=10)

        tk.Button(
            buttons,
            text="Run Diagnosis",
            command=lambda: self.start_diagnosis(
                evidence_box.get("1.0", "end").strip(),
                use_ai,
                window
            ),
            bg="#2563eb",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=15,
            pady=10
        ).pack(side="left")

        tk.Button(
            buttons,
            text="Clear",
            command=lambda: evidence_box.delete("1.0", "end"),
            bg=PANEL2,
            fg=FG,
            relief="flat",
            padx=15,
            pady=10
        ).pack(side="left", padx=10)

        tk.Button(
            buttons,
            text="Close",
            command=window.destroy,
            bg=PANEL2,
            fg=FG,
            relief="flat",
            padx=15,
            pady=10
        ).pack(side="right")

    # --------------------------------------------------------
    # DIAGNOSIS + AUTOMATIC FALLBACK
    # --------------------------------------------------------

    def start_diagnosis(self, evidence, use_ai, window=None):

        if not evidence.strip():
            messagebox.showwarning(
                "Missing Evidence",
                "Please enter network evidence first."
            )
            return

        self.current_evidence = evidence

        try:
            EVIDENCE_FILE.write_text(
                evidence,
                encoding="utf-8"
            )
        except Exception as error:
            self.log(f"Could not save evidence: {error}")

        if window:
            window.destroy()

        self.set_status("DIAGNOSIS IN PROGRESS")
        self.log("Diagnosis started.")

        if use_ai:
            self.log("Attempting Gemini AI diagnosis...")
        else:
            self.log("Using local rule engine.")

        threading.Thread(
            target=self.diagnosis_worker,
            args=(evidence, use_ai),
            daemon=True
        ).start()

    def diagnosis_worker(self, evidence, use_ai):

        diagnosis = None
        source = "Local Rule Engine"
        fallback_reason = None

        # Try Gemini first if AI mode was selected
        if use_ai:

            try:
                diagnosis = diagnose_with_ai(evidence)
                source = "Gemini AI"

                self.root.after(
                    0,
                    lambda: self.log("Gemini diagnosis successful.")
                )

            except Exception as error:

                fallback_reason = str(error)

                self.root.after(
                    0,
                    lambda msg=fallback_reason: self.log(
                        f"Gemini unavailable: {msg}"
                    )
                )

                self.root.after(
                    0,
                    lambda: self.log(
                        "Switching automatically to local rule engine..."
                    )
                )

        # Local engine if Gemini failed or local mode was selected
        if diagnosis is None:

            try:
                diagnosis = analyze_network_evidence(evidence)
                source = "Local Rule Engine"

                self.root.after(
                    0,
                    lambda: self.log(
                        "Local rule-based diagnosis completed."
                    )
                )

            except Exception as local_error:

                error_message = str(local_error)

                self.root.after(
                    0,
                    lambda msg=error_message: self.show_diagnosis_failure(msg)
                )
                return

        # Add source information
        if isinstance(diagnosis, dict):

            diagnosis["_diagnosis_source"] = source

            if fallback_reason:
                diagnosis["_fallback_reason"] = fallback_reason

        # Save diagnosis history
        try:
            self.save_diagnosis_history(
                evidence,
                diagnosis,
                source
            )
        except Exception as error:
            self.root.after(
                0,
                lambda msg=str(error): self.log(
                    f"History logging failed: {msg}"
                )
            )

        # Update UI and open human review
        self.root.after(
            0,
            lambda d=diagnosis, s=source, r=fallback_reason:
            self.finish_diagnosis(d, s, r, evidence)
        )

    def finish_diagnosis(self, diagnosis, source, fallback_reason, evidence):

        self.set_status("DIAGNOSIS COMPLETE")

        if source == "Gemini AI":
            self.mode_var.set("ENGINE: GEMINI AI")
            self.log("Diagnosis source: Gemini AI")
        else:
            self.mode_var.set("ENGINE: LOCAL")
            self.log("Diagnosis source: Local Rule Engine")

        if fallback_reason:
            self.log("Gemini quota or API failure detected.")
            self.log("Local fallback was used.")

        self.log("Opening Human Review window...")

        try:
            show_review_window(
                self.root,
                evidence,
                diagnosis
            )

        except Exception as error:

            messagebox.showerror(
                "Review Window Error",
                f"Could not open the human review window:\n{error}"
            )

    def show_diagnosis_failure(self, error_message):

        self.set_status("DIAGNOSIS FAILED", RED)
        self.log("Both diagnosis methods failed.")

        messagebox.showerror(
            "Diagnosis Failed",
            "Gemini and the local rule engine failed.\n\n"
            + error_message
        )

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    def save_diagnosis_history(self, evidence, diagnosis, source):

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        entry = (
            "\n" + "=" * 70 + "\n"
            + f"Time: {timestamp}\n"
            + f"Source: {source}\n"
            + "Evidence:\n"
            + evidence + "\n"
            + "Diagnosis:\n"
            + json.dumps(
                diagnosis,
                indent=2,
                ensure_ascii=False
            )
            + "\n"
        )

        with open(
            DIAGNOSIS_LOG,
            "a",
            encoding="utf-8"
        ) as file:
            file.write(entry)

    def view_history(self):

        window = tk.Toplevel(self.root)
        window.title("Diagnosis History")
        window.geometry("850x600")
        window.configure(bg=BG)

        tk.Label(
            window,
            text="DIAGNOSIS HISTORY",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        text_box = scrolledtext.ScrolledText(
            window,
            bg=PANEL,
            fg=FG,
            font=("Consolas", 10),
            wrap="word"
        )
        text_box.pack(fill="both", expand=True, padx=15, pady=15)

        if DIAGNOSIS_LOG.exists():

            text_box.insert(
                "1.0",
                DIAGNOSIS_LOG.read_text(encoding="utf-8")
            )

        else:
            text_box.insert("1.0", "No diagnosis history yet.")

        text_box.configure(state="disabled")

    # --------------------------------------------------------
    # DATASET
    # --------------------------------------------------------

    def load_dataset_case(self):

        if not DATASET_FILE.exists():

            messagebox.showerror(
                "Dataset Missing",
                f"Dataset not found:\n{DATASET_FILE}"
            )
            return

        try:

            with open(
                DATASET_FILE,
                "r",
                encoding="utf-8-sig"
            ) as file:

                reader = csv.DictReader(file)
                cases = list(reader)

        except Exception as error:

            messagebox.showerror(
                "Dataset Error",
                str(error)
            )
            return

        if not cases:

            messagebox.showinfo(
                "Dataset",
                "The dataset contains no cases."
            )
            return

        window = tk.Toplevel(self.root)
        window.title("Dataset Cases")
        window.geometry("750x500")
        window.configure(bg=BG)

        tk.Label(
            window,
            text="SELECT A NETWORK CASE",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        case_list = tk.Listbox(
            window,
            bg=PANEL,
            fg=FG,
            font=("Consolas", 10),
            selectbackground="#2563eb"
        )
        case_list.pack(fill="both", expand=True, padx=15, pady=10)

        for case in cases:

            case_id = case.get("case_id", case.get("ID", ""))
            title = case.get("title", case.get("problem", ""))
            case_list.insert(
                "end",
                f"{case_id} | {title}"
            )

        def load_selected():

            selection = case_list.curselection()

            if not selection:
                messagebox.showwarning(
                    "Select Case",
                    "Please select a dataset case."
                )
                return

            case = cases[selection[0]]

            evidence = (
                case.get("evidence")
                or case.get("network_evidence")
                or case.get("description")
                or case.get("problem")
                or ""
            )

            if not evidence:

                evidence = "\n".join(
                    f"{key}: {value}"
                    for key, value in case.items()
                )

            window.destroy()

            self.log(
                f"Loaded dataset case: {selection[0] + 1}"
            )

            self.create_evidence_window_with_text(evidence)

        tk.Button(
            window,
            text="Load Selected Case",
            command=load_selected,
            bg="#2563eb",
            fg="white",
            relief="flat",
            padx=15,
            pady=10
        ).pack(pady=10)

    def create_evidence_window_with_text(self, evidence):

        window = tk.Toplevel(self.root)
        window.title("Dataset Evidence")
        window.geometry("700x520")
        window.configure(bg=BG)

        tk.Label(
            window,
            text="LOADED NETWORK EVIDENCE",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        evidence_box = scrolledtext.ScrolledText(
            window,
            bg=PANEL,
            fg=FG,
            insertbackground=FG,
            font=("Consolas", 10),
            wrap="word"
        )
        evidence_box.pack(fill="both", expand=True, padx=15, pady=10)

        evidence_box.insert("1.0", evidence)

        buttons = tk.Frame(window, bg=BG)
        buttons.pack(fill="x", padx=15, pady=10)

        tk.Button(
            buttons,
            text="Gemini + Fallback Diagnosis",
            command=lambda: self.start_diagnosis(
                evidence_box.get("1.0", "end").strip(),
                True,
                window
            ),
            bg="#2563eb",
            fg="white",
            relief="flat",
            padx=10,
            pady=10
        ).pack(side="left")

        tk.Button(
            buttons,
            text="Local Diagnosis",
            command=lambda: self.start_diagnosis(
                evidence_box.get("1.0", "end").strip(),
                False,
                window
            ),
            bg=PANEL2,
            fg=FG,
            relief="flat",
            padx=10,
            pady=10
        ).pack(side="left", padx=10)

    def view_dataset(self):

        if not DATASET_FILE.exists():

            messagebox.showerror(
                "Dataset Missing",
                f"Dataset not found:\n{DATASET_FILE}"
            )
            return

        window = tk.Toplevel(self.root)
        window.title("NetSage Dataset")
        window.geometry("950x550")
        window.configure(bg=BG)

        tk.Label(
            window,
            text="NETWORK DATASET",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        frame = tk.Frame(window, bg=BG)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree = ttk.Treeview(
            frame,
            show="headings"
        )

        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )
        scrollbar.pack(side="right", fill="y")

        tree.configure(yscrollcommand=scrollbar.set)

        try:

            with open(
                DATASET_FILE,
                "r",
                encoding="utf-8-sig"
            ) as file:

                reader = csv.DictReader(file)
                rows = list(reader)
                columns = reader.fieldnames or []

            tree["columns"] = columns

            for column in columns:

                tree.heading(
                    column,
                    text=column
                )

                tree.column(
                    column,
                    width=150,
                    minwidth=100
                )

            for row in rows:

                tree.insert(
                    "",
                    "end",
                    values=[
                        row.get(column, "")
                        for column in columns
                    ]
                )

        except Exception as error:

            messagebox.showerror(
                "Dataset Error",
                str(error)
            )

    # --------------------------------------------------------
    # NETWORK UTILITIES
    # --------------------------------------------------------

    def run_ipconfig(self):

        self.log("Running IP configuration command...")

        threading.Thread(
            target=self.ipconfig_worker,
            daemon=True
        ).start()

    def ipconfig_worker(self):

        try:

            system = platform.system()

            if system == "Windows":
                command = ["ipconfig", "/all"]
            else:
                command = ["ifconfig"]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=15
            )

            output = result.stdout or result.stderr

            self.root.after(
                0,
                lambda o=output: self.show_output_window(
                    "IP Configuration",
                    o
                )
            )

            self.root.after(
                0,
                lambda: self.log("IP configuration completed.")
            )

        except Exception as error:

            error_message = str(error)

            self.root.after(
                0,
                lambda msg=error_message: messagebox.showerror(
                    "IP Configuration Error",
                    msg
                )
            )

    def open_ping_window(self):

        window = tk.Toplevel(self.root)
        window.title("Ping Test")
        window.geometry("500x250")
        window.configure(bg=BG)

        tk.Label(
            window,
            text="PING TEST",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        tk.Label(
            window,
            text="Enter an IP address or hostname:",
            bg=BG,
            fg=FG
        ).pack(pady=5)

        ip_entry = tk.Entry(
            window,
            bg=PANEL,
            fg=FG,
            insertbackground=FG,
            font=("Consolas", 12)
        )
        ip_entry.pack(fill="x", padx=20, pady=10)

        def run_ping():

            target = ip_entry.get().strip()

            if not target:

                messagebox.showwarning(
                    "Missing Target",
                    "Enter an IP address or hostname."
                )
                return

            window.destroy()

            self.log(f"Starting ping test to {target}...")

            threading.Thread(
                target=self.ping_worker,
                args=(target,),
                daemon=True
            ).start()

        tk.Button(
            window,
            text="Run Ping",
            command=run_ping,
            bg="#2563eb",
            fg="white",
            relief="flat",
            padx=15,
            pady=10
        ).pack(pady=10)

    def ping_worker(self, target):

        try:

            if platform.system() == "Windows":
                command = ["ping", "-n", "4", target]
            else:
                command = ["ping", "-c", "4", target]

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=20
            )

            output = result.stdout or result.stderr

            self.root.after(
                0,
                lambda o=output: self.show_output_window(
                    "Ping Results",
                    o
                )
            )

            self.root.after(
                0,
                lambda: self.log(
                    f"Ping test completed: {target}"
                )
            )

        except Exception as error:

            error_message = str(error)

            self.root.after(
                0,
                lambda msg=error_message: messagebox.showerror(
                    "Ping Error",
                    msg
                )
            )

    def show_output_window(self, title, output):

        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("800x500")
        window.configure(bg=BG)

        tk.Label(
            window,
            text=title.upper(),
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=10)

        text_box = scrolledtext.ScrolledText(
            window,
            bg=PANEL,
            fg=FG,
            font=("Consolas", 10),
            wrap="word"
        )
        text_box.pack(fill="both", expand=True, padx=15, pady=15)

        text_box.insert("1.0", output)
        text_box.configure(state="disabled")

    # --------------------------------------------------------
    # REVIEW STATISTICS
    # --------------------------------------------------------

    def view_review_stats(self):

        window = tk.Toplevel(self.root)
        window.title("Human Review Statistics")
        window.geometry("650x450")
        window.configure(bg=BG)

        tk.Label(
            window,
            text="HUMAN REVIEW STATISTICS",
            bg=BG,
            fg=ACCENT,
            font=("Segoe UI", 14, "bold")
        ).pack(pady=15)

        if not REVIEW_LOG.exists():

            tk.Label(
                window,
                text="No review data available yet.",
                bg=BG,
                fg=FG
            ).pack(pady=20)

            return

        try:

            with open(
                REVIEW_LOG,
                "r",
                encoding="utf-8-sig"
            ) as file:

                rows = list(csv.DictReader(file))

        except Exception as error:

            messagebox.showerror(
                "Review Log Error",
                str(error)
            )
            return

        total = len(rows)

        accepted = 0
        edited = 0
        rejected = 0

        for row in rows:

            action = (
                row.get("action")
                or row.get("review")
                or row.get("decision")
                or ""
            ).lower()

            if "accept" in action:
                accepted += 1

            elif "edit" in action:
                edited += 1

            elif "reject" in action:
                rejected += 1

        stats_frame = tk.Frame(window, bg=PANEL, padx=20, pady=20)
        stats_frame.pack(fill="x", padx=20, pady=20)

        statistics = [
            ("Total Reviews", total, ACCENT),
            ("Accepted", accepted, GREEN),
            ("Edited", edited, ORANGE),
            ("Rejected", rejected, RED)
        ]

        for label, value, color in statistics:

            row = tk.Frame(stats_frame, bg=PANEL)
            row.pack(fill="x", pady=8)

            tk.Label(
                row,
                text=label,
                bg=PANEL,
                fg=FG,
                font=("Segoe UI", 11)
            ).pack(side="left")

            tk.Label(
                row,
                text=str(value),
                bg=PANEL,
                fg=color,
                font=("Segoe UI", 11, "bold")
            ).pack(side="right")

        tk.Label(
            window,
            text="Statistics are based on the review log.",
            bg=BG,
            fg=MUTED
        ).pack(pady=10)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()
    app = NetSageApp(root)
    root.mainloop()
