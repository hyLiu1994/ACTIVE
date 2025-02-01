from Index.RTree import RTree

class SVTI(RTree):
    def __init__(self, M):
        super().__init__(M) 

    def search_traj_list(self, MBR, endFlag=True):
        mark_dict = {}
        search_result = self.search(MBR)
        for idx in range(len(search_result)):
            shipId = search_result[idx][0][0]
            segId = search_result[idx][0][1]
            if (shipId not in mark_dict):
                mark_dict[shipId] = segId
            else:
                if (endFlag):
                    mark_dict[shipId] = max(mark_dict[shipId], segId)
                else:
                    mark_dict[shipId] = min(mark_dict[shipId], segId)
        return mark_dict 

if __name__ == "__main__":
    rtree = SVTI(M=2)
    rtree.insert((('A', 3), (0, 0, 1, 1))) 
    rtree.insert((('B', 3), (2, 2, 2, 2)))
    rtree.insert((('C', 1), (0, 0, 1.5, 1.5))) 
    rtree.insert((('D', 1), (2.5, 2.5, 2, 2)))
    rtree.insert((('E', 1), (0, 0, 2, 2))) 
    rtree.insert((('B', 4), (3, 3, 2, 2)))
    print(rtree.search((2, 2, 2, 2)))
    print(rtree.search_traj_list((2, 2, 2, 2), endFlag=False))
    # rtree.debug()
