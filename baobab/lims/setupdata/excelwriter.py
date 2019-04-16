import xlsxwriter
import datetime


class ExcelWriter(object):

    def __init__(self):
        filename = str(datetime.datetime.now().date()) + '_' + \
            str(datetime.datetime.now().time()).replace(':', '.')
        self.dir_path = "/usr/local/Plone/zeocluster/src/baobab.lims/baobab/lims/static/downloads/{}.xlsx".format(
            filename)
        self.workbook = xlsxwriter.Workbook(self.dir_path, {'in_memory': True})
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
