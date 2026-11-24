
import pandas as pd
from pathlib import Path

# Load the dataset
data = pd.read_csv("data/network_dataset.csv")

# Load evidence
evidence_path = Path("data/evidence.txt")

if not evidence_path.exists():
    print("Evidence file not found!")
    exit()

evidence = evidence_path.read_text(encoding="utf-8").lower()

print("===== NETSAGE AI DIAGNOSTIC SYSTEM =====")

# Detect possible fault patterns
detected_case_id = None

# Rule 1: Gateway evidence
if "192.168.1.245" in evidence:
    detected_case_id = "NS002"

# Rule 2: VLAN evidence
elif "vlan mismatch" in evidence or "wrong vlan" in evidence:
    detected_case_id = "NS003"

# Rule 3: IP addressing evidence
elif "different subnet" in evidence:
    detected_case_id = "NS001"


# Retrieve diagnosis from dataset
if detected_case_id:

    result = data[data["case_id"] == detected_case_id]

    if not result.empty:
        case = result.iloc[0]

        print("\n===== POSSIBLE DIAGNOSIS =====")
        print("Case ID:", case["case_id"])
        print("Root Cause:", case["root_cause"])
        print("OSI Layer:", case["osi_layer"])
        print("Concept:", case["concept_tag"])
        print("Severity:", case["severity"])
        print("Evidence:", case["evidence"])
        print("Recommended Solution:", case["solution"])

    else:
        print("Matching case was not found in dataset.")

else:
    print("\nNo known fault pattern detected.")
    print("More network evidence is required.")

print("\n===== ANALYSIS COMPLETE =====")

