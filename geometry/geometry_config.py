import os
import shipunit as u
import ROOT as r
from ShipGeoConfig import AttrDict, ConfigRegistry
import yaml

# the following params should be passed through 'ConfigRegistry.loadpy' method
# nuTargetPassive = 1  #0 = with active layers, 1 = only passive
# nuTauTargetDesign  =   #0 = TP, 1 = NEW with magnet, 2 = NEW without magnet, 3 = 2018 design

# targetOpt      = 5  # 0=solid   >0 sliced, 5: 5 pieces of tungsten, 4 air slits, 17: molybdenum tungsten interleaved with H20
# strawOpt       = 0  # 0=simplistic tracking stations defined in veto.cxx  1=detailed strawtube design 4=sophisticated straw tube design, horizontal wires 10=2 cm straw diameter for compact layout (default)
# tankDesign = 5 #  4=TP elliptical tank design, 5 = optimized conical rectangular design, 6=5 without segment-1

# Here you can taylor the MS geometry, if the MS design is using SC magnet change the Hybrid_flag to True
# The first row is the length of the magnets
# The other rows are the transverse dimensions of the magnets:  dXIn[i], dXOut[i] , dYIn[i], dYOut[i], gapIn[i], gapOut[i].
shield_db = { 
	"supernut_v4":{
        "Hybrid_flag": True,
        "WithConstField" : False,
        "params": [   
                   [0,  115.5,  50.00, 50.00, 119.00, 119.00, 2.00, 2.00, 1.00, 1.00, 50.00, 50.00, 0.00, 0.00, 1.90], 
                   #[20, 31.11592674255371-5, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0,] 
                   [10 + 20 + (31.11592674255371-5)*2, 321.8030700683594-5, 32.99003982543945, 32.99003982543945, 28.940202713012695, 28.940202713012695, 84.76240539550781, 89.08029174804688, 3.8877923488616943, 2.3109750747680664, 121.617431640625, 111.95079803466797, 0.0, 0.0, 5.699999809265137],
                   #[10, 194.82484436035156 -5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, ]
                   [10 + 10 + (194.82484436035156 -5)*2, 285.1916809082031 -5, 5.0, 50.12767791748047, 21.614580154418945, 48.287078857421875, 2.1587438583374023, 2.0606417655944824, 0.8619040250778198, 0.9806503057479858, 5.263000011444092, 50.069000244140625, 1.276513934135437, 1.276513934135437, -1.899999976158142],
                   [10, 222.07371520996094 -5, 39.65019226074219+30, 8.155497550964355+30, 140.63357543945312, 169.48484802246094, 98.34573364257812, 18.75028419494629, 0.9625361561775208* (39.65/69.65), 0.837262749671936 * (8.15/38.15), 31.663000106811523, 12.232999801635742, 30.0*0, 30.0*0, -1.899999976158142],
                   [10, 175.13963317871094 -5, 30.0, 41.98078918457031, 192.35153198242188, 198.1654815673828, 2.4200000762939453, 86.76644897460938, 0.528433620929718, 0.9397773146629333, 15.755000114440918, 69.56400299072266, 0.08826220780611038, 0.08826220780611038, -1.899999976158142]
		   ]
		   },
    
#     "stellatryon_v2": {
#             "Hybrid_flag": False,
#             "WithConstField" : False,
#             "params": [120.50, 500.00, 285.48, 0.00, 237.53, 90.00, 238.82, 
#                     50.00, 50.00, 119.00, 119.00, 2.00, 2.00, 1.00, 1.00, 50.00, 50.00, 0.00, 0.00, 1.90, 
#                     67.10, 79.92, 27.00, 43.00, 5.00, 5.00, 1.38, 1.06, 67.10, 79.92, 0.00, 0.00, 1.90, 
#                     53.12, 49.56, 43.00, 56.00, 5.03, 5.00, 2.11, 2.40, 53.12, 49.56, 0.00, 0.00, 1.90, 
#                     0.00, 0.00, 0.00, 0.00, 0.00, 0.00, 1.00, 1.00, 1.00, 1.00, 0.00, 0.00, 0.00, 
#                     2.73, 3.68, 56.00, 56.00, 5.00, 5.21, 60.44, 45.63, 2.73, 3.68, 0.50, 0.50, -1.91, 
#                     1.00 + 30.00, 77.12 + 30.00 , 56.00, 56.00, 5.27, 5.00, 140.93*(1/31), 0.88*(77.12/107.12), 1.00, 77.12, 30.00*0, 30.00*0, -1.91, 
#                     30.03, 40.00, 56.00, 56.00, 5.00, 5.01, 4.83, 3.37, 30.03, 40.00, 0.00, 0.00, -1.91]
#         },
    "stellatryon_v2": {
             "Hybrid_flag": False,
             "WithConstField" : False,
             "params":
                     # Zgap Lenght/2 dXcore[1,2] dYcore[1,2] dXvoid[1,2] dRatio[1,2] dYyoke[1,2] dmXgap[1,2] B_goal 
                     [ 
                     [0,  115.5,  50.00, 50.00, 119.00, 119.00, 2.00, 2.00, 1.00, 1.00, 50.00, 50.00, 0.00, 0.00, 1.90], 
                     [20, 495.00, 67.10, 79.92, 27.00, 43.00, 5.00, 5.00, 1.38, 1.06, 67.10, 79.92, 0.00, 0.00, 1.90], 
                     [10, 280.48, 53.12, 49.56, 43.00, 56.00, 5.03, 5.00, 2.11, 2.40, 53.12, 49.56, 0.00, 0.00, 1.90], 
                     [10, 232.53, 2.73, 3.68, 56.00, 56.00, 5.00, 5.21, 60.44, 45.63, 2.73, 3.68, 0.50, 0.50, -1.91], 
                     [10, 85.00,  1.00 + 30.00, 77.12 + 30.00 , 56.00, 56.00, 5.27, 5.00, 140.93*(1/31), 0.88*(77.12/107.12), 1.00, 77.12, 30.00*0, 30.00*0, -1.91], 
                     [10, 233.82, 30.03, 40.00, 56.00, 56.00, 5.00, 5.01, 4.83, 3.37, 30.03, 40.00, 0.00, 0.00, -1.91]
                     ]
         },

#     "Stellatryon_v2_m2":{ "Hybrid_flag": False,
#                 "WithConstField" : False,
#                 "params": [120.5, 175.00, 500.0 - 175, 285.5, 237.5, 90.0, 238.8,
#                         50.0, 50.0, 119.0, 119.0, 2.0, 2.0, 1.0, 1.0, 50.0, 50.0, 0.0, 0.0, 1.9, 
#                         50.1, 50.1, 27.0, 27.0 , 5.0, 5.0, 1, 1 , 67.1, 67.1, 0.0, 0.0, 1.9,
#                         50.1 + 350*(79.9 - 50.1)/(990), 50.1 + 350*(79.9 - 50.1)/(990), 27.0 + 350*(43.0-27.0)/(990), 27.0 + 350*(43.0-27.0)/(990), 5.0, 5.0, 1.4 + 350*(1.1-1.4)/990, 1.4+ 350*(1.1-1.4)/990, 67.1, 67.1, 0.0, 0.0, 1.9, 
#                         53.1, 46.6, 48.0, 48.0, 5.0, 5.0, 1.98, 2.4, 51.6, 51.6, 0.0, 0.0, 1.9, 
#                         2.7, 3.7, 56.0, 56.0, 6.0, 6., 60.4+2.4, 45.6, 2.7, 2.7, 0.5, 0.5, -1.9*0, 
#                         2.0, 75.8, 56.0, 56.0, 6., 6.0, 70.9, 0.9, 40.0, 40.1, 30.0, 30.0, -1.9, 
#                         30.0, 40.0, 56.0, 56.0, 6.0, 6.0, 4.8, 3.35, 40.0, 40.0, 0.0, 0.0, -1.9]
#                 },

#     "Stellatryon_v2_m":{ "Hybrid_flag": False,
#                 "WithConstField" : False,
#                 "params": [120.5, 175.00, 500.0 - 175, 285.5, 237.5, 90.0, 238.8,
#                         50.0, 50.0, 119.0, 119.0, 2.0, 2.0, 1.0, 1.0, 50.0, 50.0, 0.0, 0.0, 1.9, 
#                         50.1, 50.1 + 350*(79.9 - 50.1)/(990), 27.0, 27.0 + 350*(43.0-27.0)/(990), 5.0, 5.0, 1, 1.4 + 350*(1.1-1.4)/990 , 67.1, 79.9, 0.0, 0.0, 1.9,
#                         50.1 + 350*(79.9 - 50.1)/(990), 79.9, 27.0 + 350*(43.0-27.0)/(990), 43.0, 5.0, 5.0, 1.4 + 350*(1.1-1.4)/990, 1.1, 67.1, 79.9, 0.0, 0.0, 1.9, 
#                         53.1, 46.6, 43.0, 56.0, 5.0, 5.0, 2.1, 2.4, 53.1, 49.6, 0.0, 0.0, 1.9, 
#                         2.7, 3.7, 56.0, 56.0, 5.0, 5.2, 60.4, 45.6, 2.7, 3.7, 0, 0, -1.9*0, 
#                         1.0, 77.1, 56.0, 56.0, 5.3, 5.0, 140.9, 0.9, 40.0, 40.1, 30.0, 30.0, -1.9, 
#                         30.0, 40.0, 56.0, 56.0, 5.0, 5.0, 4.8, 3.4, 30.0, 40.0, 0.0, 0.0, -1.9]
#                 },

"stellatryon_v3": {
             "Hybrid_flag": False,
             "WithConstField" : False,
             "params":
			[
			     [0.0, 115.5, 50.0, 50.0, 119.0, 119.0, 2.0, 2.0, 1.0, 1.0, 50.0, 50.0, 0.0, 0.0, 1.9] ,
			     [20.0, 250.53, 66.95, 66.95, 25.92, 25.92, 8.0, 8.0, 1.0, 1.0, 73.65, 73.65, 0.0, 0.0, 1.9] ,
			     [10.0, 249.91, 54.04, 55.04, 44.1, 44.1, 8.0, 8.0, 3.2, 3.13, 60.54, 60.54, 0.0, 0.0, 1.9] ,
			     [10.0, 249.29, 54.23, 53.27, 42.42, 42.42, 8.0, 8.0, 3.5, 3.58, 59.65, 59.65, 0.0, 0.0, 1.9] ,
			     [10.0, 232.01, 54.23, 53.27, 42.42, 42.42, 8.0, 8.0, 3.5, 3.58, 59.65, 59.65, 0.0, 0.0, 0.0] ,
			     [10.0, 233.24, 30.0, 123.07, 56.79, 56.79, 8.0, 8.0, 7.2, 1.0, 135.38, 135.38, 0.0, 0.0, -1.4]
			]},
			
"stellatryon_LFP_v1":{
	     "Hybrid_flag": False,
             "WithConstField" : False,
             "params":
			[[0.0, 120.5, 50.0, 50.0, 119.0, 119.0, 2.0, 2.0, 1.0, 1.0, 50.0, 50.0, 0.0, 0.0, 1.899999976158142],
			[10.0, 497.73455810546875, 68.57454681396484, 64.2499771118164, 26.496477127075195, 43.0, 7.169546127319336, 6.942736625671387, 1.2972147464752197, 1.5377016067504883, 68.57454681396484, 64.2499771118164, 0.0, 0.0, 1.899999976158142],
			[10.0, 323.02130126953125, 64.56716918945312, 54.67230987548828, 43.169898986816406, 56.0, 17.243274688720703, 9.491291046142578, 1.3657028675079346, 2.0025932788848877, 64.56716918945312, 54.67230987548828, 0.0, 0.0, 1.899999976158142], 
			[10.0, 179.83663940429688, 15.863336563110352, 24.713699340820312, 152.9152069091797, 56.0, 9.494522094726562, 10.222557067871094, 9.296140670776367, 5.729996681213379, 15.863336563110352, 24.713699340820312, 0.574324905872345, 0.574324905872345, -1.8547784090042114],
			[10.0, 102.50101470947266, 60.14191436767578, 45.4398193359375, 47.679840087890625, 56.0, 12.87015151977539, 5.0, 1.067857027053833, 1.972305417060852, 60.14191436767578, 45.4398193359375, 39.884979248046875, 39.884979248046875, -1.878922939300537], 
			[10.0, 240.88064575195312, 36.58916473388672, 58.690738677978516, 108.27197265625, 56.0, 8.682084083557129, 5.0, 3.680727481842041, 1.9842867851257324, 36.58916473388672, 58.690738677978516, 0.0, 0.0, -1.872436761856079]
			]},
			
"tokanut_snd_2": {"Hybrid_flag": False,
         "WithConstField" : False,
         "params":[[0.0, 115.5, 50.0, 50.0, 119.0, 119.0, 2.0, 2.0, 1.0, 1.0, 50.0, 50.0, 0.0, 0.0, 1.899999976158142], 
                   [10.0, 266.0776672363281, 37.669677734375, 73.0548324584961, 10.087491989135742, 11.227044105529785, 2.0, 81.32756805419922, 0.9900000095367432, 0.9900000095367432, 37.2929801940918, 72.32428741455078, 0.0, 0.0, 1.899999976158142],
		   [10.0, 249.71810913085938, 46.18749237060547, 7.427814960479736, 41.412960052490234, 131.64163208007812, 3.370185613632202, 3.1160995960235596, 0.9900000095367432, 0.9900000095367432, 45.725616455078125, 7.353537082672119, 0.0, 0.0, 1.899999976158142],
		   [10.0, 273.44232177734375, 35.66830825805664, 25.880535125732422, 74.22798156738281, 30.585582733154297, 92.76029968261719, 2.0, 0.9900000095367432, 0.9900000095367432, 35.31162643432617, 25.62173080444336, 0.0, 0.0, 1.899999976158142],
		   [15.653105735778809, 109.62032318115234, 5.0, 27.923311233520508, 43.870906829833984, 5.0, 2.0, 4.472686767578125, 1.0101009607315063, 0.6830093264579773, 5.050504684448242, 19.071882247924805, 0.0, 0.0, -1.899999976158142],
		   [10.0, 106.06498718261719, 89.40125274658203+31.395034790039062, 10.633211135864258+31.395034790039062, 106.95235443115234, 86.56624603271484, 6.8871564865112305, 2.0, 0.6097873449325562*(89.40125274658203/(31.395034790039062+89.40125274658203)), 1.0101009607315063*(10.633211135864258/(31.395034790039062+10.633211135864258)), 54.515750885009766, 10.740616798400879, 31.395034790039062*0, 31.395034790039062*0, -1.899999976158142],
		   [10.0, 292.60626220703125, 30.0, 64.08020782470703, 51.082481384277344, 159.60655212402344, 2.0, 2.0, 1.0101009607315063, 1.0101009607315063, 30.303028106689453, 64.72747802734375, 0.0, 0.0, -1.899999976158142]]
},

"stellatryon_soft_v1":{"Hybrid_flag": False,
         "WithConstField" : False,
         "params":[
    [0.00, 120.50, 50.00, 50.00, 119.00, 119.00, 2.00, 2.00, 1.00, 1.00, 50.00, 50.00, 0.00, 0.00, 1.90],
    [10.00, 275.23, 70.67, 68.74, 20.00, 20.00, 8.00, 8.00, 1.60, 1.67, 77.74, 77.74, 0.00, 0.00, 1.90],
    [10.00, 296.77, 72.41, 72.90, 20.00, 20.00, 8.00, 8.00, 1.54, 1.52, 80.19, 80.19, 0.00, 0.00, 1.90],
    [10.00, 287.71, 60.45, 59.59, 30.00, 30.00, 8.00, 8.00, 2.17, 2.22, 66.49, 66.49, 0.00, 0.00, 1.90],
    [10.00, 113.85, 33.75, 82.19, 30.00, 30.00, 8.00, 8.00, 3.88, 1.00, 90.41, 90.41, 0.00, 0.00, -0.00],
    [10.00, 168.00, 20.00, 30.00, 40.00, 40.00, 28.79, 11.75, 6.16, 4.34, 33.00, 33.00, 0.00, 0.00, -0.88],
    [10.00, 193.16, 51.59, 83.99, 50.00, 50.00, 8.00, 8.00, 2.87, 1.38, 92.39, 92.39, 0.00, 0.00, -1.87],
]
},
}
if "muShieldDesign" not in globals():
    muShieldDesign = 7
if "muShieldGeo" not in globals():
    muShieldGeo = None
if "nuTargetPassive" not in globals():
    nuTargetPassive = 1
if "nuTauTargetDesign" not in globals():
    nuTauTargetDesign = 4
if "TARGET_YAML" not in globals():
    TARGET_YAML = os.path.expandvars("$FAIRSHIP/geometry/target_config_old.yaml")
if "strawDesign" not in globals():
    strawDesign = 10
if "tankDesign" not in globals():
    tankDesign = 6
if "CaloDesign" not in globals():
    CaloDesign = 0
if "Yheight" not in globals():
    Yheight = 10.
if "EcalGeoFile" not in globals():
    if tankDesign > 4:
        EcalGeoFile = "ecal_rect5x10m2.geo"
    else:
        EcalGeoFile = "ecal_ellipse5x10m2.geo"
if "HcalGeoFile" not in globals():
    if tankDesign > 4:
        HcalGeoFile = "hcal_rect.geo"
    else:
        HcalGeoFile = "hcal.geo"
if "shieldName" not in globals():
    shieldName = None
if "SND" not in globals():
    SND = True
if "SND_design" not in globals():
    SND_design = 1

with ConfigRegistry.register_config("basic") as c:

    c.DecayVolumeMedium = DecayVolumeMedium
    c.SND = SND
    c.SND_design = SND_design
    c.target_yaml = TARGET_YAML

    if not shieldName:
        raise ValueError("shieldName must not be empty!")

    c.shieldName = shieldName
    c.SC_mag = shield_db[shieldName]['Hybrid_flag']

    # global muShieldDesign, targetOpt, strawDesign, Yheight
    c.Yheight = Yheight*u.m
    extraVesselLength = 10 * u.m
    windowBulge = 1*u.m
    if tankDesign > 5: windowBulge = 25*u.cm
#
    magnet_design = 2
    if tankDesign == 5: magnet_design = 3
    if tankDesign == 6: magnet_design = 4
#
    c.strawDesign = strawDesign
    c.tankDesign = tankDesign
    c.magnetDesign = magnet_design
# cave parameters
    c.cave = AttrDict()
    c.cave.floorHeightMuonShield = 5*u.m
    c.cave.floorHeightTankA = 4.2*u.m
    if strawDesign == 10:
        c.cave.floorHeightMuonShield = c.cave.floorHeightTankA  # avoid the gap, for 2018 geometry
    c.cave.floorHeightTankB = 2*u.m
#
    #neutrino detector
    c.nuTauTargetDesign=nuTauTargetDesign

    with open(c.target_yaml) as file:
        config = yaml.safe_load(file)
        c.target = AttrDict(config['target'])

    target_length = (c.target.Nplates - 1) * c.target.sl
    real_target_length = (sum(c.target.N) - 1) * c.target.sl
    for width, n in zip(c.target.L, c.target.N):
        target_length += width * n
        real_target_length += width * n
    c.target.length = target_length
    # interaction point, start of target

    c.target.z0 = 0  # Origin of SHiP coordinate system
    c.target.z = c.target.z0 + c.target.length / 2.
    c.chambers = AttrDict()
    magnetIncrease    = 100.*u.cm

    c.hadronAbsorber = AttrDict()
    
    c.target.prox_shld = 0.5536 * u.m
    c.real_target_length = real_target_length
    c.hadronAbsorber.z =  c.hadronAbsorber.halflength = c.target.z0 + c.real_target_length/2

    c.muShield = AttrDict()
    z_gap = 0.2 #cm between the absorber and the proximity shield
    c.muShield.z = c.hadronAbsorber.z + c.hadronAbsorber.halflength + c.target.prox_shld + z_gap

    params = shield_db[shieldName]['params']

    # If params is a list of lists
    c.muShield.length = sum(line[0] + line[1]*2 for line in params)
    c.muShield.nMagnets = len(params)

    c.muShield.dZ = []
    c.muShield.Z_rel = []
    c.muShield.Z = []

    # Assuming each line corresponds to one set of parameters
    for line in params:
        c.muShield.dZ.append(line[0])
        c.muShield.Z_rel.append(line[1])

    # Compute Z position for each magnet
    for i in range(len(c.muShield.dZ)):
        if i == 0:
            # First magnet uses the initial offset
            c.muShield.Z.append(c.muShield.z + c.muShield.dZ[i] + c.muShield.Z_rel[i])
        else:
            # Subsequent magnets are placed relative to the previous one
            c.muShield.Z.append(c.muShield.Z[i - 1] + c.muShield.Z_rel[i - 1] + c.muShield.dZ[i] + c.muShield.Z_rel[i])

    # Flatten the params list
    c.muShield.params = [item for sublist in params for item in sublist]


    c.decayVolume = AttrDict()

    # target absorber muon shield setup, decayVolume.length = nominal EOI length, only kept to define z=0
    c.decayVolume.length = 50 * u.m

    # make z coordinates for the decay volume and tracking stations relative to T4z
    # eventually, the only parameter which needs to be changed when the active shielding lenght changes.
    c.z = 89.57 * u.m  # absolute position of spectrometer magnet
    c.decayVolume.z = c.z - 31.450 * u.m  # Relative position of spectrometer magnet to decay vessel centre
    c.decayVolume.z0 = c.decayVolume.z - c.decayVolume.length / 2.
    if strawDesign != 4 and strawDesign != 10:
     print("this design ",strawDesign," is not supported, use strawDesign = 4 or 10")
     1/0
    else:
     c.chambers.Tub1length = 2.5 * u.m
     c.chambers.Tub2length = 17.68*u.m+extraVesselLength/2.
     c.chambers.Tub3length = 0.8*u.m
     c.chambers.Tub4length = 2.*u.m+magnetIncrease/2.
     c.chambers.Tub5length = 0.8*u.m
     c.chambers.Tub6length = 0.1*u.m+windowBulge/2.
     c.chambers.Rmin = 245.*u.cm
     c.chambers.Rmax = 250.*u.cm


     c.xMax = 2 * u.m  # max horizontal width at T4
     TrGap = 2 * u.m  # Distance between Tr1/2 and Tr3/4
     TrMagGap = 3.5 * u.m  # Distance from spectrometer magnet centre to the next tracking stations
     #
     z4 = c.z + TrMagGap + TrGap
     c.TrackStation4 = AttrDict(z=z4)
     z3 = c.z + TrMagGap
     c.TrackStation3 = AttrDict(z=z3)
     z2 = c.z - TrMagGap
     c.TrackStation2 = AttrDict(z=z2)
     z1 = c.z - TrMagGap - TrGap
     c.TrackStation1 = AttrDict(z=z1)

     # positions and lenghts of vacuum tube segments (for backward compatibility)
     c.Chamber1 = AttrDict(z=z4 - 4666. * u.cm - magnetIncrease - extraVesselLength)
     c.Chamber6 = AttrDict(z=z4 + 30. * u.cm + windowBulge / 2.)

    c.strawtubes = AttrDict()
    if strawDesign == 4:
     c.strawtubes.InnerStrawDiameter = 0.975 * u.cm
     c.strawtubes.StrawPitch = 1.76 * u.cm
     c.strawtubes.DeltazLayer = 1.1 * u.cm
     c.strawtubes.YLayerOffset = c.strawtubes.StrawPitch / 2.
     c.strawtubes.FrameMaterial = "aluminium"
     c.strawtubes.FrameLateralWidth = 1. * u.cm
     c.strawtubes.DeltazFrame = 10. * u.cm
    elif strawDesign == 10:  # 10 - baseline
     c.strawtubes.InnerStrawDiameter = 1.9928 * u.cm
     c.strawtubes.StrawPitch = 2. * u.cm
     c.strawtubes.DeltazLayer = 1.732 * u.cm
     c.strawtubes.YLayerOffset = 1. * u.cm
     c.strawtubes.FrameMaterial = "steel"
     c.strawtubes.FrameLateralWidth = 0.17 * u.m
     c.strawtubes.DeltazFrame = 2.5 * u.cm

    c.strawtubes.WallThickness = 0.0036 * u.cm
    c.strawtubes.OuterStrawDiameter = (c.strawtubes.InnerStrawDiameter + 2 * c.strawtubes.WallThickness)

    c.strawtubes.StrawsPerLayer = int(c.Yheight/c.strawtubes.StrawPitch)
    c.strawtubes.ViewAngle = 4.57
    c.strawtubes.WireThickness = 0.003 * u.cm
    c.strawtubes.DeltazView = 5. * u.cm
    c.strawtubes.VacBox_x = 240. * u.cm
    c.strawtubes.VacBox_y = 600. * u.cm * c.Yheight / (10. * u.m)

    c.Bfield = AttrDict()
    c.Bfield.z = c.z
    c.Bfield.max = 0 # 1.4361*u.kilogauss  # was 1.15 in EOI
    c.Bfield.y   = c.Yheight
    c.Bfield.x   = 2.4 * u.m
    c.Bfield.fieldMap = "files/MainSpectrometerField.root"
    if c.magnetDesign>3:                          # MISIS design
      c.Bfield.YokeWidth = 0.8 * u.m  # full width       200.*cm
      c.Bfield.YokeDepth = 1.4 * u.m  # half length      200 *cm;
      c.Bfield.CoilThick=25.*u.cm  # thickness
      c.Bfield.x = 2.2 * u.m # half apertures
      c.Bfield.y = 3.5 * u.m

# TimeDet
    c.TimeDet = AttrDict()
    c.TimeDet.dzBarRow = 1.2 * u.cm
    c.TimeDet.dzBarCol = 2.4 * u.cm
    c.TimeDet.zBar = 1 * u.cm
    c.TimeDet.DZ = (c.TimeDet.dzBarRow + c.TimeDet.dzBarCol + c.TimeDet.zBar) / 2
    c.TimeDet.DX = 225 * u.cm
    c.TimeDet.DY = 325 * u.cm
    c.TimeDet.z = 37.800 * u.m - c.TimeDet.dzBarRow * 3 / 2 + c.decayVolume.z # Relative position of first layer of timing detector to decay vessel centre

    if CaloDesign==0:
     c.HcalOption = 1
     c.EcalOption = 1
     c.splitCal = 0
    elif CaloDesign==3:
     c.HcalOption = 2
     c.EcalOption = 1
     c.splitCal = 0
    elif CaloDesign==2:
     c.HcalOption = -1
     c.EcalOption = 2
    else:
     print("CaloDesign option wrong -> ",CaloDesign)
     1/0

    c.SplitCal = AttrDict()
    c.SplitCal.ZStart = 38.450 * u.m + c.decayVolume.z # Relative start z of split cal to decay vessel centre
    c.SplitCal.XMax = 4 * u.m / 2  # half length
    c.SplitCal.YMax = 6 * u.m / 2  # half length
    c.SplitCal.Empty = 0*u.cm
    c.SplitCal.BigGap = 100*u.cm
    c.SplitCal.ActiveECALThickness = 0.56*u.cm
    c.SplitCal.FilterECALThickness = 0.28*u.cm #  0.56*u.cm   1.757*u.cm
    c.SplitCal.FilterECALThickness_first = 0.28*u.cm
    c.SplitCal.ActiveHCALThickness = 90*u.cm
    c.SplitCal.FilterHCALThickness = 90*u.cm
    c.SplitCal.nECALSamplings = 50
    c.SplitCal.nHCALSamplings = 0
    c.SplitCal.ActiveHCAL = 0
    c.SplitCal.FilterECALMaterial= 3    # 1=scintillator 2=Iron 3 = lead  4 =Argon
    c.SplitCal.FilterHCALMaterial= 2
    c.SplitCal.ActiveECALMaterial= 1
    c.SplitCal.ActiveHCALMaterial= 1
    c.SplitCal.ActiveECAL_gas_Thickness=1.12*u.cm
    c.SplitCal.num_precision_layers=1
    c.SplitCal.first_precision_layer=6
    c.SplitCal.second_precision_layer=10
    c.SplitCal.third_precision_layer=13
    c.SplitCal.ActiveECAL_gas_gap=10*u.cm
    c.SplitCal.NModulesInX = 2
    c.SplitCal.NModulesInY = 3
    c.SplitCal.NStripsPerModule = 50
    c.SplitCal.StripHalfWidth = c.SplitCal.XMax / (c.SplitCal.NStripsPerModule * c.SplitCal.NModulesInX)
    c.SplitCal.StripHalfLength = c.SplitCal.YMax / c.SplitCal.NModulesInY
    c.SplitCal.SplitCalThickness=(c.SplitCal.FilterECALThickness_first-c.SplitCal.FilterECALThickness)+(c.SplitCal.FilterECALThickness+c.SplitCal.ActiveECALThickness)*c.SplitCal.nECALSamplings+c.SplitCal.BigGap

    zecal = 38.450 * u.m + c.decayVolume.z # Relative start z of ECAL to decay vessel centre
    c.ecal = AttrDict(z=zecal)
    c.ecal.File = EcalGeoFile
    hcalThickness = 232*u.cm
    if  c.HcalOption == 2: hcalThickness = 110*u.cm  # to have same interaction length as before
    if not c.HcalOption < 0:
     zhcal = 40.850 * u.m + c.decayVolume.z # Relative position of HCAL to decay vessel centre
     c.hcal = AttrDict(z=zhcal)
     c.hcal.hcalSpace = hcalThickness + 5.5*u.cm
     c.hcal.File  =  HcalGeoFile
    else:
     c.hcal  =  AttrDict(z=c.ecal.z)
    if c.EcalOption == 1:
     c.MuonStation0 = AttrDict(z=c.hcal.z+hcalThickness/2.+20.5*u.cm)
    if c.EcalOption == 2:
     c.MuonStation0 = AttrDict(z=c.SplitCal.ZStart+10*u.cm+c.SplitCal.SplitCalThickness)

    c.MuonStation1 = AttrDict(z=c.MuonStation0.z+1*u.m)
    c.MuonStation2 = AttrDict(z=c.MuonStation0.z+2*u.m)
    c.MuonStation3 = AttrDict(z=c.MuonStation0.z+3*u.m)

    c.MuonFilter0 = AttrDict(z=c.MuonStation0.z+50.*u.cm)
    c.MuonFilter1 = AttrDict(z=c.MuonStation0.z+150.*u.cm)
    c.MuonFilter2 = AttrDict(z=c.MuonStation0.z+250.*u.cm)

    c.Muon = AttrDict()
    c.Muon.XMax = 250. * u.cm
    c.Muon.YMax = 325. * u.cm

    c.Muon.ActiveThickness = 0.5*u.cm
    c.Muon.FilterThickness = 30.*u.cm

    c.hadronAbsorber.WithConstField = shield_db[shieldName]['WithConstField'] # TO BE CHECKED: NOT SURE IT IS NEEDED
    c.muShield.WithConstField = shield_db[shieldName]['WithConstField']


# for the digitizing step
    c.strawtubes.v_drift = 1./(30*u.ns/u.mm) # for baseline NA62 5mm radius straws)
    c.strawtubes.sigma_spatial = 0.012*u.cm # according to Massi's TP section
# size of straws
    c.strawtubes.StrawLength = c.xMax
    c.strawtubes.station_height = int(c.Yheight / 2.)


    #CAMM - For Nu tau detector, keep only these parameters which are used by others...
    c.tauMudet = AttrDict()
    c.tauMudet.Ztot = 3 * u.m #space allocated to Muon spectrometer
    c.tauMudet.zMudetC = c.muShield.z + c.muShield.length / 2. - c.tauMudet.Ztot / 2. - 70 * u.cm


    #Upstream Tagger
    UBT_x_crop = 113.4 * u.cm
    c.UpstreamTagger = AttrDict()
    c.UpstreamTagger.Z_Glass = 0.2 * u.cm
    c.UpstreamTagger.Y_Glass = 105 * u.cm
    c.UpstreamTagger.X_Glass = 223. * u.cm  - UBT_x_crop
    c.UpstreamTagger.Z_Glass_Border = 0.2 * u.cm
    c.UpstreamTagger.Y_Glass_Border = 1.0 * u.cm
    c.UpstreamTagger.X_Glass_Border = 1.0 * u.cm
    c.UpstreamTagger.Z_PMMA = 0.8 * u.cm
    c.UpstreamTagger.Y_PMMA = 108 * u.cm
    c.UpstreamTagger.X_PMMA = 226 * u.cm  - UBT_x_crop
    c.UpstreamTagger.DY_PMMA = 1.5 * u.cm
    c.UpstreamTagger.DX_PMMA = 1.5 * u.cm
    c.UpstreamTagger.DZ_PMMA = 0.1 * u.cm
    c.UpstreamTagger.Z_FreonSF6 = 0.1 * u.cm
    c.UpstreamTagger.Y_FreonSF6 = 107 * u.cm
    c.UpstreamTagger.X_FreonSF6 = 225 * u.cm  - UBT_x_crop
    c.UpstreamTagger.Z_FreonSF6_2 = 0.8 * u.cm
    c.UpstreamTagger.Y_FreonSF6_2 = 0.5 * u.cm
    c.UpstreamTagger.X_FreonSF6_2 = 0.5 * u.cm
    c.UpstreamTagger.Z_FR4 = 0.15 * u.cm
    c.UpstreamTagger.Y_FR4 = 111 * u.cm
    c.UpstreamTagger.X_FR4 = 229 * u.cm  - UBT_x_crop
    c.UpstreamTagger.Z_Aluminium = 1.1503 * u.cm
    c.UpstreamTagger.Y_Aluminium = 111 * u.cm
    c.UpstreamTagger.X_Aluminium = 233 * u.cm  - UBT_x_crop
    c.UpstreamTagger.DZ_Aluminium = 0.1 * u.cm
    c.UpstreamTagger.DY_Aluminium = 1 * u.cm
    c.UpstreamTagger.DX_Aluminium = 0.2 * u.cm
    c.UpstreamTagger.Z_Air = 1.1503 * u.cm
    c.UpstreamTagger.Y_Air = 0 * u.cm
    c.UpstreamTagger.X_Air = 2 * u.cm
    c.UpstreamTagger.Z_Strip = 0.0003 * u.cm
    c.UpstreamTagger.Y_Strip = 3.1 * u.cm
    c.UpstreamTagger.X_Strip = 229 * u.cm  - UBT_x_crop
    c.UpstreamTagger.X_Strip64 = 1.534 * u.cm
    c.UpstreamTagger.Y_Strip64 = 111 * u.cm
    c.UpstreamTagger.Z_Position = -25.400 * u.m + c.decayVolume.z # Relative position of UBT to decay vessel centre
