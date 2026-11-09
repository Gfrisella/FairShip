// SPDX-License-Identifier: LGPL-3.0-or-later
// SPDX-FileCopyrightText: Copyright CERN for the benefit of the SHiP
// Collaboration

#include "SSTScoringPoint.h"

#include "FairLogger.h"

// -----   Default constructor   -------------------------------------------
SSTScoringPoint::SSTScoringPoint() : SHiP::DetectorPoint() {}
// -------------------------------------------------------------------------

// -----   Destructor   ----------------------------------------------------
SSTScoringPoint::~SSTScoringPoint() = default;
// -------------------------------------------------------------------------

void SSTScoringPoint::extraPrintInfo() const {
  LOG(info) << "SST scoring plane " << GetDetectorID()
            << ", in front of SST station 1";
}
