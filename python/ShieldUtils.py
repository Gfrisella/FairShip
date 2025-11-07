def find_offset(ship_geo):
    return ship_geo.muShield.Z[0]

def find_shield_center(ship_geo):
    return ship_geo.muShield.z + ship_geo.muShield.length/2
