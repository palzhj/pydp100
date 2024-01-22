#!/usr/bin/python
# This is pydp100 file
# author: zhj@ihep.ac.cn
# 2024-01-19 created

import hid
import crcmod
import time

VID = 0x2e3c
PID = 0xaf01

DR_H2D          = 0xFB
DR_D2H          = 0xFA

OP_NONE         = 0x00
OP_DEVICEINFO   = 0x10
OP_BASICINFO    = 0x30
OP_BASICSET     = 0x35
OP_SYSTEMINFO   = 0x40
OP_SCANOUT      = 0x50
OP_SERIALOUT    = 0x55

vin     = 0 # unit: mV
vout    = 0 # unit: mV
iout    = 0 # unit: mA
vo_max  = 0 # unit: mV
temp1   = 0 # unit: 0.1 dgree
temp2   = 0 # unit: 0.1 dgree
dc_5v   = 0 # unit: mV
out_mode= 0
work_st = 0

dev_type= ""
hdw_ver = 0
app_ver = 0
boot_ver= 0
run_area= 0
dev_sn  = bytes([])
year    = 0
month   = 0
day     = 0

blk_lev = 0
opp     = 0 # unit: mV
opt     = 0 # unit: 0.1 dgree
vol_lev = 0 

index   = 0
state   = 0 # 0:off; 1:on
vo_set  = 0 # unit: mV
io_set  = 0 # unit: mA
ovp_set = 0 # unit: mV
ocp_set = 0 # unit: mA

SET_MODIFY = 0x20
SET_ACT    = 0x80

# for device_dict in hid.enumerate():
#     keys = list(device_dict.keys())
#     keys.sort()
#     for key in keys:
#         print("%s : %s" % (key, device_dict[key]))
#     print()

crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)

def gen_frame(op_code, data=bytes([])): 
    frame = bytes([DR_H2D, op_code&0xFF, 0x0, len(data)&0xFF])+data
    crc = crc16(frame)
    return (frame+bytes([crc&0xFF,(crc>>8)&0xFF]))

def check_frame(data): 
    global vin,vout,iout,vo_max,temp1,temp2,dc_5v,out_mode,work_st
    global dev_type,hdw_ver,app_ver,boot_ver,run_area,dev_sn,year,month,day
    global blk_lev,opp,opt,vol_lev
    global index,state,vo_set,io_set,ovp_set,ocp_set

    if(data[0] == DR_D2H):
        op = data[1]
        data_len = data[3]
        if (crc16(data[0:4+data_len+2])==0): # correct if return 0
            raw_data = data[4:4+data_len]
            # print(raw_data)
            if(op == OP_BASICINFO):
                vin     = (raw_data[1]<<8) |raw_data[0]
                vout    = (raw_data[3]<<8) |raw_data[2]
                iout    = (raw_data[5]<<8) |raw_data[4]
                vo_max  = (raw_data[7]<<8) |raw_data[6]
                temp1   = (raw_data[9]<<8) |raw_data[8]
                temp2   = (raw_data[11]<<8)|raw_data[10]
                dc_5v   = (raw_data[13]<<8)|raw_data[12]
                out_mode= raw_data[14]
                work_st = raw_data[15]
                # print(vin,vout,iout,vo_max,temp1,temp2,dc_5v,out_mode,work_st)
            elif(op == OP_DEVICEINFO):
                dev_type = raw_data[0:15].split(b'\x00')[0].decode("utf-8")
                hdw_ver  = (raw_data[17]<<8) |raw_data[16] # origin:11 means 1.1
                app_ver  = (raw_data[19]<<8) |raw_data[18] # origin:11 means 1.1
                boot_ver = (raw_data[21]<<8) |raw_data[20]
                run_area = (raw_data[23]<<8) |raw_data[22]
                dev_sn   = raw_data[24:24+11]
                year     = (raw_data[37]<<8) |raw_data[36]
                month    = raw_data[38]
                day      = raw_data[39]
                # print(dev_type,hdw_ver,app_ver,boot_ver,run_area,dev_sn,year,month,day)
            elif(op == OP_SYSTEMINFO):
                blk_lev  = raw_data[0]      # backlight
                opp      = (raw_data[2]<<8) |raw_data[1] # over power
                opt      = (raw_data[4]<<8) |raw_data[3] # over temperature
                vol_lev  = raw_data[5]      # beep volumn
                # print(blk_lev, opp, opt, vol_lev)
            elif(op == OP_BASICSET):
                index    = raw_data[0] 
                state    = raw_data[1] 
                vo_set   = (raw_data[3]<<8) |raw_data[2]
                io_set   = (raw_data[5]<<8) |raw_data[4]
                ovp_set  = (raw_data[7]<<8) |raw_data[6]
                ocp_set  = (raw_data[9]<<8) |raw_data[8]
                # print(index, state, vo_set, io_set, ovp_set, ocp_set)
        else:
            print("CRC ERROR")

def gen_set(output = False, vset = 0, iset = 0, ovp = 30500, ocp = 5050):
    if(output):
        output=1
    else:
        output=0
    return bytes([SET_MODIFY, output, vset&0xFF, (vset>>8)&0xFF, iset&0xFF, (iset>>8)&0xFF,
        ovp&0xFF, (ovp>>8)&0xFF, ocp&0xFF, (ocp>>8)&0xFF])

# recv_BASICINFO = b'\xfa0\x00\x10e\x14\x00\x00\x00\x00\xba\x13?\x019\x01\xcc\x13\x02\x00\x0f/\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
# check_frame(recv_BASICINFO)

# recv_DEVICEINFO = b'\xfa\x10\x00(ATK-DP100\x00\xff\xff\xff\xff\xff\xff\x0e\x00\x0e\x00\x0b\x00\xaa\x00\xe25\x14\x00\x00\xc0&"\n\'i\x05\xe8\x07\x01\n\'\r\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
# check_frame(recv_DEVICEINFO)

# recv_SYSTEMINFO = b'\xfa@\x00\x08P\x00\x1a\x04\x02\x02\x01\x00Z4\xff\xff\xff\xff\xff\xff\x0e\x00\x0e\x00\x0b\x00\xaa\x00\xe25\x14\x00\x00\xc0&"\n\'i\x05\xe8\x07\x01\n\'\r\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
# check_frame(recv_SYSTEMINFO)

# recv_BASICSET = b'\xfa5\x00\n\x00\x00\xb8\x0b\xe8\x03$w\xba\x13V\xab\xd0\x13\x02\x00,q\x0e\x00\x0b\x00\xaa\x00\xe25\x14\x00\x00\xc0&"\n\'i\x05\xe8\x07\x01\n\'\r\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
# recv_BASICSET = b'\xfa5\x00\x01\x013\x88\x13\xd0\x07$w\xba\x135V\xd2\x13\x01\x00\x86\x1e\x0e\x00\x0b\x00\xaa\x00\xe25\x14\x00\x00\xc0&"\n\'i\x05\xe8\x07\x01\n\'\r\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
# check_frame(recv_BASICSET)

def load_config(file_name = "config.txt"):
    file = open(file_name, 'r')
    for line in file:
        line = line.lstrip(' \t')
        if(line[0]=='v'):
            voltage = float(''.join(filter(lambda x: x.isdigit() or x == '.', line)))
        elif(line[0]=='i'):
            current = float(''.join(filter(lambda x: x.isdigit() or x == '.', line)))
    file.close()
    return [int(voltage*1000),int(current*1000)]

with hid.Device(VID, PID) as dp100:
    print('Device manufacturer: %s, Serial number: %s'%(dp100.manufacturer, dp100.serial))

    dp100.write(gen_frame(OP_DEVICEINFO))
    time.sleep(0.05)
    check_frame(dp100.read(64))
    print('%s version: hardware%.1f, app%.1f, bootloader%.1f @ %d-%02d-%02d'%(dev_type, hdw_ver/10, app_ver/10, boot_ver/10, year,month,day))

    print("\nDP100 status:")
    dp100.write(gen_frame(OP_BASICINFO))
    time.sleep(0.05)
    check_frame(dp100.read(64))
    print('Vin: %.3f V, Vout: %.3f V, Iout: %.3f A, temperature: %.1f degree'%(vin/1000, vout/1000, iout/1000, temp1/10))

    dp100.write(gen_frame(OP_BASICSET, bytes([SET_ACT])))
    time.sleep(0.05)
    check_frame(dp100.read(64))
    print('Over voltage protect: %.3f V, Over current protect: %.3f A'%(ovp_set/1000, ocp_set/1000))

    [new_voltage,new_current] = (load_config())
    if new_voltage > vo_max:
        print("ERROR: Type-c input voltage is too low to set!")
    elif new_current > ocp_set:
        print("ERROR: Output current is too large to set!")
    else:
        dp100.write(gen_frame(OP_BASICSET, gen_set(True, new_voltage, new_current)))
        print("\n%.3f V output enable."%(new_voltage/1000))
        # time.sleep(0.05)
        # print(dp100.read(64))
