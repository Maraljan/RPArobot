import datetime
import time
from pathlib import Path

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
    OUTPUT_DIR = Path('output').absolute()
    EXCEL_FILE_PATH = OUTPUT_DIR / 'agencies.xlsx'

    def __init__(self):
        self._file_system = FileSystem()
        self._excel = Files()
        self._browser = Selenium()

        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        self._browser.set_download_directory(str(self.OUTPUT_DIR))
        self._browser.open_available_browser(self.URL)

        if self._file_system.does_file_exist(self.EXCEL_FILE_PATH):
            self._workbook = self._excel.open_workbook(self.EXCEL_FILE_PATH)
        else:
            self._workbook = self._excel.create_workbook(self.EXCEL_FILE_PATH, fmt='xlsx')
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
        self._browser.click_element(HomePageLocators.small_view_btn)

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

        # Export to excel headers.
        for idx, header in enumerate(self._browser.find_elements(headers)):
            self._workbook.set_cell_value(1, index2col_name(idx), self._browser.get_text(header), ExcelTable.table_data)
        hrefs = []

        # Export to excel all data from table.
        rows = self._browser.find_elements(IndividualInvestmentsLocators.table_rows)
        for row_idx, row_el in tqdm(
                iterable=enumerate(rows, 2),
                desc='Exporting data to excel',
                unit='row',
                total=len(rows),
        ):  # type: int, WebElement
            for col_idx, col in enumerate(row_el.find_elements_by_css_selector('td')):
                self._workbook.set_cell_value(row_idx, index2col_name(col_idx), col.text, ExcelTable.table_data)
                # Store all links in hrefs
                if col_idx == 0:
                    try:
                        link = col.find_element_by_tag_name('a')
                        hrefs.append(link.get_attribute('href'))
                    except NoSuchElementException:
                        pass
        self.open_link_download_pdf(hrefs)

    def open_link_download_pdf(self, hrefs: list):
        for link in tqdm(hrefs, total=len(hrefs), desc='Downloading pdf'):
            self._browser.driver.get(link)
            try:
                self._browser.wait_until_page_contains_element(
                    BusinessCaseLocators.download_pdf,
                    timeout=datetime.timedelta(seconds=10)
                )
                self._browser.click_element(BusinessCaseLocators.download_pdf)
                time.sleep(3)
            except AssertionError:
                print('HELlo MOTHERFUCKER')

    def close(self):
        self._browser.close_browser()
        self._workbook.save()
        self._workbook.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# loader = Loader()
# loader.store_web_page_content()
# loader.export_table_data()
# loader.close()
