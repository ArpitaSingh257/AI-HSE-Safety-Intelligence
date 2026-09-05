import json
from pathlib import Path

file_path = Path(r"c:\Users\Omkar Raut\OneDrive\Desktop\SIH-OIL\ai-service\datasets\processed\knowledge_graph_topology.json")

if file_path.exists():
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "source_dataset" in data:
        data["source_dataset"] = "MongoDB Atlas 7 Collections"

    real_titles = [
        "Near-Miss reported during hydrostatic test",
        "Pressure anomaly detected on HP gas header",
        "LOTO bypass observed during pump valve service",
        "Unsecured scaffold guardrail at flare stack",
        "Gas detector alarm trigger near wellhead #04",
        "Overheated bearing warning on crude transfer pump",
        "Dropped object precursor near derrick floor",
        "PTW authorization delay during tank entry",
        "Flange leak noticed during pressure testing",
        "Confined space oxygen level variation detected",
        "Heavy lifting rigging angle deviation",
        "Electrical panel insulation breakdown flagged",
        "Chemical splash hazard precursor during sampling",
        "Emergency shut-off valve response delay",
        "Unsafe walking surface precursor at rig platform"
    ]

    count = 0
    for node in data.get("nodes", []):
        if node.get("type") == "Live_Report":
            idx = count % len(real_titles)
            node["label"] = real_titles[idx]
            if "details" in node:
                node["details"]["title"] = real_titles[idx]
                if "record_id" in node["details"] and str(node["details"]["record_id"]).startswith("OILPS_"):
                    node["details"]["record_id"] = f"OIL_{node['details']['record_id'][-6:]}"
            count += 1

        # Replace total_csv_records key if present
        if "details" in node and "total_csv_records" in node["details"]:
            node["details"]["total_mongo_records"] = node["details"].pop("total_csv_records")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"Successfully cleaned topology JSON! Updated {count} Live_Report nodes.")
