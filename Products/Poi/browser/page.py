# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.Archetypes.atapi import DisplayList

from Products.Poi.content.PoiIssue import PoiIssue
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from AccessControl.SecurityManagement import newSecurityManager, getSecurityManager, setSecurityManager
from zope.component import getUtility
from plone.i18n.normalizer.interfaces import IIDNormalizer


from Products.Poi import PoiMessageFactory as _






class CreateIssue(BrowserView):

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
        return self.context

    def getAreasVocab(self):
        """
        Get the available areas as a DispayList.
        """
        tracker = self.getTracker()
        field = tracker.getField('availableAreas')
        area = field.getAsDisplayList(tracker)

        L = []
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
        
        count = 0
        normalizer = getUtility(IIDNormalizer)
        
        nome_arquivo = nome_org = normalizer.normalize(unicode(nome, 'utf-8'))
        while nome_arquivo in tracker:
            count +=1
            nome_arquivo = nome_org + '-' + str(count) 

        portal_member = self.context.portal_membership
        user_admin = portal_member.getMemberById('admin')  
         
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
         
         
        tracker.invokeFactory(**objeto)   

        obj = tracker.get(nome_arquivo,'')

        # restore the original context
        setSecurityManager(old_security_manager)     

        return obj


    def default(self):
        self.errors = {}
        form = self.request.form
        
        campos = ['title','details','area','issueType',
                  'severity','contactEmail'] #'responsibleManager',
        
        if 'form.submited' in form.keys():
            for item in campos:
                if not form.get(item):
                    self.errors[item] = 'Este Campo não pode ficar em branco.'
                
            if not self.errors:
                obj = self.createIssue(form)
                
                url = obj.absolute_url()
                self.request.set('ajax_load',True)
                self.request.set('ajax_include_head',True)
                
                self.request.response.redirect(url, lock=True)
            
        return ''
