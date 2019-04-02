import collections

import os
import json

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

from bika.lims.exportimport.dataimport import ImportView as IV
from exporters import *
from excelwriter import ExcelWriter

from bika.lims.browser import BrowserView

class RemoveExports(BrowserView):
    def __init__(self, context, request):

        super(RemoveExports, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        uc = getToolByName(self.context, 'portal_catalog')
        doc_id = self.request.form['id']

        filename = 'src/baobab.lims/baobab/lims/static/downloads/' + doc_id
        if os.path.exists(filename):
            os.remove(filename)

        return json.dumps({
            'row_id': doc_id
        })

class ExportView(IV):
    """
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/export.pt")

    def __init__(self, context, request):
        IV.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        if 'submitted' in self.request:
            lab = self.context.bika_setup.laboratory
            self.excel_writer = ExcelWriter()
            self.export_data()

            self.download_file = True
            self.files = self.get_filenames()
            self.context.plone_utils.addPortalMessage('Export successfully completed.')
        else:
            self.submit_button = True
        return self.template()

    def get_filenames(self):
        from os import listdir
        from os.path import isfile, join, getmtime
        path = 'src/baobab.lims/baobab/lims/static/downloads/'
        files = [f for f in listdir(path) if isfile(join(path, f))]
        files.sort(key=lambda x: getmtime(join(path, x)), reverse=True)
        return files

    def export_data(self):
        export_dict = collections.OrderedDict()

        # get the batch samples
        exporter = SamplesExporter(self.context)
        export_dict['Parent Samples'] = exporter.export()

        # get the samples
        batch_sample_exporter = SampleBatchesExporter(self.context)
        export_dict['SampleBatch'] = batch_sample_exporter.export()

        # get the aliquot samples
        exporter = SamplesAliquotExporter(self.context)
        export_dict['Aliquot'] = exporter.export()

        # get the box-movement
        exporter = BoxMovementExporter(self.context)
        export_dict['Box Movement'] = exporter.export()


        self.excel_writer.write_output(export_dict)
