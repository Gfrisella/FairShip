# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import os
import pickle
import ROOT
import numpy as np
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
from time import time

t0 = time()
shipRoot_conf.configure()
PDG = ROOT.TDatabasePDG.Instance()

parser = ArgumentParser()

parser.add_argument("-f", "--inputFile", dest="inputFile", help="Input file", required=True)
parser.add_argument("-n", "--nEvents",   dest="nEvents",   help="Number of events to analyze", required=False,  default=9999999999,type=int)
parser.add_argument("-d", "--directory", dest="directory", help="the directory of the file", required=False, default='')
parser.add_argument("-g", "--geoFile",   dest="geoFile",   help="ROOT geofile", required=True)
parser.add_argument("-Ana", "--OnlyAnalysis",   dest="Ana",   help="IF you already have the file saved", action="store_true")
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

def chainTheFiles(maindir, filenames, treename='cbmsim'):
    t = ROOT.TChain(treename)
    for fn in filenames:
        full_path = os.path.join(maindir, fn)
        t.AddFile(full_path)
        print(f'Added file {full_path} to chain. Now total entries: {t.GetEntries()}')
    return t

# Base directory where the subdirs live
if options.directory:
    maindir = options.directory  # <- change this to the actual path    
else:
    maindir = ""  # <- change this to the actual path

# File to look for
target_filename = "ship.conical.MuonBack-TGeant4_D_SaveCrit_rec.root"

# Walk through maindir and collect relative paths to the target file
filenames = []
event_number = 0
counter = True  # Flag to control geo_filename assignment
if options.geoFile:
    geo_filename = options.geoFile
else:
    assert False, "Geo file must be specified with --geoFile option"

for root, dirs, files in os.walk(maindir):
    if target_filename in files:
        tmp = root.split('/')
        if 0:
            if not tmp[-1].startswith(('0_400000_10000001')):continue
        if counter:
            geo_filename = os.path.join(root, geo_filename)
            counter  = False
        tmp = tmp[-1].split('_')
        event_number += int(tmp[1])
        rel_path = os.path.relpath(os.path.join(root, target_filename), start=maindir)
        
        filenames.append(rel_path)
print("event_number = ", event_number)
# Now call the function
if not options.Ana: 
    sTree = chainTheFiles(maindir, filenames, treename='cbmsim')
    print("sTree has %d"%sTree.GetEntries()+" entries")


fgeo = ROOT.TFile(geo_filename)

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
ut.bookHist(h,'WeightedComb','weighted comb vertex XZ taking B into account',1000,-60.0,40.0,80,-4.0,4.0)
ut.bookHist(h,'CombVtxZWithB','comb vertex XZ taking B into account',1000,-60.0,40.0,80,-4.0,4.0)
ut.bookHist(h,'CombDocaNoB','Doca between two comb tracks without taking B into account',250,0.,25.)
ut.bookHist(h,'CombDocaWithB','Doca between two comb tracks with B taken into account',250,0.,25.)
ut.bookHist(h,'CombDocaWithVsNoB' ,'Doca comparison with/without B' ,250,.0,25.0,250,.0,25.0)
ut.bookHist(h,'Y vs X straight','straight extrap used',40,-200.0,200.0,40,-200.0,200.0)
ut.bookHist(h,'Y vs X tool'    ,'tool extrap used'    ,40,-200.0,200.0,40,-200.0,200.0)
ut.bookHist(h,'dist straight vs tool','dist straight vs tool at UBT',40,0.0,40.0)
ut.bookHist(h,'Weight', 'Weighted Distribution of the Background Muons', 10000, 0, 1000)
# ----------end combinatorial loop, massi

###################################################################

def extract_track_data(sTree,chi2,real_track = False):
    data = {
                "strawtubesPoints": {
                    "track_id":[],
                    "pos": [],
                    "mom": [],
                    "W": [],
                    "pid": [],
                },
                "fitTracks": {
                    "track_number": [],
                    "rawMeasurement": [],
                    "pos": [],
                    "mom": [],
                    "chi2": [],
                },
                "OutputInfo": {
                  "Xubt_real": [],
                  "Yubt_real": [],
                  "Xubt_retrieved": [],
                  "Yubt_retrieved": [],
                  "W": [],
                  "UBT_rel_dist": [],
                  "bouncing": False,  # Flag to indicate if the track bounced
                },
                # Store all info in a dict keyed by track_number
                "track_positions" : {
                  "fitted_pos": [],
                  "fitted_dir": [],
                  "extrapolated_pos": [],
                  "extrapolated_dir": [],
                  "W": [],
               }
            }
    # --- Collect strawtubesPoint info grouped by TrackID ---
    for i in range(len(sTree.strawtubesPoint)):
        p = sTree.strawtubesPoint[i]
        mcPartKey = sTree.fitTrack2MC[0]
        mcPart = sTree.MCTrack[mcPartKey]
        #track_id = n #p.GetTrackID()

        entry = {
            "track_id": [p.GetTrackID()],
            "pos": (p.GetX(), p.GetY(), p.GetZ()),
            "mom": (p.GetPx(), p.GetPy(), p.GetPz()),
            "W": mcPart.GetWeight(),
            "pid": mcPart.GetPdgCode()
        }            
        data["strawtubesPoints"]["track_id"].append(entry["track_id"])
        data["strawtubesPoints"]["pos"].append(entry["pos"])
        data["strawtubesPoints"]["mom"].append(entry["mom"])
    data["strawtubesPoints"]["W"].append(entry["W"])
    data["strawtubesPoints"]["pid"].append(entry["pid"])


    # --- Collect FitTracks info (fitted points) ---
    for track_number, track in enumerate(sTree.FitTracks):
        rep = track.getCardinalRep()
        nPoints = track.getNumPoints()
        extrapolated_once = False
        if real_track:
            extrapolated_once = True
            _,_pos,_ = TrackExtrapolateTool.extrapolateToPlane(track,Zubt) # extrapolated pos @UBT
            _,aPos,aMom = TrackExtrapolateTool.extrapolateToPlane(track,Znofield) # extrapolated pos and mom @Znofield

            if extrapolated_once:
                # Find ID track in Scoring plane to associate extrapolated position to real one
                match_index = next(
                    (i for i, p1 in enumerate(sTree.sco0_Point_1)
                    if i < len(sTree.strawtubesPoint) and p1.GetTrackID() == sTree.strawtubesPoint[i].GetTrackID()),
                    None
                )
                if match_index is None:
                    error = "TrackID not found in BT, it pass in the walls ....... HERE"
                    atrack_pos = ROOT.TVector3(track.getFittedState().getPos()) # no B taken into account !
                    atrack_dir = ROOT.TVector3(track.getFittedState().getDir()) # no B taken into account ! 
                    Xubt_real  = Yubt_real  = None
                    UBT_rel_dist = None
                    Xubt_retrieved = Yubt_retrieved = None
                    extrapolated_once = False
                    bouncing = False
                    print(error) 
                    ut.reportError(error)
                else:
                    Xubt_real = sTree.sco0_Point_1[match_index].GetX()
                    Yubt_real = sTree.sco0_Point_1[match_index].GetY()
                    Xubt_retrieved = _pos.x()
                    Yubt_retrieved = _pos.y()
                    # Bouncing?
                    trkid=sTree.sco0_Point_1[match_index].GetTrackID()
                    bouncing =  False
                    for i, p2 in enumerate(sTree.sco0_Point_2):
                        #
                        if sTree.sco0_Point_2[i].GetZ() > 30*100 and sTree.sco0_Point_2[i].GetZ() < 84*100 and (abs(sTree.sco0_Point_2[i].GetX()) > 4.3*100 or sTree.sco0_Point_2[i].GetY() < -3.35*100):
                            error = "bouncing ....... HERE"
                            print(error)
                            print(f" The ID is {trkid}, but here is {sTree.sco0_Point_2[i].GetTrackID()}")
                            if trkid != sTree.sco0_Point_2[i].GetTrackID(): continue
                            bouncing = True
                            print(f"Point i:{i}\n Position (x,y,z): {[sTree.sco0_Point_2[i].GetX(),sTree.sco0_Point_2[i].GetY(),sTree.sco0_Point_2[i].GetZ()]}")
                            print(f"The retrieved position is (x,y) = {[_pos.x(),_pos.y()]}")
                            print(f"The real position is (x,y) = {(Xubt_real,Yubt_real)}")
                            print(f"The relative distance is {sTree.sco0_Point_2[i].GetZ()}")
                            if Xubt_real > 0:
                                break
                            ut.reportError(error)
                            break
                        
                    UBT_rel_dist = ROOT.TMath.Sqrt( (_pos.x()-Xubt_real)**2 + (_pos.y()-Yubt_real)**2 )
                    atrack_pos = ROOT.TVector3(track.getFittedState().getPos()) # no B taken into account !
                    atrack_dir = ROOT.TVector3(track.getFittedState().getDir()) # no B taken into account ! 
                    extrapolated_once = False
            else: 
                atrack_pos = atrack_dir = None
                Xubt_real  = Yubt_real  = UBT_rel_dist = None
                Xubt_retrieved = Yubt_retrieved = None
                extrapolated_once = False 

        for i in range(nPoints):
            tp = track.getPoint(i)
            if not tp:
                continue

            # Raw measurement
            meas = tp.getRawMeasurement()
            if meas:
                try:
                    coords = list(meas.getRawHitCoords())
                    raw_measurement = coords
                except Exception:
                    raw_measurement = None
            else:
                raw_measurement = None

            # Fitted position and momentum
            fi = tp.getFitterInfo(rep)
            if fi:
                try:
                    fittedState = fi.getFittedState()
                    pos = fittedState.getPos()
                    mom = fittedState.getMom()
                    pos_tuple = (pos.X(), pos.Y(), pos.Z())
                    mom_tuple = (mom.X(), mom.Y(), mom.Z())
                except Exception:
                    pos_tuple = None
                    mom_tuple = None
            else:
                pos_tuple = None
                mom_tuple = None
            # Append to data
            data["fitTracks"]["track_number"].append(track_number)
            data["fitTracks"]["rawMeasurement"].append(raw_measurement)
            data["fitTracks"]["pos"].append(pos_tuple)
            data["fitTracks"]["mom"].append(mom_tuple)
               # Step 1: Global dictionary to store track positions
        
         # the just above is the state at T1 entrance ? Not right! there is B field before T1!! 
         # => Get it just upstream T1, where no field:
        if real_track:
            atr_pos = ROOT.TVector3(aPos)
            atr_dir = ROOT.TVector3(aMom.x()/aMom.Mag(),aMom.y()/aMom.Mag(),aMom.z()/aMom.Mag())
            data["OutputInfo"]["Xubt_real"].append(Xubt_real)
            data["OutputInfo"]["Yubt_real"].append(Yubt_real)
            data["OutputInfo"]["Xubt_retrieved"].append(Xubt_retrieved)
            data["OutputInfo"]["Yubt_retrieved"].append(Yubt_retrieved)
            data["OutputInfo"]["UBT_rel_dist"].append(UBT_rel_dist)
            data["OutputInfo"]["bouncing"] = bouncing  # Store the bouncing flag
            data["track_positions"]["fitted_pos"].append(atrack_pos)
            data["track_positions"]["fitted_dir"].append(atrack_dir)
            data["track_positions"]["extrapolated_pos"].append(atr_pos)
            data["track_positions"]["extrapolated_dir"].append(atr_dir)
            data["track_positions"]["W"].append(entry["W"])

        data["fitTracks"]["chi2"].append(chi2)
        data["OutputInfo"]["W"].append(entry["W"])
        

    return data

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

def CheckVertexInFiducialVolume(abxv, abyv, abzv):
    # Define z bounds
    z1, z2 = 3270, 8300
    if not (z1 <= abzv <= z2):
        # print("z too big")
        return False

    # Linear interpolation for half-widths at abzv
    x_half = 0.5*100 + (abzv - z1) * (2.0*100 - 0.5*100) / (z2 - z1)
    y_half = 1.35*100 + (abzv - z1) * (3.0*100 - 1.35*100) / (z2 - z1)

    # if not abs(abxv) <= x_half : print(f"x too big {abxv} > {x_half} ")
    # if not abs(abyv) <= x_half : print(f"x too big {abyv} > {y_half} ")
    # Check if point is inside current trapezoid cross-section
    return abs(abxv) <= x_half and abs(abyv) <= y_half


def backtrack_to_z0(abxv, abyv, abzv, res_vec):
    """
    Backtrack position (abxv, abyv, abzv) along direction vector res_vec to z=0.

    Parameters:
        abxv, abyv, abzv: float - initial position coordinates
        res_vec: ROOT.TVector3 - direction vector (assumed normalized or not)

    Returns:
        TVector3 - backtracked position at z=0
    """
    vz = res_vec.Z()
    if vz == 0:
        raise ValueError("Direction vector Z component is zero; cannot backtrack.")

    t = -abzv / vz  # since target z = 0
    x = abxv + t * res_vec.X()
    y = abyv + t * res_vec.Y()
    z = 0.0

    return ROOT.TVector3(x, y, z)


def backtrack_radius_to_z0(abxv, abyv, abzv, res_vec):
    """
    Backtrack position (abxv, abyv, abzv) along direction vector res_vec to z=0,
    then return the transverse radius sqrt(x^2 + y^2) at that point.

    Parameters:
        abxv, abyv, abzv: float - initial position coordinates
        res_vec: ROOT.TVector3 - direction vector (can be normalized or not)

    Returns:
        float - transverse radius at z=0
    """
    vz = res_vec.Z()
    if vz == 0:
        raise ValueError("Direction vector Z component is zero; cannot backtrack.")

    t = -abzv / vz  # parameter to reach z=0
    x = abxv + t * res_vec.X()
    y = abyv + t * res_vec.Y()

    radius = ROOT.TMath.Sqrt(x**2 + y**2)
    return radius


def reconstruct_parent_mass(m1, p1_vec, m2, p2_vec):
    # Convert to energies
    E1 = ROOT.TMath.Sqrt(p1_vec.Mag2() + m1**2)
    E2 = ROOT.TMath.Sqrt(p2_vec.Mag2() + m2**2)

    # Total momentum and energy
    total_p = p1_vec + p2_vec
    total_E = E1 + E2

    # Invariant mass
    M2 = total_E**2 - total_p.Mag2()
    return ROOT.TMath.Sqrt(M2) if M2 > 0 else 0.0

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

def DOCAfromP(Q1, P_1, Q2, P_2):
    """
    Calculate the minimum distance of approach (DOCA) between two lines in 3D space.
    Assumes P_1 and P_2 are already normalized ROOT.TVector3 objects.
    
    Parameters:
        Q1, Q2: ROOT.TVector3 points on each line
        P_1, P_2: Normalized ROOT.TVector3 direction vectors
        
    Returns:
        x, y, z: Coordinates of the midpoint of closest approach
        distance: DOCA between the two lines
    """
    q1 = np.array([Q1.X(), Q1.Y(), Q1.Z()])
    q2 = np.array([Q2.X(), Q2.Y(), Q2.Z()])
    e1 = np.array([P_1.X(), P_1.Y(), P_1.Z()])
    e2 = np.array([P_2.X(), P_2.Y(), P_2.Z()])

    n = np.cross(e1, e2)
    norm_n = np.linalg.norm(n)

    if np.round(norm_n, 6) == 0:
        # Lines are parallel
        return None, None, None, float('inf')

    t1 = np.dot((q2 - q1), np.cross(e2, n)) / np.dot(n, n)
    t2 = np.dot((q2 - q1), np.cross(e1, n)) / np.dot(n, n)

    closest_point_1 = q1 + t1 * e1
    closest_point_2 = q2 + t2 * e2
    middle_point = (closest_point_1 + closest_point_2) / 2.0
    distance = np.linalg.norm(closest_point_2 - closest_point_1)

    return middle_point[0], middle_point[1], middle_point[2], distance

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
        # if global_variables.debug:
        #   print(" event %i"%global_variables.iEvent+" reconstructible track PDG=",self.sTree.MCTrack[trID].GetPdgCode()," trID = ",trID,hitspertrack[trID])
  return nRecTracks

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

    ut.bookCanvas(h,key='Weighted combinatorial vertices',title='Weighted vertex XZ positon with B in extrap'+strZnoB,nx=800,ny=800,cx=1,cy=1)
    cv = h['WeightedComb']
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

    ut.bookCanvas(h,key='Weight Background Muons',title='vWeight Background Muons',nx=800,ny=800,cx=1,cy=1)
    cv = h['Weight']
    h['Weight'].SetXTitle('W / Rate')
    h['Weight'].SetYTitle('count')
    h['Weight'].Draw()


    print('finished making plots')
    return

def myEventLoop(n):
    ar = Significant_data[n].setdefault("Analysis_results", {})
    ar.setdefault("doca_B", [])
    ar.setdefault("doca_noB", [])
    ar.setdefault("m", [])
    ar.setdefault("W", [])
    ar.setdefault("Fail_status", [])
    ar.setdefault("Inv_mass", [])

    atrack_pos = Significant_data[n]["track_positions"]['fitted_pos'][0]
    atrack_dir = Significant_data[n]["track_positions"]['fitted_dir'][0]

    if atrack_dir == None or atrack_pos == None:
        # print("fitted points are corrupted. Abort at ",n)
        error = "fitted points are corrupted."
        ut.reportError(error)
        return False


    atr_pos =  Significant_data[n]["track_positions"]['extrapolated_pos'][0] 
    atr_dir =  Significant_data[n]["track_positions"]['extrapolated_dir'][0]

    if atr_pos == None or atr_dir == None:
        # print("Extrapolated points are corrupted. Abort at", n)
        error = "fitted points are corrupted."
        ut.reportError(error)
        return False
    
    for m in Significant_data: # for m in range(n+1,sTree.GetEntries()):
        if m <= n : continue
        ar["m"].append(m)
        Fails_status = False

        if Significant_data[m]['strawtubesPoints']['pid'] == Significant_data[n]['strawtubesPoints']['pid']:
            Fails_status = True
            ar["Fail_status"].append(Fails_status)
            error = "same pdg code"
            ut.reportError(error)
            continue

        W_comb = Significant_data[m]['OutputInfo']['W'][0] * Significant_data[n]['OutputInfo']['W'][0]

        # Track Fit Point in the first Straw Tubes it met ( like this -> no B taken into account !)
        btrack_pos = Significant_data[m]["track_positions"]['fitted_pos'][0]
        btrack_dir = Significant_data[m]["track_positions"]['fitted_dir'][0] 

        if btrack_dir == None or btrack_pos == None:
            Fails_status = True
            ar["Fail_status"].append(Fails_status)
            # print("fitted points are corrupted. Abort at ",m)
            error = "fitted points are corrupted."
            ut.reportError(error)
            continue
        # Extrapolated Track Point in the first point without B field
        btr_pos =  Significant_data[m]["track_positions"]['extrapolated_pos'][0]
        btr_dir =  Significant_data[m]["track_positions"]['extrapolated_dir'][0]

        if btr_pos == None or btr_dir == None:
            Fails_status = True
            ar["Fail_status"].append(Fails_status)
            # print("Extrapolated points are corrupted. Abort at ",m)
            error = "fitted points are corrupted."
            ut.reportError(error)
            continue

        # Doca of tracks in the two cases

        # 1) no B taken into account
        myxv, myyv, myzv, mydoca = DOCAfromP( atrack_pos , atrack_dir , btrack_pos , btrack_dir )

        # 2) B taken into account
        abxv, abyv, abzv, abdoca = DOCAfromP( atr_pos , atr_dir , btr_pos , btr_dir )

        if not abdoca or not abzv:
            # print("The abdoca: ", abdoca) 
            # print("The abzv: ", abzv) 
            Fails_status = True
            ar["Fail_status"].append(Fails_status)
            error = "Doca not correctly evaluated."
            ut.reportError(error)
            continue

        if abdoca > np.sqrt(400**2 + 600**2) or mydoca > np.sqrt(400**2 + 600**2):
            # print("DOCA no sense big (no B)", abdoca)
            # print("DOCA no sense big (B)", mydoca)
            error = "Doca bigger than the Straws."
            ut.reportError(error)
            Fails_status = True
            ar["Fail_status"].append(Fails_status)
            continue
        
        if not CheckVertexInFiducialVolume(abxv, abyv, abzv):
        #    print("Outside the fiducial volume, the position is:", abzv)
           Fails_status = True
           ar["Fail_status"].append(Fails_status)
           error = "Outside the fiducial volume"
           ut.reportError(error)
           continue

        if abdoca > 2:
        #    print("Discarded for doca otuside 2 cm")
           Fails_status = True
           ar["Fail_status"].append(Fails_status)
           error = "Discarded for doca > 2 cm"
           ut.reportError(error)
           continue

        if abzv > Znofield: # not correct linear extrapolation ! vertex must be re-done !
            #print("abzv > Znofield")
            # print("Event ",m)
            # print("x,y,z:",Significant_data[m]["track_positions"]['extrapolated_pos'])
            # print("px,py,pz:",Significant_data[m]["track_positions"]['extrapolated_dir'])
            # print("Event ",n)
            # print("x,y,z:",Significant_data[n]["track_positions"]['extrapolated_pos'])
            # print("px,py,pz:",Significant_data[n]["track_positions"]['extrapolated_dir'])
            error = "abzv > Znofield"
            ut.reportError(error)
            Fails_status = True
            ar["Fail_status"].append(Fails_status)
            continue
            # print(abzv)
            # print(myzv)

        # Take the first momentum in SST and conver into TVector3
        mom_n, mom_m = (ROOT.TVector3(*Significant_data[i]['strawtubesPoints']['mom'][0]) for i in (n, m))
        # The resultant direction vector of the vertex
        res_vec = (atr_dir * mom_n.Mag() + btr_dir * mom_m.Mag()).Unit()

        # Check if in target location the backtracked coordinates of the vertex are inside a radius of 2.5 m
        if backtrack_radius_to_z0(abxv, abyv, abzv, res_vec) > 2.5 * 100:
            error = "r(z=0) > 2.5 m"
            ut.reportError(error)
            Fails_status = True
            ar["Fail_status"].append(Fails_status)
            continue          
        
        mass1 = mass2 = 0.105  # muon mass [GeV]
        Inv_mass = reconstruct_parent_mass(mass1, mom_n, mass2, mom_m)

        if Inv_mass < (mass1+mass2):
            error = "m_inv < 2*m_mu"
            ut.reportError(error)
            Fails_status = True
            ar["Fail_status"].append(Fails_status)
            continue  

        ar["Fail_status"].append(Fails_status)
        ar["doca_B"].append([abxv, abyv, abzv, abdoca])
        ar["doca_noB"].append([myxv, myyv, myzv, mydoca])
        ar["W"].append(W_comb)
        ar["Inv_mass"].append(Inv_mass)
        h['CombVtxZWithB'].Fill(abzv/100.0,abxv/100.0)
        h['WeightedComb'].Fill(abzv/100,abxv/100,W_comb)
        h['CombDocaNoB'].Fill(mydoca)
        h['CombDocaWithB'].Fill(abdoca)
        h['CombDocaWithVsNoB'].Fill(mydoca,abdoca)
    ut.errorSummary()
    print(f"The number of failures for the event {n} are: {sum(ar['Fail_status'])} over {len(ar['Fail_status'])}")
###################################################################

if showB: # show some B field profile
   zstart = 1500.0 # cm
   zend   = 4500.0 # cm
   showBfield(zstart,zend,nsteps=2000)
   plt.show(block=False)
#
if not options.Ana:
    sTree.GetEvent(0)
    nEvents = min(sTree.GetEntries(),options.nEvents)
    print("Will process %i"%nEvents+" events")
t1 = time()
print("Initialization time: ", t1-t0)

# Event/track classification counters
Reconstructed_tracks_not_valids = 0
skipped_events = 0

# Reasons for rejection
Reconstructed_tracks_not_valids_less_4_tracking_stations = 0
Reconstructed_tracks_not_valids_chi2 = 0
Reconstructed_tracks_not_valids_Fit_tracks = 0
Reconstructed_tracks_not_valids_Outsdie_decay_vessel = 0
Reconstructed_tracks_not_valids_FitStatus_not_converged = 0
Reconstructed_tracks_not_valids_nmeas_under_25 = 0
Reconstructed_tracks_not_valids_no_MCtrack = 0
Reconstructed_tracks_not_valids_momenta = 0
Reconstructed_tracks_not_valids_copy = 0
Reconstructed_tracks_not_valids_pdg = 0
count_not_rec_why = 0
founded_tracks = 0
# Store important event identifiers if needed
Significant_Events = []
Significant_data = {}

# for debug
data = {}
nmeas_values = []
trackpoints_values = []

# Step 1: Global dictionary to store track positions
track_positions = {}

if not options.Ana:
    #Fist Loop to remove invalid tracks
    for n in range(nEvents):
        rc = sTree.GetEntry(n)
        # Check if the event has FitTracks (e.g., FitTracks_PR or FitTracks)
        fit_tracks = None
        measCut = measCutFK

        # if sTree.GetBranch("FitTracks_PR") and len(sTree.FitTracks_PR) > 0:
        #     sTree.FitTracks = sTree.FitTracks_PR
        #     measCut = measCutPR
        #     fit_tracks = sTree.FitTracks
        if sTree.GetBranch("FitTracks") and len(sTree.FitTracks) > 0:
            fit_tracks = sTree.FitTracks

        if fit_tracks is None:
            
            skipped_events+=1
            temp1 = findReconstructible(sTree)
            founded_tracks += temp1
            if temp1 > 0:
                print("========= Not-selected event %d"%n+" =========================")
                print(f" The number of tracks that were reconstructible and were not are: {temp1}")
            if len(sTree.strawtubesPoint)>24:
                print("========= Not-selected event %d"%n+" =========================")
                stations_hit = set()  # Will collect unique station identifiers

                for i in range(len(sTree.strawtubesPoint)):
                    p = sTree.strawtubesPoint[i]
                    stations_hit.add(int(p.GetDetectorID() // 10**6)) # first digit identify the tracking station

                if len(stations_hit) > 3:
                    print(f"Should have been reconstructed: with {len(stations_hit)} stations hit and {len(sTree.strawtubesPoint)} hits .")
                    count_not_rec_why +=1

            continue

        print("========= Pre-selected event %d"%n+" =========================")

        if abs(sTree.MCTrack[sTree.fitTrack2MC[0]].GetPdgCode()) != 13:
            print("The pdg code is wrong: ", sTree.MCTrack[sTree.fitTrack2MC[0]].GetPdgCode())
            Reconstructed_tracks_not_valids_pdg +=1
            continue
        # FitTracks has to be 1
        if len(sTree.FitTracks)>1: 
            print(f"len(sTree.FitTracks) = {len(sTree.FitTracks)}"+" ......... skip")
            Reconstructed_tracks_not_valids_Fit_tracks+=1
            continue
        
        # Check Fiducial Volume
        if not checkFiducialVolume(sTree,0,dy): 
            print("checkFiducialVolume(sTree,key,dy) is False"+" ......... skip")
            Reconstructed_tracks_not_valids_Outsdie_decay_vessel+=1 
            continue

        # Check if the fit has converged
        atrack = sTree.FitTracks[0]
        fitStatus   = atrack.getFitStatus()

        if not fitStatus.isFitConverged() : 
            print("fitStatus.isFitConverged() is False"+" ......... skip")
            Reconstructed_tracks_not_valids_FitStatus_not_converged+=1
            continue

        # Check if the file is currupted
        nmeas = fitStatus.getNdf()

        if len(sTree.strawtubesPoint)<25 or sTree.fitTrack2MC[0] != sTree.strawtubesPoint[0].GetTrackID():
            print("len(sTree.fitTrack2MC[0]):", len(sTree.fitTrack2MC))
            print("mcPartKey:", sTree.fitTrack2MC[0])
            print("p.GetTrackID():",p.GetTrackID())
            print(f"len(sTree.FitTracks) = {len(sTree.FitTracks)}")
            print("chi2 = %d"%fitStatus.getChi2())
            print(f"The number of points in stratubesPoint: {len(sTree.strawtubesPoint)}")
            print("Something is broken in the file (straw tubes point < 25).... skip")
            Reconstructed_tracks_not_valids_copy+=1
            continue

        if nmeas < measCut:

            # Check if the reason for the cut is the low number of stations_hit
            stations_hit = set()  # Will collect unique station identifiers

            for i in range(len(sTree.strawtubesPoint)):
                p = sTree.strawtubesPoint[i]
                stations_hit.add(int(p.GetDetectorID() // 10**6)) # first digit identify the tracking station

            if len(stations_hit) < 4:
                print(f"Rejecting track: only {len(stations_hit)} stations hit.")
                Reconstructed_tracks_not_valids_less_4_tracking_stations +=1

            if 1:
                data[n] = extract_track_data(sTree,fitStatus.getChi2())
                at = data[n].setdefault("ErrorInfo", {})
                at.setdefault("nSST", [len(stations_hit)])
                at.setdefault("ndof", [nmeas])
                at.setdefault("TrackPoints", [atrack.getNumPointsWithMeasurement()])

            print(f"Number of point stored in The Track in ShipDigiReco: {atrack.getNumPointsWithMeasurement()}")
            print("nmeas (ndof) = %d"%nmeas+" < measCut (selected by user)= %d"%measCut+" ......... skip")
            
            Reconstructed_tracks_not_valids_nmeas_under_25+=1
            continue
        
        rchi2 = fitStatus.getChi2()
        #prob = ROOT.TMath.Prob(rchi2,int(nmeas))
        chi2 = rchi2/nmeas
        if chi2>chi2CutOff:
            print("chi2 = %d"%chi2+" > chi2CutOff = %d"%chi2CutOff+" ......... skip")
            Reconstructed_tracks_not_valids_chi2 +=1
            continue
        


        Ptruth,_,_,_ = getPtruthFirst(sTree,sTree.fitTrack2MC[0])
        if Ptruth < 1:
            print(f"P_truth={Ptruth} GeV/c")
            print("P < 1 GeV/c"+" ......... skip")
            Reconstructed_tracks_not_valids_momenta+=1
            continue

        print("========= selected event %d"%n+" =========================")
        Significant_Events.append(n)
        Significant_data[n] = extract_track_data(sTree, chi2, True)

if data:
    # Save to pickle
    with open("Rejected_tracks.pkl", "wb") as f:
        pickle.dump(data, f)
else:
    try:
        with open("Rejected_tracks.pkl", "rb") as f:
            data = pickle.load(f)
    except:
        print("no file")
        assert False

t2 = time()

Reconstructed_tracks_not_valids = Reconstructed_tracks_not_valids_Fit_tracks + Reconstructed_tracks_not_valids_FitStatus_not_converged + Reconstructed_tracks_not_valids_chi2 + Reconstructed_tracks_not_valids_nmeas_under_25 + Reconstructed_tracks_not_valids_Outsdie_decay_vessel + Reconstructed_tracks_not_valids_no_MCtrack + Reconstructed_tracks_not_valids_momenta+Reconstructed_tracks_not_valids_copy + Reconstructed_tracks_not_valids_pdg
print("\n===== Track Selection Process Summary =====")
print("Time needed to select the events: ",t2-t1)
print(f"Total Events analyzed: {event_number}")
print(f"Skipped events: {skipped_events}")
print(f"Total reconstructed tracks: {len(Significant_Events) + Reconstructed_tracks_not_valids }")
print(f"Valid reconstructed tracks: {len(Significant_Events)}")
print(f"Invalid reconstructed tracks: {Reconstructed_tracks_not_valids}")
print(f" - Not valid pdg (!=13): {Reconstructed_tracks_not_valids_pdg}")
print(f" - FitTracks missing: {Reconstructed_tracks_not_valids_Fit_tracks}")
print(f" - Fit did not converge: {Reconstructed_tracks_not_valids_FitStatus_not_converged}")
print(f" - Chi2/NDF too large: {Reconstructed_tracks_not_valids_chi2}")
print(f" - N measurements < 25: {Reconstructed_tracks_not_valids_nmeas_under_25}")
print(f" - N measurements < 25  and <4 tracking stations hit: {Reconstructed_tracks_not_valids_less_4_tracking_stations}")
print(f" - Outside decay vessel: {Reconstructed_tracks_not_valids_Outsdie_decay_vessel}")
print(f" - No valid MCtrack: {Reconstructed_tracks_not_valids_no_MCtrack}")
print(f" - No valid Momenta: {Reconstructed_tracks_not_valids_momenta}")
print(f" - Not valid copy?: {Reconstructed_tracks_not_valids_copy}")
print(f" The vents that should have been reconstructed but no: {count_not_rec_why}")
print(f" The reconstructible tracks lost are: {founded_tracks}")


if Significant_data and Reconstructed_tracks_not_valids_copy == 0:
   # Save to pickle
   with open("Selected_tracks.pkl", "wb") as f:
      pickle.dump(Significant_data, f)

if not Significant_data:
    try:
        with open("Selected_tracks.pkl", "rb") as f:
            Significant_data = pickle.load(f)
    except:
        print("no file")
        assert False

for n in Significant_data:
    print(f"\n===== Combinatorail Evaluation of Event {n} =====")
    myEventLoop(n)
    
   #sTree.FitTracks.Delete()
t3 = time()

print("\n===== Track Reconstruction Summary =====")
print("Time needed to select the events: ",t2-t1)
print("time for myEventLoop: ",t3-t2)
print(f"Valid reconstructed tracks: {len(Significant_data)}")

total_failures = sum(
    sum(ar.get("Fail_status", []))
    for d in Significant_data.values()
    if (ar := d.get("Analysis_results")) and isinstance(ar.get("Fail_status"), list)
)

total_entries = sum(
    len(ar.get("Fail_status", []))
    for d in Significant_data.values()
    if (ar := d.get("Analysis_results")) and isinstance(ar.get("Fail_status"), list)
)

total_bkg_rate_vertices = sum(
    sum(ar.get("W", []))
    for d in Significant_data.values()
    if (ar := d.get("Analysis_results")) and isinstance(ar.get("W"), list)
)

print(f"Total number of failures: {total_failures} over {total_entries}")
print(f"Total number of valid combinatorial vertices : {total_entries - total_failures}")
print(f"Total Combinatorial Vertex Background : {total_bkg_rate_vertices} Hz")


if Significant_data:
   # Save to pickle
   with open("Selected_tracks.pkl", "wb") as f:
      pickle.dump(Significant_data, f)

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