# import time
from utils import getLocalServerTime
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime


def ObjectInitializedEventHandler(instance, event):
    """called an object is created
    """
    if instance.portal_type == 'SampleShipment':
        membership = getToolByName(instance, 'portal_membership')
        if membership.isAnonymousUser():
            member = 'anonymous'
        else:
            member = membership.getAuthenticatedMember().getUserName()

        instance.getField('ChangeUserName').set(instance, member)
        instance.getField('ChangeDateTime').set(instance, DateTime())

def ObjectModifiedEventHandler(instance, event):
    """ Called if the object is modified
    """
    if instance.portal_type == 'SampleShipment':
        membership = getToolByName(instance, 'portal_membership')
        if membership.isAnonymousUser():
            member = 'anonymous'
        else:
            member = membership.getAuthenticatedMember().getUserName()

        instance.getField('ChangeUserName').set(instance, member)
        instance.getField('ChangeDateTime').set(instance, DateTime())
