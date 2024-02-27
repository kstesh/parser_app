import pandas as pd
import os
import sys
from urllib.parse import unquote
import re


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS2
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class SheetManager:
    def update_sheet(self, sheet: pd.DataFrame, path: str, term: str) -> None:
        """
        Updates the existing sheet or saves a new sheet to the specified path with the given name.

        Parameters:
        - sheet (pd.DataFrame): The new sheet to be added.
        - path (str): The directory path to save the sheet.
        - name (str): The name of the Excel file (without extension).
        """
        if sheet is None or sheet.shape==(0,0):
            return
        name = re.sub(r'[^a-zA-Z0-9\u0400-\u04FF_]', '', unquote(term))
        print(name)
        file_path = os.path.join(path, f"{name}.xlsx")
        os.makedirs(path, exist_ok=True)
        if os.path.isfile(file_path):
            old_sheet = pd.read_excel(file_path)
            if old_sheet.shape != (0, 0):
                updated_sheet = self.__union_sheets(old_sheet, sheet)
            else:
                updated_sheet = sheet
        else:
            updated_sheet = sheet

        self.__save_sheet(updated_sheet, path, name)

    def __union_sheets(self, old_sheet: pd.DataFrame, new_sheet: pd.DataFrame) -> pd.DataFrame:
        """
        Unions (concatenates) two DataFrames vertically without duplicating rows.

        Parameters:
        - old_sheet (pd.DataFrame): The existing sheet.
        - new_sheet (pd.DataFrame): The new sheet to be added.

        Returns:
        - pd.DataFrame: The union of old_sheet and new_sheet.
        """
        common_rows = pd.merge(old_sheet, new_sheet, how='inner')
        unique_rows = pd.concat([old_sheet, new_sheet.loc[~new_sheet.index.isin(common_rows.index)]], ignore_index=True)
        return unique_rows

    def __save_sheet(self, sheet: pd.DataFrame, path: str, name: str) -> None:
        """
        Saves the given sheet to the specified path with the given name.

        Parameters:
        - sheet (pd.DataFrame): The sheet to be saved.
        - path (str): The directory path to save the sheet.
        - name (str): The name of the Excel file (without extension).
        """

        sheet.to_excel(os.path.join(path, f"{name}.xlsx"), index=False)

    @staticmethod
    def save_current_path(path) -> None:
        with open(resource_path('parser_save_to_path.txt'), 'w') as file:
            text_to_save = path
            file.write(text_to_save)

    @staticmethod
    def get_last_path() -> str:
        file_path = resource_path('parser_save_to_path.txt')

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                path_from_file = file.readline()
            return path_from_file
        else:
            return 'Select path!!!'

if __name__ == "__main__":
    # Create a SheetManager instance
    sheet_manager = SheetManager()

    # Create two sample DataFrames for testing
    sheet1_data = {'ID': [1, 2, 3], 'Name': ['Alice', 'Bob', 'Charlie']}
    sheet2_data = {'ID': [2, 3, 4], 'Name': ['Bob', 'Charlie', 'David']}
    sheet1 = pd.DataFrame(sheet1_data)
    sheet2 = pd.DataFrame(sheet2_data)

    # Specify the directory path and name for saving the sheet
    path = r"d:\test_parser"
    name = 'merged_sheet'

    # Test the update_sheet method
    sheet_manager.update_sheet(sheet1, path, name)

    # Optional: Print the updated or new sheet for verification
    merged_sheet = pd.read_excel(os.path.join(path, f"{name}.xlsx"))
    print("New Sheet:")
    print(merged_sheet)

    sheet_manager.update_sheet(sheet2, path, name)
    merged_sheet = pd.read_excel(os.path.join(path, f"{name}.xlsx"))
    print("Merged Sheet:")
    print(merged_sheet)

    sheet3 = pd.DataFrame()
    name = 'empty_sheet'

    # Test the update_sheet method
    sheet_manager.update_sheet(sheet3, path, name)

    # Optional: Print the updated or new sheet for verification
    assert FileNotFoundError, pd.read_excel(os.path.join(path, f"{name}.xlsx"))
    print("New Sheet: not found")
