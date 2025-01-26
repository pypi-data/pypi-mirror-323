import re
import logging
import warnings
from typing import Callable
import pandas as pd
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import gspread
from gspread_dataframe import set_with_dataframe
from ..y4a_retry import retry_on_error
from ..y4a_credentials import get_credentials
import time

warnings.filterwarnings("ignore", category=UserWarning)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

class GGSheetUtils:
    """
    Utils for Google Sheets

    :param account_name: the client account name for Google Sheet
        defaults to 'da'
    :param auth_dict: the dictionary of user credentials for the Google Sheet,
        defaults to None
        if None, the module will use the default credentials
        of DA team
    """


    def __init__(
        self,
        account_name: str = 'da',
        user_creds: dict = None,
    ) -> None:
        self.account_name = account_name
        self.user_creds = user_creds

    def construct_data(
        self,
        data: pd.DataFrame,
    ) -> pd.DataFrame:
        df = data.copy()

        for col in df.columns:
            try:
                df[col] = df[col].astype('float')
            except Exception:
                try:
                    pd.to_datetime(df[col])
                    df[col] = df[col].astype('string').apply(
                        lambda x: re.sub('^[0-9]+$', '', x)
                    )
                    df[col] = pd.to_datetime(
                        df[col]
                    ).dt.strftime('%Y-%m-%d').astype('string')
                except Exception:
                    df[col] = df[col].astype('string')

        df.fillna('', inplace=True)

        return df

    @retry_on_error(delay=30)
    def open_spread_sheet(
        self,
        sheet_id: str,
    ) -> Callable:
        """
        Open the spreadsheet from the given spreadsheet id

        :param sheet_id: id of the spreadsheet

        :return: spreadsheet object
        """

        if self.user_creds:
            auth_dict = self.user_creds
        else:
            credentials = get_credentials(
                platform='gg_api',
                account_name=self.account_name,
            )

            email = credentials['email']
            private_key = credentials['secret_key']

            auth_dict = {
                'client_email': email,
                'private_key': private_key,
                'token_uri': 'https://oauth2.googleapis.com/token',
            }

        client = gspread.service_account_from_dict(auth_dict)

        spread_sheet = client.open_by_key(
            key=sheet_id,
        )

        return spread_sheet

    @retry_on_error(delay=30)
    def open_spread_sheet_by_title(
        self,
        title: str,
        folder_id: str = None,
    ) -> Callable:
        """
        Open the spreadsheet from the given spreadsheet title

        :param title: title of the spreadsheet
        :param folder_id: the id of folder that contains the spreadsheet
            defaults to None

        :return: spreadsheet object
        """

        if self.user_creds:
            auth_dict = self.user_creds
        else:
            credentials = get_credentials(
                platform='gg_api',
                account_name=self.account_name,
            )

            email = credentials['email']
            private_key = credentials['secret_key']

            auth_dict = {
                'client_email': email,
                'private_key': private_key,
                'token_uri': 'https://oauth2.googleapis.com/token',
            }

        client = gspread.service_account_from_dict(auth_dict)

        spread_sheet = client.open(
            title=title,
            folder_id=folder_id,
        )

        return spread_sheet


    @retry_on_error(delay=30)
    def get_spread_sheet_id(
        self,
        title: str,
        folder_id: str = None,
    ) -> str:
        """
        Get the spreadsheet id from the given spreadsheet title

        :param title: title of the spreadsheet
        :param folder_id: the id of folder that contains the spreadsheet
            defaults to None

        :return: spreadsheet id
        """

        sheet_id = self.open_spread_sheet_by_title(
            title=title,
            folder_id=folder_id,
        ).id

        return sheet_id

    @retry_on_error(delay=30)
    def get_work_sheet(
        self,
        spread_sheet: Callable,
        sheet_name: str,
    ) -> Callable:
        work_sheet = spread_sheet.worksheet(sheet_name)

        return work_sheet


    @retry_on_error(delay=30)
    def create_spread_sheet(
        self,
        sheet_name: str,
        folder_id: str = None,
        share_to: list = [],
    ) -> str:
        """
        Create a new spread sheet

        :param sheet_name: name of the sheet
        :param folder_id: id of the folder contains spreadsheet
        :param share_to: list of email to share the spreadsheet
            defaults to []

        :return: the created spreadsheet id
        """

        if self.user_creds:
            auth_dict = self.user_creds
        else:
            credentials = get_credentials(
                platform='gg_api',
                account_name=self.account_name,
            )

            email = credentials['email']
            private_key = credentials['secret_key']

            auth_dict = {
                'client_email': email,
                'private_key': private_key,
                'token_uri': 'https://oauth2.googleapis.com/token',
            }

        client = gspread.service_account_from_dict(auth_dict)

        spread_sheet = client.create(
            title=sheet_name,
            folder_id=folder_id,
        )
        if share_to:
            for mail in share_to:
                spread_sheet.share(
                    email_address=mail,
                    perm_type='user',
                    role='writer',
                )

        return spread_sheet.id

    @retry_on_error(delay=30)
    def add_work_sheet(
        self,
        title: str,
        sheet_id: str,
        num_rows: int = 1000,
        num_cols: int = 26,
    ) -> Callable:
        """
        Add new worksheet from the given spreadsheet

        :param title: title of the new worksheet
        :param sheet_id: spreadsheet id
        :param num_rows: number rows of the new worksheet
            defaults to 1000
        :param num_cols: number columns of the new worksheet
            defaults to 26

        :return: worksheet object
        """

        spread_sheet = self.open_spread_sheet(
            sheet_id=sheet_id,
        )
        work_sheet = spread_sheet.add_worksheet(
            title=title,
            rows=num_rows,
            cols=num_cols,
        )

        return work_sheet

    @retry_on_error(delay=30)
    def list_all_work_sheets(
        self,
        sheet_id: str,
    ) -> list:
        """
        Get all available worksheet of spreadsheet

        :param sheet_id: spreadsheet id

        :return: list all worksheets of spreadsheet
        """

        spread_sheet = self.open_spread_sheet(sheet_id)

        work_sheets = spread_sheet.worksheets()

        return work_sheets

    @retry_on_error(delay=30)
    def delete_work_sheet(
        self,
        sheet_id: str,
        sheet_name: str = 'Sheet1',
    ) -> None:
        """
        Delete specific worksheet of spreadsheet

        :param sheet_id: spreadsheet id
        :param sheet_name: worksheet name
            defaults to 'Sheet1'
        """

        spread_sheet = self.open_spread_sheet(sheet_id)

        work_sheet = self.get_work_sheet(
            spread_sheet=spread_sheet,
            sheet_name=sheet_name,
        )

        spread_sheet.del_worksheet(work_sheet)

    @retry_on_error(delay=30)
    def clear_work_sheet(
        self,
        sheet_id: str,
        sheet_name: str = 'Sheet1',
        delete_cells: bool = False,
    ) -> None:
        """
        Clear all data of specific worksheet of spreadsheet

        :param sheet_id: spreadsheet id
        :param sheet_name: worksheet name
            defaults to 'Sheet1'
        :param delete_cells: whether to delete all cells
            defaults to False
        """

        spread_sheet = self.open_spread_sheet(sheet_id)

        work_sheet = self.get_work_sheet(
            spread_sheet=spread_sheet,
            sheet_name=sheet_name,
        )

        work_sheet.clear()

        if delete_cells:
            work_sheet.delete_columns(2, work_sheet.col_count)
            work_sheet.delete_rows(2, work_sheet.row_count)

    @retry_on_error(delay=30)
    def protect_work_sheet(
        self,
        spreadsheet_id: str,
        worksheet_name: str,
        editors: dict = {
            "users": [],
            "groups": [],
        },
        start_col_index: int = None,
        end_col_index: int = None,
        start_row_index: int = None,
        end_row_index: int = None,
    ) -> None:
        """
        Protect data from the given sheet

        :param spreadsheet_id: spreadsheet id
        :param worksheet_name: worksheet name
        :param editors: dictionary of emails of user and group
            that can edit the sheet
        :param start_col_index: The zero-based index of start column to protect
            defaults to None
        :param end_col_index: The zero-based index of end column
            to protect (not included)
            defaults to None
        :param start_row_index: The zero-based index of start row to protect
            defaults to None
        :param end_row_index: The zero-based index of end row
            to protect (not included)
            defaults to None
        """

        spread_sheet = self.open_spread_sheet(spreadsheet_id)
        work_sheet_id = self.get_work_sheet(
            spread_sheet,
            worksheet_name,
        ).id

        if self.user_creds:
            auth_dict = self.user_creds
        else:
            credentials = get_credentials(
                platform='gg_api',
                account_name=self.account_name,
            )

            email = credentials['email']
            private_key = credentials['secret_key']

            auth_dict = {
                'client_email': email,
                'private_key': private_key,
                'token_uri': 'https://oauth2.googleapis.com/token',
            }

        service = build(
            'sheets',
            'v4',
            credentials=Credentials.from_service_account_info(
                auth_dict,
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ],
            )
        )

        req_protect_range = {
            "sheetId": work_sheet_id,
        }
        if start_col_index:
            req_protect_range['startColumnIndex'] = start_col_index
        if end_col_index:
            req_protect_range['endColumnIndex'] = end_col_index
        if start_row_index:
            req_protect_range['startRowIndex'] = start_row_index
        if end_row_index:
            req_protect_range['endRowIndex'] = end_row_index

        req_protect = {
            "addProtectedRange": {
                "protectedRange": {
                    "range": req_protect_range,
                    "description": "Protected range with specific editors",
                    "warningOnly": False,
                    "editors": editors,
                }
            }
        }

        body = {
            'requests': [req_protect]
        }

        response = service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
        logging.info(response)


    def batch_update_data(
        self,
        data: pd.DataFrame,
        spreadsheet_id: str,
        sheet_id: str,
        sheet_name: str = 'Sheet1',
        remove_format: bool = False,
        updateRowIndex: int = 0,
        updateColIndex: int = 0,
        clearRowIndex: int = 0,
        clearColIndex: int = 0,
        batch_size: int = 10000
    ):
        print("Batch update data")

        if self.user_creds:
            auth_dict = self.user_creds
        else:
            credentials = get_credentials(
                platform='gg_api',
                account_name=self.account_name,
            )

            email = credentials['email']
            private_key = credentials['secret_key']

            auth_dict = {
                'client_email': email,
                'private_key': private_key,
                'token_uri': 'https://oauth2.googleapis.com/token',
            }

        service = build(
            'sheets',
            'v4',
            credentials=Credentials.from_service_account_info(
                auth_dict,
                scopes=[
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive'
                ],
            ),
            cache_discovery=False
        )

        for col in data.columns:
            data[col] = data[col].replace('\n',' ', regex=True).replace('\r',' ', regex=True)
            
        data = self.construct_data(data)
        sheet_data = [data.columns.tolist()] + data.values.tolist()

        if remove_format:
            format = 'PASTE_NORMAL' 
        else:
            format = 'PASTE_VALUES'

        requests = [
            # Clear all data on the sheet
            {
            "updateCells": {
                "range": {
                    "sheetId": sheet_id,  # ID of the sheet (taken from spreadsheet.get API)
                    "startRowIndex": clearRowIndex,  # Dòng bắt đầu (bao gồm)
                    "startColumnIndex": clearColIndex,  
                },
                "fields": "userEnteredValue"  # Clear all
            }
            }
        ]

        body = {"requests": requests}

        service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()

        # Convert date objects to strings
        for start_row in range(0, len(sheet_data), batch_size):
            print(f"Updating rows {start_row} to {start_row + batch_size}")
            batch_data = sheet_data[start_row:start_row + batch_size]
            range_ = f"{sheet_name}!{gspread.utils.rowcol_to_a1(updateRowIndex + start_row + 1, updateColIndex + 1)}"
            body = {
            "range": range_,
            "majorDimension": "ROWS",
            "values": batch_data
            }

            result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=range_,
            valueInputOption="USER_ENTERED",
            body=body
            ).execute()
            time.sleep(1)

        return result

        

    @retry_on_error(delay=30)
    def get_data(
        self,
        sheet_id: str,
        sheet_name: str = 'Sheet1',
        range_from: str = None,
        range_to: str = None,
        columns_first_row: bool = False,
        auto_format_columns: bool = False,
    ) -> pd.DataFrame:
        """
        Get data from the given sheet

        :param sheet_id: spreadsheet name
        :param sheet_name: worksheet name
            defaults to 'Sheet1'
        :param range_from: the begining of the range
            of data from sheet to get
            defaults to None
        :param range_to: the end of the range
            of data from sheet to get
            defaults to None
        :param columns_first_row: whether to convert the first row
            to columns
            defaults to False
        :param auto_format_columns: whether to format columns name
            of the dataframe
            defaults to False

        :return: the dataframe contains data from sheet
        """

        spread_sheet = self.open_spread_sheet(sheet_id)

        work_sheet = self.get_work_sheet(
            spread_sheet=spread_sheet,
            sheet_name=sheet_name,
        )

        if not range_from and not range_to:
            data = work_sheet.get_values()
        else:
            if not range_from:
                range_from = 'A1'
            if not range_to:
                range_to = gspread.utils.rowcol_to_a1(
                    work_sheet.row_count,
                    work_sheet.col_count,
                )

            data = work_sheet.get_values(f'{range_from}:{range_to}')

        df = pd.DataFrame(data)
        if columns_first_row:
            df.columns = df.iloc[0].to_list()
            df = df.iloc[1:].reset_index(drop=True)
        if auto_format_columns:
            if columns_first_row:
                formatted_cols = list()
                for col in df.columns:
                    if not col:
                        col = ''
                    col = str(col).lower()
                    col = re.sub(r'[^\w]+', '_', col)
                    col = re.sub(r'^_', '', col)
                    col = re.sub(r'_$', '', col)
                    formatted_cols.append(col)
                df.columns = formatted_cols
            else:
                raise ValueError(
                    'Can not format column names when '
                    'the value of param `columns_first_row` is False'
                )

        return df

    @retry_on_error(delay=30)
    def insert_data(
        self,
        data: pd.DataFrame,
        sheet_id: str,
        sheet_name: str = 'Sheet1',
        from_row_index: int = 1,
        insert_column_names: bool = False,
        parse_input: bool = True,
        pre_process: bool = True,
    ) -> None:
        """
        Insert data to the given sheet

        :param data: dataframe contains data to insert
        :param sheet_id: spreadsheet id
        :param sheet_name: worksheet name
            defaults to 'Sheet1'
        :param from_row_index: the index of the row
            beginning to insert
            defaults to 1
        :param insert_column_names: whether to insert column names
            defaults to False
        :param parse_input: whether to parse input values
            as if the user typed them into the UI
            defaults to True
        :param pre_process: whether to process input values
            based on the pre-defined function of DA
            defaults to True
        """

        spread_sheet = self.open_spread_sheet(sheet_id)

        work_sheet = self.get_work_sheet(
            spread_sheet=spread_sheet,
            sheet_name=sheet_name,
        )

        input_option = 'RAW'
        if parse_input:
            input_option = 'USER_ENTERED'

        if pre_process:
            constructed_data = self.construct_data(data)
        else:
            constructed_data = data.copy()
        data_values = constructed_data.values.tolist()

        if insert_column_names:
            col_values = [data.columns.to_list()]
            work_sheet.insert_rows(
                col_values,
                row=from_row_index,
            )
            work_sheet.insert_rows(
                data_values,
                row=from_row_index+1,
                value_input_option=input_option,
            )
        else:
            work_sheet.insert_rows(
                data_values,
                row=from_row_index,
                value_input_option=input_option,
            )

    @retry_on_error(delay=30)
    def update_data(
        self,
        data: pd.DataFrame,
        sheet_id: str,
        sheet_name: str = 'Sheet1',
        range_from: str = 'A1',
        parse_input: bool = True,
        pre_process: bool = True,
    ) -> None:
        """
        Update data of the given sheet

        :param data: dataframe contains data to update
        :param sheet_id: spreadsheet name
        :param sheet_name: worksheet name
            defaults to 'Sheet1'
        :param range_from: the begining of the range
            of data from sheet to update
            defaults to 'A1'
        :param parse_input: whether to parse input values
            as if the user typed them into the UI
            defaults to True
        :param pre_process: whether to process input values
            based on the pre-defined function of DA
            defaults to True
        """

        spread_sheet = self.open_spread_sheet(sheet_id)

        work_sheet = self.get_work_sheet(
            spread_sheet=spread_sheet,
            sheet_name=sheet_name,
        )

        input_option = 'RAW'
        if parse_input:
            input_option = 'USER_ENTERED'

        if pre_process:
            constructed_data = self.construct_data(data)
        else:
            constructed_data = data.copy()
        data_values = constructed_data.values.tolist()

        num_current_rows = work_sheet.row_count
        num_current_cols = work_sheet.col_count

        range_from_index = gspread.utils.a1_to_rowcol(range_from)
        row_from_index = range_from_index[0]
        col_from_index = range_from_index[-1]

        if row_from_index > num_current_rows:
            rows_to_resize = row_from_index
        else:
            rows_to_resize = num_current_rows

        if col_from_index > num_current_cols:
            cols_to_resize = col_from_index
        else:
            cols_to_resize = num_current_cols

        work_sheet.resize(
            rows=rows_to_resize,
            cols=cols_to_resize,
        )

        work_sheet.update(
            f'{range_from}',
            data_values,
            value_input_option=input_option,
        )

    @retry_on_error(delay=30)
    def gspread_load_data(
        self,
        data: pd.DataFrame,
        sheet_id: str,
        sheet_name: str = 'Sheet1',
        from_row: int = 1,
        from_col: int = 1,
        include_index: bool = False,
        include_column: bool = True,
        resize_worksheet: bool = False,
        allow_formulas: bool = True,
        string_escaping: str = 'default',
    ) -> None:
        """
        Load data to the given sheet. This method
        is integrated with GSpread load data function
        that provides the high efficiency and convenience,
        it can be used as the alternative of two methods
        'insert_data' and 'update_data'

        :param data: dataframe contains data to load
        :param sheet_id: spreadsheet name
        :param sheet_name: worksheet name
            defaults to 'Sheet1'
        :param from_row: row at which to start loading the DataFrame
            defaults to 1
        :param from_col: column at which to start loading the DataFrame
            defaults to 1
        :param include_index: if True, include the DataFrame's index as an
            additional column
            defaults to False
        :param include_column: if True, add a header row or rows before data
            with column names (if include_index is True, the index's name(s)
            will be used as its columns' headers)
            defaults to True
        :param resize_worksheet: if True, changes the worksheet's
            size to match the shape of the provided DataFrame,
            if False, worksheet will only be
            resized as necessary to contain the DataFrame contents
            defaults to False
        :param allow_formulas: if True, interprets `=foo` as a formula in
            cell values; otherwise all text beginning with `=` is escaped
            to avoid its interpretation as a formula
            defaults to True
        :param string_escaping: determines when string values are
            escaped as text literals (by adding an initial `'` character)
            in requests to Sheets API
            4 parameter values are accepted:
            - 'default': only escape strings starting with a literal `'`
                character
            - 'off': escape nothing; cell values starting with a `'` will be
                interpreted by sheets as an escape character followed by
                a text literal
            - 'full': escape all string values
            - any callable object: will be called once for each cell's string
                value; if return value is true, string will be escaped
                with preceding `'` (A useful technique is to pass a
                regular expression bound method, e.g.
                `re.compile(r'^my_regex_.*$').search`.)
            the escaping done when allow_formulas=False (escaping string values
            beginning with `=`) is unaffected by this parameter's value
            defaults to 'default'
        """

        spreadsheet = self.open_spread_sheet(sheet_id)
        worksheet = self.get_work_sheet(
            spreadsheet,
            sheet_name,
        )

        set_with_dataframe(
            worksheet=worksheet,
            dataframe=data,
            row=from_row,
            col=from_col,
            include_index=include_index,
            include_column_header=include_column,
            resize=resize_worksheet,
            allow_formulas=allow_formulas,
            string_escaping=string_escaping,
        )

    @retry_on_error(delay=30)
    def remove_data(
        self,
        sheet_id: str,
        sheet_name: str = 'Sheet1',
        list_range: list = [
            'A1:Z1',
            'A4:Z4',
        ],
    ) -> None:
        """
        Remove data from specific range of the given sheet

        :param sheet_id: spreadsheet name
        :param sheet_name: worksheet name
            defaults to 'Sheet1'
        :param list_range: list of data ranges to remove
            defaults to ['A1:Z1', 'A4:Z4']
        """

        spread_sheet = self.open_spread_sheet(sheet_id)

        work_sheet = self.get_work_sheet(
            spread_sheet=spread_sheet,
            sheet_name=sheet_name,
        )
        work_sheet.batch_clear(list_range)


    # @retry_on_error(delay=30)
    def duplicate_sheet(
        self,
        sheet_id: str,
        source_sheet_id: int,
        new_sheet_name: str,
        format_only: bool = False
    ) -> Callable:
        """
        Duplicate an existing sheet with the same format and number of rows/columns.

        :param sheet_id: spreadsheet id
        :param source_sheet_id: worksheet id (gid)
        :param new_sheet_name: name of the new duplicated sheet
        :format_only: just duplicate format, default False
        """
        
        spread_sheet = self.open_spread_sheet(sheet_id)

        work_sheet = spread_sheet.duplicate_sheet(
            source_sheet_id=source_sheet_id, 
            new_sheet_name=new_sheet_name
        )

        if format_only:
            self.clear_work_sheet(
                sheet_id=sheet_id,
                sheet_name=new_sheet_name
            )

        return work_sheet