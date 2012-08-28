# -*- coding: utf-8 -*-
""" Liberiun Technologies Sistemas de Informação Ltda. """
""" Produto:                 """

from zope.interface import implements
from zope.formlib import form 
from zope import schema
from Products.Poi import PoiMessageFactory as _
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.app.component.hooks import getSite

class IPortletPortletPoiTracker(IPortletDataProvider):
      
    """A portlet
    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    title_portlet = schema.TextLine(title=_(u"Título"),
                                  description=_(u"Título que aparecerá no cabeçalho do portlet."),
                                  required=True)
    
    
    description = schema.Text(title=unicode("Descrição", 'utf-8'),
                              description=unicode("Adicione uma descrição para os usuarios sobre mais informações para adição de ocorrências", 'utf-8'),
                              required=False)
    
    
    poi_tracker = schema.Choice(title=_(u"Gerenciador de Ocorrências"),
                                description=_(u"Selecione o gerenciador de ocorrências, onde serão adicionadas as ocorrêcias."),
                                required=True,
                                source=SearchableTextSourceBinder({'portal_type': 'PoiTracker'},
                                                                  default_query='path:')
                                )
    
    

class Assignment(base.Assignment):
    """Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(IPortletPortletPoiTracker)
    
    title_portlet=u''
    poi_tracker = None
    
    # TODO: Add keyword parameters for configurable parameters here
    def __init__(self, title_portlet=u'', poi_tracker=None,description=u''):
       self.title_portlet = title_portlet
       self.poi_tracker = poi_tracker
       self.description = description

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Portlet Gerenciar Ocorrências"
    
class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    render = ViewPageTemplateFile('portletPoiTracker.pt')            
    
    def get_title(self):
        return self.data.title_portlet
    
    def get_description(self):
        return self.data.description
    
    def get_tracker(self):
        return self.data.poi_tracker
    
    def getObjectPoi(self):
        x = 'getSite()'
        tmp = self.data.poi_tracker.split('/')
        for i in tmp[1:]:
            x += "['"+i+"']"
        
        obj = eval(x) 
        return obj
        
class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    
    form_fields = form.Fields(IPortletPortletPoiTracker)
    form_fields['poi_tracker'].custom_widget = UberSelectionWidget
    form_fields['description'].custom_widget = WYSIWYGWidget
    
    def create(self, data):
       return Assignment(**data)
   
class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IPortletPortletPoiTracker)
    form_fields['poi_tracker'].custom_widget = UberSelectionWidget
    form_fields['description'].custom_widget = WYSIWYGWidget