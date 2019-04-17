import xlsxwriter
import datetime
import os


class ExcelWriter(object):

    _DOWNLOADS_DIR = 'static/downloads/'

    def __init__(self):
        filename = str(datetime.datetime.now().date()) + '_' + \
            str(datetime.datetime.now().time()).replace(':', '.')

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.download_dir = os.path.join(base_dir, self._DOWNLOADS_DIR)

        self.workbook = xlsxwriter.Workbook(
            self.download_dir + "{}.xlsx".format(filename))

        self.bold = self.workbook.add_format({'bold': True})

    def write_output(self, worksheet_data):
        for sheet_name, sheet_data in worksheet_data.iteritems():
            work_sheet = self.workbook.add_worksheet(sheet_name)
            for i, row in enumerate(sheet_data):
                if i == 0:
                    work_sheet.write_row(i, 0, row, self.bold)
                else:
                    work_sheet.write_row(i, 0, row)

        self.workbook.close()
