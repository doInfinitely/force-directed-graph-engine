import math

def quadratic(a, b, c):
    #print a,b,c
    if a == 0 and b != 0:
        return tuple([-1*c / (1.0*b)])
    elif b == 0 and a != 0:
        return -1*math.sqrt(-1*c/a),math.sqrt(-1*c/a)
    try:
        disc = math.sqrt(b**2 - 4*a*c)
    except ValueError:
        return None, None
    try:
        val1 = (-1*b - disc) / (2.0*a)
    except ZeroDivisionError:
        val1 = None
    try:
        val2 = (-1*b + disc) / (2.0*a)
    except ZeroDivisionError:
        val2 = None
    return val1, val2

def prune(input):
    if len(input) == 1:
        return input[0]
    elif min(input) >= 0:
        return min(input)
    else:
        return max(input)




#input is an array of dictionaries. each dictionary represents a point and contains three keys:
# 'pos' position vector
# 'vel' velocity vector
# 'rad' radius function
# dimension is the other input
# optional argument 1 is a mask that determines which points have to have their collisions recomputed
# other optional argument is a collision dictionary to populate
#engulf checks for when one particle is contained in another instead of just an edge collision
def collide(dim, points, mask = None, coll = None, engulf = False):
    ordered = []
    if mask == None:
    	mask = set()
    if not coll:
        coll = dict()
    count = 0
    for i in set(points.keys())-mask:
        for j in points:
            if i != j and (not mask or i not in mask or j not in mask):
                count += 1
                a = 0
                b = 0
                c = 0
                for k in range(dim):
                    a += (points[i]['vel'][k] - points[j]['vel'][k])**2
                    b += 2*(points[i]['vel'][k] - points[j]['vel'][k])*(points[i]['pos'][k] - points[j]['pos'][k])
                    c += (points[i]['pos'][k] - points[j]['pos'][k])**2
                
                a -= (points[i]['rad'][1] + (1-2*engulf)*points[j]['rad'][1])**2
                b -= 2*(points[i]['rad'][1] + (1-2*engulf)*points[j]['rad'][1])*(points[i]['rad'][0] + (1-2*engulf)*points[j]['rad'][0])
                c -= (points[i]['rad'][0] + (1-2*engulf)*points[j]['rad'][0])**2
                coll[frozenset([ i,j ])] = quadratic(a,b,c)
                k = 0
                while k < len(ordered) and prune(coll[ordered[k]]) <= prune(coll[frozenset([ i,j ])] ) and prune(coll[ordered[k]]) != None:
                    k += 1
                if prune(coll[frozenset([ i,j ])] ) == None:
                    k = len(ordered)
                ordered.insert(k, frozenset([ i,j ]) )
    print count, ( len(points)-len(mask) ) * len(points)
    return coll, ordered
if __name__ == "__main__":
    #particle, starting at (0,2), with velocity of (0,-1) and starting radius 0 expanding at a rate of 1 unit-distance/unit-time
    temp = dict()
    temp['pos'] = [0,2]
    temp['vel'] = [0,-1]
    temp['rad'] = [1,0]
    temp['ID'] = 0
    points = dict()
    points[temp['ID']] = temp


    #particle, starting at (0,-2), with velocity of (0,1) and starting radius 0 expanding at a rate of 1 unit-distance/unit-time
    temp = dict()
    temp['pos'] = [0,-2]
    temp['vel'] = [0,1]
    temp['rad'] = [.5,0]
    temp['ID'] = 1

    points[temp['ID']] = temp
    print collide(2,points,engulf=True)
