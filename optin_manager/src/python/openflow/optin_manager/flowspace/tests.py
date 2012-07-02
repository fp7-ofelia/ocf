from expedient.common.tests.manager import SettingsTestCase
from openflow.optin_manager.flowspace.models import FlowSpace
from openflow.optin_manager.flowspace.helper import single_fs_intersect,\
multi_fs_intersect, singlefs_is_subset_of, multifs_is_subset_of
from openflow.optin_manager.opts.models import OptsFlowSpace

class Tests(SettingsTestCase):
    
    def setUp(self):
        pass
    
    def test_single_fs_intersection(self):
        f1 = FlowSpace(ip_src_s=10, ip_src_e=10)
        f2 = FlowSpace(ip_dst_s=10, ip_dst_e=10)
        f3 = FlowSpace(ip_src_s=10, ip_src_e=10, mac_src_s = 20, mac_src_e=30)
        fi = single_fs_intersect(f1,f2,FlowSpace)
        self.assertNotEqual(fi,None)
        self.assertEqual(fi.ip_src_s,10)
        self.assertEqual(fi.ip_src_e,10)
        self.assertEqual(fi.ip_dst_s,10)
        self.assertEqual(fi.ip_dst_e,10)
        fi = single_fs_intersect(f1,f3,FlowSpace)
        self.assertNotEqual(fi,None)
        self.assertEqual(fi.ip_src_s,10)
        self.assertEqual(fi.ip_src_e,10)
        self.assertEqual(fi.mac_src_s,20)
        self.assertEqual(fi.mac_src_e,30)
        
        f4 = FlowSpace(ip_src_s=30, ip_src_e=40, mac_src_s = 50, mac_src_e=60,
                       ip_dst_s=70, ip_dst_e=80, mac_dst_s = 90, mac_dst_e=100,)
        f5 = FlowSpace(ip_src_s=35, ip_src_e=45, mac_src_s = 55, mac_src_e=65,
                       ip_dst_s=75, ip_dst_e=85, mac_dst_s = 95, mac_dst_e=105,)
        f6 = FlowSpace(ip_src_s=35, ip_src_e=45, vlan_id_s = 55, vlan_id_e=65,
                       ip_dst_s=75, ip_dst_e=85, mac_dst_s = 65, mac_dst_e=75,)
        fi = single_fs_intersect(f4,f5,FlowSpace)
        self.assertNotEqual(fi,None)
        self.assertEqual(fi.ip_src_s,35)
        self.assertEqual(fi.ip_src_e,40)
        self.assertEqual(fi.mac_src_s,55)
        self.assertEqual(fi.mac_src_e,60)
        self.assertEqual(fi.ip_dst_s,75)
        self.assertEqual(fi.ip_dst_e,80) 
        self.assertEqual(fi.mac_dst_s,95)
        self.assertEqual(fi.mac_dst_e,100) 
        fi = single_fs_intersect(f5,f6,FlowSpace)
        self.assertEqual(fi,None)
        
    def test_multi_fs_intersect(self):
        f1 = OptsFlowSpace(dpid="00:00:00:00:00:00:01",ip_src_s=10, ip_src_e=20,)
        f2 = OptsFlowSpace(dpid="00:00:00:00:00:00:01",port_number_s = 2,
                           port_number_e=5, ip_src_s=10, ip_src_e=10,)
        f3 = OptsFlowSpace(dpid="00:00:00:00:00:00:02",ip_src_s=10, ip_src_e=20,)
        f4 = OptsFlowSpace(dpid="00:00:00:00:00:00:02",ip_dst_s=15, ip_dst_e=25,)
        fi = multi_fs_intersect([f1,f3], [f2,f4], OptsFlowSpace, True)
        self.assertNotEqual(fi,None)
        self.assertEqual(len(fi),2)
        
        if fi[0].dpid=="00:00:00:00:00:00:01":
            self.assertEqual(fi[0].port_number_s,2)
            self.assertEqual(fi[0].port_number_e,5)
            self.assertEqual(fi[0].ip_src_s,10)
            self.assertEqual(fi[0].ip_src_e,10)
            self.assertEqual(fi[1].ip_src_s,10)
            self.assertEqual(fi[1].ip_src_e,20)
            self.assertEqual(fi[1].ip_dst_s,15)
            self.assertEqual(fi[1].ip_dst_e,25)
        else:
            self.assertEqual(fi[1].port_number_s,2)
            self.assertEqual(fi[1].port_number_e,5)
            self.assertEqual(fi[1].ip_src_s,10)
            self.assertEqual(fi[1].ip_src_e,10)
            self.assertEqual(fi[0].ip_src_s,10)
            self.assertEqual(fi[0].ip_src_e,20)
            self.assertEqual(fi[0].ip_dst_s,15)
            self.assertEqual(fi[0].ip_dst_e,25)
            
    def test_singlefs_is_subset_of(self):
       
        f1 = FlowSpace(ip_src_s=10, ip_src_e=10)
        f2 = FlowSpace(ip_dst_s=10, ip_dst_e=10)
        f3 = FlowSpace(ip_src_s=10, ip_src_e=10, mac_src_s = 20, mac_src_e=30)

        
        self.assertTrue(singlefs_is_subset_of(f1,[f1]))
        self.assertFalse(singlefs_is_subset_of(f1,[f2]))
        self.assertTrue(singlefs_is_subset_of(f1,[f1,f2]))
        self.assertTrue(singlefs_is_subset_of(f3,[f1]))
        self.assertFalse(singlefs_is_subset_of(f1,[f3]))
        
        f4 = FlowSpace(mac_dst_s = 90, mac_dst_e=100,)
        f5 = FlowSpace(mac_dst_s = 100, mac_dst_e=100,)
        self.assertTrue(singlefs_is_subset_of(f5,[f4]))
        
        
        f6 = FlowSpace(ip_src_s=30, ip_src_e=40, mac_src_s = 50, mac_src_e=60,
                       ip_dst_s=70, ip_dst_e=70, mac_dst_s = 90, mac_dst_e=100,)
        f7 = FlowSpace(ip_src_s=35, ip_src_e=40, mac_src_s = 50, mac_src_e=60,
                       ip_dst_s=70, ip_dst_e=70, mac_dst_s = 100, mac_dst_e=100,)
        f8 = FlowSpace(ip_src_s=35, ip_src_e=40, mac_src_s = 50, mac_src_e=60,
                       ip_dst_s=70, ip_dst_e=70, mac_dst_s = 95, mac_dst_e=105,)
        self.assertTrue(singlefs_is_subset_of(f7,[f6]))
        self.assertFalse(singlefs_is_subset_of(f8,[f7]))
        
        f9 = FlowSpace(ip_src_s=1, ip_src_e=1, mac_src_s = 2, mac_src_e=2,
                       ip_dst_s=3, ip_dst_e=3, mac_dst_s = 4, mac_dst_e=4,)
        f10 = FlowSpace(ip_src_s=1, ip_src_e=2, mac_src_s = 1, mac_src_e=2,
                       ip_dst_s=3, ip_dst_e=3, mac_dst_s = 3, mac_dst_e=5,)
        f11 = FlowSpace(ip_src_s=2, ip_src_e=2, mac_src_s = 2, mac_src_e=2,
                       ip_dst_s=3, ip_dst_e=3, mac_dst_s = 3, mac_dst_e=5,)
        self.assertTrue(singlefs_is_subset_of(f9,[f9]))
        self.assertTrue(singlefs_is_subset_of(f9,[f10]))
        self.assertFalse(singlefs_is_subset_of(f9,[f11]))
        
        f12 = FlowSpace(ip_src_s=1, ip_src_e=4, mac_src_s = 2, mac_src_e=5,
                       ip_dst_s=3, ip_dst_e=6, mac_dst_s = 4, mac_dst_e=7,)
        f13 = FlowSpace(ip_src_s=1, ip_src_e=2, mac_src_s = 2, mac_src_e=3,
                       ip_dst_s=3, ip_dst_e=4, mac_dst_s = 4, mac_dst_e=5,)
        f14 = FlowSpace(ip_src_s=3, ip_src_e=4, mac_src_s = 4, mac_src_e=5,
                       ip_dst_s=5, ip_dst_e=6, mac_dst_s = 6, mac_dst_e=7,)
        f15 = FlowSpace(ip_src_s=1, ip_src_e=4)
        f16 = FlowSpace(ip_src_s=1, ip_src_e=2)
        f17 = FlowSpace(ip_src_s=3, ip_src_e=4)
        self.assertFalse(singlefs_is_subset_of(f12,[f13,f14]))
        self.assertTrue(singlefs_is_subset_of(f15,[f16,f17]))
        
    def test_multifs_is_subset_of(self):
        f1 = FlowSpace(ip_src_s=2, ip_src_e=4)
        f2 = FlowSpace(ip_src_s=5, ip_src_e=9)
        f3 = FlowSpace(ip_src_s=1, ip_src_e=6)
        f4 = FlowSpace(ip_src_s=7, ip_src_e=11)  
        self.assertTrue(multifs_is_subset_of([f1,f2],[f3,f4]))
        
            