from enum import Enum


class StrEnum(str, Enum):
    pass


class HomePageLocators(StrEnum):
    dive_in_btn = 'css:a[class="btn btn-default btn-lg-2x trend_sans_oneregular"]'
    agency_names = 'css:a  span.h4.w200'
    spending_amount = 'css:a  span.h1.w900'
    small_view_btn = 'css:a[class="btn btn-default btn-sm"]'


class IndividualInvestmentsLocators(StrEnum):
    data_table = 'css:div[class="dataTables_wrapper no-footer"]'
    select_form = 'css:select[name="investments-table-object_length"]'
    choose_all_option = 'css:option[value="-1"]'
    data_table_info = 'css:.dataTables_info'
    table_rows = 'css:#investments-table-object > tbody > tr'
    table_headers = 'css:.dataTables_scrollHeadInner > table > thead > tr[role="row"] > th'


class BusinessCaseLocators(StrEnum):
    download_pdf = 'css: #business-case-pdf > a'


class ExcelTable(StrEnum):
    agency = 'Agencies'
    table_data = 'TableData'

