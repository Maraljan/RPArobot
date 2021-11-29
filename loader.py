import datetime
import time
import os

from pathlib import Path
from collections import defaultdict

from RPA.PDF import PDF
from RPA.Excel.Files import Files
from RPA.FileSystem import FileSystem
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

from tqdm import tqdm

from locators import ExcelTable, HomePageLocators, IndividualInvestmentsLocators, BusinessCaseLocators
from utils import index2col_name, wait_for_condition, get_number_entries


class Loader:
    URL = "https://itdashboard.gov/"
    OUTPUT_DIR_NAME = 'output'

    def __init__(self):
        self._file_system = FileSystem()
        self._excel = Files()
        self._browser = Selenium()
        self._pdf = PDF()

        self._file_system.create_directory(path=self.OUTPUT_DIR_NAME, parents=True, exist_ok=True)
        self._output_dir = self._file_system.absolute_path(self.OUTPUT_DIR_NAME)
        self._excel_file_path = self._file_system.join_path(self._output_dir, 'agencies.xlsx')
        self._browser.set_download_directory(self._output_dir)

        self._browser.open_available_browser(self.URL)

        # Open excel file if exists else create excel file.
        if self._file_system.does_file_exist(self._excel_file_path):
            self._workbook = self._excel.open_workbook(self._excel_file_path)
        else:
            self._workbook = self._excel.create_workbook(self._excel_file_path, fmt='xlsx')
            self._workbook.create_worksheet(ExcelTable.agency)
            self._workbook.create_worksheet(ExcelTable.table_data)

    def store_web_page_content(self):
        # Click the main button "Dive in".
        self._browser.wait_until_page_contains_element(
            HomePageLocators.dive_in_btn, datetime.timedelta(seconds=3),
        )
        self._browser.click_element(HomePageLocators.dive_in_btn)
        time.sleep(3)

        # Finds all agencies name and all spending amounts selectors.
        agency_names = self._browser.find_elements(HomePageLocators.agency_names)
        spending_amounts = self._browser.find_elements(HomePageLocators.spending_amount)

        # Export to excel two columns with agencies name and all spending amounts.
        for idx, (name_el, amount_el) in enumerate(zip(agency_names, spending_amounts), 1):
            self._workbook.set_cell_value(idx, 'A', self._browser.get_text(name_el), ExcelTable.agency)
            self._workbook.set_cell_value(idx, 'B', self._browser.get_text(amount_el), ExcelTable.agency)

    def export_table_data(self):
        self._browser.wait_until_page_contains_element(HomePageLocators.small_view_btn)

        # Choose agency name from os ev
        self.open_agency(os.getenv('AGENCY_NAME', 'Department of Commerce'))
        self._browser.wait_until_page_contains_element(
            IndividualInvestmentsLocators.data_table,
            datetime.timedelta(seconds=10)
        )

        # From select form choosing 'all' option to get all data in one page.
        self._browser.click_element(IndividualInvestmentsLocators.select_form)
        self._browser.click_element(IndividualInvestmentsLocators.choose_all_option)
        count_of_row = get_number_entries(self._browser.get_text(IndividualInvestmentsLocators.data_table_info))

        # Waiting until if number of entries equal with table rows.
        wait_for_condition(
            lambda: self._browser.get_element_count(IndividualInvestmentsLocators.table_rows) == count_of_row,
            timeout=datetime.timedelta(seconds=10),
        )

        headers = IndividualInvestmentsLocators.table_headers

        # Export to excel headers from table
        column_idx = 0
        for header in self._browser.find_elements(headers):
            self._workbook.set_cell_value(1, index2col_name(column_idx),
                                          self._browser.get_text(header), ExcelTable.table_data)
            column_idx += 1
        # Add new two columns for data from pdf
        self._workbook.set_cell_value(1, index2col_name(column_idx), 'Investment Title PDF', ExcelTable.table_data)
        self._workbook.set_cell_value(1, index2col_name(column_idx + 1), 'UII PDF', ExcelTable.table_data)

        # Export to excel all data from table.
        hrefs = []
        rows = self._browser.find_elements(IndividualInvestmentsLocators.table_rows)
        for row_idx, row_el in tqdm(
                iterable=enumerate(rows, 2),
                desc='Exporting data to excel',
                unit='row',
                total=len(rows),
        ):  # type: int, WebElement
            for col_idx, col in enumerate(row_el.find_elements_by_css_selector('td')):
                self._workbook.set_cell_value(row_idx, index2col_name(col_idx), col.text, ExcelTable.table_data)
                # Store all links in hrefs.
                if col_idx == 0:
                    try:
                        link = col.find_element_by_tag_name('a')
                        hrefs.append(link.get_attribute('href'))
                    except NoSuchElementException:
                        pass
        self.open_link_download_pdf(hrefs)

    def open_link_download_pdf(self, hrefs: list):
        """
        Download pdf files by links.
        """
        for link in tqdm(hrefs, total=len(hrefs), desc='Downloading pdf'):
            self._browser.driver.get(link)
            try:
                self._browser.wait_until_page_contains_element(
                    BusinessCaseLocators.download_pdf,
                    timeout=datetime.timedelta(seconds=10)
                )
                self._browser.click_element(BusinessCaseLocators.download_pdf)
                time.sleep(15)
            except AssertionError:
                pass

    def open_agency(self, agency_name: str):
        """
        Open agency block by name.
        """
        agency_name = agency_name.strip().lower()
        for el in self._browser.find_elements(HomePageLocators.agency_block):  # type: WebElement
            name_el = el.find_element_by_css_selector('span.h4.w200')

            if name_el.text.strip().lower() == agency_name:
                self._browser.click_element(el.find_elements_by_css_selector('a[class="btn btn-default btn-sm"]'))
                return None
        raise ValueError(f'Doesnt exist {agency_name} on the page!')

    def extract_data_from_pdf(self):
        """
        Extract data from pdf and export to excel if data equal with Investment name and UII
        """
        uii2row_idx_map = defaultdict(list)
        empty_index = self._workbook.find_empty_row(ExcelTable.table_data)
        for row in range(2, empty_index):
            value = self._workbook.get_cell_value(row, index2col_name(0), ExcelTable.table_data)
            uii2row_idx_map[value].append(row)

        for file in tqdm(Path(self._output_dir).iterdir(), desc='Compare title and uii', ):
            if file.suffix == '.pdf':
                text: str = self._pdf.get_text_from_pdf(file)
                name_investment = text[1].split('Name of this Investment: ')[1].split('.')[0]
                uii = text[1].split('Unique Investment Identifier (UII): ')[1].split('Section B')[0]
                for row_idx in uii2row_idx_map[file.stem]:
                    self._workbook.set_cell_value(row_idx, index2col_name(7), name_investment, ExcelTable.table_data)
                    self._workbook.set_cell_value(row_idx, index2col_name(8), uii, ExcelTable.table_data)

    def close(self):
        self._browser.close_browser()
        self._workbook.save()
        self._workbook.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
