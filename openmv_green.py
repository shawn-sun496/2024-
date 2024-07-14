#此为【激光云台-追踪部分】视觉代码
import sensor, image, time
from machine import UART

#g_thresholds = [(60, 100, -128, 10, -10, 127)] # 绿色阈值
g_thresholds = [(93, 100, -39, 34, -44, 57)]
r_thresholds = [(0, 100, 10, 127, 0, 127)] # 红色阈值
cxh_roi=(142,64,320,320)
g_data = [0,0,0,0]
r_data = [0,0,0,0]
data  =  [0xfe,0x00,0x00,0xff]
max_size=0

#UART(3)是P4-TX P5-RX
uart = UART(3, 115200)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.VGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # 自动增益 关
sensor.set_auto_whitebal(False) # 白平衡 关
sensor.set_auto_exposure(False,20000)
time.sleep(1)
clock = time.clock()


while(True):
    clock.tick()
    img = sensor.snapshot()
    img = img.lens_corr(strength = 1.8, zoom = 1.0)
    img.draw_rectangle(cxh_roi,color=(0,0,255))

    # 绿激光坐标识别
    g_blobs = img.find_blobs(g_thresholds)
    max_size=0
    for blob in g_blobs:
        if blob[2]*blob[3] > max_size:
            g_max_blob=blob
            max_size = blob[2]*blob[3]
    if max_size>0:
        img.draw_rectangle(g_max_blob.rect(),color=(0,0,255))# 给绿激光标红
        g_data[1]=int(g_max_blob[0]+g_max_blob[2]/2)
        g_data[2]=int(g_max_blob[1]+g_max_blob[3]/2)

    # 红激光坐标识别
    r_blobs = img.find_blobs(r_thresholds)
    max_size=0
    for blob in r_blobs:
        if blob[2]*blob[3] > max_size:
            r_max_blob=blob
            max_size = blob[2]*blob[3]
    if max_size>0:
        img.draw_rectangle(r_max_blob.rect(),color=(0,0,255))# 给红激光标绿
        r_data[1]=int(r_max_blob[0]+r_max_blob[2]/2)
        r_data[2]=int(r_max_blob[1]+r_max_blob[3]/2)

    data[1] = int((r_data[1] - g_data[1])/4+128)
    data[2] = int((r_data[2] - g_data[2])/4+128)
    print("Δx:"+str(data[1])+","+"Δy:"+str(data[2]))
    print("rx:"+str(r_data[1])+","+"ry:"+str(r_data[2]))
    print("gx:"+str(g_data[1])+","+"gy:"+str(g_data[2]))
    uart.write(bytearray(data))

    print(clock.fps())


