
import pandas as pd

# Load the NetSage AI dataset
data = pd.read_csv("data/network_dataset.csv")


def diagnose_network(symptom):

    symptom = symptom.lower()

    # Rule 1: IP addressing problem
    if "different subnet" in symptom or "ip address" in symptom:
        case = data[data["case_id"] == "NS001"]

    # Rule 2: Default gateway problem
    elif "gateway" in symptom or "remote network" in symptom:
        case = data[data["case_id"] == "NS002"]

    # Rule 3: VLAN problem
    elif "vlan" in symptom or "same vlan" in symptom:
        case = data[data["case_id"] == "NS003"]

    else:
        print("\nNetSage AI: No matching rule found.")
        print("More troubleshooting evidence is needed.")
        return

    if case.empty:
        print("Diagnosis information not found in dataset.")
        return

    # Retrieve matching case
    result = case.iloc[0]

    # Display diagnosis
    print("\n===== NETSAGE AI DIAGNOSIS =====")
    print("Symptom:", symptom)
    print("Likely Root Cause:", result["root_cause"])
    print("OSI Layer:", result["osi_layer"])
    print("Network Concept:", result["concept_tag"])
    print("Severity:", result["severity"])
    print("Evidence:", result["evidence"])
    print("Recommended Solution:", result["solution"])


# User input
user_symptom = input("Describe your network problem: ")

# Run diagnosis
diagnose_network(user_symptom)
