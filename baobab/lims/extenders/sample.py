from Products.Archetypes.references import HoldingReference
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from zope.component import adapts
from Products.CMFCore import permissions

# from bika.lims.browser.fields import DateTimeField
from bika.lims.fields import *
from bika.lims.interfaces import ISample
from bika.lims.browser.widgets import ReferenceWidget as bika_ReferenceWidget
from bika.lims.browser.widgets import SelectionWidget as BikaSelectionWidget
from bika.lims.browser.widgets import DateTimeWidget
from bika.lims.content.sample import Sample as BaseSample
from bika.lims.workflow import doActionFor

from baobab.lims import bikaMessageFactory as _
from baobab.lims.interfaces import ISampleStorageLocation
from zope.component import queryUtility
from Products.Archetypes.interfaces.vocabulary import IVocabulary
from plone.registry.interfaces import IRegistry
from Products.Archetypes.utils import DisplayList
import sys


class ExtFixedPointField(ExtensionField, FixedPointField):
    "Field extender"

class UnitsVocabulary(object):
    implements(IVocabulary)

    def getDisplayList(self, context):

        registry = queryUtility(IRegistry)
        units = []
        if registry is not None:

            for unit in registry.get('baobab.lims.biospecimen.units', ()):
                units.append([unit, unit])

        return DisplayList(units)


class SampleSchemaExtender(object):
    adapts(ISample)
    implements(IOrderableSchemaExtender)

    fields = [
        ExtReferenceField(
            'Project',
            required=True,
            allowed_types=('Project',),
            relationship='SampleProject',
            mode="rw",
            read_permission=permissions.View,
            write_permission=permissions.ModifyPortalContent,
            widget=bika_ReferenceWidget(
                label=_("Project"),
                description=_("Select the project of the sample."),
                render_own_label=True,
                size=50,
                # catalog_name='bika_catalog',
                # visible=False,
                visible={
                    'edit': 'visible',
                    'view': 'visible',
                    'header_table': 'visible',
                    'sample_registered': {'view': 'visible', 'edit': 'visible'},
                    'sample_due': {'view': 'visible', 'edit': 'visible'},
                    'sampled': {'view': 'visible', 'edit': 'invisible'},
                    'sample_received': {'view': 'visible', 'edit': 'visible'},
                    'expired': {'view': 'visible', 'edit': 'invisible'},
                    'disposed': {'view': 'visible', 'edit': 'invisible'},
                },
                base_query={'inactive_state': 'active'},
                colModel=[{"columnName": "UID", "hidden": True},
                          {"columnName": "Title", "align": "left", "width": "60", "label": "Title"},
                          {"columnName": "Description", "align": "left", "label": "Description", "width": "40"}
                          ],
                showOn=True,
            )
        ),

        ExtBooleanField(
            'WillReturnFromShipment',
            default=False,
            # write_permission = ManageClients,
            widget=BooleanWidget(
                label=_("Will Return From Shipment"),
                description=_("Indicates if sample will return if shipped."),
                visible={'edit': 'invisible',
                         'view': 'invisible',
                         'header_table': 'invisible',
                         'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                         },
                render_own_label=True,
            ),
        ),
        ExtReferenceField(
            'Kit',
            vocabulary_display_path_bound=sys.maxint,
            allowed_types=('Kit',),
            relationship='SampleKit',
            referenceClass=HoldingReference,
            widget=bika_ReferenceWidget(
                label=_("Kit"),
                catalog_name='bika_catalog',
                # visible=False,
                visible={'view': 'visible',
                         'edit': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'visible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                showOn=True,
                render_own_label = True,
                description=_("Select the kit of the sample if exists."),
            ),
        ),
        ExtReferenceField(
            'SampleType',
            required=1,
            vocabulary_display_path_bound=sys.maxsize,
            allowed_types=('SampleType',),
            relationship='SampleSampleType',
            referenceClass=HoldingReference,
            mode="rw",
            read_permission=permissions.View,
            write_permission=permissions.ModifyPortalContent,
            widget=bika_ReferenceWidget(
                label=_("Sample Type"),
                render_own_label=True,
                size=60,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'to_be_sampled': {'view': 'visible', 'edit': 'invisible'},
                         'scheduled_sampling': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'to_be_preserved': {'view': 'visible', 'edit': 'invisible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         'rejected': {'view': 'visible', 'edit': 'invisible'},
                         },
                catalog_name='bika_setup_catalog',
                base_query={'inactive_state': 'active'},
                colModel=[{'columnName': 'UID', 'hidden': True},
                          {'columnName': 'Title', "align": "left", 'width': '60', 'label': _('Title')},
                          {"columnName": "Description", "align": "left", "label": "Description", "width": "40"}
                          ],
                showOn=True,
            ),
        ),
        ExtReferenceField(
            'Batch',
            vocabulary_display_path_bound=sys.maxint,
            allowed_types=('SampleBatch',),
            relationship='SampleBatch',
            referenceClass=HoldingReference,
            widget=bika_ReferenceWidget(
                label=_("Batch"),
                catalog_name='bika_catalog',
                visible={'view': 'invisible',
                         'edit': 'invisible',
                         'header_table': 'invisible',
                         'sample_registered': {'view': 'invisible', 'edit': 'invisible'},
                         'sample_due': {'view': 'invisible', 'edit': 'invisible'},
                         'sample_received': {'view': 'invisible', 'edit': 'invisible'},
                         },
                showOn=True,
                render_own_label=True,
                description=_("Batch."),
            ),
        ),
        ExtReferenceField(
            'StorageLocation',
            #required=True,
            allowed_types=('StoragePosition',),
            relationship='ItemStorageLocation',
            widget=bika_ReferenceWidget(
                label=_("Storage Location"),
                description=_("Location where item is kept"),
                size=50,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                catalog_name='portal_catalog',
                showOn=True,
                render_own_label=True,
                base_query={'inactive_state': 'active',
                            'review_state': 'available',
                            'object_provides': ISampleStorageLocation.__identifier__},
                colModel=[{'columnName': 'UID', 'hidden': True},
                          {'columnName': 'Title', "align": "left", 'width': '100', 'label': _('Title')}
                          ],
            )
        ),
        ExtReferenceField(
            'ReservedLocation',
            # required=True,
            allowed_types=('StoragePosition',),
            relationship='ReservedItemStorageLocation',
            widget=bika_ReferenceWidget(
                label=_("Reserved Storage Location"),
                description=_("Location reserved for this sample"),
                size=40,
                visible={'edit': 'invisible',
                         'view': 'invisible'},
                catalog_name='portal_catalog',
            )
        ),
        ExtReferenceField(
            'SampleCondition',
            allowed_types=('SampleCondition',),
            relationship='SampleSampleCondition',
            widget=bika_ReferenceWidget(
                visible=False,
            ),
        ),
        ExtStringField(
            'SubjectID',
            required=1,
            searchable=True,
            widget=StringWidget(
                label=_("Subject ID"),
                description=_("Human-subject ID the specimen is taken from."),
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                render_own_label=True,
            )
        ),
        ExtStringField(
            'Barcode',
            required=0,
            searchable=True,
            widget=StringWidget(
                label=_("Barcode"),
                description=_("Biospecimen barcode."),
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                render_own_label=True,
            )
        ),
        ExtFixedPointField(
            'Volume',
            required=1,
            default="0.00",
            widget=DecimalWidget(
                label=_("Volume"),
                size=15,
                description=_("The volume of the biospecimen taken from the subject. For placenta parent biospecimen, enter Placenta Weight here."),
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                render_own_label=True,
            )
        ),
        ExtStringField(
            'ChangeUserName',
            widget=StringWidget(
                label=_('ChangeUserName'),
                description=_('The user who created or last made a change to this sample.'),
                visible={'view': 'invisible', 'edit': 'invisible'}
            )
        ),
        ExtDateTimeField(
            'ChangeDateTime',
            widget=StringWidget(
                label=_('ChangeDateTime'),
                description=_('The date and time when the sample was created or last updated.'),
                visible={'view': 'invisible', 'edit': 'invisible'}
            )
        ),
        ExtStringField(
            'Unit',
            required=1,
            default="",
            # vocabulary=UnitsVocabulary(),
            vocabulary='getUnits',
            # widget=SelectionWidget(
            widget=BikaSelectionWidget(
                format='select',
                label=_("Unit"),
                description=_('The unit for Volume'),
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                render_own_label=True,
                showOn=True,
            )
        ),
        ExtStringField(
            'BabyNumber',
            default="0",
            vocabulary='getBabyNumber',
            # widget=SelectionWidget(
            widget=BikaSelectionWidget(
                format='select',
                label=_("Baby No. (if applicable)"),
                description=_('Indicate baby number if the sample is collected from a baby.'),
                visible={'edit': 'visible',
                         'view': 'visible',
                         },
                render_own_label=True,
                showOn=True,
            )
        ),
        ExtReferenceField(
            'LinkedSample',
            vocabulary_display_path_bound=sys.maxsize,
            multiValue=1,
            allowed_types=('Sample',),
            relationship='SampleSample',
            referenceClass=HoldingReference,
            mode="rw",
            read_permission=permissions.View,
            write_permission=permissions.ModifyPortalContent,
            widget=bika_ReferenceWidget(
                label=_("Parent Biospecimen"),
                description=_("Create an Aliquot of the biospecimen selected."),
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'visible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                showOn=True,
                render_own_label=True,
                base_query={
                    'cancellation_state': 'active',
                    'review_state': 'sample_received'
                },
                colModel=[{'columnName': 'UID', 'hidden': True},
                          {'columnName': 'Title', 'width': '50', 'label': _('Title')},
                          {"columnName": "LocationTitle", "align": "left", "label": "Location", "width": "50"}
                          ],
            ),
        ),
        ExtDateTimeField(
            'DateCreated',
            mode="rw",
            read_permission=permissions.View,
            write_permission=permissions.ModifyPortalContent,
            widget=DateTimeWidget(
                label=_("Date Created"),
                description=_("Define when the sample has been created."),
                show_time=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'invisible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                render_own_label=True,
            ),
        ),
        ExtComputedField(
            'LocationTitle',
            searchable=True,
            expression="here.getStorageLocation() and here.getStorageLocation().Title() or ''",
            widget=ComputedWidget(
                visible=False,
            ),
        ),
        ExtDateTimeField(
            'FrozenTime',
            mode="rw",
            read_permission=permissions.View,
            write_permission=permissions.ModifyPortalContent,
            widget=DateTimeWidget(
                label=_("Frozen Time"),
                description=_("Define when this aliquot was frozen."),
                show_time=True,
                visible={'edit': 'visible',
                         'view': 'visible',
                         'header_table': 'invisible',
                         'sample_registered': {'view': 'visible', 'edit': 'visible'},
                         'sample_due': {'view': 'visible', 'edit': 'visible'},
                         'sampled': {'view': 'visible', 'edit': 'invisible'},
                         'sample_received': {'view': 'visible', 'edit': 'visible'},
                         'expired': {'view': 'visible', 'edit': 'invisible'},
                         'disposed': {'view': 'visible', 'edit': 'invisible'},
                         },
                render_own_label=True,
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        sch = schematas['default']
        sch.remove('Project')
        sch.remove('Kit')
        sch.insert(sch.index('SampleType'), 'Project')
        sch.insert(sch.index('SampleType'), 'Kit')
        return schematas

    def getFields(self):
        return self.fields

class SampleSchemaModifier(object):
    adapts(ISample)
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        schema['SamplingDate'].widget.description = "Define when the samples are collected."
        return schema


class Sample(BaseSample):
    """ Inherits from bika.lims.content.sample
    """
    _at_rename_after_creation = True

    def _renameAfterCreation(self, check_auto_id=False):
        from baobab.lims.idserver import renameAfterCreation
        renameAfterCreation(self)

    def getProjectUID(self):
        if self.aq_parent.Title() == 'Biospecimens':
            return self.getField('Project').get(self).UID()
        else:
            return self.aq_parent.UID()

    def getUnits(self):
        return ['', 'ul', 'ml', 'mg', 'g', 'mm', 'swabs', 'pieces', 'each']

    def getLastARNumber(self):
        ARs = self.getBackReferences("AnalysisRequestSample")
        prefix = self.getId() + '-' + self.getSampleType().getPrefix()
        ar_ids = sorted([AR.id for AR in ARs if AR.id.startswith(prefix)])
        try:
            last_ar_number = int(ar_ids[-1].split("-R")[-1])
        except:
            return 0
        return last_ar_number

    def update_box_status(self, location):
        box = location.aq_parent
        state = self.portal_workflow.getInfoFor(box, 'review_state')
        free_pos = box.get_free_positions()
        if not free_pos and state == 'available':
            doActionFor(box, 'occupy')
        elif free_pos and state == 'occupied':
            doActionFor(box, 'liberate')

    def workflow_script_receive(self):
        super(Sample, self).workflow_script_receive()

        self.getField('WillReturnFromShipment').set(self, False)
        location = self.getField('ReservedLocation').get(self)
        review_state = self.portal_workflow.getInfoFor(location, 'review_state')

        if location is not None:
            if review_state in ('reserved', 'available'):
                self.setStorageLocation(location)
                doActionFor(location, 'occupy')
                self.update_box_status(location)
            else:
                raise ValueError('Location %s is already occupied.' % location.Title())

            self.getField('ReservedLocation').set(self, None)
            self.reindexObject()

    def getBabyNumber(self):
        return ['0', '1', '2', '3']

from Products.Archetypes import atapi
from bika.lims.config import PROJECTNAME
# Overrides type bika.lims.content.sample
atapi.registerType(Sample, PROJECTNAME)
