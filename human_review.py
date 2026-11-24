import csv
import json
from datetime import datetime
from pathlib import Path


# =========================================
# NETSAGE AI - HUMAN REVIEW SYSTEM
# =========================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REVIEW_FILE = DATA_DIR / "review_log.csv"

DATA_DIR.mkdir(exist_ok=True)

CSV_FIELDS = [
    "timestamp",
    "evidence",
    "ai_diagnosis",
    "decision",
    "human_diagnosis",
    "reviewer_notes",
]


def save_review(
    evidence,
    ai_diagnosis,
    decision,
    human_diagnosis=None,
    reviewer_notes=""
):
    """Save a human review of an AI network diagnosis."""

    decision = decision.strip().capitalize()

    if decision not in ["Accept", "Edit", "Reject"]:
        raise ValueError("Decision must be Accept, Edit, or Reject.")

    if decision == "Edit" and not human_diagnosis:
        raise ValueError("An Edit needs the corrected diagnosis.")

    if human_diagnosis is None:
        human_diagnosis = {} if decision == "Reject" else ai_diagnosis

    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "evidence": str(evidence),
        "ai_diagnosis": json.dumps(ai_diagnosis),
        "decision": decision,
        "human_diagnosis": json.dumps(human_diagnosis),
        "reviewer_notes": str(reviewer_notes),
    }

    file_exists = REVIEW_FILE.exists()

    with open(
        REVIEW_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=CSV_FIELDS
        )

        if not file_exists or REVIEW_FILE.stat().st_size == 0:
            writer.writeheader()

        writer.writerow(record)

    print("\nHuman review saved successfully.")
    print(f"Review file: {REVIEW_FILE}")


def accept_diagnosis(evidence, ai_diagnosis, notes=""):
    """Accept the original AI diagnosis."""

    save_review(
        evidence=evidence,
        ai_diagnosis=ai_diagnosis,
        decision="Accept",
        human_diagnosis=ai_diagnosis,
        reviewer_notes=notes
    )


def edit_diagnosis(
    evidence,
    ai_diagnosis,
    corrected_diagnosis,
    notes=""
):
    """Save a human-corrected diagnosis."""

    save_review(
        evidence=evidence,
        ai_diagnosis=ai_diagnosis,
        decision="Edit",
        human_diagnosis=corrected_diagnosis,
        reviewer_notes=notes
    )


def reject_diagnosis(evidence, ai_diagnosis, notes=""):
    """Reject the AI diagnosis."""

    save_review(
        evidence=evidence,
        ai_diagnosis=ai_diagnosis,
        decision="Reject",
        human_diagnosis={},
        reviewer_notes=notes
    )


def get_review_statistics():

    if not REVIEW_FILE.exists():
        return {
            "total": 0,
            "accepted": 0,
            "edited": 0,
            "rejected": 0,
        }

    with open(
        REVIEW_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        rows = list(csv.DictReader(file))

    return {
        "total": len(rows),
        "accepted": sum(
            row["decision"] == "Accept" for row in rows
        ),
        "edited": sum(
            row["decision"] == "Edit" for row in rows
        ),
        "rejected": sum(
            row["decision"] == "Reject" for row in rows
        ),
    }


# =========================================
# TEST
# =========================================

if __name__ == "__main__":

    # Use a separate file so test runs don't pollute your real review log.
    REVIEW_FILE = DATA_DIR / "review_log_test.csv"

    sample_evidence = (
        "PC gateway is configured incorrectly. "
        "Configured gateway 192.168.1.254. "
        "Expected gateway 192.168.1.1."
    )

    sample_diagnosis = {
        "case_id": "NS002",
        "problem_summary": "Incorrect default gateway",
        "probable_root_cause": "Incorrect gateway configuration",
        "confidence": 95,
        "recommended_fix": "Change gateway to 192.168.1.1",
        "human_approval_required": True,
    }

    accept_diagnosis(
        evidence=sample_evidence,
        ai_diagnosis=sample_diagnosis,
        notes="Test review accepted."
    )

    print("\nReview statistics:")
    print(json.dumps(get_review_statistics(), indent=4))