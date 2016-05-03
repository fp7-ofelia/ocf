"""
Mapper to bind URN of image with basic parameters (image path, HD setup and
virtualisation setup).

@date: April 8, 2016
@author: CarolinaFernandez
"""

from geniutils.src.xrn.xrn import hrn_to_urn
from geniutils.src.xrn.xrn import urn_to_hrn

class ReservationMapper(object):

    @staticmethod
    def get_template_info_from_urn(urn, cm=""):
        # print "\n\n\n\n\n\nurn=", urn
        # print "cm=", cm
        hrn_cm = ""
        hrn = urn_to_hrn(urn)
        # print "*** hrn: ", hrn
        # 1. Obtain CM from URN, otherwise 2. Obtain CM from argument tuple
        if isinstance(cm, str) and len(cm) > 0:
            hrn_cm = cm.split(".")[1]
        elif isinstance(cm, tuple):
            hrn_cm = hrn[0].split(".")[1]
        # print "\n\n\n\n\n\nhrn_cm=", hrn_cm
        # Base URN: "urn:publicid:IDN+i2cat+image+emulab"
        # URN for Emulab image: "urn:publicid:IDN+i2cat+image+emulab:Debian604-64b"
        debian6_path = "legacy/legacy.tar.gz"
        debian6_urn = ReservationMapper.get_template_urn(hrn_cm, "Debian604-64b")
        debian7_path = "debian7/debian7.img"
        # URN for Emulab image: "urn:publicid:IDN+i2cat+image+emulab:Debian7-64b"
        debian7_urn = ReservationMapper.get_template_urn(hrn_cm, "Debian7-64b")
        ubuntu14_path = "ubuntu/ubuntu14.img"
        # URN for Emulab image: "urn:publicid:IDN+i2cat+image+emulab:Ubuntu1404-64b"
        ubuntu14_urn = ReservationMapper.get_template_urn(hrn_cm, "Ubuntu1404-64b")
        irati_path = "irati/irati.img"
        # URN for Emulab image: "urn:publicid:IDN+i2cat+image+emulab:IRATI"
        irati_urn = ReservationMapper.get_template_urn(hrn_cm, "IRATI")
        disk_image_alternatives = {
            debian6_urn: {
                "img-path": debian6_path,
                "hd-setup": "file-image",
                "virt-setup": "paravirtualization",
            },
            debian7_urn: {
                "img-path": debian7_path,
                "hd-setup": "full-file-image",
                "virt-setup": "hvm",
            },
            ubuntu14_urn: {
                "img-path": ubuntu14_path,
                "hd-setup": "full-file-image",
                "virt-setup": "hvm",
            },
            irati_urn: {
                "img-path": irati_path,
                "hd-setup": "full-file-image",
                "virt-setup": "hvm",
            },
        }
        DEFAULT_IMG_URN = debian6_urn

        try:
            print "\n\n\n\n\n disk_image_alternatives: ", disk_image_alternatives
            return disk_image_alternatives[urn]
        except:
            return disk_image_alternatives[DEFAULT_IMG_URN]

    @staticmethod
    def get_template_urn(hrn_cm, image_name):
        hrn_type = "image"
        return hrn_to_urn("%s.emulab:%s" % (hrn_cm, image_name), hrn_type)

    @staticmethod
    def translate_disk_image(urn, cm):
        return ReservationMapper.get_template_from_urn(urn, cm)

    @staticmethod
    def check_memory(memory):
        MAX_MEMORY = 1024
        DEFAULT_IMG_MEMORY = 512
        memory_mb = DEFAULT_IMG_MEMORY
        try:
            memory_mb = int(memory or 0)
            if memory_mb <= 0:
                memory_mb = DEFAULT_IMG_MEMORY
            elif memory_mb > MAX_MEMORY:
                memory_mb = MAX_MEMORY
        except:
            pass
        # print "\n\n\n\nMEMORY (mb): ", memory_mb
        return memory_mb
