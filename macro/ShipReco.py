#!/usr/bin/env python
from argparse import ArgumentParser

withHists = True
pidProton = False  # if true, take truth, if False fake with pion mass

import resource
import ROOT, os, sys
import numpy as np
import global_variables
import rootUtils as ut
import shipunit as u
import shipRoot_conf
import shutil
import time

def mem_monitor():
    pid = os.getpid()
    with open(os.path.join("/proc", str(pid), "status")) as f:
        lines = f.readlines()
    _vmsize = [l for l in lines if l.startswith("VmSize")][0]
    vmsize = int(_vmsize.split()[1])
    pmsize = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print("memory: virtual = %5.2F MB  physical = %5.2F MB" % (vmsize/1.0E3, pmsize/1.0E3))

shipRoot_conf.configure()

parser = ArgumentParser()

parser.add_argument("-f", "--inputFile", dest="inputFile", help="Input file", required=True)
parser.add_argument("-n", "--nEvents", dest="nEvents", help="Number of events", default=999999, type=int)
parser.add_argument("-g", "--geoFile", dest="geoFile", help="Geometry file", required=True)
parser.add_argument("-d", "--directory", dest="directory", help="Directory path", default='.')
parser.add_argument("--noVertexing", dest="noVertexing", help="Disable vertexing", action="store_true")
parser.add_argument("--noStrawSmearing", dest="withNoStrawSmearing", help="Disable straw smearing", action="store_true")
parser.add_argument("--withT0", dest="withT0", help="Enable T0 correction", action="store_true")
parser.add_argument("--ecalDebugDraw", dest="EcalDebugDraw", help="ECAL debug draw", action="store_true")
parser.add_argument("--saveDisk", dest="saveDisk", help="Remove input after reco", action="store_true")
parser.add_argument("-i", "--firstEvent", dest="firstEvent", help="Start at event", default=0, type=int)
parser.add_argument("--realPR", dest="realPR", help="Real pattern reco method", choices=['FH', 'AR', 'TemplateMatching'], default='')
parser.add_argument("-dy", dest="dy", help="Max Y height", default=None, type=int)
parser.add_argument("--Debug", dest="Debug", help="Enable debug mode", action="store_true")

options = parser.parse_args()
vertexing = not options.noVertexing

if options.EcalDebugDraw:
    ROOT.gSystem.Load("libASImage")

input_path = os.path.join(options.directory, options.inputFile)
geo_path = os.path.join(options.directory, options.geoFile)
outFile = input_path.replace('.root', '_rec.root')

# Load geometry
fgeo = ROOT.TFile.Open(geo_path)
geoMat = ROOT.genfit.TGeoMaterialInterface()

from ShipGeoConfig import ConfigRegistry
from rootpyPickler import Unpickler
upkl = Unpickler(fgeo)
ShipGeo = upkl.load('ShipGeo')
ecalGeoFile = ShipGeo.ecal.File

h, log = {}, {}
if withHists:
    ut.bookHist(h, 'distu', 'distance to wire', 100, 0., 5.)
    ut.bookHist(h, 'distv', 'distance to wire', 100, 0., 5.)
    ut.bookHist(h, 'disty', 'distance to wire', 100, 0., 5.)
    ut.bookHist(h, 'nmeas', 'nr measurements', 100, 0., 50.)
    ut.bookHist(h, 'chi2', 'Chi2/DOF', 100, 0., 20.)
    ut.bookHist(h, 'nGoodTracks', 'nGoodTracks', 10, 0., 10)
    ut.bookHist(h, 'ntracks', 'ntracks', 10, 0., 10)
    ut.bookHist(h,'nrec','nrec',10,0.,10)

import shipDet_conf
run = ROOT.FairRunSim()
run.SetName("TGeant4")
run.SetSink(ROOT.FairRootFileSink(ROOT.TMemFile('output', 'recreate')))
run.SetUserConfig("g4Config_basic.C")
rtdb = run.GetRuntimeDb()
modules = shipDet_conf.configure(run, ShipGeo)
fgeo.Get("FAIRGeom")

import geomGeant4
fieldMaker = geomGeant4.addVMCFields(ShipGeo, '', True, withVirtualMC=False) if hasattr(ShipGeo.Bfield, "fieldMap") else None

# Global vars
global_variables.debug = options.Debug
global_variables.fieldMaker = fieldMaker
global_variables.pidProton = pidProton
global_variables.withT0 = options.withT0
global_variables.realPR = options.realPR
global_variables.vertexing = vertexing
global_variables.ecalGeoFile = ecalGeoFile
global_variables.ShipGeo = ShipGeo
global_variables.modules = modules
global_variables.EcalDebugDraw = options.EcalDebugDraw
global_variables.withNoStrawSmearing = options.withNoStrawSmearing
global_variables.h = h
global_variables.log = log
global_variables.iEvent = 0

# Run reconstruction
import shipDigiReco

SHiP = shipDigiReco.ShipDigiReco(outFile, fgeo)
options.nEvents = min(SHiP.sTree.GetEntries(), options.nEvents)

def findReconstructible(sTree,nhits=25,nstations=3):
  hitspertrack = {} # hit counter per station and particle (trID)
  nRecTracks = 0
  for hit in sTree.strawtubesPoint:
    trID = hit.GetTrackID()
    if trID not in hitspertrack: hitspertrack[trID] = [0,0,0,0]
    detID = hit.GetDetectorID()
    # increment hit counter for this station and this particle (trID)
    hitspertrack[trID][ int(detID//10**6) - 1] += 1  # operator "//" is a Floor Division
    # check requirement for particle being "reconstructible" (customizable definition):
  for trID in hitspertrack:
    countstations = 0
    counthits = 0
    for st in [0,1,2,3]:
        if hitspertrack[trID][st] > 0 :
            countstations += 1
            counthits += hitspertrack[trID][st]
    # this is the requirement:
    if countstations >= nstations and counthits >= nhits:
        nRecTracks += 1
        if global_variables.debug:
          print(" event %i"%global_variables.iEvent+" reconstructible track PDG=",sTree.MCTrack[trID].GetPdgCode()," trID = ",trID,hitspertrack[trID])
  return nRecTracks

for global_variables.iEvent in range(options.firstEvent, options.nEvents):
    if global_variables.iEvent % 1000 == 0 or global_variables.debug:
        print('Event', global_variables.iEvent)
    rc = SHiP.sTree.GetEvent(global_variables.iEvent)
    temp = findReconstructible(SHiP.sTree)
    if temp>0:
        print('event ', global_variables.iEvent)
        print(f' Number of event expected to be reconstructed: {temp}')
    SHiP.digitize()
    SHiP.reconstruct()

SHiP.finish()
ut.writeHists(global_variables.h,"recohists.root")
