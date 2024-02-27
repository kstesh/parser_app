#states: 0 - init
#1 - processing
#2 - finished
from ParserProm import ParserProm
from SheetManager import SheetManager



class Processor:
    def __init__(self):
        self._state = 0

    def search_data(self, term, path):
        term = term.strip()
        term_is_link = "prom.ua" in term
        print(term_is_link)
        parse_result = ParserProm(term, status=1).search() if term_is_link else ParserProm(term).search()
        SheetManager().update_sheet(parse_result, path, term.replace(" ", "_"))
        self.__save_current_path(path)
        print(parse_result.head(5))


    def __save_current_path(self, path) -> None:
        SheetManager.save_current_path(path)

    @staticmethod
    def get_last_path() -> str:
        return SheetManager.get_last_path()



if __name__=="__main__":
    Processor().search_data("склоструй", "./output")