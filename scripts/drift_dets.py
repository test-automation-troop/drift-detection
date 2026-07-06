import json

with open("reports/plan.json", "r") as f:
    plan = json.load(f)

for resource in plan.get("resource_changes", []):

    before = resource["change"].get("before", {})
    after = resource["change"].get("after", {})

    print(f"\nResource: {resource['address']}")
    print("-" * 50)

    for key in before:
        if key in after and before[key] != after[key]:
            print(f"{key}")
            print(f"  Before: {before[key]}")
            print(f"  After : {after[key]}")
            print()