#include "ShipMuonShield.h"

#include "FairLogger.h"   /// for FairLogger, MESSAGE_ORIGIN
#include "TGeoManager.h"
#include "TObjArray.h"                  // for TObjArray
#include "TString.h"                    // for TString
#include "TGeoBBox.h"
#include "TGeoTrd1.h"
#include "TGeoCompositeShape.h"
#include "TGeoBoolNode.h"
#include "TGeoTube.h"
#include "TGeoMaterial.h"
#include "FairGeoInterface.h"
#include "FairGeoMedia.h"
#include "FairGeoBuilder.h"
#include "FairRuntimeDb.h"              // for FairRuntimeDb
#include "TFile.h"
#include <iostream>                     // for operator<<, basic_ostream, etc

Double_t cm = 1;
Double_t m = 100 * cm;
Double_t mm = 0.1 * cm;
Double_t kilogauss = 1.;
Double_t tesla = 10 * kilogauss;

ShipMuonShield::~ShipMuonShield() {}
ShipMuonShield::ShipMuonShield() : FairModule("ShipMuonShield", "") {}

ShipMuonShield::ShipMuonShield(std::vector<double> in_params,
                               Double_t z,
                               const Bool_t WithConstShieldField,
                               const Bool_t SC_key,
			                         const Bool_t SND)
                               : FairModule("MuonShield", "ShipMuonShield")
{
  for(size_t i = 0; i < in_params.size(); i++){
      shield_params.push_back(in_params[i]);
  }
  LOG(INFO) << " THE in_params.size() IS: " << in_params.size();
  nParams = 15;
  num_magnets = in_params.size() / nParams;  // integer division
  LOG(INFO) << " THE num_magnets IS: " << num_magnets;

  if (in_params.size() % 15 != 0) {
    std::cerr << "Warning: incomplete magnet data!\n";
  }


  fWithConstShieldField = WithConstShieldField;
  fSC_mag = SC_key;
  fSND = SND;
  LOG(INFO) << " THE ShipMuonShield FLAG SND IS: " << fSND;
  zEndOfProxShield = z;
}

// -----   Private method InitMedium
Int_t ShipMuonShield::InitMedium(TString name)
{
   static FairGeoLoader *geoLoad=FairGeoLoader::Instance();
   static FairGeoInterface *geoFace=geoLoad->getGeoInterface();
   static FairGeoMedia *media=geoFace->getMedia();
   static FairGeoBuilder *geoBuild=geoLoad->getGeoBuilder();

   FairGeoMedium *ShipMedium=media->getMedium(name);

   if (!ShipMedium)
     Fatal("InitMedium","Material %s not defined in media file.", name.Data());
   TGeoMedium* medium=gGeoManager->GetMedium(name);
   if (medium)
     return ShipMedium->getMediumIndex();
   return geoBuild->createMedium(ShipMedium);
}

void ShipMuonShield::CreateArb8(TString arbName, TGeoMedium *medium,
				Double_t dZ, std::array<Double_t, 16> corners,
				Int_t color, TGeoUniformMagField *magField,
				TGeoVolume *tShield, Double_t x_translation,
				Double_t y_translation,
				Double_t z_translation) {
  TGeoVolume *magF =
      gGeoManager->MakeArb8(arbName, medium, dZ, corners.data());
  magF->SetLineColor(color);
  if (fWithConstShieldField) {
      magF->SetField(magField);
  }
  tShield->AddNode(magF, 1, new TGeoTranslation(x_translation, y_translation,
						z_translation));
}

void ShipMuonShield::CreateArb8(TString arbName, TGeoMedium *medium,
  Double_t dZ, std::array<Double_t, 16> corners,
  Int_t color, TGeoUniformMagField *magField,
  TGeoVolume *tShield, Double_t x_translation,
  Double_t y_translation,
  Double_t z_translation,Bool_t fstepwise,
  Double_t fstepsLenght, Bool_t fstaircase) {

    if (!fstepwise)
  {
    CreateArb8 (arbName, medium, dZ, corners, color, magField, tShield, x_translation, y_translation, z_translation);
    return;
  }
    Int_t zParts = std::ceil(2.0*dZ/fstepsLenght);
    Double_t finalCorners[zParts][16];
    Double_t dxdy[4][2];
    Double_t dZp = dZ/Double_t(zParts);
    Double_t inter_space = (fSND) ? 0.12 : 0.01;

    for (int i = 0; i < 4; ++i)
    {
    dxdy[i][0] = (corners[8+2*i] - corners[0+2*i])/Double_t(zParts);
    dxdy[i][1] = (corners[9+2*i] - corners[1+2*i])/Double_t(zParts);
    }

    std::copy(corners.data() + 0,  corners.data() + 8, finalCorners[0]);

    for (int i = 0; i < zParts; ++i)
    {
    for (int k = 0; k < 4; ++k)
    {
    finalCorners[i][8+2*k] = finalCorners[i][0+2*k] + dxdy[k][0];
    finalCorners[i][9+2*k] = finalCorners[i][1+2*k] + dxdy[k][1];
    }
    if (i != zParts-1)
    {
    std::copy(finalCorners[i] + 8, finalCorners[i] + 16, finalCorners[i+1]);
    }
    }

    //Bool_t staircase = true;
    
    if (fstaircase){
      for (int i = 0; i < zParts; ++i)
      {
      for (int k = 0; k < 4; ++k)
      {
      finalCorners[i][8+2*k] = finalCorners[i][0+2*k]  = (finalCorners[i][0+2*k] + finalCorners[i][8+2*k]) / 2.0;
      finalCorners[i][9+2*k] = finalCorners[i][1+2*k]  = (finalCorners[i][9+2*k] + finalCorners[i][1+2*k]) / 2.0;
      }
      }
    }

    std::vector<TGeoVolume*> magF;
    for (int i = 0; i < zParts; ++i)
    {
    magF.push_back(gGeoManager->MakeArb8(arbName + '_' + std::to_string(i), medium, dZp - inter_space, finalCorners[i]));
    magF[i]->SetLineColor(color);
    if (fWithConstShieldField) {
    magF[i]->SetField(magField);
    }
    }

    for (int i = 0; i < zParts; ++i)
    {
    Double_t true_z_translation = z_translation + 2.0 * Double_t(i) * dZp - dZ + dZp;
    tShield->AddNode(magF[i], 1, new TGeoTranslation(x_translation, y_translation, true_z_translation));
    }
}


void ShipMuonShield::CreateMagnet(TString magnetName,TGeoMedium* medium,TGeoVolume *tShield,TGeoUniformMagField *fields[4],FieldDirection fieldDirection,
				  Double_t dX, Double_t dY, Double_t dX2, Double_t dY2, 
          Double_t ratio_yoke_1, Double_t ratio_yoke_2,
          Double_t dY_yoke_1, Double_t dY_yoke_2,
          Double_t dZ,
				  Double_t middleGap,Double_t middleGap2,
				  Double_t gap,Double_t gap2, Double_t Z, Bool_t NotMagnet,
          Bool_t SC_key = false)
  {
    if(SC_key) { dY = dY + 5; }

    Double_t coil_gap,coil_gap2;
    Int_t color[4] = {45,31,30,38};
    gap = std::ceil(std::max(100. / dY, gap));
    gap2 = std::ceil(std::max(100. / dY2, gap2));
    coil_gap = gap;
    coil_gap2 = gap2;

    Double_t anti_overlap = 0; // gap between fields in the
						   // corners for mitred joints
						   // (Geant goes crazy when
						   // they touch each other)

    std::array<Double_t, 16> cornersMainL = {
      middleGap, 
      -(dY +dY_yoke_1)- anti_overlap, 
      middleGap, 
      dY + dY_yoke_1- anti_overlap,
      dX + middleGap, 
      dY- anti_overlap, 
      dX + middleGap,
      -(dY- anti_overlap),
      middleGap2,
      -(dY2 + dY_yoke_2- anti_overlap), middleGap2, 
      dY2 + dY_yoke_2- anti_overlap,
      dX2 + middleGap2, 
      dY2- anti_overlap, 
      dX2 + middleGap2,
      -(dY2- anti_overlap)
      };

      std::array<Double_t, 16> cornersTL = {
        middleGap + dX,dY,
        middleGap,
        dY + dY_yoke_1,
        dX + ratio_yoke_1*dX + middleGap + coil_gap,
        dY + dY_yoke_1,
        dX + middleGap + coil_gap,
        dY,
        middleGap2 + dX2,
        dY2,
        middleGap2,
        dY2 + dY_yoke_2,
        dX2 + ratio_yoke_2*dX2 + middleGap2 + coil_gap2,
        dY2 + dY_yoke_2,
        dX2 + middleGap2 + coil_gap2,
        dY2
      };
      std::array<Double_t, 16> cornersMainSideL = {
        dX + middleGap + gap,
        -(dY), 
        dX + middleGap + gap,
        dY, 
        dX + ratio_yoke_1*dX + middleGap + gap, 
        dY + dY_yoke_1,
        dX + ratio_yoke_1*dX + middleGap + gap, 
        -(dY + dY_yoke_1), 
        dX2 + middleGap2 + gap2,
        -(dY2), 
        dX2 + middleGap2 + gap2, 
        dY2,
        dX2 + ratio_yoke_2*dX2 + middleGap2 + gap2, 
        dY2 + dY_yoke_2, 
        dX2 + ratio_yoke_2*dX2 + middleGap2 + gap2,
        -(dY2 + dY_yoke_2)
      };
    std::array<Double_t, 16> cornersMainR, cornersCLBA,
       cornersMainSideR, cornersCLTA, cornersCRBA,
       cornersCRTA, cornersTR, cornersBL, cornersBR;
    // Use symmetries to define remaining magnets
    for (int i = 0; i < 16; ++i) {
      cornersMainR[i] = -cornersMainL[i];
      cornersMainSideR[i] = -cornersMainSideL[i];
      cornersCRTA[i] = -cornersCLBA[i];
      cornersBR[i] = -cornersTL[i];
    }
    // Need to change order as corners need to be defined clockwise
    for (int i = 0, j = 4; i < 8; ++i) {
      j = (11 - i) % 8;
      cornersCLTA[2 * j] = cornersCLBA[2 * i];
      cornersCLTA[2 * j + 1] = -cornersCLBA[2 * i + 1];
      cornersTR[2 * j] = -cornersTL[2 * i];
      cornersTR[2 * j + 1] = cornersTL[2 * i + 1];
    }
    for (int i = 0; i < 16; ++i) {
      cornersCRBA[i] = -cornersCLTA[i];
      cornersBL[i] = -cornersTR[i];
    }

    TString str1L = "_MiddleMagL";
    TString str1R = "_MiddleMagR";
    TString str2 = "_MagRetL";
    TString str3 = "_MagRetR";
    TString str4 = "_MagCLB";
    TString str5 = "_MagCLT";
    TString str6 = "_MagCRT";
    TString str7 = "_MagCRB";
    TString str8 = "_MagTopLeft";
    TString str9 = "_MagTopRight";
    TString str10 = "_MagBotLeft";
    TString str11 = "_MagBotRight";

    // Determine stepwise
    Bool_t usestepwise = stepwise;  
    if (magnetName == "MagnAbsorb") {
        usestepwise = false;
    }

    switch (fieldDirection){

    case FieldDirection::up:
      CreateArb8(magnetName + str1L, medium, dZ, cornersMainL, color[0], fields[0], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str1R, medium, dZ, cornersMainR, color[0], fields[0], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str2, medium, dZ, cornersMainSideL, color[1], fields[1], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str3, medium, dZ, cornersMainSideR, color[1], fields[1], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str8, medium, dZ, cornersTL, color[3], fields[3], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str9, medium, dZ, cornersTR, color[2], fields[2], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str10, medium, dZ, cornersBL, color[2], fields[2], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str11, medium, dZ, cornersBR, color[3], fields[3], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      break;
    case FieldDirection::down:
      CreateArb8(magnetName + str1L, medium, dZ, cornersMainL, color[1], fields[1], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str1R, medium, dZ, cornersMainR, color[1], fields[1], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str2, medium, dZ, cornersMainSideL, color[0], fields[0], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str3, medium, dZ, cornersMainSideR, color[0], fields[0], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str8, medium, dZ, cornersTL, color[2], fields[2], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str9, medium, dZ, cornersTR, color[3], fields[3], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str10, medium, dZ, cornersBL, color[3], fields[3], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      CreateArb8(magnetName + str11, medium, dZ, cornersBR, color[2], fields[2], tShield,  0, 0, Z, usestepwise, stepsLenght, staircase);
      break;
    }
  }

void ShipMuonShield::Initialize(std::vector<TString> &magnetName,
				std::vector<FieldDirection> &fieldDirection,
				std::vector<Double_t> &dXIn, std::vector<Double_t> &dYIn,
				std::vector<Double_t> &dXOut, std::vector<Double_t> &dYOut,
        std::vector<Double_t> &ratio_yokesIn, std::vector<Double_t> &ratio_yokesOut,
        std::vector<Double_t> &dY_yokeIn, std::vector<Double_t> &dY_yokeOut,
				std::vector<Double_t> &dZ, std::vector<Double_t> &Z_rel,
        std::vector<Double_t> &midGapIn,
				std::vector<Double_t> &midGapOut,
        std::vector<Double_t> &Bgoal,
				std::vector<Double_t> &gapIn, std::vector<Double_t> &gapOut,
				std::vector<Double_t> &Z) {

  LOG(INFO) << " Initialize the MS ";
  magnetName.reserve(num_magnets);
  fieldDirection.reserve(num_magnets);
  for (auto i :
       {&dXIn, &dXOut, &dYIn, &dYOut, &dZ, &Z_rel, &midGapIn, &midGapOut,
	&ratio_yokesIn , &ratio_yokesOut, &dY_yokeIn, &dY_yokeOut, &Bgoal, &gapIn, &gapOut, &Z}) {
    i->reserve(num_magnets);
  }

  magnetName.push_back("MagnAbsorb");
  for (size_t i = 1; i < num_magnets; ++i) {
    magnetName.push_back(Form("Magn%d", i));
  }

  fieldDirection = {
FieldDirection::up,   FieldDirection::up,   FieldDirection::up,
FieldDirection::up,   FieldDirection::down,   FieldDirection::down,
FieldDirection::down };

  std::vector<Double_t> params;
  params = shield_params;

  const int offset = 0;

  for (size_t i = 0; i < num_magnets; ++i) {
    // --- Load parameters for each magnet ---
    dZ[i]           = params[offset + i * nParams + 0];
    Z_rel[i]        = params[offset + i * nParams + 1];
    dXIn[i]         = params[offset + i * nParams + 2];
    dXOut[i]        = params[offset + i * nParams + 3];
    dYIn[i]         = params[offset + i * nParams + 4];
    dYOut[i]        = params[offset + i * nParams + 5];
    gapIn[i]        = params[offset + i * nParams + 6];
    gapOut[i]       = params[offset + i * nParams + 7];
    ratio_yokesIn[i]  = params[offset + i * nParams + 8];
    ratio_yokesOut[i] = params[offset + i * nParams + 9];
    dY_yokeIn[i]    = params[offset + i * nParams + 10];
    dY_yokeOut[i]   = params[offset + i * nParams + 11];
    midGapIn[i]     = params[offset + i * nParams + 12];
    midGapOut[i]    = params[offset + i * nParams + 13];
    Bgoal[i]        = params[offset + i * nParams + 14];

    // --- Compute Z position for each magnet ---
    if (i == 0) {
        // First magnet uses the initial offset
        Z[i] = zEndOfProxShield + dZ[i] + Z_rel[i];
    } else {
        // Subsequent magnets are placed relative to the previous one
        Z[i] = Z[i - 1] + Z_rel[i - 1] + dZ[i] + Z_rel[i];
    }
// --- Print all values for this magnet ---
    LOG(INFO) << "Magnet " << i
              << ": dZ=" << dZ[i]
              << ", Z_rel=" << Z_rel[i]
              << ", dXIn=" << dXIn[i]
              << ", dXOut=" << dXOut[i]
              << ", dYIn=" << dYIn[i]
              << ", dYOut=" << dYOut[i]
              << ", gapIn=" << gapIn[i]
              << ", gapOut=" << gapOut[i]
              << ", ratio_yokesIn=" << ratio_yokesIn[i]
              << ", ratio_yokesOut=" << ratio_yokesOut[i]
              << ", dY_yokeIn=" << dY_yokeIn[i]
              << ", dY_yokeOut=" << dY_yokeOut[i]
              << ", midGapIn=" << midGapIn[i]
              << ", midGapOut=" << midGapOut[i]
              << ", Bgoal=" << Bgoal[i]
              << ", Z=" << Z[i];
}

}
void ShipMuonShield::ConstructGeometry()
{
    TGeoVolume *top=gGeoManager->GetTopVolume();
    TGeoVolume *tShield = new TGeoVolumeAssembly("MuonShieldArea");
    InitMedium("steel");
    TGeoMedium *steel =gGeoManager->GetMedium("steel");
    InitMedium("iron");
    TGeoMedium *iron  =gGeoManager->GetMedium("iron");
    InitMedium("Concrete");
    TGeoMedium *concrete  =gGeoManager->GetMedium("Concrete");
    InitMedium("copper");
    TGeoMedium *copper  =gGeoManager->GetMedium("copper");

      std::vector<TString> magnetName;
      std::vector<FieldDirection> fieldDirection;
      std::vector<Double_t> dXIn, dYIn, dXOut, dYOut, dZf, Z_relf, midGapIn, midGapOut, ratio_yokesIn, ratio_yokesOut, dY_yokeIn, dY_yokeOut, gapIn, gapOut, Bgoal, Z;
      Initialize(magnetName, fieldDirection, dXIn, dYIn, dXOut, dYOut, ratio_yokesIn, ratio_yokesOut,
        dY_yokeIn, dY_yokeOut, dZf, Z_relf, midGapIn, midGapOut, Bgoal, gapIn, gapOut, Z);

      // Create TCC8 tunnel around muon shield
      Double_t TCC8_length =  170 * m;
      // Add small stair step at the beginning of ECN3
      Double_t stair_step_length = 0.82 * m;
      Double_t ECN3_length =  100 * m;
      Double_t TCC8_trench_length = 12 * m;
      Double_t zgap = 0.1 * cm;
      Double_t Proximity_shield_half_length = 55.36/2 * cm;
      Double_t zEndOfTarget = zEndOfProxShield - 2*Proximity_shield_half_length;
      Double_t absorber_half_length = (Z_relf[0]);
      Double_t z_transition = 20.52 * m ;
      auto *rock = new TGeoBBox("rock", 20 * m, 20 * m, TCC8_length / 2. + ECN3_length / 2. + 5 * m);
      auto *muon_shield_cavern = new TGeoBBox("muon_shield_cavern", 4.995 * m, 3.75 * m, TCC8_length / 2.);
      auto *TCC8_shift = new TGeoTranslation("TCC8_shift", 1.435 * m, 2.05 * m, - TCC8_length / 2.);
      TCC8_shift->RegisterYourself();

      // Create ECN3 cavern around vessel
      auto *experiment_rock = new TGeoBBox("experiment_rock", 20 * m, 20 * m, ECN3_length / 2.);
      auto *stair_step = new TGeoBBox("stair_step", 7.995 * m, 5.6 * m , stair_step_length / 2.);
      auto *stair_step_shift = new TGeoTranslation("stair_step_shift", 3.435 * m, 3.04 * m , stair_step_length / 2.);
      stair_step_shift->RegisterYourself();
      auto *experiment_cavern = new TGeoBBox("experiment_cavern", 7.995 * m, 6 * m, ECN3_length / 2. - stair_step_length / 2.);
      auto *ECN3_shift = new TGeoTranslation("ECN3_shift", 3.435 * m, 2.64 * m, ECN3_length / 2. + stair_step_length / 2.);
      ECN3_shift->RegisterYourself();

      auto *yoke_pit = new TGeoBBox("yoke_pit", 3.5 * m, 4.3 * m + 1 * cm, 2.5 * m);
      auto* yoke_pit_shift =
          new TGeoTranslation("yoke_pit_shift", 0 * m, 0 * m, 89.57 * m - z_transition);
      yoke_pit_shift->RegisterYourself();

      auto *target_pit = new TGeoBBox("target_pit", 2 * m, 0.5 * m, 2 * m);
      auto *target_pit_shift = new TGeoTranslation("target_pit_shift", 0 * m, -2.2 * m, zEndOfTarget - 2 * m - z_transition);
      target_pit_shift->RegisterYourself();


      std::array<double, 7> fieldScale = {{1., 1., 1., 1., 1., 1., 1.}};
      for (Int_t nM = 0; nM < (num_magnets); nM++) {
        if (Z_relf[nM] < 1e-5 || dXIn[nM] == 0){
                    continue;
                  }
	      LOG(INFO) << " THE ConstructGeometry magnet " << nM;
        LOG(INFO) << " THE ConstructGeometry FLAG STEPWISE IS " << stepwise;
        LOG(INFO) << " THE ConstructGeometry FLAG STAIRCASE IS " << staircase;
        LOG(INFO) << " THE ConstructGeometry FLAG STEPSLENGHT IS " << stepsLenght;

        Double_t ironField_s = Bgoal[nM] * fieldScale[nM] * tesla;
        TGeoUniformMagField *magFieldIron_s = new TGeoUniformMagField(0.,ironField_s,0.);
        TGeoUniformMagField *RetField_s     = new TGeoUniformMagField(0.,-ironField_s,0.);
        TGeoUniformMagField *ConRField_s    = new TGeoUniformMagField(-ironField_s,0.,0.);
        TGeoUniformMagField *ConLField_s    = new TGeoUniformMagField(ironField_s,0.,0.);
        TGeoUniformMagField *fields_s[4] = {magFieldIron_s,RetField_s,ConRField_s,ConLField_s};
        // Create the magnet
        CreateMagnet(magnetName[nM], iron, tShield, fields_s, fieldDirection[nM],
          dXIn[nM], dYIn[nM], dXOut[nM], dYOut[nM],  ratio_yokesIn[nM], ratio_yokesOut[nM], dY_yokeIn[nM], dY_yokeOut[nM], Z_relf[nM],
          midGapIn[nM], midGapOut[nM], gapIn[nM], gapOut[nM], Z[nM], nM==0, nM == 3 && fSC_mag);
        }

      // Place in origin of SHiP coordinate system as subnodes placed correctly
      top->AddNode(tShield, 1);

      // Create the cavern
      std::vector<TGeoTranslation*> mag_trans;

      auto mag2 = new TGeoTranslation("mag2", 0, 0, -0.001*m);
      mag2->RegisterYourself();
      mag_trans.push_back(mag2);

      // Proximity Shielding
      auto Proximity_Shielding = new TGeoBBox("Proximity_Shielding",  50*cm, 50 * cm, Proximity_shield_half_length - zgap);
      auto *Proximity_Shift = new TGeoTranslation("Proximity_Shift", 0 * m, 0 * m,0 * m );
      Proximity_Shift -> RegisterYourself();
      TGeoVolume *Proximity_Shielding_vol = new TGeoVolume("Proximity_Shielding_vol", Proximity_Shielding, copper);
      tShield->AddNode(Proximity_Shielding_vol, 1, new TGeoTranslation(0, 0,  zEndOfProxShield -  Proximity_shield_half_length));

      // Absorber

      auto abs = new TGeoBBox("absorber",  4.995 * m -0.002*m, 3.75 * m, absorber_half_length - 0.2*cm);
      auto *absorber_shift = new TGeoTranslation("absorber_shift", 1.435 * m, 2.05 * m, 0);
      absorber_shift->RegisterYourself();

      const std::vector<TString> absorber_magnets = {"MagnAbsorb"};
      const std::vector<TString> magnet_components = {
        "_MiddleMagL", "_MiddleMagR",  "_MagRetL",    "_MagRetR",
        "_MagTopLeft", "_MagTopRight", "_MagBotLeft", "_MagBotRight",
    };
      TString absorber_magnet_components;
      for (auto &&magnet_component : magnet_components) {
	// format: "-<magnetName>_<magnet_component>:<translation>"
	absorber_magnet_components += ("-" + absorber_magnets[0] + magnet_component + ":" + mag_trans[0]->GetName());
      }
      TGeoCompositeShape *absorberShape = new TGeoCompositeShape(
	  "Absorber", "absorber:absorber_shift" + absorber_magnet_components); // cutting out
								// magnet parts
								// from absorber
      TGeoVolume *absorber = new TGeoVolume("AbsorberVol", absorberShape, iron);
      absorber->SetLineColor(42); // brown / light red
      tShield->AddNode(absorber, 1, new TGeoTranslation(0, 0, zEndOfProxShield + absorber_half_length )); // - Passive?

      auto *compRock = new TGeoCompositeShape("compRock",
                                              "rock - muon_shield_cavern:TCC8_shift"
                                              "- experiment_cavern:ECN3_shift"
                                              "- stair_step:stair_step_shift"
                                              "- yoke_pit:yoke_pit_shift"
                                              "- target_pit:target_pit_shift"
      );
      auto *Cavern = new TGeoVolume("Cavern", compRock, concrete);
      Cavern->SetLineColor(11);  // grey
      Cavern->SetTransparency(50);
      top->AddNode(Cavern, 1, new TGeoTranslation(0, 0, z_transition ));

}
