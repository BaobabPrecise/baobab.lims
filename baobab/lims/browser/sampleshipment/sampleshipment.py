import os
import traceback

from DateTime import DateTime
from Products.ATContentTypes.lib import constraintypes
from Products.Archetypes.public import BaseFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

#from Products.Five.browser import BrowserView
from bika.lims.browser import BrowserView
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser.multifile import MultifileView
from bika.lims.utils import to_utf8
from baobab.lims import bikaMessageFactory as _


class SampleShipmentView(BrowserView):
    template = ViewPageTemplateFile('templates/sample_shipment_view.pt')

    def __init__(self, context, request):
        super(SampleShipmentView, self).__init__(context, request)
        self.title = self.context.Title()
        self.context = context
        self.request = request

    def __call__(self):

        samples = self.context.getSamplesList()

        workflow = getToolByName(self.context, 'portal_workflow')
        reviewState = workflow.getInfoFor(self.context, 'review_state')

        self.reviewState = reviewState
        self.absolute_url = self.context.absolute_url()
        self.id = self.context.getId()
        self.sample_shipment_uid = self.context.UID()
        self.title = self.context.Title()
        self.description = self.context.Description()
        self.from_contact = self.context.getFromEmailAddress()
        self.to_contact = self.context.getToEmailAddress()
        self.client = self.context.getClient().Title()
        self.delivery_address = self.context.getDeliveryAddress()
        self.shipping_date = self.context.getShippingDate()
        self.date_dispatched = self.context.getDateDispatched()
        self.date_delivered = self.context.getDateDelivered()
        self.courier_name = self.context.getCourier()
        self.courier_instructions = self.context.getCourierInstructions()
        self.tracking_url = self.context.getTrackingURL()
        self.shipment_conditions = self.context.getShipmentConditions()
        self.shipping_cost = self.context.getShippingCost()
        self.weight = self.context.getWeight()
        self.volume = self.context.getVolume()
        self.samples = samples     # self.context.getSamplesList()
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/shipment_big.png"

        return self.template()

class SampleShipmentEdit(BrowserView):
    # template = ViewPageTemplateFile('templates/sample_shipment_edit.pt')
    template = ViewPageTemplateFile('templates/sample_shipment_edit.pt')

    def __call__(self):
        # print('----SampleShipment call---------')
        portal = self.portal
        request = self.request
        context = self.context
        setup = portal.bika_setup

        if 'submitted' in request:
            # print('----SampleShipment submitted---------')
            # pdb.set_trace()
            context.setConstrainTypesMode(constraintypes.DISABLED)
            # This following line does the same as precedent which one is the
            #  best?

            # context.aq_parent.setConstrainTypesMode(constraintypes.DISABLED)
            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)
            context.processForm()

            # print('---after the SampleShipment process form')

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return

        # print('-------the SampleShipment template-------')

        return self.template()

    # def get_fields_with_visibility(self, visibility, mode=None):
    #     mode = mode if mode else 'edit'
    #     schema = self.context.Schema()
    #     fields = []
    #     for field in schema.fields():
    #         # print('-------------')
    #         isVisible = field.widget.isVisible
    #         v = isVisible(self.context, mode, default='invisible', field=field)
    #         if v == visibility:
    #             fields.append(field)
    #     return fields

    def get_fields_with_visibility(self, visibility, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        schemata = {}
        # fields = []
        for field in schema.fields():
            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            if v == visibility:
                if field.schemata in schemata:
                    schemata[field.schemata].append(field)
                # fields.append(field)
                else:
                    schemata[field.schemata] = [field]

        print('--------')
        print(schemata)
        return schemata
