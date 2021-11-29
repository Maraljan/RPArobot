from loader import Loader


def main():
    with Loader() as loader:
        loader.store_web_page_content()
        loader.export_table_data()
        loader.extract_data_from_pdf()


if __name__ == '__main__':
    main()
