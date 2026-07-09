import json

with open("reports/plan.json", "r") as f:
    plan = json.load(f)


def is_trivial_change(before, after):
    return (
        (before is None and after in ({}, []))
        or (before == "" and after not in ("", None))
    )


def find_changes(before, after, path=""):
    changes = []

    if isinstance(before, dict) and isinstance(after, dict):
        for key in set(before) | set(after):
            new_path = f"{path}.{key}" if path else key
            changes.extend(
                find_changes(before.get(key), after.get(key), new_path)
            )

    elif before != after and not is_trivial_change(before, after):
        changes.append({
            "field": path,
            "from": before,
            "to": after
        })

    return changes


report = []

for drift in plan.get("resource_drift", []):
    changes = find_changes(
        drift.get("change", {}).get("before", {}),
        drift.get("change", {}).get("after", {})
    )

    if changes:
        report.append({
            "resource": drift.get("address"),
            "changes": changes
        })

with open("reports/drift_report.json", "w") as f:
    json.dump(report, f, indent=4)