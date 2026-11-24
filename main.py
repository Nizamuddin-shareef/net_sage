
import pandas as pd

# Load dataset
data = pd.read_csv("data/network_dataset.csv")

print("===== NETSAGE AI: NETWORK FAULT ANALYSIS =====")

# 1. Count faults by OSI layer
print("\n===== FAULTS BY OSI LAYER =====")
print(data["osi_layer"].value_counts())

# 2. Count faults by network concept
print("\n===== FAULTS BY NETWORK CONCEPT =====")
print(data["concept_tag"].value_counts())

# 3. Count faults by severity
print("\n===== FAULTS BY SEVERITY =====")
print(data["severity"].value_counts())

# 4. Count total cases
print("\n===== TOTAL CASES =====")
print("Total cases:", len(data))

# 5. Count unique root causes
print("\n===== UNIQUE ROOT CAUSES =====")
print("Unique root causes:", data["root_cause"].nunique())

# 6. Show all root causes
print("\n===== ROOT CAUSE LIST =====")
for cause in data["root_cause"].unique():
    print("-", cause)

# 7. Analyze cases by OSI layer and severity
print("\n===== OSI LAYER vs SEVERITY =====")
print(pd.crosstab(data["osi_layer"], data["severity"]))
