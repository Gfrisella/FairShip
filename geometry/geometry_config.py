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
    "combi_rescaled": {
        "Hybrid_flag": False,
        "WithConstField" : True,
        "params": [
            231.0, 208.0, 207.0, 281.0, 172.82, 212.54, 168.64,
            50.0, 50.0, 119.0, 119.0, 2.0, 2.0, 1.0, 1.0, 50.0, 50.0, 0.0, 0.0, 0.0,
            72.0, 51.0, 29.0, 46.0, 10.0, 7.0,  1.0, 1.0,72.0, 51.0, 0.0, 0.0, 0.0,
            54.0, 38.0, 46.0, 122.0, 14.0, 9.0,  1.0, 1.0,54.0, 38.0, 0.0, 0.0, 0.0,
            10.0, 31.0, 35.0, 31.0, 51.0, 11.0, 1.0, 1.0,0.0, 31.0, 0.0, 0.0, 0.0,
            3.0, 32.0, 54.0, 24.0, 8.0, 8.0, 3.0, 1.0, 1.0,32.0,  0.0, 0.0, 0.0,
            22.0, 32.0, 209.0, 35.0, 8.0, 13.0, 1.0, 1.0,22.0, 32.0, 0.0, 0.0, 0.0,
            33.0, 77.0, 85.0, 241.0, 9.0, 26.0, 1.0, 1.0,33.0, 77.0, 0.0, 0.0, 0.0,
        ]
    },
    "sc_v6": {
        "Hybrid_flag": True,
        "WithConstField" : False,
        "params": [231.00,  0., 353.08, 125.08, 184.83, 150.19, 186.81, 
         50.00,  50.00, 119.00, 119.00,   2.00,   2.00, 1.00,1.0,50.00,  50.00,0.0, 0.00, 45000,
        0.,  0.,  0.,  0.,  0.,   0., 1.,1.0,0.,0.,0.0, 0.,0.,
        45.69,  45.69,  22.18,  22.18,  27.01,  16.24, 3.00,3.0,137.1,137.1,0.0, 0.00, 3360000.0,
        0.,  0.,  0.,  0.,  0.,  0., 1.,1.0,0.,0.,0.0, 0., 0.,
        24.80,  48.76,   8.00, 104.73,  15.80,  16.78, 1.00,1.0,24.80,  48.76,0.0, 0.00, 14240.8,
        3.00, 100.00, 192.00, 192.00,   2.00,   4.80, 1.00,1.0,3.00, 100.00,0.0, 0.00, 30375.55,
        3.00, 100.00,   8.00, 172.73,  46.83,   2.00, 1.00,1.0,3.00, 100.00,0.0, 0.00, 21393.79
        ]
    },
    "sc_v6_old": {
        "Hybrid_flag": True,
        "WithConstField" : False,
        "params": [231.00,  0., 353.08, 125.08, 184.83, 150.19, 186.81, 
         50.00,  50.00, 119.00, 119.00,   2.00,   2.00, 1.00,1.0,50.00,  50.00,0.0, 0.00, 45000,
        0.,  0.,  0.,  0.,  0.,   0., 1.,1.0,0.,0.,0.0, 0.,0.,
        45.69,  45.69,  22.18,  22.18,  27.01,  16.24, 3.00,3.0,137.1,137.1,0.0, 0.00, 3360000.0,
        0.,  0.,  0.,  0.,  0.,  0., 1.,1.0,0.,0.,0.0, 0., 0.,
        24.80,  48.76,   8.00, 104.73,  15.80,  16.78, 1.00,1.0,24.80,  48.76,0.0, 0.00, 14240.8,
        3.00, 100.00, 192.00, 192.00,   2.00,   4.80, 1.00,1.0,3.00, 100.00,0.0, 0.00, 30375.55,
        3.00, 100.00,   8.00, 172.73,  46.83,   2.00, 1.00,1.0,3.00, 100.00,0.0, 0.00, 21393.79
        ]
    },

    "SC_1": {
        "Hybrid_flag": True,
        "WithConstField" : False,
        "params": [120.5, 0.0, 209.48, 258.92, 203.45, 212.04, 293.42, 
        50.0, 50.0, 119.0, 119.0, 2.0, 2.0, 1.0, 1.0,  50.0, 50.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
        45.0, 45.0, 25.0, 25.0, 30.69, 66.77, 3.68, 2.08, 111.47, 128.08, 0.0, 0.0, 3200000.0, 
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
        7.86, 24.22, 58.65, 5.77, 2.29, 14.44,  0.94, 0.87, 5.26, 50.07, 0.1, 0.1, 0.0, 
        18.44, 11.06, 76.75, 110.38, 23.35, 2.34, 0.84, 0.88,  31.66, 12.23, 0.1, 0.1, 0.0, 
        7.77, 39.6, 100.13, 49.32, 2.05, 103.75, 0.95, 0.94, 15.76, 69.56, 0.09, 0.09, 0.0
]
    },
"SC_2": {
        "Hybrid_flag": True,
        "WithConstField" : False,
        "params": [120.5, 31.599035263061523, 263.5232238769531, 273.9796447753906, 249.0243377685547, 177.1697998046875, 172.24513244628906, 50.0, 50.0, 119.0, 119.0, 2.0, 2.0, 1.0, 1.0, 50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 45.0, 45.0, 25.0, 25.0, 65.80142211914062, 50.64552688598633, 2.444321632385254, 3.287796974182129, 107.83118438720703, 120.28192138671875, 0.0, 0.0, 3200000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.393310070037842, 21.555952072143555, 29.390918731689453, 17.263904571533203, 68.86524963378906, 65.04042053222656, 0.9386410117149353, 0.8389843702316284, 5.260000228881836, 50.06999969482422, 77.40785217285156, 77.40785217285156, 0.0, 34.19750213623047, 8.872260093688965, 100.69390869140625, 32.74705505371094, 148.15402221679688, 38.29597854614258, 0.9860916137695312, 0.6521316766738892, 31.65999984741211, 12.229999542236328, 51.03839111328125, 51.03839111328125, 0.0, 21.437395095825195, 62.74828338623047, 197.1008758544922, 143.47642517089844, 6.6328020095825195, 22.104467391967773, 0.9386381506919861, 0.9386382102966309, 15.760000228881836, 69.55999755859375, 0.06135864183306694, 0.06135864183306694, 0.0]
    },

    "Piet_1": {
        "Hybrid_flag": False,
        "WithConstField" : False,
        "params":[230.00, 375.00, 245.00, 255.00, 0.00, 197.00, 197.00,
        30.00, 30.00, 20.00, 20.00, 30.00, 30.00, 1.17, 1.17, 144.00, 144.00, 0.00, 0.00, -10000.00,
        30.00, 31.00, 27.00, 43.00, 6.00, 6.00, 4.29, 4.29, 34.00, 34.00, 0.00, 0.00, -10000.00,
        31.00, 35.00, 43.00, 56.00, 6.00, 6.00, 4.29, 3.79, 44.00, 44.00, 0.00, 0.00, -10000.00,
        3.00, 18.60, 56.00, 56.00, 6.00, 6.00, 54.80, 8.20, 44.00, 44.00, 0.00, 0.00, -10000.00,
        64.40, 68.10, 56.00, 56.00, 6.00, 6.00, 0.46, 0.15, 44.00, 44.00, 0.00, 0.00, -10000.00,
        18.60, 31.80, 56.00, 56.00, 6.00, 6.00, 8.20, 4.47, 44.00, 44.00, 0.00, 0.00, -10000.00,
        31.80, 45.00, 56.00, 56.00, 6.00, 6.00, 4.47, 2.87, 44.00, 44.00, 0.00, 0.00, -10000.00]
    },

"Piet_2": {
        "Hybrid_flag": False,
        "WithConstField" : False,
        "params": [
120.50, 375.00, 371.06, 222.98, 0.00, 129.64, 238.99,
50.00, 50.00, 119.00, 119.00, 2.00, 2.00, 1.00, 1.00, 50.00, 50.00, 0.00, 0.00, 0.00,
35.21, 29.61, 27.00, 43.00, 6.63, 27.84, 1.18, 1.00, 35.21, 29.61, 0.00, 0.00, 0.00,
28.48, 24.44, 43.00, 56.00, 6.00, 6.00, 4.29, 3.79, 28.48, 24.44, 0.00, 0.00, 0.00,
1.14, 15.58, 56.00, 56.00, 6.00, 6.00, 54.80, 8.20, 1.14, 15.58, 0.00, 0.00, 0.00,
64.40, 68.10, 56.00, 56.00, 6.00, 6.00, 0.46, 0.15, 64.40, 68.10, 0.00, 0.00, 0.00,
27.33, 20.85, 56.00, 56.00, 6.00, 6.00, 8.20, 4.47, 27.33, 20.85, 0.00, 0.00, 0.00,
24.05, 55.91, 56.00, 56.00, 6.00, 6.00, 4.47, 2.87, 24.05, 55.91, 0.00, 0.00, 0.00,
]

    },


     "LFP_1": {
        "Hybrid_flag": False,
        "WithConstField" : False,
        "params": [120.5, 244.2, 239.6, 236.5, 203.6,201.3, 194.4,
              50.0, 50.0, 119.0,119.0, 2.0, 2.0, 1.0, 1.0, 50.0, 50.0, 0.0, 0.0, 0.0, 
              65.4, 62.9, 35.3, 45.9, 5.0,3.2, 1.0, 1.0, 65.4, 62.9,0.0, 0.0, 0.0, 
              58.9, 40.3,32.7, 122.4, 14.2, 3.9, 1.0,1.0, 58.9, 40.3, 0.0, 0.0,0.0, 
              11.1, 33.3, 46.1, 31.6,55.3, 6.1, 1.0, 1.0, 11.1,33.3, 0.0, 0.0, 0.0,
               5.0,48.5, 47.5, 18.7, 2.0, 4.7,1.0, 1.0, 5.0, 48.5, 0.0,0.0, 0.0, 
               7.2, 37.0, 130.4,47.6, 2.0, 4.1, 1.0, 1.0,7.2, 37.0, 0.0, 0.0, 0.0,
               35.6, 84.3, 89.6, 98.4, 8.5,14.2, 1.0, 1.0, 35.6, 84.3,0.0, 0.0, 0.0]
    },
        "LFP_2": {
        "Hybrid_flag": False,
        "WithConstField" : False,
        "params": [120.5, 208.88208, 265.111237, 264.502136, 173.762497, 165.456131, 216.073425, 50.0,
             50.0, 119.0, 119.0, 2.0, 2.0, 1.0, 1.0, 50.0, 50.0, 0.0, 0.0, 0.0,
             68.7499695, 67.4365158, 9.01386642, 58.6246796, 2.0, 36.973732, 1.0, 1.02536869,
             68.7499695, 69.1472919, 0.0, 0.0, 0.0, 62.6257439, 9.70884609, 46.7029037,
             88.7386703, 2.10785651, 2.08063197, 1.0, 1.0, 62.6257439, 9.70884609, 0.0,
             0.0, 0.0, 19.0715885, 34.6058617, 45.667778, 46.9257927, 108.437241, 2.2,
             1.0, 1.0, 19.0715885, 34.6058617, 0.0, 0.0, 0.0, 5.26260042, 55.6316719,
             39.85952, 5.27801466, 2.0, 2.0, 1.0, 0.9, 5.26260042, 50.0685034, 0.1,
             0.1, 0.0, 33.0158005, 12.8334885, 123.269882, 78.5234451, 22.4136696, 2.00064135,
             0.959014773, 0.953226984, 31.6626404, 12.2332275, 0.1, 0.1, 0.0, 15.7549067,
             77.2927856, 69.3983994, 152.828476, 2.0, 35.4020729, 1.0, 0.9, 15.7549067,
             69.5635052, 0.00161715306, 0.00161715306, 0.0]
    },
    "LFP_3":{
        "Hybrid_flag": False,
        "WithConstField" : False,
        "params": [ 120.50, 225.45, 270.73, 291.16, 188.49, 164.33, 194.23,
                50.00, 50.00, 119.00, 119.00, 2.00, 2.00, 1.00, 1.00, 50.00, 50.00, 0.00, 0.00, 0.00,
                70.46, 66.43, 9.19, 59.73, 2.00, 32.78, 1.00, 1.00, 70.46, 66.43, 0.00, 0.00, 0.00, 
                66.12, 8.58, 50.87, 82.89, 2.00, 2.00, 1.00, 1.00, 66.12, 8.58, 0.00, 0.00, 0.00,
                18.06, 35.29, 43.72, 39.16, 108.63, 2.00, 1.00, 1.00, 18.06, 35.29, 0.00, 0.00, 0.00, 
                5.00, 51.53, 37.19, 5.00, 2.00, 2.00, 1.00, 0.94, 5.00, 48.20, 0.11, 0.11, 0.00, 
                33.70, 13.00, 118.72, 75.03, 22.71, 2.00, 0.78, 0.97, 26.40, 12.61, 0.10, 0.10, 0.00, 
                17.69, 68.43, 67.91, 133.75, 2.00, 41.88, 1.00, 0.75, 17.69, 51.27, 0.00, 0.00, 0.00
                ]
    },
    "LFP_4":
	{"Hybrid_flag": False,
        "WithConstField" : False,
        "params":[ 120.50, 225.45, 270.73, 291.16, 195.07, 158.48, 212.25, 
    50.00, 50.00, 119.00, 119.00, 2.00, 2.00, 1.00, 1.00, 50.00, 50.00, 0.00, 0.00, 0.00,
    69.95, 69.53, 9.55, 55.77, 2.00, 29.38, 1.00, 1.00, 69.95, 69.53, 0.00, 0.00, 0.00, 
    59.37, 8.08, 53.30, 84.96, 2.00, 2.00, 1.00, 1.00, 59.37, 8.08, 0.00, 0.00, 0.00,
    16.57, 35.95, 48.77, 41.05, 99.80, 2.00, 1.00, 1.00, 16.57, 35.95, 0.00, 0.00, 0.00, 
    5.05, 46.18, 36.56, 5.00, 2.00, 2.00, 1.00, 0.94, 5.05, 43.53, 0.11, 0.11, 0.00, 
    34.46, 13.41, 116.71, 69.61, 23.22, 2.00, 0.82, 0.97, 28.31, 13.05, 0.10, 0.10, 0.00, 
    17.19, 72.10, 64.78, 127.38, 2.00, 43.25, 1.00, 0.82, 17.19, 59.26, 0.00, 0.00, 0.00
]
    },

    "LFP_5":
        {"Hybrid_flag": False,
        "WithConstField" : False,
        "params":[120.50, 230.38, 279.43, 289.85, 119.58, 170.53, 249.28,
 50.00, 50.00, 119.00, 119.00, 2.00, 2.00, 1.00, 1.00, 50.00, 50.00, 0.00, 0.00, 0.00, 
 52.25, 78.36, 6.54, 9.37, 2.04, 40.36, 1.01, 1.05, 52.88, 82.20, 0.00, 0.00, 0.00, 
52.47, 11.70, 41.59, 79.05, 2.19, 2.01, 1.03, 1.00, 54.15, 11.70, 0.00, 0.00, 0.00, 
33.05, 24.10, 55.13, 30.61, 90.36, 2.00, 1.00, 1.00, 33.05, 24.10, 0.11, 0.11, 0.00, 
5.62, 60.38, 31.37, 5.00, 2.00, 2.86, 1.00, 0.74, 5.59, 44.82, 0.00, 0.00, 0.00, 
90.85, 7.44, 137.45, 66.69, 10.09, 2.00, 0.88, 1.00, 80.16, 7.41, 0.00, 0.00, 0.00, 
 9.81, 47.60, 19.59, 164.19, 2.00, 2.05, 1.00, 0.89, 9.81, 42.16, 0.10, 0.10, 0.00]

    },
    "LFP_5_v2":
        {"Hybrid_flag": False,
        "WithConstField" : False,
        "params":[120.50, 230.38, 279.43, 289.85, 119.58, 170.53, 249.28,
 50.00, 50.00, 119.00, 119.00, 2.00, 2.00, 1.00, 1.00, 50.00, 50.00, 0.00, 0.00, 0.00,
 52.25, 78.36, 6.54, 9.37, 2.04, 40.36, 1.01, 1.05, 52.88, 82.20, 0.00, 0.00, 0.00,
52.47, 11.70, 41.59, 79.05, 2.19, 2.01, 1.03, 1.00, 54.15, 11.70, 0.00, 0.00, 0.00,
33.05, 24.10, 55.13, 30.61, 90.36, 2.00, 1.00, 1.00, 33.05, 24.10, 0.11, 0.11, 0.00,
5.62, 60.38, 31.37, 5.00, 2.00, 2.86, 1.00, 0.74, 5.59, 44.82, 0.00, 0.00, 0.00,
90.85, 7.44, 137.45, 66.69, 10.09, 2.00, 0.88, 1.00, 80.16, 7.41, 0.00, 0.00, 0.00,
9.811164855957031 + 25, 47.601898193359375, 19.590896606445312, 164.1947784423828, 2.0, 2.0470468997955322, 1.0, 0.8856719732284546, 9.811164855957031+25, 42.15966796875, 0.1002342477440834*0, 0.1002342477440834*0, 0.0]
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
    c.muShield = AttrDict()
    c.muShield.Field = 1.7 # in units of Tesla expected by ShipMuonShield
    c.muShield.LE = 7 * u.m     # - 0.5 m air - Goliath: 4.5 m - 0.5 m air - nu-tau mu-det: 3 m - 0.5 m air. finally 10m asked by Giovanni
    c.muShield.dZ0 = 1 * u.m


    # zGap to compensate automatic shortening of magnets
    zGap = 0.05 * u.m  # halflengh of gap


    params = shield_db[shieldName]['params']
    c.muShield.params = params
    c.muShield.dZ1 = params[0]
    c.muShield.dZ2 = params[1]
    c.muShield.dZ3 = params[2]
    c.muShield.dZ4 = params[3]
    c.muShield.dZ5 = params[4]
    c.muShield.dZ6 = params[5]
    c.muShield.dZ7 = params[6]
    c.muShield.dXgap = 0. *u.m


    c.muShield.length = 2 * (
            c.muShield.dZ1 + c.muShield.dZ2 +
            c.muShield.dZ3 + c.muShield.dZ4 +
            c.muShield.dZ5 + c.muShield.dZ6 +
            c.muShield.dZ7
    ) + c.muShield.LE

    c.hadronAbsorber = AttrDict()
    
    c.target.prox_shld = 0.5536 * u.m
    c.real_target_length = real_target_length
    c.hadronAbsorber.z =  c.hadronAbsorber.halflength = c.target.z0 + c.real_target_length/2
    c.muShield.z = c.hadronAbsorber.z + c.hadronAbsorber.halflength + c.target.prox_shld
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
