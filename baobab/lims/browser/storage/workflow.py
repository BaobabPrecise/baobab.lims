from Products.Archetypes.exceptions import ReferenceException
from Products.CMFCore.utils import getToolByName
from bika.lims.browser.bika_listing import WorkflowAction
import plone


class StorageWorkflowAction(WorkflowAction):

    def __call__(self):
        form = self.request.form
        plone.protect.CheckAuthenticator(form)
        action, _ = WorkflowAction._get_form_workflow_action(self)
        if type(action) in (list, tuple):
            action = action[0]

        # Call out to the workflow action method
        method_name = 'workflow_action_' + action
        method = getattr(self, method_name, False)
        if method:
            method()
        else:
            WorkflowAction.__call__(self)

    def workflow_action_deactivate(self):
        context = self.context
        selected_elements = WorkflowAction._get_selected_items(self)
        catalog = getToolByName(self, 'portal_catalog')
        # import pdb;pdb.set_trace()
        for uid in selected_elements.keys():
            try:
                obj = selected_elements.get(uid, None)
                units = []
                if obj.portal_type in ['ManagedStorage', 'UnmanagedStorage']:
                    units.append(obj)
                else:
                    unit_path = '/'.join(obj.getPhysicalPath())
                    brains = catalog(portal_type=['StorageUnit', 'UnmanagedStorage', 'ManagedStorage'],
                                    path={'query': unit_path, 'level': 0})
                    units += [brain.getObject() for brain in brains]
                for unit in units:
                    review_state = context.portal_workflow.getInfoFor(unit, 'inactive_state')
                    if review_state == 'active':
                        context.portal_workflow.doActionFor(unit, 'deactivate')

            except ReferenceException:
                pass
            
        self.request.response.redirect(context.absolute_url())
