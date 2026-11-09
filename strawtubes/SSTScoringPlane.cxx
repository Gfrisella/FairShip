// SPDX-License-Identifier: LGPL-3.0-or-later
// SPDX-FileCopyrightText: Copyright CERN for the benefit of the SHiP
// Collaboration

#include "SSTScoringPlane.h"

#include "ShipDetectorList.h"

SSTScoringPlane::SSTScoringPlane()
    : ScoringPlane("SSTScoringPlane", kTRUE, kSSTScoringPlane) {}

SSTScoringPlane::SSTScoringPlane(const char* name, Bool_t active)
    : ScoringPlane(name, active, kSSTScoringPlane) {}
