
import pandas as pd
from datetime import datetime
from diagnostic_engine import analyze_network_evidence

# Load network dataset
data = pd.read_csv("data/network_dataset.csv")


# Display diagnosis and save log
def display_diagnosis(case_id, confidence=None):
    result = data[data["case_id"] == case_id]

    if result.empty:
        print("Case not found.")
        return

    case = result.iloc[0]

    print("\n===== NETSAGE AI DIAGNOSIS =====")
    print("Case ID:", case["case_id"])
    print("Symptom:", case["symptom"])
    print("Root Cause:", case["root_cause"])
    print("OSI Layer:", case["osi_layer"])
    print("Concept:", case["concept_tag"])
    print("Severity:", case["severity"])
    print("Evidence:", case["evidence"])
    print("Solution:", case["solution"])

    if confidence is not None:
        print("Rule-match confidence:", confidence, "%")

    # Save diagnosis to log file
    with open("data/diagnosis_log.txt", "a") as log_file:
        log_file.write("\n" + "=" * 40 + "\n")
        log_file.write(
            "Date: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n"
        )
        log_file.write("Case ID: " + str(case["case_id"]) + "\n")
        log_file.write("Root Cause: " + str(case["root_cause"]) + "\n")
        log_file.write("OSI Layer: " + str(case["osi_layer"]) + "\n")
        log_file.write("Severity: " + str(case["severity"]) + "\n")
        log_file.write("Solution: " + str(case["solution"]) + "\n")

        if confidence is not None:
            log_file.write("Rule-match confidence: " + str(confidence) + "%\n")

    print("\nDiagnosis saved to diagnosis_log.txt")


# Analyze evidence file
def analyze_evidence():
    with open("data/evidence.txt", "r") as file:
        evidence = file.read()

    case_id, confidence, signals = analyze_network_evidence(evidence)

    print("\n===== EVIDENCE ANALYSIS =====")

    print("\nEvidence signals:")
    for signal in signals:
        print("-", signal)

    if case_id is not None:
        print("\nPossible problem detected.")
        display_diagnosis(case_id, confidence)

    else:
        print("\nNo known network issue detected.")
        print("More evidence is required.")


# View diagnosis history
def view_diagnosis_history():
    try:
        with open("data/diagnosis_log.txt", "r") as log_file:
            history = log_file.read()

        if history.strip():
            print("\n===== DIAGNOSIS HISTORY =====")
            print(history)
        else:
            print("\nDiagnosis history is empty.")

    except FileNotFoundError:
        print("\nNo diagnosis history found yet.")


# Main menu
while True:
    print("\n===== NETSAGE AI =====")
    print("1. IP Addressing Problem")
    print("2. Default Gateway Problem")
    print("3. VLAN Problem")
    print("4. View All Cases")
    print("5. Exit")
    print("6. Analyze Evidence File")
    print("7. View Diagnosis History")

    choice = input("Enter your choice: ").strip()

    if choice == "1":
        display_diagnosis("NS001")

    elif choice == "2":
        display_diagnosis("NS002")

    elif choice == "3":
        display_diagnosis("NS003")

    elif choice == "4":
        print(data[["case_id", "symptom", "root_cause"]])

    elif choice == "5":
        print("NetSage AI shutting down.")
        break

    elif choice == "6":
        analyze_evidence()

    elif choice == "7":
        view_diagnosis_history()

    else:
        print("Invalid choice. Please try again.")
