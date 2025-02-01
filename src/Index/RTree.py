import math
def format_mbr(mbr):
    return (min(mbr[0], mbr[2]),\
            min(mbr[1], mbr[3]),\
            max(mbr[0], mbr[2]),\
            max(mbr[1], mbr[3]))

def area_mbr(mbr):
    x = abs(mbr[2] - mbr[0])
    y = abs(mbr[3] - mbr[1])
    return x*y

def merge_mbr(mbr1, mbr2):
    if (mbr1 == None):
        return mbr2
    if (mbr2 == None):
        return mbr1
    mbr1 = format_mbr(mbr1)
    mbr2 = format_mbr(mbr2)
    return (min(mbr1[0], mbr2[0]), min(mbr1[1], mbr2[1]), \
            max(mbr1[2], mbr2[2]), max(mbr1[3], mbr2[3]),)

def central_point_mbr(mbr):
    return ((mbr[0] + mbr[2])/2.0, (mbr[1] + mbr[3])/2.0)

def decide_two_MBR(MBRT, MBR):
    T_lower_left, T_upper_right = (MBRT[0], MBRT[1]), (MBRT[2], MBRT[3])
    A_lower_left, A_upper_right = (MBR[0], MBR[1]), (MBR[2], MBR[3])

    if (T_lower_left[0] <= A_lower_left[0] and
        T_lower_left[1] <= A_lower_left[1] and
        T_upper_right[0] >= A_upper_right[0] and
        T_upper_right[1] >= A_upper_right[1]):
        return 1

    if not (T_upper_right[0] < A_lower_left[0] or
            T_lower_left[0] > A_upper_right[0] or
            T_upper_right[1] < A_lower_left[1] or
            T_lower_left[1] > A_upper_right[1]):
        return 2
    return 0

def distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
def farthest_points(points):
    max_distance = 0
    farthest_pair = None
    farthest_idx_pair = None
    for i in range(len(points)):
        for j in range(i+1, len(points)):
            d = distance(points[i], points[j])
            if d >= max_distance:
                max_distance = d
                farthest_pair = (points[i], points[j])
                farthest_idx_pair = (i, j)
    return farthest_pair, farthest_idx_pair

class RTreeNode:
    def __init__(self, M, parent=None):
        # Tree Structure
        self.M = M
        self.is_leaf = True
        self.parent = parent
        # (x1, y1, x2, y2)
        self.MBR = None
        # [(idx, mbr),...] or [(item_idx, (x1,y1,x2,y2))]
        self.children = [] 

    def required_enlargement(self, mbr):
        if (self.MBR == None):
            return area_mbr(mbr)
        return area_mbr(merge_mbr(self.MBR, mbr)) - area_mbr(self.MBR)

    def linear_pick_seeds(self):
        point_list = []
        for idx in range(len(self.children)):
            point_list.append(central_point_mbr(self.children[idx][1]))
        _, (candidate_1_idx, candidate_2_idx) = farthest_points(point_list)
        return candidate_1_idx, candidate_2_idx
     
    def split(self):    
        def distance_between_group_and_mbr(group, mbr):
            distance_total = 0
            for entry in group:
                distance_total += distance(central_point_mbr(entry[1]), central_point_mbr(mbr))
            return distance_total / len(group) 

        candidate_1_idx, candidate_2_idx = self.linear_pick_seeds()
        group1, group2 = [self.children[candidate_1_idx]], [self.children[candidate_2_idx]]

        self.children.pop(candidate_2_idx)
        self.children.pop(candidate_1_idx)
        
        while self.children:
            entry = self.children.pop(0) 
            group1.append(entry) if distance_between_group_and_mbr(group1, entry[1]) < distance_between_group_and_mbr(group2, entry[1]) else group2.append(entry)

        MBR_group1 = None 
        for idx in range(len(group1)):
            MBR_group1 = merge_mbr(MBR_group1, group1[idx][1])
        MBR_group2 = None 
        for idx in range(len(group2)):
            MBR_group2 = merge_mbr(MBR_group2, group2[idx][1])

        new_node = RTreeNode(self.M, self.parent)
        new_node.is_leaf = self.is_leaf
        new_node.children = group2
        new_node.MBR = MBR_group2
        self.children = group1
        self.MBR = MBR_group1

        return new_node

class RTree:
    def __init__(self, M):
        self.M = M
        self.node_list = [RTreeNode(M)]
        self.node_num = 1
        self.root_idx = 0

    def split(self, cur_node_idx):
        cur_node = self.node_list[cur_node_idx]
        new_node = cur_node.split()
        self.node_list.append(new_node)
        new_node_idx = self.node_num
        self.node_num += 1

        if not cur_node.parent:
            new_root = RTreeNode(self.M)
            new_root.is_leaf = False
            new_root.children = [(cur_node_idx, cur_node.MBR), (new_node_idx, new_node.MBR)]
            new_root.MBR = merge_mbr(cur_node.MBR, new_node.MBR)
            self.node_list.append(new_root)
            cur_node.parent = new_node.parent = self.node_num
            self.node_num += 1
        else:
            cur_parent_node_idx = cur_node.parent
            cur_parent_node = self.node_list[cur_parent_node_idx]
            cur_parent_node.children.append((new_node_idx, new_node.MBR))
            cur_parent_node.MBR = merge_mbr(cur_parent_node.MBR, new_node.MBR)
            if len(cur_parent_node.children) > self.M:
                self.split(cur_parent_node_idx)

    def insert(self, item):
        item = item[:1] + (format_mbr(item[1]), ) + item[2:]
        cur_node = self.node_list[self.root_idx]
        cur_node_idx = self.root_idx
        cur_node.MBR = merge_mbr(cur_node.MBR, item[1])
        while (cur_node.is_leaf == False):  
            # children [(idx, mbr)]
            min_enlargement = 1e10
            chosen_child_idx = None
            related_child_idx = None
            for idx, child_entries in enumerate(cur_node.children):
                child_node = self.node_list[child_entries[0]]
                enlargement_area = child_node.required_enlargement(item[1])
                if (min_enlargement > enlargement_area):
                    min_enlargement = enlargement_area
                    chosen_child_idx = child_entries[0]
                    related_child_idx = idx
            self.node_list[chosen_child_idx].MBR = merge_mbr(self.node_list[chosen_child_idx].MBR, item[1])
            cur_node.children[related_child_idx] = cur_node.children[related_child_idx][:1] + (self.node_list[chosen_child_idx].MBR,) + \
                                                     cur_node.children[related_child_idx][2:] 
            cur_node = self.node_list[chosen_child_idx]
            cur_node_idx = chosen_child_idx

        # item (item_idx, (x1,y1,x2,y2))
        cur_node.children.append(item)
        if len(cur_node.children) > self.M:
            self.split(cur_node_idx)

        while (self.node_list[self.root_idx].parent != None):
            self.root_idx = self.node_list[self.root_idx].parent

    def search(self, MBRQ, cur_node_idx = None):
        MBRQ = format_mbr(MBRQ)
        if (cur_node_idx == None):
            cur_node_idx = self.root_idx
        cur_node = self.node_list[cur_node_idx]
        item_list = []
        if cur_node.is_leaf:
            for item in cur_node.children:
                if (decide_two_MBR(item[1], MBRQ) != 0):
                    item_list.append(item)
            return item_list
        else:
            for child in cur_node.children:
                if (decide_two_MBR(child[1], MBRQ) != 0):
                    item_list += self.search(MBRQ, child[0])
        return item_list
    def debug(self, cur_node_idx = None):
        if (cur_node_idx == None):
            cur_node_idx = self.root_idx
        cur_node = self.node_list[cur_node_idx]
        print("----------")
        print("cur_node_idx", cur_node_idx, cur_node.M)
        print("cur_node_idx.parent", cur_node.parent)
        print("cur_node_idx.MBR", cur_node.MBR)
        print("is_leaf", cur_node.is_leaf)
        print("children", cur_node.children)
        print("----------")
        if (cur_node.is_leaf == False):
            for child in cur_node.children:
                self.debug(child[0])




if __name__ == "__main__":
    rtree = RTree(M=2)
    rtree.insert(('A', (0, 0, 1, 1))) 
    rtree.insert(('B', (2, 2, 2, 2)))
    rtree.insert(('C', (0, 0, 1.5, 1.5))) 
    rtree.insert(('D', (2.5, 2.5, 2, 2)))
    rtree.insert(('E', (0, 0, 2, 2))) 
    rtree.insert(('F', (3, 3, 2, 2)))
    print(rtree.search((2, 2, 2, 2)))
    # rtree.debug()
