import json
from operator import itemgetter

import plone
from Products.CMFCore.utils import getToolByName

from bika.lims.browser import BrowserView

class BoxMovementCreationDate(BrowserView):

    def __init__(self, context, request):

        super(BoxMovementCreationDate, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        uc = getToolByName(self.context, 'portal_catalog')
        title = self.request.form['title']

        brains = uc.searchResults(portal_type='BoxMovement', Title=title)

        try:
            boxmovement = brains[0].getObject()
            return_val = {
                'creation_date_time': str(boxmovement.getField('DateCreated').get(boxmovement) or ''),
                }

            return json.dumps(return_val)

        except:
            return json.dumps({
                'creation_date_time': '',
            })


