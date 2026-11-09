// SPDX-License-Identifier: LGPL-3.0-or-later
// SPDX-FileCopyrightText: Copyright CERN for the benefit of the SHiP
// Collaboration

#ifndef STRAWTUBES_SSTSCORINGPOINT_H_
#define STRAWTUBES_SSTSCORINGPOINT_H_

#include "DetectorPoint.h"

/**
 * @brief Track crossing of the vacuum scoring plane in front of SST station 1
 *
 * Position, momentum and time are those at the end of the track's first step
 * in the plane.
 */
class SSTScoringPoint : public SHiP::DetectorPoint {
 public:
  /** Default constructor **/
  SSTScoringPoint();

  using SHiP::DetectorPoint::DetectorPoint;
  /** Destructor **/
  ~SSTScoringPoint() override;

  void extraPrintInfo() const override;

 private:
  ClassDefOverride(SSTScoringPoint, 1)
};

#endif  // STRAWTUBES_SSTSCORINGPOINT_H_
