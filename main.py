import logger
from loader import Loader


def main():
    logger.configure('INFO', 'WARNING')
    with Loader() as loader:
        loader.store_web_page_content()
        loader.export_table_data()


if __name__ == '__main__':
    main()
