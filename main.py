from config import configure_logging, parse_args
from exporters import ExportService
from pipeline import ItemPipeline


def main(argv=None):
    config = parse_args(argv)
    configure_logging(config.log_level)
    exporter = ExportService(config.output_dir)

    if config.item_type == "class":
        exporter.export_classes(config.items_folder, config.output_type)
        return

    if config.item_type == "enemy":
        exporter.export_enemies(config.enemy_directories, config.output_type)
        return

    items_by_type = ItemPipeline(config.items_folder, config.online_items_url).load_items()

    if config.item_type == "all":
        exporter.export_all_items(items_by_type, config.output_type)
        exporter.export_classes(config.items_folder, config.output_type)
        return

    exporter.export_items(items_by_type, config.item_type, config.output_type)


if __name__ == "__main__":
    main()
