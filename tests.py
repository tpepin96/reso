from PIL import Image
import unittest as ut
import numpy as np
from resoboard import pR, pr, pY, py, pG, pg, pC, pc, pB, pb, pM, pm, _rgb_to_resel, _resel_to_rgb, ResoBoard

class DefaultPaletteTests(ut.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def test_bidirectionality(self):
        for rgb in _rgb_to_resel.keys():
            self.assertEqual(_resel_to_rgb[_rgb_to_resel[rgb]], rgb)
        for resel in _resel_to_rgb.keys():
            self.assertEqual(_rgb_to_resel[_resel_to_rgb[resel]], resel)

class ResoBoardInitTest(ut.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_resel_map(self):
        RB = ResoBoard("testing/test_01.png")
        self.assertEqual(RB._resel_map[0,0], pR)
        self.assertEqual(RB._resel_map[1,1], pR)
        self.assertEqual(RB._resel_map[2,2], pb)
        self.assertEqual(RB._resel_map[1,0], pm)
        self.assertEqual(RB._resel_map[2,0], 0)
        self.assertEqual(RB._resel_map[0,1], pG)
        self.assertEqual(RB._resel_map[2,4], pr)

    def test_region_map(self):
        RB = ResoBoard("testing/test_02.png")
        self.assertEqual(len(RB._RM._regions), 12)
        self.assertEqual(len(RB._RM.regions_with_class(pR)), 2)
        self.assertEqual(len(RB._RM.regions_with_class(pB)), 2)
        self.assertEqual(len(RB._RM.adjacent_regions(RB._RM.region_at_pixel(4,3))), 2)

    def test_object_lists(self):
        RB = ResoBoard("testing/test_02.png")
        self.assertEqual(len(RB._inputs),  4)
        self.assertEqual(len(RB._outputs), 4)
        self.assertEqual(len(RB._xors), 0)
        self.assertEqual(len(RB._ands), 0)

    def test_wires(self):
        RB = ResoBoard("testing/test_02.png")
        self.assertEqual(len(RB._red_wires),  2)
        self.assertEqual(len(RB._blue_wires), 2)
        self.assertEqual(RB._red_wires[0].state,  True)
        self.assertEqual(RB._red_wires[1].state,  True)
        self.assertEqual(RB._blue_wires[0].state, False)
        self.assertEqual(RB._blue_wires[1].state, False)

    def test_adjs(self):
        RB = ResoBoard("testing/test_02.png")
        # The wires
        longredwire = RB._RM.region_at_pixel(3,3)
        longbluwire = RB._RM.region_at_pixel(2,7)
        shortredwire = RB._RM.region_at_pixel(8,2)
        shortbluwire = RB._RM.region_at_pixel(9,2)
        # Left to right
        out_1 = RB._RM.region_at_pixel(2,5)
        out_2 = RB._RM.region_at_pixel(5,5)
        out_3 = RB._RM.region_at_pixel(8,3)
        out_4 = RB._RM.region_at_pixel(9,1)
        in_1 = RB._RM.region_at_pixel(2,6)
        in_2 = RB._RM.region_at_pixel(5,4)
        in_3 = RB._RM.region_at_pixel(8,1)
        in_4 = RB._RM.region_at_pixel(9,3)
        
        # Test adj_inputs
        self.assertEqual(RB._adj_inputs[longredwire][0].regionid, in_2)
        self.assertEqual(RB._adj_inputs[longbluwire][0].regionid, in_1)
        self.assertEqual(RB._adj_inputs[shortredwire][0].regionid, in_3)
        self.assertEqual(RB._adj_inputs[shortbluwire][0].regionid, in_4)
        
        # Test adj_xors, adj_ands
        for in_n in (in_1, in_2, in_3, in_4):
            # Should be empty
            self.assertEqual(RB._adj_xors[in_n], [])
            self.assertEqual(RB._adj_ands[in_n], [])

        # Test adj_outputs (for input nodes)
        self.assertEqual(RB._adj_outputs[in_1][0].regionid, out_1)
        self.assertEqual(RB._adj_outputs[in_2][0].regionid, out_2)
        self.assertEqual(RB._adj_outputs[in_3][0].regionid, out_4)
        self.assertEqual(RB._adj_outputs[in_4][0].regionid, out_3)
        
        # adj_outputs for logic nodes is empty
        
        # Test adj_wires for output nodes
        self.assertEqual(RB._adj_wires[out_1][0].regionid, longredwire)
        self.assertEqual(RB._adj_wires[out_2][0].regionid, longbluwire)
        self.assertEqual(RB._adj_wires[out_3][0].regionid, shortredwire)
        self.assertEqual(RB._adj_wires[out_4][0].regionid, shortbluwire)
        
        # TODO: Tests for xors and ands; Tests for elements with multiple adjacent nodes
    
    def test_reference(self):
        RB = ResoBoard("testing/test_02.png")
        # Make sure _resel_objects and, say, self._red_wires point to the same object
        regionid = RB._red_wires[0].regionid
        starting_state = RB._red_wires[0].state
        RB._red_wires[0].state = not starting_state
        
        self.assertEqual(RB._red_wires[0].state, RB._resel_objects[regionid].state)

    def test_sanity_01(self):
        # Make sure a number of the new functions run:
        RB = ResoBoard("testing/test_02.png")
        RB._update()

    def test_update(self):
        RB = ResoBoard("testing/test_03_01.png")
        # Turn on all the wires
        for wire in RB._red_wires + RB._blue_wires:
            wire.state = True
        # Update the image
        RB._update()
        # Load the 'all on' array to a new image
        fullRB = ResoBoard("testing/test_03_allon.png")
        im1 = fullRB.get_image()
        im2 = RB.get_image()
        self.assertTrue(np.array_equal(im1, im2))
        
        # Turn off all the wires
        for wire in RB._red_wires + RB._blue_wires:
            wire.state = False
        RB._update()
        im1 = RB.get_image()
        im3 = ResoBoard("testing/test_03_alloff.png").get_image()
        self.assertTrue(np.array_equal(im1, im3))
        
    def test_iterate_1(self):
        # Test a simple clock
        RB = ResoBoard("testing/test_02.png")
        im1 = np.swapaxes(Image.open("testing/test_02.png"),0,1)
        im2 = np.swapaxes(Image.open("testing/test_02_01.png"),0,1)[:,:,:3]
        
        self.assertTrue(np.array_equal(im1, RB.get_image()))
        RB.iterate()
        self.assertTrue(np.array_equal(im2, RB.get_image()))
        RB.iterate()
        self.assertTrue(np.array_equal(im1, RB.get_image()))
        RB.iterate()
        self.assertTrue(np.array_equal(im2, RB.get_image()))
        RB.iterate()
        self.assertTrue(np.array_equal(im1, RB.get_image()))
        
    def test_iterate_2(self):
        # Test using in-out gates as 'or'
        fn1 = "testing/test_05_01.png"
        fn2 = "testing/test_05_02.png"
        fn3 = "testing/test_05_03.png"
        fn4 = "testing/test_05_04.png"
        fn5 = "testing/test_05_05.png"
        fn6 = "testing/test_05_06.png"
        
        im1 = np.swapaxes(Image.open(fn1),0,1)[:,:,:3]
        im2 = np.swapaxes(Image.open(fn2),0,1)[:,:,:3]
        im3 = np.swapaxes(Image.open(fn3),0,1)[:,:,:3]
        im4 = np.swapaxes(Image.open(fn4),0,1)[:,:,:3]
        im5 = np.swapaxes(Image.open(fn5),0,1)[:,:,:3]
        im6 = np.swapaxes(Image.open(fn6),0,1)[:,:,:3]
        
        RB = ResoBoard(fn1)
        #Image.fromarray(np.swapaxes(RB.get_image(),0,1),'RGB').save("testing/debug_05_01.png")
        self.assertTrue(np.array_equal(im1, RB.get_image()))
        RB.iterate()
        #Image.fromarray(np.swapaxes(RB.get_image(),0,1),'RGB').save("testing/debug_05_02.png")
        self.assertTrue(np.array_equal(im2, RB.get_image()))
        RB.iterate()
        #Image.fromarray(np.swapaxes(RB.get_image(),0,1),'RGB').save("testing/debug_05_03.png")
        self.assertTrue(np.array_equal(im3, RB.get_image()))
        RB.iterate()
        #Image.fromarray(np.swapaxes(RB.get_image(),0,1),'RGB').save("testing/debug_05_04.png")
        self.assertTrue(np.array_equal(im4, RB.get_image()))
        RB.iterate()
        #Image.fromarray(np.swapaxes(RB.get_image(),0,1),'RGB').save("testing/debug_05_05.png")
        self.assertTrue(np.array_equal(im5, RB.get_image()))
        RB.iterate()
        #Image.fromarray(np.swapaxes(RB.get_image(),0,1),'RGB').save("testing/debug_05_06.png")
        self.assertTrue(np.array_equal(im6, RB.get_image()))
        RB.iterate()
        

    def test_iterate_3(self):
        # Test the steady-state values of each logic gate
        im = np.swapaxes(Image.open("testing/test_04.png"),0,1)[:,:,:3]
        RB = ResoBoard("testing/test_04.png")
        
        self.assertTrue(np.array_equal(im, RB.get_image()))
        RB.iterate()
        #Image.fromarray(np.swapaxes(RB.get_image(),0,1),'RGB').save("testing/debug_04_02.png")
        self.assertTrue(np.array_equal(im, RB.get_image()))
        RB.iterate()
        #Image.fromarray(np.swapaxes(RB.get_image(),0,1),'RGB').save("testing/debug_04_03.png")
        self.assertTrue(np.array_equal(im, RB.get_image()))
        RB.iterate()
        #Image.fromarray(np.swapaxes(RB.get_image(),0,1),'RGB').save("testing/debug_04_04.png")

    def test_iterate_4(self):
        fn1 = "testing/test_03_01.png"
        fn2 = "testing/test_03_02.png"
        fn3 = "testing/test_03_03.png"
        fn4 = "testing/test_03_04.png"
        
        # Images
        im1 = np.swapaxes(Image.open(fn1),0,1)[:,:,:3]
        im2 = np.swapaxes(Image.open(fn2),0,1)[:,:,:3]
        im3 = np.swapaxes(Image.open(fn3),0,1)[:,:,:3]
        im4 = np.swapaxes(Image.open(fn4),0,1)[:,:,:3]
        
        RB = ResoBoard(fn1)
        self.assertTrue(np.array_equal(im1, RB.get_image()))
        RB.iterate()
        
        self.assertTrue(np.array_equal(im2, RB.get_image()))
        RB.iterate()
        self.assertTrue(np.array_equal(im3, RB.get_image()))
        RB.iterate()
        self.assertTrue(np.array_equal(im4, RB.get_image()))


all_tests = [DefaultPaletteTests,
             ResoBoardInitTest]


for test in all_tests:
    ut.TextTestRunner(verbosity=2).run(ut.TestLoader().loadTestsFromTestCase(test))
