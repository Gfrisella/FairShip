// SPDX-License-Identifier: LGPL-3.0-or-later
// SPDX-FileCopyrightText: Copyright CERN for the benefit of the SHiP
// Collaboration

#ifndef STRAWTUBES_SSTSCORINGPLANE_H_
#define STRAWTUBES_SSTSCORINGPLANE_H_

#include "SSTScoringPoint.h"
#include "ScoringPlane.h"

/**
 * @brief Thin vacuum scoring plane in front of the first SST station
 *
 * Every track entering the plane produces one SSTScoringPoint (see
 * SHiP::ScoringPlane for what a point holds), so the flux reaching the
 * spectrometer can be studied without the straw hits. The plane is set with
 * AddPlane, from the geometry configuration.
 */
class SSTScoringPlane : public SHiP::ScoringPlane<SSTScoringPoint> {
 public:
  SSTScoringPlane(const char* Name, Bool_t Active);
  SSTScoringPlane();

 private:
  SSTScoringPlane(const SSTScoringPlane&) = delete;
  SSTScoringPlane& operator=(const SSTScoringPlane&) = delete;
};

#endif  // STRAWTUBES_SSTSCORINGPLANE_H_
