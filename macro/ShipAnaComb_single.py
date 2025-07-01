# -*- coding: utf-8 -*-
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import sys
import ROOT
import ctypes
import rootUtils as ut
import shipunit as u
from ShipGeoConfig import ConfigRegistry
from rootpyPickler import Unpickler
from decorators import *
import shipRoot_conf
from argparse import ArgumentParser
import geomGeant4
import shipDet_conf
import TrackExtrapolateTool
from array import array

shipRoot_conf.configure()
PDG = ROOT.TDatabasePDG.Instance()

parser = ArgumentParser()

parser.add_argument("-f", "--inputFile", dest="inputFile", help="Input file", required=True)
parser.add_argument("-n", "--nEvents",   dest="nEvents",   help="Number of events to analyze", required=False,  default=9999999999,type=int)
parser.add_argument("-g", "--geoFile",   dest="geoFile",   help="ROOT geofile", required=True)
parser.add_argument("--Debug",           dest="Debug", help="Switch on debugging", required=False, action="store_true")
# added by massi: Assumes Z target starts around -60 m , not 0 m ... Decay volume's center at about Z = 0.
parser.add_argument("-p", "--doPlots",   dest="doPlots", help="also make plots", required=False, action="store_true")
parser.add_argument("--Zubt",           help="Z UBT / cm",      default=3270.0 , type=float)  #dest="Zubt",    
parser.add_argument("--showB",         dest="showB", help="show B spectrometer", required=False, action="store_true")
parser.add_argument("--fiducialCut",   dest="fiducialCut", help="fiducialCut on/off", required=False, action="store_true")
parser.add_argument("--chi2CutOff",    help="chi2CutOff",  default=4.0  , type=float) 
parser.add_argument("--measCutFK",     help="measCutFK",  default=25  , type=int) 
parser.add_argument("--measCutPR",     help="measCutPR",  default=22  , type=int) 
parser.add_argument("--docaCut",       help="docaCut / cm",    default=2.0 , type=float) 
options = parser.parse_args()

# set some global variables:
fiducialCut = options.fiducialCut     # fiducialCut = False
chi2CutOff  = options.chi2CutOff      # chi2CutOff  = 4.
measCutFK   = options.measCutFK       # measCutFK  = 25
measCutPR   = options.measCutPR       # measCutPR  = 22
docaCut     = options.docaCut         # docaCut  = 2.
Debug   = options.Debug
doPlots = options.doPlots
showB = options.showB
Zubt          = options.Zubt          # some guessed Z position to extrapolate the tracks to (UBT?)
ZcenterSpectr = Zubt + 5640 # cm, approximately
ZhalfextentB  = 990.0  # half extent in Z of spectrometer B field
Znofield      = ZcenterSpectr - ZhalfextentB # some Z upstream of T1 where the spect field is zero
cntnotrack = 0

print("#####################################################################")
print("#### WEIGHTS ARE NOT USED IN THIS EXAMPLE      ######################")
print("####    MUST BE ADDED !!                       ######################")
print("#####################################################################")


f = ROOT.TFile(options.inputFile)
sTree = f.Get("cbmsim")
print("sTree: opened file "+options.inputFile)
print("sTree has %d"%sTree.GetEntries()+" entries")
myfile = options.inputFile
os.system('cp '+options.inputFile+' '+(options.inputFile).replace(".root","_copy.root"))
myfile = (options.inputFile).replace(".root","_copy.root")
myf = ROOT.TFile(myfile)
myTree = myf.Get("cbmsim")
print("myTree: opened file "+myfile)
print("myTree has %d"%myTree.GetEntries()+" entries")
print("sTree has %d"%sTree.GetEntries()+" entries")

if not options.geoFile:
 options.geoFile = options.inputFile.replace('ship.','geofile_full.').replace('_rec.','.')
else:
  fgeo = ROOT.TFile(options.geoFile)

# new geofile, load Shipgeo dictionary written by run_simScript.py
upkl    = Unpickler(fgeo)
ShipGeo = upkl.load('ShipGeo')
dy = ShipGeo.Yheight/u.m

# -----Create geometry----------------------------------------------
run = ROOT.FairRunSim()
run.SetName("TGeant4")  # Transport engine
run.SetSink(ROOT.FairRootFileSink(ROOT.TMemFile('output', 'recreate')))  # Dummy output file
run.SetUserConfig("g4Config_basic.C") # geant4 transport not used, only needed for the mag field
rtdb = run.GetRuntimeDb()
# -----Create geometry----------------------------------------------
modules = shipDet_conf.configure(run,ShipGeo)


if hasattr(ShipGeo.Bfield,"fieldMap"):
  fieldMaker = geomGeant4.addVMCFields(ShipGeo, '', True, withVirtualMC = False)
else:
  print("no fieldmap given, geofile too old, not anymore support")
  exit(-1)
sGeo = fgeo.Get("FAIRGeom")
geoMat =  ROOT.genfit.TGeoMaterialInterface()
ROOT.genfit.MaterialEffects.getInstance().init(geoMat)
bfield = ROOT.genfit.FairShipFields()
bfield.setField(fieldMaker.getGlobalField())
fM = ROOT.genfit.FieldManager.getInstance()
fM.init(bfield)

volDict = {}
i=0
for x in ROOT.gGeoManager.GetListOfVolumes():
 volDict[i]=x.GetName()
 i+=1

log={}
h = {}
#ut.bookHist(h,'Doca','Doca between two tracks',100,0.,10.)
# ----------add combinatorial loop, massi:
ut.bookHist(h,'CombVtxZWithB','comb vertex XZ taking B into account',1000,-60.0,40.0,80,-4.0,4.0)
ut.bookHist(h,'CombDocaNoB','Doca between two comb tracks without taking B into account',250,0.,25.)
ut.bookHist(h,'CombDocaWithB','Doca between two comb tracks with B taken into account',250,0.,25.)
ut.bookHist(h,'CombDocaWithVsNoB' ,'Doca comparison with/without B' ,250,.0,25.0,250,.0,25.0)
ut.bookHist(h,'Y vs X straight','straight extrap used',40,-200.0,200.0,40,-200.0,200.0)
ut.bookHist(h,'Y vs X tool'    ,'tool extrap used'    ,40,-200.0,200.0,40,-200.0,200.0)
ut.bookHist(h,'dist straight vs tool','dist straight vs tool at UBT',40,0.0,40.0)
# ----------end combinatorial loop, massi

###################################################################
def dist2InnerWall(X,Y,Z):
  dist = 0
 # return distance to inner wall perpendicular to z-axis, if outside decayVolume return 0.
  node = sGeo.FindNode(X,Y,Z)
  if ShipGeo.tankDesign < 5:
     if not 'cave' in node.GetName(): return dist  # TP
  else:
     if not 'DecayVacuum' in node.GetName(): return dist
  start = array('d',[X,Y,Z])
  nsteps = 8
  dalpha = 2*ROOT.TMath.Pi()/nsteps
  rsq = X**2+Y**2
  minDistance = 100 *u.m
  for n in range(nsteps):
    alpha = n * dalpha
    sdir  = array('d',[ROOT.TMath.Sin(alpha),ROOT.TMath.Cos(alpha),0.])
    node = sGeo.InitTrack(start, sdir)
    nxt = sGeo.FindNextBoundary()
    if ShipGeo.tankDesign < 5 and nxt.GetName().find('I')<0: return 0
    distance = sGeo.GetStep()
    if distance < minDistance  : minDistance = distance
  return minDistance

def checkFiducialVolume(sTree,tkey,dy):
# extrapolate track to middle of magnet and check if in decay volume
   inside = True
   if not fiducialCut: return True
   fT = sTree.FitTracks[tkey]
   rc,pos,mom = TrackExtrapolateTool.extrapolateToPlane(fT,ShipGeo.Bfield.z)
   if not rc: return False
   if not dist2InnerWall(pos.X(),pos.Y(),pos.Z())>0: return False
   return inside

def getPtruthFirst(sTree,mcPartKey):
   Ptruth,Ptruthx,Ptruthy,Ptruthz = -1.,-1.,-1.,-1.
   for ahit in sTree.strawtubesPoint:
     if ahit.GetTrackID() == mcPartKey:
        Ptruthx,Ptruthy,Ptruthz = ahit.GetPx(),ahit.GetPy(),ahit.GetPz()
        Ptruth  = ROOT.TMath.Sqrt(Ptruthx**2+Ptruthy**2+Ptruthz**2)
        break
   return Ptruth,Ptruthx,Ptruthy,Ptruthz

def myVertex(t1,t2,PosDir):
 # closest distance between two tracks
    # d = |pq . u x v|/|u x v|
   a = ROOT.TVector3(PosDir[t1][0](0) ,PosDir[t1][0](1), PosDir[t1][0](2))
   u = ROOT.TVector3(PosDir[t1][1](0),PosDir[t1][1](1),PosDir[t1][1](2))
   c = ROOT.TVector3(PosDir[t2][0](0) ,PosDir[t2][0](1), PosDir[t2][0](2))
   v = ROOT.TVector3(PosDir[t2][1](0),PosDir[t2][1](1),PosDir[t2][1](2))
   return MyVertex(a,u,c,v)

def MyVertex(a,u,c,v):
   pq = a-c
   uCrossv = u.Cross(v)
   dist  = pq.Dot(uCrossv)/(uCrossv.Mag()+1E-8)
   # u.a - u.c + s*|u|**2 - u.v*t    = 0
   # v.a - v.c + s*v.u    - t*|v|**2 = 0
   E = u.Dot(a) - u.Dot(c)
   F = v.Dot(a) - v.Dot(c)
   A,B = u.Mag2(), -u.Dot(v)
   C,D = u.Dot(v), -v.Mag2()
   t = -(C*E-A*F)/(B*C-A*D+1e-89)
   X = c.x()+v.x()*t
   Y = c.y()+v.y()*t
   Z = c.z()+v.z()*t
   return X,Y,Z,abs(dist)

def getBfield(zstart,zend,nsteps=100):
    # fieldMaker.SetPlotOption("SURF3")
    # fieldMaker.plotField(1, ROOT.TVector3(-6000.0,4000.0, 10.0), ROOT.TVector3(-400.0, 400.0, 2.0),  'tmp', 0.0)
    # fieldMaker.plotField(1, ROOT.TVector3(-6000.0,4000.0, 10.0), ROOT.TVector3(-400.0, 400.0, 2.0),  'tmp')
    # fieldMaker.plotField(1, ROOT.TVector3(-6000.0,4000.0, 10.0), ROOT.TVector3(-400.0, 400.0, 2.0),  'tmp.pdf')
    # fieldMaker.plotField(1, ROOT.TVector3(2000.0,4000.0, 10.0), ROOT.TVector3(-400.0, 400.0, 2.0),  'tmp2.pdf')
    gloB = fieldMaker.getGlobalField()
    z,bx,by,bz = [],[],[],[]
    if zstart >= zend: 
       print("making fun of me ?")
       return z,bx,by,bz
    dz = (zend - zstart)/float(nsteps)
    for i in range(0,nsteps):
       Z = zstart + i * dz # cm
       pos = array('d',[0.,0.,Z])
       gloBkG = array('d',[0.0,0.0,0.0]) # !!!! kG !!!!
       gloB.Field(pos,gloBkG)
       z.append(Z)
       bx.append(gloBkG[0]/10.) # go to Tesla
       by.append(gloBkG[1]/10.) # go to Tesla
       bz.append(gloBkG[2]/10.) # go to Tesla
    return z,bx,by,bz

def showBfield(zstart,zend,nsteps=100):
    z,bx,by,bz = getBfield(zstart,zend,nsteps)
    fig, [ax1, ax2, ax3] = plt.subplots(3, 1, sharex=True, figsize=(10,24), dpi=75)
    ax1.plot(z,bx)
    ax2.plot(z,by)
    ax3.plot(z,bz)
    plt.show(block=False)

def makePlots():
# ----------add combinatorial loop, massi
    strZubt = ' to Z = %5.1f'%Zubt+' cm'
    ROOT.gStyle.SetOptStat(11111111)
    ut.bookCanvas(h,key='comparison straight vs tool',title='compare straight and tool extrap',nx=2450,ny=800,cx=3,cy=1)
    cv = h['comparison straight vs tool'].cd(1)
    h['Y vs X straight'].SetXTitle('X / cm')
    h['Y vs X straight'].SetYTitle('Y / cm')
    h['Y vs X straight'].SetTitle(       h['Y vs X straight'].GetTitle()       + strZubt)
    h['Y vs X straight'].Draw()
    cv = h['comparison straight vs tool'].cd(2)
    h['Y vs X tool'].SetXTitle('X / cm')
    h['Y vs X tool'].SetYTitle('Y / cm')
    h['Y vs X tool'].SetTitle(h['Y vs X tool'].GetTitle() + strZubt)
    h['Y vs X tool'].Draw()
    cv = h['comparison straight vs tool'].cd(3)
    h['dist straight vs tool'].SetTitle( h['dist straight vs tool'].GetTitle() + strZubt)
    h['dist straight vs tool'].SetXTitle('dist / cm')
    h['dist straight vs tool'].Draw()

    strZnoB = ' (Z = %5.1f'%Znofield+' cm)'
    ut.bookCanvas(h,key='combinatorial vertices',title='vertex XZ positon with B in extrap'+strZnoB,nx=800,ny=800,cx=1,cy=1)
    cv = h['CombVtxZWithB']
    h['CombVtxZWithB'].SetXTitle('Z / m')
    h['CombVtxZWithB'].SetYTitle('X / m')
    h['CombVtxZWithB'].Draw()

    ut.bookCanvas(h,key='combinatorial analysis',title='DOCA(2 comb tracks) with/out B'+strZnoB,nx=2450,ny=800,cx=3,cy=1)
    cv = h['combinatorial analysis'].cd(1)
    h['CombDocaNoB'].SetXTitle('Combinatorial DOCA [cm]')
    h['CombDocaNoB'].SetYTitle('counts/mm')
    h['CombDocaNoB'].Draw()
    cv = h['combinatorial analysis'].cd(2)
    h['CombDocaWithB'].SetXTitle('Combinatorial DOCA [cm]')
    h['CombDocaWithB'].SetYTitle('counts/mm')
    h['CombDocaWithB'].Draw()
    cv = h['combinatorial analysis'].cd(3)
    h['CombDocaWithVsNoB'].SetXTitle('Combinatorial DOCA without B  [cm]')
    h['CombDocaWithVsNoB'].SetYTitle('Combinatorial DOCA with B  [cm]')
    h['CombDocaWithVsNoB'].Draw()

    print('finished making plots')
    return

def myEventLoop(n):
    rc = sTree.GetEntry(n)
    print("========= Got event %d"%n+" =========================")
    # check if tracks are made from real pattern recognition, if not adapt cut
    measCut = measCutFK
    if sTree.GetBranch("FitTracks_PR"):
       sTree.FitTracks = sTree.FitTracks_PR
       measCut = measCutPR
    if sTree.GetBranch("fitTrack2MC_PR"):  sTree.fitTrack2MC = sTree.fitTrack2MC_PR
    if sTree.GetBranch("Particles_PR"):    sTree.Particles   = sTree.Particles_PR

    key = -1
    fittedTracks = {}
    lenfittracks = "len(sTree.FitTracks) = %d"%len(sTree.FitTracks)
    if len(sTree.FitTracks)>1: lenfittracks += "   this cannot be!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    print(lenfittracks)
  # ---------- massi add track extrapolation, massi: rep is a Track representation
    for atrack in sTree.FitTracks:
       key+=1
  #   kill tracks outside fiducial volume
       if not checkFiducialVolume(sTree,key,dy): 
          print("checkFiducialVolume(sTree,key,dy) is False"+" ......... skip") 
          continue
       fitStatus   = atrack.getFitStatus()
       nmeas = fitStatus.getNdf()
       if not fitStatus.isFitConverged() : 
          print("fitStatus.isFitConverged() is False"+" ......... skip")
          continue
       if nmeas < measCut: 
          print("nmeas = %d"%nmeas+" < measCut = %d"%measCut+" ......... skip")
          continue
       fittedTracks[key] = atrack
  #   needs different study why fit has not converged, continue with fitted tracks
       rchi2 = fitStatus.getChi2()
      #prob = ROOT.TMath.Prob(rchi2,int(nmeas))
       chi2 = rchi2/nmeas
       fittedState = atrack.getFittedState()
       P = fittedState.getMomMag()
       Px,Py,Pz = fittedState.getMom().x(),fittedState.getMom().y(),fittedState.getMom().z()
       Rx,Ry,Rz = fittedState.getPos().x(),fittedState.getPos().y(),fittedState.getPos().z()
       cov = fittedState.get6DCov()
       # massi: this the fittedtrack-to-MCTrack association:
       if len(sTree.fitTrack2MC)-1<key: # massi: what is this for ? check.
          print("len(sTree.fitTrack2MC)-1 = %d"%(len(sTree.fitTrack2MC)-1)+" < key = %d"%key+" ......... skip")
          continue
       mcPartKey = sTree.fitTrack2MC[key]
       mcPart    = sTree.MCTrack[mcPartKey]
       if not mcPart :
          print("no mcPart found"+" ......... skip")
          continue
       Ptruth_start   = mcPart.GetP()
       Ptruthz_start  = mcPart.GetPz()
       Ptruth,Ptruthx,Ptruthy,Ptruthz = getPtruthFirst(sTree,mcPartKey) # get p truth from first strawpoint
       delPOverP = (Ptruth - P)/Ptruth
       delPOverPz = (1./Ptruthz - 1./Pz) * Ptruthz
       # ... end fittedtrack-to-MCTrack association
       if chi2>chi2CutOff:
          print("chi2 = %d"%chi2+" > chi2CutOff = %d"%chi2CutOff+" ......... skip")
          continue
  #   try measure impact parameter
  #    trackDir = fittedState.getDir()
  #    trackPos = fittedState.getPos()
  #    vx = ROOT.TVector3()
  #    mcPart.GetStartVertex(vx)
  #    t = 0
  #    for i in range(3):   t += trackDir(i)*(vx(i)-trackPos(i))
  #    dist = 0
  #    for i in range(3):   dist += (vx(i)-trackPos(i)-t*trackDir(i))**2
  #    dist = ROOT.TMath.Sqrt(dist)
  #   ---
       _rc,_pos,_mom = TrackExtrapolateTool.extrapolateToPlane(atrack,Zubt) # ShipGeo.UBT.z)
  #    compare to straight extrapolation from anchor point Rx,Ry,Rz and direction Px,Py,Pz 
       Xubt = Rx + (Zubt-Rz)*Px/Pz
       Yubt = Ry + (Zubt-Rz)*Py/Pz
      #print("Start from Fitted State Pos/Mom: %9.6f"%Rx+" %9.6f"%Ry+" %9.6f"%Rz+" / %9.6f"%Px+" %9.6f"%Py+" %9.6f"%Pz)
      #print("  Compare straight vs tool extrapolation at Z = %6.2f"%Zubt+" cm")
      #print("    straight X,Y: %9.6f"%Xubt     +" %9.6f"%Yubt     )
      #print("        tool X,Y: %9.6f"%_pos.x() +" %9.6f"%_pos.y() )
       h['Y vs X straight'].Fill(Xubt,Yubt)
       h['Y vs X tool'].Fill(_pos.x(),_pos.y())
       distanza = ROOT.TMath.Sqrt( (_pos.x()-Xubt)**2 + (_pos.y()-Yubt)**2 ) 
       h['dist straight vs tool'].Fill(distanza)
  #   ----------add combinatorial loop, massi:
       atrack_pos = ROOT.TVector3(atrack.getFittedState().getPos()) # no B taken into account !
       atrack_dir = ROOT.TVector3(atrack.getFittedState().getDir()) # no B taken into account !
       # the just above is the state at T1 entrance ? Not right! there is B field before T1!! 
       # => Get it just upstream T1, where no field:
       arc,aPos,aMom = TrackExtrapolateTool.extrapolateToPlane(atrack,Znofield)
       atr_pos = ROOT.TVector3(aPos)
       atr_dir = ROOT.TVector3(aMom.x()/aMom.Mag(),aMom.y()/aMom.Mag(),aMom.z()/aMom.Mag())
       #print("    m  mykey mynmeas (  Px  ,  Py  ,  Pz  ) ")
       for m in range(n+1,nEvents): # for m in range(n+1,sTree.GetEntries()):
           myrc = myTree.GetEntry(m)
           mykey = -1
           myfittedTracks = {}
           try:
            for btrack in myTree.FitTracks:
                  print("This has FitTracks:", m)
                  mykey+=1
                  myfitStatus   = btrack.getFitStatus()
                  mynmeas = myfitStatus.getNdf()
                  if not myfitStatus.isFitConverged() : continue
                  if mynmeas < measCut: continue
                  myfittedTracks[key] = btrack
                  myfittedState = btrack.getFittedState()
                  myP = myfittedState.getMomMag()
                  myPx,myPy,myPz = myfittedState.getMom().x(),myfittedState.getMom().y(),myfittedState.getMom().z()
                  btrack_pos = ROOT.TVector3(myfittedState.getPos()) # no B taken into account !
                  btrack_dir = ROOT.TVector3(myfittedState.getDir()) # no B taken into account !
                  # the just above is the state at T1 entrance ? Not right! there is B field before T1!! 
                  # => Get it just upstream T1, where no field:
                  brc,bPos,bMom = TrackExtrapolateTool.extrapolateToPlane(btrack,Znofield)
                  btr_pos = ROOT.TVector3(bPos)
                  btr_dir = ROOT.TVector3(bMom.x()/bMom.Mag(),bMom.y()/bMom.Mag(),bMom.z()/bMom.Mag())
                  myxv, myyv, myzv, mydoca = MyVertex( atrack_pos , atrack_dir , btrack_pos , btrack_dir ) # no B taken into account !
                  abxv, abyv, abzv, abdoca = MyVertex( atr_pos , atr_dir , btr_pos , btr_dir )       
                  h['CombVtxZWithB'].Fill(abzv/100.0,abxv/100.0)
                  if abzv > Znofield: # not correct linear extrapolation ! vertex must be re-done !
                     abdoca = 100000.0 # large number, sent to overflow bin
                  if Debug and m-n<3: 
                     print(" "+str(m)+"  "+str(mykey)+" "+str(mynmeas)+" %6.2f"%myPx+" %6.2f"%myPy+" %6.2f"%myPz)
                     print("With tracks extrapolated not taking B into account:")
                     print(" atrack Pos/Dir: %9.6f"%atrack_pos[0]+" %9.6f"%atrack_pos[1]+" %9.6f"%atrack_pos[2]\
                                          +" %9.6f"%atrack_dir[0]+" %9.6f"%atrack_dir[1]+" %9.6f"%atrack_dir[2])
                     print(" btrack Pos/Dir: %9.6f"%btrack_pos[0]+" %9.6f"%btrack_pos[1]+" %9.6f"%btrack_pos[2]\
                                          +" %9.6f"%btrack_dir[0]+" %9.6f"%btrack_dir[1]+" %9.6f"%btrack_dir[2])
                     print("vtx,vty,vtz,doca: %9.6f"%myxv+" %9.6f"%myyv+" %9.6f"%myzv+" %9.6f"%mydoca)
                     print("With tracks extrapolated with B taken into account:")
                     print("    atr Pos/Dir: %9.6f"%atr_pos[0]+" %9.6f"%atr_pos[1]+" %9.6f"%atr_pos[2]\
                                          +" %9.6f"%atr_dir[0]+" %9.6f"%atr_dir[1]+" %9.6f"%atr_dir[2])
                     print("    btr Pos/Dir: %9.6f"%btr_pos[0]+" %9.6f"%btr_pos[1]+" %9.6f"%btr_pos[2]\
                                          +" %9.6f"%btr_dir[0]+" %9.6f"%btr_dir[1]+" %9.6f"%btr_dir[2])
                     print("vtx,vty,vtz,doca: %9.6f"%abxv+" %9.6f"%abyv+" %9.6f"%abzv+" %9.6f"%abdoca)
                  h['CombDocaNoB'].Fill(mydoca)
                  h['CombDocaWithB'].Fill(abdoca)
                  h['CombDocaWithVsNoB'].Fill(mydoca,abdoca)
           except:
            continue
            #print("This has no FitTracks:", m)
###################################################################

if showB: # show some B field profile
   zstart = 1500.0 # cm
   zend   = 4500.0 # cm
   showBfield(zstart,zend,nsteps=2000)
   plt.show(block=False)
#
sTree.GetEvent(0)
nEvents = min(sTree.GetEntries(),options.nEvents)
print("Will process %i"%nEvents+" events")

for n in range(nEvents):
    rc = sTree.GetEntry(n)
    # Check if the event has FitTracks (e.g., FitTracks_PR or FitTracks)
    fit_tracks = None
    measCut = measCutFK

    if sTree.GetBranch("FitTracks_PR") and len(sTree.FitTracks_PR) > 0:
        sTree.FitTracks = sTree.FitTracks_PR
        measCut = measCutPR
        fit_tracks = sTree.FitTracks
    elif sTree.GetBranch("FitTracks") and len(sTree.FitTracks) > 0:
        fit_tracks = sTree.FitTracks

    if fit_tracks is None:
        print(f"Event {n} skipped: no reconstructed tracks.")
        continue

    myEventLoop(n)
    sTree.FitTracks.Delete()


if doPlots: 
   makePlots()


# output histograms
hfile = options.inputFile.split(',')[0].replace('_rec','_ana')
if "/eos" in hfile or not options.inputFile.find(',')<0:
    # do not write to eos, write to local directory
    tmp = hfile.split('/')
    hfile = tmp[len(tmp)-1]
ROOT.gROOT.cd()
ut.writeHists(h,hfile)


# 0_400000_9600001
# 39_400000_1/
# 41_400000_400001
# 59_400000_400001
# 5_400000_4000001