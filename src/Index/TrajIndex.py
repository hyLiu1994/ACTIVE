# Latitude [-90, 90]
# Longitude [-180, 180]

def getChildArea(childID, pointA, pointB):
    lowx = pointA[0]
    lowy = pointA[1]
    highx = pointB[0]
    highy = pointB[1]
    midx = pointA[0] + (pointB[0] - pointA[0]) / 2.0
    midy = pointA[1] + (pointB[1] - pointA[1]) / 2.0
    if (childID == 0):
        return [lowx, midy], [midx, highy]
    if (childID == 1):
        return [midx, midy], [highx, highy]
    if (childID == 2):
        return [lowx, lowy], [midx, midy]
    if (childID == 3):
        return [midx, lowy], [highx,midy] 

def decide_point_area(pointT, pointA, pointB):
    if (pointT[0] >= pointA[0] and pointT[0] < pointB[0] and pointT[1] >= pointA[1] and pointT[1] < pointB[1]):
        return True
    return False

def decide_two_area(pointTA, pointTB, pointA, pointB):
    T_lower_left, T_upper_right = pointTA, pointTB
    A_lower_left, A_upper_right = pointA, pointB

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

def merge_continuous_elements(lst):
    result = []
    temp = [lst[0]]

    for i in range(1, len(lst)):
        if lst[i] == lst[i - 1] + 1:
            temp.append(lst[i])
        else:
            result.append([temp[0], temp[-1]])
            temp = [lst[i]]

    result.append([temp[0], temp[-1]])
    return result

def merge_dicts(dict1, dict2):
    for key, value in dict2.items():
        if key in dict1:
            dict1[key] += value
        else:
            dict1[key] = value

    return dict1

class TrajIndex():
    def __init__(self, pointA = [-90, -180], pointB = [90, 180], min_latitude=1, dep=1, MaxNumberPoint=100):
        self.min_latitude = min_latitude
        self.pointA = pointA
        self.pointB = pointB
        self.dep = dep
        self.childNode = [0,0,0,0]
        self.NodeInfo = {}
        self.NumberPoint = 0
        self.MaxNumberPoint = MaxNumberPoint
        # print(pointA, pointB, dep)

    def search_traj_list(self, MBR):
        pointTA, pointTB = (MBR[0], MBR[1]), (MBR[2], MBR[3])
        decide_area_result = decide_two_area(pointTA, pointTB, self.pointA, self.pointB)

        if (decide_area_result == 1 or (decide_area_result == 2 and self.pointB[0] - self.pointA[0] <= self.min_latitude)):
            return self.NodeInfo 
        if (decide_area_result == 0):
            return {}
        NodeInfo = {}
        for i in range(4):
            tmpInfo = {}
            if (self.childNode[i] == 0):
                continue
            tmpInfo = self.childNode[i].search_traj_list(MBR)
            if len(tmpInfo) != 0:
                NodeInfo = merge_dicts(NodeInfo, tmpInfo)

        return NodeInfo

    def del_Traj_Base_TrajID(self, TrajID):
        if TrajID not in self.NodeInfo:
            return
        del self.NodeInfo[TrajID]

        for i in range(4):
            if (self.childNode[i] == 0):
                continue
            self.childNode[i].del_Traj_Base_TrajID(TrajID)

    def Add_TrajRange(self, TrajID, TrajRange, TrajSequence):
        if (self.pointB[0] - self.pointA[0] > self.min_latitude and 
            self.NumberPoint + TrajRange[1] - TrajRange[0] + 1 > self.MaxNumberPoint):
            for i in range(4):
                c_pointA, c_pointB = getChildArea(i, self.pointA, self.pointB)
                point_list = []
                for idx in range(TrajRange[0], TrajRange[1]+1):
                    if (decide_point_area(TrajSequence[idx], c_pointA, c_pointB)):
                        point_list.append(idx)
                if (len(point_list) == 0):
                    continue

                Range_list = merge_continuous_elements(point_list)

                if (self.childNode[i] == 0):
                    self.childNode[i] = TrajIndex(pointA = c_pointA, pointB = c_pointB, min_latitude=self.min_latitude, dep = self.dep + 1, MaxNumberPoint=self.MaxNumberPoint)
                for idx in range(len(Range_list)):
                    self.childNode[i].Add_TrajRange(TrajID, Range_list[idx], TrajSequence)

        self.NumberPoint += TrajRange[1] - TrajRange[0] + 1
        if (TrajID not in self.NodeInfo):
            self.NodeInfo[TrajID] = [TrajRange]
        else:
            if (self.NodeInfo[TrajID][-1][1] == TrajRange[0] - 1):
                self.NodeInfo[TrajID][-1][1] = TrajRange[1]
                return 
            if (self.NodeInfo[TrajID][-1][0] < TrajRange[0]):
                self.NodeInfo[TrajID].append(TrajRange)
                return
            for i in range(len(self.NodeInfo[TrajID])):
                if (self.NodeInfo[TrajID][i][1] == TrajRange[0] - 1):
                    self.NodeInfo[TrajID][i][1] = TrajRange[1]
                    return
                if (self.NodeInfo[TrajID][i][0] > TrajRange[0]):
                    self.NodeInfo[TrajID].insert(i, TrajRange) 
                    return
            