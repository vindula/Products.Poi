# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Archetypes.atapi import DisplayList

from Products.Poi.content.PoiIssue import PoiIssue
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from AccessControl.SecurityManagement import newSecurityManager, getSecurityManager, setSecurityManager
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

from Products.Poi import PoiMessageFactory as _

from vindula.network.browser.utils import ToolBox

class CreateIssue(BrowserView):
    
    index = ViewPageTemplateFile("vindula_poi_issue.pt")
    
    def __call__(self):
        self.request.set('ajax_include_head',True)
        self.request.set('ajax_load',True)
        
        return self.index()

    # define se aparece ou nao as mensagens e marcacoes de erros  
    def field_class(self, errors, field_name):
        if errors is not None:
            if errors.get(field_name, None) is not None:
                return 'field error'                   
            else:
                 return 'field'
        else:
              return 'field'

    def getTracker(self):
        #return self.context
        self.tool = ToolBox(self)
        portal_membership = self.tool.membership
        
        key = self.request.form.get('key','')
        
        query = {}
        obj = None
        user_admin = portal_membership.getMemberById('admin')  
        
        # stash the existing security manager so we can restore it
        old_security_manager = getSecurityManager()
        
        # create a new context, as the owner of the folder
        newSecurityManager(self.request,user_admin)
        
        query['portal_type'] = ['ClienteNetwork']
        items = self.tool.busca_catalog(**query)
        for item in items:
            item = item.getObject()
            if item.getChaveVindula() == key:
                poi = item.getFolderContents(contentFilter={'portal_type' : 'PoiTracker'})
                if poi:
                    obj = poi[0].getObject()
        
        # restore the original context
        setSecurityManager(old_security_manager)  
        
        return obj
        
        

    def getAreasVocab(self):
        """
        Get the available areas as a DispayList.
        """
        tracker = self.getTracker()
        L = []
        field = tracker.getField('availableAreas')
        area = field.getAsDisplayList(tracker)

        
        for iten in area:
            L.append({'id':iten,'label':area.getValue(iten)})
        
        return L
    
    def getIssueTypesVocab(self):
        """
        Get the issue types available as a DisplayList.
        """
        tracker = self.getTracker()
        field = tracker.getField('availableIssueTypes')
        
        issuesTypes = field.getAsDisplayList(tracker)
        L = []
        for iten in issuesTypes:
            L.append({'id':iten,'label':issuesTypes.getValue(iten)})
            
        return L 
    
    def getAvailableSeverities(self):
        tracker = self.getTracker()
        severitys = tracker.getAvailableSeverities()
        L = []
        for iten in severitys:
            L.append({'id':iten,'label':iten})
        
        return L
        

    def getManagersVocab(self, strict=False):
        """
        Get the managers available as a DisplayList. The first item is 'None',
        with a key of '(UNASSIGNED)'.

        Note, we now also allow Technicians here, unless we are called
        with 'strict' is True.
        """
        tracker = self.getTracker()
        vocab = DisplayList()
        #vocab.add('(UNASSIGNED)', _(u'None'))
        for item in tracker.getManagers():
            vocab.add(item, item)
        if not strict:
            for item in tracker.getTechnicians():
                vocab.add(item, item)

        L = []
        for iten in vocab:
            L.append({'id':iten,'label':vocab.getValue(iten)})
               
        return L


    def createIssue(self, form):
        tracker = self.getTracker()
        nome = form.get('title')
        cliente_obj = tracker.aq_parent
        
        count = 0
        normalizer = getUtility(IIDNormalizer)
        
        nome_arquivo = nome_org = normalizer.normalize(unicode(nome, 'utf-8'))
        while nome_arquivo in tracker:
            count +=1
            nome_arquivo = nome_org + '-' + str(count) 

        portal_member = self.context.portal_membership
        
        super_user = cliente_obj.getUsuarioSistema()
        user_admin = portal_member.getMemberById(super_user)  
         
        # stash the existing security manager so we can restore it
        old_security_manager = getSecurityManager()

        # create a new context, as the owner of the folder
        newSecurityManager(self.request,user_admin)

        objeto = {'type_name':'PoiIssue',
                   'id': nome_arquivo,
                   'title':form.get('title',''),
                   'details':form.get('details',''),
                   'area':form.get('area',''),
                   'issueType':form.get('issueType',''),
                   'severity':form.get('severity',''),
                   'responsibleManager':form.get('responsibleManager',''),
                   'contactEmail':form.get('contactEmail',''),
                   }
         
         
        issue_created = tracker.invokeFactory(**objeto)   
        issue_created = tracker.get(issue_created, '')
        
        #Muda o status do ticket para aberto
        portal = tracker.portal_url.getPortalObject()
        portal_workflow = getToolByName(portal, 'portal_workflow')
        portal_workflow.doActionFor(issue_created, 'post')

        # restore the original context
        setSecurityManager(old_security_manager)     

        return issue_created


    def default(self):
        self.errors = {}
        form = self.request.form
        self.authorized = True

        if not self.getTracker():
            self.authorized = False
        
        
        campos = ['title','details','area','issueType',
                  'severity','contactEmail'] #'responsibleManager',
        
        if 'form.submited' in form.keys():
            for item in campos:
                if not form.get(item):
                    self.errors[item] = 'Este Campo não pode ficar em branco.'
                
            if not self.errors:
                obj = self.createIssue(form)
                
                url = obj.portal_url()+'/vindula_poi_issue?key='+form.get('key','')
#                self.request.set('ajax_load',True)
#                self.request.set('ajax_include_head',True)
                
                IStatusMessage(self.request).addStatusMessage(_(u"Obrigado, o seu ticket foi criado com sucesso."), "info")
                self.request.response.redirect(url, lock=True)
            
        return ''
