import math
import optimization
from PIL import Image,ImageDraw
people=['Charlie','Augustus','Veruca','Violet','Mike','Joe','Willy','Miranda']

links=[('Augustus', 'Willy'),
       ('Mike', 'Joe'),
       ('Miranda', 'Mike'),
       ('Violet', 'Augustus'),
       ('Miranda', 'Willy'),
       ('Charlie', 'Mike'),
       ('Veruca', 'Joe'),
       ('Miranda', 'Augustus'),
       ('Willy', 'Augustus'),
       ('Joe', 'Charlie'),
       ('Veruca', 'Augustus'),
       ('Miranda', 'Joe')]


#v=[(x1,y1),(x2,y2)...] 保存初始构造的每个人的坐标

def crosscount(v):
    #将数字序列转换成person:(x,y)的字典
    loc=dict([(people[i],(v[i*2],v[i*2+1]))
              for i in range(0,len(people))])
    total=0
    #遍历所有连线
    for i in range(len(links)):
        for j in range(i+1,len(links)):
            #获取每个人的坐标，每个link对应两个人，可以获得两对坐标
            (x1,y1),(x2,y2)=loc[links[i][0]],loc[links[i][1]]
            (x3,y3),(x4,y4)=loc[links[j][0]],loc[links[j][1]]
            #查看两个link是否有交叉
            #两线是否交叉算法公式需要学习，包括三维空间是否交叉？ 计算几何
            #股票中均线是否交叉？
            den=(y4-y3)*(x2-x1)-(x4-x3)*(y2-y1)

            if den==0: continue

            ua=((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/den
            ub=((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/den
            if ua>0 and ua<1 and ub>0 and ub<1:
                total+=1
    return total

def drawnetwork(sol):
    img=Image.new('RGB',(400,400),(255,255,255))
    draw=ImageDraw.Draw(img)

    pos=dict([(people[i],(sol[i*2],sol[i*2+1])) for i in range(0,len(people))])
    for (a,b) in links:
        draw.line((pos[a],pos[b]),fill=(255,0,0))
    for n,p in pos.items():
        draw.text(p,n,(0,0,0))

    img.show()

#假设要在400×400的图片上显示网络
domain=[(10,370)]*(len(people)*2)
print(domain)
sol=optimization.randomoptimize(domain,crosscount)
crosscount(sol)
print(sol)

drawnetwork(sol)
