# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

from enum import Enum

class Model(Enum):
    """
    References the model of the printer.
    """

    def from_int(v:int):
        try:
            return Model(v)
        except ValueError:
            return Model.INVALID

    INVALID = 0
    Evolis_KC100 = 1
    Evolis_KC100B = 2
    Evolis_KC200 = 3
    Evolis_KC200B = 4
    Evolis_KM500B = 5
    Evolis_KM2000B = 6
    Evolis_Primacy = 7
    Evolis_Altess = 8
    Evolis_Altess_Elite = 9
    BadgePass_Connect = 10
    BadgePass_NXT5000 = 11
    ID_Maker_Primacy = 12
    Evolis_Elypso = 13
    ID_Maker_Elypso = 14
    Evolis_Zenius = 15
    ID_Maker_Zenius = 16
    Evolis_Apteo = 17
    BadgePass_Connect_Lite = 18
    Durable_Duracard_ID_300 = 19
    Edikio_Access = 20
    Edikio_Flex = 21
    Edikio_Duplex = 22
    Evolis_Badgy100 = 23
    Evolis_Badgy200 = 24
    Bodno_Badgy100X = 25
    Bodno_Badgy200X = 26
    Evolis_Lamination_Module = 27
    Evolis_KC_Essential = 28
    Evolis_KC_Prime = 29
    Evolis_KC_Max = 30
    Evolis_Primacy_2 = 31
    Evolis_Asmi = 32
    BadgePass_NXTElite = 33
    BadgePass_CONNECTplus = 34
    ID_Maker_Primacy_Infinity = 35
    Plasco_Primacy_2_LE = 36
    Identisys_Primacy_2_SE = 37
    BRAVO_DC_3300 = 38
    Evolis_Avansia = 39
    Evolis_Agilia = 40
    Evolis_Quantum2 = 41
