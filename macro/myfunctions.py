from __future__ import print_function
import shipunit as u
#import ROOT 
import numpy as numpy
from array import array
import math
import os
import sys
#from math import *
import ROOT

#############################################################
def isthiscritical(collection, Xcrit, Ycrit, muonsonly=False):
    # watch out for neutrinos if muonsonly=False
    iscritical  = False
    for v in collection:
        if v: # why this ??
           abspid = 0
           if muonsonly: abspid = abs(v.PdgCode())
           if (not(muonsonly)) or (muonsonly and abspid == 13):
              if (abs(v.GetX())<Xcrit and abs(v.GetY())<Ycrit):
                 iscritical = True
                 break
    return iscritical

#############################################################
def myprint(fileptr, line):
    print(line)
    fileptr.write(line+'\n')

#############################################################
class TestTask(ROOT.FairTask):
      "user task: for testing"
      def Init(self):
          self.countevents = 0
          print("TestTask(): Init()  countevents = %i"%self.countevents)
          return ROOT.kSUCCESS
      def Exec(self,opt=''):
          self.countevents += 1
          print("TestTask(): Exec()  countevents = %i"%self.countevents)
      def Finish(self):
          print("TestTask(): Finish()  countevents = %i"%self.countevents)
      def InitTask(self):
          print("TestTask(): InitTask()  countevents = %i"%self.countevents)
      def ExecuteTask(self):
          self.countevents += 1
          print("TestTask(): ExecuteTask()  countevents = %i"%self.countevents)
      def FinishEvent(self):
          print("TestTask(): FinishEvent()  countevents = %i"%self.countevents)
          run.SetStoreTraj(ROOT.kTRUE)
          # Set cuts for storing the trajectories, can only be done after initialization of run (?!)
          trajFilter = ROOT.FairTrajFilter.Instance()
          trajFilter.SetStepSizeCut(1*u.mm);
          trajFilter.SetVertexCut(-20*u.m, -20*u.m,ship_geo.target.z0-1*u.m, 20*u.m, 20*u.m, 200.*u.m)
          trajFilter.SetMomentumCutP(0.1*u.GeV)
          trajFilter.SetEnergyCut(0., 400.*u.GeV)
          trajFilter.SetStorePrimaries(ROOT.kTRUE)
          trajFilter.SetStoreSecondaries(ROOT.kTRUE)

#############################################################
class SaveByCriterionTask(ROOT.FairTask):
      "user task: saveOnlyCriticalEvents"

      def InitializeMembers(self,direc,colnames,Xcrit,Ycrit,samplesize=100,MuonHitsOnly=True):
          self.logging = open(direc+'/saveByCriterion.log','w')
          myprint(self.logging, "SaveByCriterionTask(): will save events ")
          self.ioman = ROOT.FairRootManager.Instance()
          self.colnames = colnames
          self.Xcrit = Xcrit # cm 
          self.Ycrit = Ycrit # cm
          myprint(self.logging, "SaveByCriterionTask(): using only these critical detectors (with Xcrit and Ycrit in cm):")
          for kk in range(0,len(self.colnames)): myprint(self.logging, " ... colname = "+self.colnames[kk]+" %f"%self.Xcrit[kk]+" %f"%self.Ycrit[kk])
          if MuonHitsOnly:  myprint(self.logging, "SaveByCriterionTask(): consider only muon hits")
          self.hitcollections = []
          for colname in self.colnames: self.hitcollections.append( self.ioman.GetObject(colname) )
          self.samplesize = samplesize
          self.MuonHitsOnly = MuonHitsOnly
          # useful counters:
          self.allevents_counter      = 0
          self.savedevents_counter    = 0
          self.criticalevents_counter = 0
          self.firstevent  = True
     #def Init(self):
     #    print("Init::SaveByCriterionTask(): will save events")
     #    print("Init::SaveByCriterionTask(): using only these critical detectors (with Xcrit and Ycrit in cm):")
     #    for kk in range(0,len(self.colnames)): print(" ... colname = "+self.colnames[kk]+" %f"%self.Xcrit[kk]+" %f"%self.Ycrit[kk])
     #    if self.MuonHitsOnly: print("Init::SaveByCriterionTask(): consider only muon hits")
     #    return ROOT.kSUCCESS
     #def InitTask(self):
     #    print("InitTask::SaveByCriterionTask(): call Init()")
     #    return self.Init(self)
      def FinishMembers(self):
          myprint(self.logging, "SaveByCriterionTask(): finishing, closing log file.")
          myprint(self.logging, "  events looped over     = %i"%self.allevents_counter)
          myprint(self.logging, "  criticalevents_counter = %i"%self.criticalevents_counter)
          myprint(self.logging, "  savedevents_counter    = %i"%self.savedevents_counter)
          self.logging.close()
     #def FinishEvent(self):
     #    print("FinishEvent::SaveByCriterionTask(): call FinishMembers()")
     #    self.FinishMembers()
     #def Finish(self):
     #    print("Finish::SaveByCriterionTask(): call FinishMembers()")
     #    self.FinishMembers()
      def Exec(self,opt):
          self.allevents_counter += 1
         #if self.allevents_counter == 1: print("Exec::SaveByCriterionTask(): this is the first call to Exec()")
          mcApp = ROOT.FairMCApplication.Instance()
         #MCTracks = ioman.GetObject("MCTrack")
         #print('MyTask: Hello',opt,MCTracks.GetEntries())
         #fMC = ROOT.TVirtualMC.GetMC()
         #for ncrit in ncritlist: colname = colnames[ncrit]
         #hitcollection = eval("t." + colname)
         #hitcollection = ioman.GetObject("sco1_Point")
         #Xcrit, Ycrit = 30.0,30.0
         #criticalevent = isthiscritical(hitcollection, 51.0, 31.0, muonsonly=True)
          criticalevent = False
          if self.firstevent: 
             myprint(self.logging,"1st event, inspect colnames: ")
             for kk in range(0,len(self.colnames)): myprint(self.logging,self.colnames[kk])
          for kk in range(0,len(self.colnames)):
              hitcollection = self.ioman.GetObject(self.colnames[kk]) #hitcollection = self.hitcollections[kk]
              if self.firstevent: 
                 if hitcollection: myprint(self.logging,"1st event, hit collection "+self.colnames[kk]+" contains %i"%hitcollection.GetEntries()+" entries")
                 else:             myprint(self.logging,"1st event, hit collection "+self.colnames[kk]+" is just None") 
              if hitcollection:
                 criticalevent = isthiscritical(hitcollection, self.Xcrit[kk], self.Ycrit[kk], muonsonly=self.MuonHitsOnly)
                 if criticalevent: 
                    EventHeader = self.ioman.GetObject("MCEventHeader.")
                    EventID = EventHeader.GetEventID()
                    myprint(self.logging, "  save critical, event = %i"%self.allevents_counter+", EventID = %i"%EventID)
                    self.criticalevents_counter += 1
                    break
          if not criticalevent:
             mcApp.SetSaveCurrentEvent(ROOT.kFALSE);
             #print('SaveByCriterionTask(): not criticalevent, I do not save.')
          else:
             mcApp.SetSaveCurrentEvent(ROOT.kTRUE);
             self.savedevents_counter += 1
             #print('SaveByCriterionTask(): yes criticalevent or random, I save.')
             #fMC.StopRun()
          if self.firstevent: self.firstevent = False
     #def ExecuteTask(self,opt):
     #    print("ExecuteTask::SaveByCriterionTask(): call Exec()")
     #    self.Exec(opt)


