import sys
import time

from config import configure_logging, parse_args
from exporters import ExportService
from pipeline import ItemPipeline


def _report(message=""):
    """Write a human-facing line to stderr, keeping stdout free for --stdout content."""
    print(message, file=sys.stderr)


def _print_header(config):
    _report(f"Magic Rampage Item Parser  (format: {config.output_type})")
    if config.item_type != "enemy":
        note = "" if config.items_folder.exists() else "   (not found)"
        _report(f"  items   : {config.items_folder}{note}")
    if config.item_type in ("enemy", "all"):
        missing = [d for d in config.enemy_directories if not d.exists()]
        note = f"   ({len(missing)} of {len(config.enemy_directories)} not found)" if missing else ""
        dirs = "; ".join(str(d) for d in config.enemy_directories)
        _report(f"  enemies : {dirs}{note}")
    _report(f"  output  : {'stdout' if config.to_stdout else str(config.output_dir) + '/'}")
    _report()


def _print_summary(results, config, elapsed):
    for result in results:
        target = "stdout" if result.path is None else result.path
        _report(f"  {result.label:<9}{result.count:>4}  -> {target}")
    total = sum(result.count for result in results)
    if config.to_stdout:
        _report(f"\nDone: {total} records across {len(results)} section(s)  ({elapsed:.1f}s)")
    else:
        files = sum(1 for result in results if result.path is not None)
        _report(f"\nDone: {total} records -> {files} file(s) in {config.output_dir}/  ({elapsed:.1f}s)")
        _report("Tip: re-run with --stdout to preview without writing.")


def main(argv=None):
    # Keep emoji/non-ASCII names from crashing on a redirected non-UTF-8 stream.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    config = parse_args(argv)
    configure_logging(config.log_level)
    exporter = ExportService(config.output_dir, to_stdout=config.to_stdout)

    started = time.perf_counter()
    _print_header(config)

    results = []
    if config.item_type == "class":
        results.append(exporter.export_classes(config.items_folder, config.output_type))
    elif config.item_type == "enemy":
        results.append(exporter.export_enemies(config.enemy_directories, config.output_type))
    else:
        items_by_type = ItemPipeline(config.items_folder, config.online_items_url).load_items()
        if config.item_type == "all":
            results.extend(exporter.export_all_items(items_by_type, config.output_type))
            results.append(exporter.export_classes(config.items_folder, config.output_type))
            results.append(exporter.export_enemies(config.enemy_directories, config.output_type))
        else:
            results.append(exporter.export_items(items_by_type, config.item_type, config.output_type))

    _print_summary(results, config, time.perf_counter() - started)


if __name__ == "__main__":
    main()
