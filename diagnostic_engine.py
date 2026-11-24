
import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "data" / "network_dataset.csv"


# --------------------------------------------------
# DIAGNOSTIC RULES
# --------------------------------------------------

DIAGNOSTIC_RULES = [
    {
        "case_id": "NS004",
        "patterns": ["169.254.", "apipa"],
        "root_cause": "DHCP Failure",
        "severity": "HIGH",
        "recommended_fix": (
            "Check DHCP server availability, DHCP scope, "
            "and client DHCP configuration."
        ),
        "confidence": 0.95,
        "signal": "DHCP WARNING: APIPA address detected. "
                  "The host may not have received a DHCP lease."
    },
    {
        "case_id": "NS017",
        "patterns": [
            "duplicate ip", "ip conflict",
            "address conflict", "duplicate address"
        ],
        "root_cause": "Duplicate IP Address",
        "severity": "HIGH",
        "recommended_fix": (
            "Identify the conflicting devices and assign "
            "unique IP addresses."
        ),
        "confidence": 0.95,
        "signal": "IP WARNING: Possible duplicate IP address detected."
    },
    {
        "case_id": "NS018",
        "patterns": [
            "incorrect subnet mask", "wrong subnet mask",
            "subnet mask mismatch", "mask mismatch"
        ],
        "root_cause": "Incorrect Subnet Mask",
        "severity": "MEDIUM",
        "recommended_fix": (
            "Verify and correct the subnet mask on the affected device."
        ),
        "confidence": 0.95,
        "signal": "IP WARNING: Possible subnet mask mismatch."
    },
    {
        "case_id": "NS002",
        "patterns": [
            "wrong gateway", "incorrect gateway",
            "gateway mismatch", "invalid gateway"
        ],
        "root_cause": "Incorrect Default Gateway",
        "severity": "HIGH",
        "recommended_fix": (
            "Verify the default gateway and correct the "
            "gateway configuration."
        ),
        "confidence": 0.95,
        "signal": "GATEWAY WARNING: Incorrect gateway detected."
    },
    {
        "case_id": "NS011",
        "patterns": [
            "administratively down", "interface down",
            "interface is down", "link down"
        ],
        "root_cause": "Network Interface Down",
        "severity": "HIGH",
        "recommended_fix": (
            "Check physical connectivity and interface status. "
            "Enable the interface if administratively disabled."
        ),
        "confidence": 0.90,
        "signal": "INTERFACE WARNING: Network interface may be down."
    },
    {
        "case_id": "NS003",
        "patterns": [
            "wrong vlan", "incorrect vlan",
            "vlan mismatch", "assigned to wrong vlan"
        ],
        "root_cause": "Incorrect VLAN Assignment",
        "severity": "HIGH",
        "recommended_fix": (
            "Verify the switch port VLAN assignment and "
            "configure the correct VLAN."
        ),
        "confidence": 0.95,
        "signal": "VLAN WARNING: Possible VLAN assignment problem."
    },
    {
        "case_id": "NS015",
        "patterns": [
            "trunk mismatch", "trunk not configured",
            "vlan missing from trunk", "allowed vlan"
        ],
        "root_cause": "Trunk Configuration Problem",
        "severity": "HIGH",
        "recommended_fix": (
            "Verify trunk configuration and ensure required "
            "VLANs are included in the allowed VLAN list."
        ),
        "confidence": 0.90,
        "signal": "TRUNK WARNING: Check trunk configuration and allowed VLANs."
    },
    {
        "case_id": "NS006",
        "patterns": [
            "dns failure", "dns problem",
            "cannot resolve", "name resolution failure",
            "nslookup failed"
        ],
        "root_cause": "DNS Resolution Failure",
        "severity": "MEDIUM",
        "recommended_fix": (
            "Verify DNS server configuration, connectivity, "
            "and DNS records."
        ),
        "confidence": 0.90,
        "signal": "DNS WARNING: Name resolution may be failing."
    },
    {
        "case_id": "NS008",
        "patterns": [
            "missing route", "no route",
            "route missing", "destination network unreachable"
        ],
        "root_cause": "Missing Routing Entry",
        "severity": "HIGH",
        "recommended_fix": (
            "Inspect the routing table and configure the "
            "missing route or correct next hop."
        ),
        "confidence": 0.90,
        "signal": "ROUTING WARNING: Possible routing problem."
    },
    {
        "case_id": "NS020",
        "patterns": [
            "acl blocked", "access list denied",
            "access-list deny", "blocked by acl"
        ],
        "root_cause": "Access Control List Blocking Traffic",
        "severity": "HIGH",
        "recommended_fix": (
            "Inspect ACL rules and verify whether traffic "
            "is being denied by an incorrect access rule."
        ),
        "confidence": 0.90,
        "signal": "ACL WARNING: Traffic may be blocked by an ACL."
    },
    {
        "case_id": "NS022",
        "patterns": [
            "nat failure", "nat not working",
            "nat missing", "translation failure"
        ],
        "root_cause": "NAT Configuration Failure",
        "severity": "HIGH",
        "recommended_fix": (
            "Verify NAT rules, interface roles, and "
            "translation entries."
        ),
        "confidence": 0.90,
        "signal": "NAT WARNING: Check NAT configuration and translations."
    }
]


# --------------------------------------------------
# DATASET MATCHING
# --------------------------------------------------

STOPWORDS = {
    "this", "that", "with", "from", "have",
    "been", "were", "when", "where", "which",
    "there", "their", "network", "device",
    "problem", "issue", "check", "using"
}


def extract_keywords(value):
    words = re.findall(r"[a-z0-9]+", str(value).lower())

    return {
        word for word in words
        if len(word) > 2 and word not in STOPWORDS
    }


def match_dataset(text):
    """
    Match evidence against dataset symptoms and evidence.

    Uses keyword overlap and Jaccard similarity instead
    of matching only two common symptom words.
    """

    if not DATASET_PATH.exists():
        return None

    try:
        dataset = pd.read_csv(DATASET_PATH)

        if not {"case_id", "symptom"}.issubset(dataset.columns):
            return None

        input_words = extract_keywords(text)

        if not input_words:
            return None

        best_match = None
        best_score = 0

        for _, row in dataset.iterrows():

            symptom_words = extract_keywords(
                row.get("symptom", "")
            )

            evidence_words = extract_keywords(
                row.get("evidence", "")
            )

            case_words = symptom_words | evidence_words

            if not case_words:
                continue

            overlap = input_words & case_words

            if len(overlap) < 2:
                continue

            precision = len(overlap) / len(input_words)
            recall = len(overlap) / len(case_words)

            if precision + recall == 0:
                continue

            score = (
                2 * precision * recall
            ) / (precision + recall)

            if score > best_score:
                best_score = score

                best_match = {
                    "case_id": str(row["case_id"]),
                    "root_cause": str(row["symptom"]),
                    "confidence": min(score * 0.70, 0.70),
                    "severity": str(
                        row.get("severity", "MEDIUM")
                    ),
                    "recommended_fix": str(
                        row.get(
                            "recommended_fix",
                            "Collect additional evidence and "
                            "verify the suspected network fault."
                        )
                    )
                }

        # Reject weak or ambiguous matches.
        if best_score < 0.35:
            return None

        return best_match

    except Exception:
        return None


# --------------------------------------------------
# MAIN DIAGNOSTIC ENGINE
# --------------------------------------------------

def analyze_network_evidence(evidence):

    text = str(evidence).lower()

    signals = []
    detected_cases = []

    # --------------------------------------------------
    # RULE-BASED DIAGNOSIS
    # --------------------------------------------------

    for rule in DIAGNOSTIC_RULES:

        if any(pattern in text for pattern in rule["patterns"]):

            detected_cases.append(rule)

            signals.append(rule["signal"])

    # --------------------------------------------------
    # PING FAILURE
    # --------------------------------------------------

    ping_failure = any(term in text for term in [
        "request timed out",
        "100% loss",
        "destination host unreachable",
        "ping failed"
    ])

    if ping_failure:

        signals.append(
            "CONNECTIVITY WARNING: Ping failure detected. "
            "The destination may be unreachable. "
            "Further investigation is required to identify the cause."
        )

    # --------------------------------------------------
    # PING SUCCESS
    # --------------------------------------------------

    if any(term in text for term in [
        "0% loss",
        "ping completed successfully",
        "received = 4, lost = 0"
    ]):

        signals.append(
            "CONNECTIVITY INFO: Successful ping connectivity "
            "to the tested destination."
        )

    # --------------------------------------------------
    # IP CONFIGURATION
    # --------------------------------------------------

    if "ipconfig" in text:

        signals.append(
            "IP CONFIGURATION INFO: Review IP address, "
            "subnet mask, gateway and DNS values."
        )

    # --------------------------------------------------
    # ROUTING TABLE
    # --------------------------------------------------

    if "show ip route" in text:

        signals.append(
            "ROUTING INFO: Review destination routes, "
            "next hops and default route."
        )

    # --------------------------------------------------
    # SELECT RULE-BASED DIAGNOSIS
    # --------------------------------------------------

    if detected_cases:

        detected_cases.sort(
            key=lambda item: item["confidence"],
            reverse=True
        )

        best = detected_cases[0]

        result = {
            "case_id": best["case_id"],
            "root_cause": best["root_cause"],
            "severity": best["severity"],
            "confidence": best["confidence"],
            "recommended_fix": best["recommended_fix"],
            "signals": signals,
            "diagnosis_source": "RULE_BASED"
        }

    else:

        # --------------------------------------------------
        # DATASET FALLBACK
        # --------------------------------------------------

        dataset_match = match_dataset(text)

        if dataset_match:

            result = {
                **dataset_match,
                "signals": signals,
                "diagnosis_source": "DATASET_MATCH"
            }

        else:

            # --------------------------------------------------
            # UNKNOWN DIAGNOSIS
            # --------------------------------------------------

            result = {
                "case_id": "UNKNOWN",
                "root_cause": (
                    "Insufficient evidence to identify "
                    "a specific network fault."
                ),
                "severity": "UNKNOWN",
                "confidence": 0.30,
                "recommended_fix": (
                    "Collect additional diagnostic evidence. "
                    "Check IP configuration, gateway, DNS, "
                    "interface status and routing."
                ),
                "signals": signals,
                "diagnosis_source": "INSUFFICIENT_EVIDENCE"
            }

    # --------------------------------------------------
    # FINAL SIGNAL
    # --------------------------------------------------

    if not result["signals"]:

        result["signals"].append(
            "No specific diagnostic rule matched. "
            "Collect additional network evidence."
        )

    result["signals"].append(
        "Recommended next step: verify the diagnosis "
        "with additional evidence before applying changes."
    )

    return result
