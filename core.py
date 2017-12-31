#!/usr/bin/env python
# encoding: utf-8


import Image,sys,math,os,time

def isSimilarColor(base_color, color, ratio):
    #print type(base_color)
    #print type(color)
    c = map(lambda x,y:abs(x-y), base_color, color)
    return max(c[:-1])<=ratio

def highlightPoint(region, pos, color):
    (width,height) = region.size
    for w in range(0,width):
        region.putpixel((w, pos[1]), color)
    for h in range(0,height):
        region.putpixel((pos[0], h), color)
  

def findStartPos(region):
    (width,height) = region.size
    # start pos must be the downer half screen
    pos = [0,0]
    for h in range(height/2, height):
        for w in range(0,width):
            p = region.getpixel((w,h))
            if isSimilarColor((55,55,90,255),p,5):
                pos[0] = w
                pos[1] = h
    return pos

def findEndPos(region, halfscreen):
    (width,height) = region.size
    offset=10
    row = [0]*(height/2)
    end_pos = [0,0]
    for h in range(0, height/2):
        # first dot is base color
        firstdot = region.getpixel((0,h))
        start_pos = 0
        max_distance = 0
        mid_pos=[0,0]
        for w in range(0, width):
            p = region.getpixel((w,h))
            isSame = isSimilarColor(firstdot, p, 0)
            if start_pos==0 and isSame==False:# start pos
                start_pos = w
            if start_pos!=0 and isSame:# stop pos
                # here we strict the end case must satisfiy NextN==firstdot
                isNextNSame=True
                for sw in range(w+1,width):
                    sp = region.getpixel((sw,h))
                    isNextNSame = isNextNSame and isSimilarColor(firstdot, sp, 0)
                    if isNextNSame==False:
                        break
                    if sw-w > offset:
                        break
                if isNextNSame:
                    distance = w-start_pos           
                    if distance > max_distance:
                        max_distance = distance
                        mid_pos[0] = (w+start_pos)/2
                        mid_pos[1] = h
                    start_pos = 0
                else:
                    continue
        #save the cal result in row
        row[h] = max_distance
        #judge if we find the end pos
        if h < 3:
            continue
        if row[h]!=0 and row[h-1]>=row[h] and row[h-2]>=row[h] and row[h-3]>=row[h]:
            end_pos[0] = mid_pos[0]
            end_pos[1] = mid_pos[1] - 3;
            if halfscreen=="right" and end_pos[0] < width/2:
                continue
            if halfscreen=="left" and end_pos[0] > width/2:
                continue
            break
    return tuple(end_pos)

def imageFilter(im):
    (width,height) = im.size
    shadow_param = 1.4
    print 'process.....'
    for h in range(0, height):
        firstdot = im.getpixel((0,h))
        shadowdot = tuple( x/shadow_param for x in firstdot)
        for w in range(0, width):
            p = im.getpixel((w,h))
            if isSimilarColor(firstdot, p, 10):
                im.putpixel((w,h), firstdot)
            if isSimilarColor(shadowdot, p, 30):
                im.putpixel((w,h), firstdot)
    

def run():
    os.system("adb shell screencap -p /sdcard/screenshot.png")
    os.system("adb pull sdcard/screenshot.png")
    im = Image.open('screenshot.png')
    im_resize = im.resize((im.size[0]/2, im.size[1]/2))
    (width, height) = im_resize.size
    print '/* width %d */ ' % width
    print '/* height %d */ ' % height 

    region = im_resize.crop((0, (height-width)/2, width-1, (height-width)/2+width-1))
    halfscreen = ""

    imageFilter(region)
    start = findStartPos(region)
    
    if start[0]<width/2:
        halfscreen="right"
    else:
        halfscreen="left"
    stop = findEndPos(region, halfscreen)
    highlightPoint(region,start, (255,0,0,255))
    highlightPoint(region,stop,(0,255,0,255))
    region.save("output.png")
    
    distance = math.pow((start[0]-stop[0]), 2) + math.pow((start[1]-stop[1]),2)
    distance = math.sqrt(distance)
    print start,stop,distance
    os.system("adb shell input swipe 540 600 540 600 %d" % int(distance*2.728))

def main():
    while 1:
        run()
        time.sleep(1)

if __name__ == '__main__':
    main()
