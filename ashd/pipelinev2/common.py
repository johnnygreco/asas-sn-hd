import sep

# use sep to get a total listing of the objects from the given image `data`
def get_objs(data, byteswap = False):
    if byteswap: data = data.byteswap().newbyteorder()
    background = sep.Background(data)
    dsub = data - background
    objects = sep.extract(dsub, 1.5, err=background.globalrms)
    return (objects, dsub, background)

# basically, corners in the ASAS-SN data are borked
# this function culls any objects in those regions
def cut_corners(objlist, thresh=30, size=[2048, 2048]):
    for i in objlist:
        x = i['x']; y = i['y']
        if not (x < thresh and y < thresh) and not (x > (size[0] - thresh) and y < thresh):
            if not (x < thresh and y > (size[1] - thresh)) and not (x > (size[0] - thresh) and y > (size[1] - thresh)):
                yield i