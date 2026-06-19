import threading
import webbrowser
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from config import (
    DEFAULT_BASELINE,
    DEFAULT_ENEMY_DIRECTORIES,
    DEFAULT_ITEMS_FOLDER,
    DEFAULT_ONLINE_ITEMS_URL,
    DEFAULT_OUTPUT_DIR,
)
from diff_checker import DiffChecker
from exporters import ExportService
from pipeline import ItemPipeline

app = Flask(__name__)
OUTPUT_DIR = Path(DEFAULT_OUTPUT_DIR)


def _exporter():
    return ExportService(OUTPUT_DIR)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/run", methods=["POST"])
def api_run():
    body = request.get_json(force=True)
    action = body.get("action", "")
    output_type = body.get("output_type", "normal")
    items_folder = body.get("items_folder") or DEFAULT_ITEMS_FOLDER
    online_url = body.get("online_url") or DEFAULT_ONLINE_ITEMS_URL
    baseline = body.get("baseline") or DEFAULT_BASELINE
    raw_dirs = body.get("enemy_dirs") or DEFAULT_ENEMY_DIRECTORIES
    enemy_dirs = [Path(p) for p in (raw_dirs if isinstance(raw_dirs, list) else [raw_dirs])]

    try:
        if action == "diff":
            return _run_diff(items_folder, online_url)
        if action in ("armor", "ring", "sword", "hammer", "spear", "staff", "dagger", "axe"):
            return _run_single_type(action, output_type, items_folder, online_url)
        if action == "all":
            return _run_all(output_type, items_folder, online_url)
        if action == "class":
            return _run_classes(output_type, items_folder)
        if action == "enemy":
            return _run_enemies(output_type, enemy_dirs)
        return jsonify({"error": f"Unknown action: {action}"}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/download/<path:filename>")
def download(filename):
    return send_from_directory(OUTPUT_DIR.resolve(), filename, as_attachment=True)


def _run_diff(items_folder, online_url):
    checker = DiffChecker(items_folder, online_url)
    new_items, removed_items, changes, local = checker.run()

    report = DiffChecker.format_report(new_items, removed_items, changes, local)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "diff_report.txt").write_text(report, encoding="utf-8")

    serialized_changes = {
        name: {field: [online_val, local_val] for field, (online_val, local_val) in diffs.items()}
        for name, diffs in changes.items()
    }

    return jsonify({
        "type": "diff",
        "new_items": [
            {
                "name": n,
                "secondary_type": local.get(n, {}).get("secondaryType")
                    or local.get(n, {}).get("type", "?"),
            }
            for n in new_items
        ],
        "removed_items": removed_items,
        "changes": serialized_changes,
        "filename": "diff_report.txt",
    })


def _run_single_type(item_type, output_type, items_folder, online_url):
    items_by_type = ItemPipeline(items_folder, online_url).load_items()
    out_path = _exporter().export_items(items_by_type, item_type, output_type)
    return jsonify({
        "type": "parse",
        "item_type": item_type,
        "content": out_path.read_text(encoding="utf-8"),
        "filename": out_path.name,
    })


def _run_all(output_type, items_folder, online_url):
    items_by_type = ItemPipeline(items_folder, online_url).load_items()
    exporter = _exporter()
    paths = exporter.export_all_items(items_by_type, output_type)

    try:
        class_path = exporter.export_classes(items_folder, output_type)
        if class_path:
            paths.append(class_path)
    except Exception:
        pass

    files = [
        {"filename": p.name, "item_type": p.stem.replace("_code", "")}
        for p in paths if p
    ]
    return jsonify({"type": "all", "files": files})


def _run_classes(output_type, items_folder):
    out_path = _exporter().export_classes(items_folder, output_type)
    return jsonify({
        "type": "parse",
        "item_type": "class",
        "content": out_path.read_text(encoding="utf-8"),
        "filename": out_path.name,
    })


def _run_enemies(output_type, enemy_dirs):
    out_path = _exporter().export_enemies(enemy_dirs, output_type)
    return jsonify({
        "type": "parse",
        "item_type": "enemy",
        "content": out_path.read_text(encoding="utf-8"),
        "filename": out_path.name,
    })


if __name__ == "__main__":
    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(debug=False, host="127.0.0.1", port=5000)
