import json
import subprocess
from datetime import datetime
 
with open("reports/plan.json", "r") as f:
    plan = json.load(f)

changes = len(plan.get("resource_changes", []))

status = "NO_DRIFT" if changes == 0 else "DRIFT"

drift_report = {
    "status": status,
    "changes": changes,
    "time": datetime.now().isoformat()
}

with open("reports/drift.json", "w") as f:
    json.dump(drift_report, f, indent=2)

print(f"Status: {status}")
print(f"Changes: {changes}")
print("Report generated: reports/drift.json")