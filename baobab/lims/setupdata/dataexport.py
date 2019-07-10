import collections

import os
import json

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

from bika.lims.exportimport.dataimport import ImportView as IV
from exporters import *
from excelwriter import ExcelWriter

from bika.lims.browser import BrowserView


class RemoveExports(BrowserView):
    _DOWNLOADS_DIR = 'static/downloads/'

    def __init__(self, context, request):

        super(RemoveExports, self).__init__(context, request)
        self.context = context
        self.request = request

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.download_dir = os.path.join(base_dir, self._DOWNLOADS_DIR)

    def __call__(self):
        uc = getToolByName(self.context, 'portal_catalog')

        filename = self.download_dir + self.request.form['id']
        if os.path.exists(filename):
            os.remove(filename)

        return json.dumps({
            'row_id': self.request.form['id']
        })


class ExportView(IV):
    """
    """
    implements(IViewView)
    template = ViewPageTemplateFile("templates/export.pt")
    _DOWNLOADS_DIR = 'static/downloads/'

    def __init__(self, context, request):
        IV.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        if 'submitted' in self.request:
            lab = self.context.bika_setup.laboratory
            self.excel_writer = ExcelWriter(self.context)
            self.excel_writer.create_workbook()

            base_dir = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))
            self.download_dir = os.path.join(base_dir, self._DOWNLOADS_DIR)

            self.export_data()

            self.download_file = True
            self.files = self.get_filenames()
            self.context.plone_utils.addPortalMessage(
                'Export successfully completed.')
        else:
            self.submit_button = True
        return self.template()

    def get_filenames(self):
        from os import listdir
        from os.path import isfile, join, getmtime

        files = [f for f in listdir(self.download_dir) if isfile(
            join(self.download_dir, f))]

        files.sort(key=lambda x: getmtime(
            join(self.download_dir, x)), reverse=True)
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

        # get the sample shipment
        exporter = SampleShipmentExporter(self.context)
        export_dict['Sample Shipment'] = exporter.export()

        # get the sample types
        exporter = SampleTypesExporter(self.context)
        export_dict['Sample Types'] = exporter.export()

        exporter = ProjectsExporter(self.context)
        export_dict['Projects'] = exporter.export()

        membership = getToolByName(self.context, 'portal_membership')
        if not membership.isAnonymousUser() and membership.getAuthenticatedMember().getUserName() == 'admin':
            exporter = AuditLogExporter(self.context)
            export_dict['Audit Logs'] = exporter.export()

        self.excel_writer.write_output(export_dict)
