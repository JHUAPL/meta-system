#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#  **********************************************************************
import unittest

from system.utils.biology import TaxonomicHierarchy


class TestTaxonomicHierarchy(unittest.TestCase):
    def setUp(self) -> None:
        self.tree = None
        pass

    def test_node_init(self):
        root_node = TaxonomicHierarchy.Node(taxid=12345, name="organism", rank="phylum", abundance=0.56)

        self.assertEqual(root_node.taxid, 12345)
        self.assertEqual(root_node.name, "organism")
        self.assertEqual(root_node.rank, "phylum")
        self.assertEqual(root_node.abundance, 0.56)

    def test_init(self):
        root_node = TaxonomicHierarchy.Node(taxid=12345, name="organism", rank="phylum", abundance=0.56)
        th = TaxonomicHierarchy(root=root_node)

        self.assertEqual(th.tree.taxid, 12345)
        self.assertEqual(th.tree.name, "organism")
        self.assertEqual(th.tree.rank, "phylum")
        self.assertEqual(th.tree.abundance, 0.56)
        self.assertEqual(th.ranks, [])

    def test_to_dict(self):
        pass

    def tearDown(self) -> None:
        pass
