#  **********************************************************************
#  Copyright (C) 2020 Johns Hopkins University Applied Physics Laboratory
#
#  All Rights Reserved.
#  For any other permission, please contact the Legal Office at JHU/APL.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#  **********************************************************************

import json


class TaxonomicHierarchy(object):
    """
    Construct taxonomic hierarchy tree for sunburst visualization
    """
    class Node(object):
        def __init__(self, taxid: int, name: str, rank: str, abundance: float or None):
            self.taxid = taxid
            self.name = name
            self.rank = rank
            self.abundance = abundance
            self.children = []

    def __init__(self, root: Node):
        self.tree = root
        self.ranks = []

    def to_dict(self):
        return json.loads(json.dumps(self.tree, default=lambda o: o.__dict__))

    def add_child_to_tree(self, parent: Node, child: Node):
        self.tree = self._add_child_in_tree_(tree=self.tree, parent=parent, child=child)

        if child.rank not in self.ranks:
            self.ranks.append(child.rank)

    @staticmethod  # recursive
    def _add_child_in_tree_(tree: Node, parent: Node, child: Node):
        if tree.taxid == parent.taxid:
            if child.taxid not in [c.taxid for c in tree.children]:
                tree.children.append(child)
        else:
            for subtree in tree.children:
                TaxonomicHierarchy._add_child_in_tree_(tree=subtree, parent=parent, child=child)
        return tree
