import json
from operator import itemgetter

import plone
from Products.CMFCore.utils import getToolByName

from bika.lims.browser import BrowserView


class GetSampleDates(BrowserView):

    def __init__(self, context, request):

        super(GetSampleDates, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):

        uc = getToolByName(self.context, 'portal_catalog')

        try:
            uid = self.request['UID']
            brains = uc.searchResults(portal_type='Sample', UID=uid)
            sample = brains[0].getObject()

            return_val = {
                'sampling_date': str(sample.getField('SamplingDate').get(sample) or ''),
                'frozen_time': str(sample.getField('FrozenTime').get(sample) or '')
            }

            return json.dumps(return_val)

        except:
            return json.dumps({
                'sampling_date': '',
                'frozen_time': ''
            })