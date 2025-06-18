# echo_client.py
import socket
import os
import time
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte
#import winsound
#frequency=3000
#duration=500
import random
#import pyttsx3 
from rgbmatrix5x5 import RGBMatrix5x5

rgbmatrix5x5 = RGBMatrix5x5()

rgbmatrix5x5.set_clear_on_exit()
rgbmatrix5x5.set_brightness(0.8)

height = rgbmatrix5x5.height
width = rgbmatrix5x5.width

forest_width = width
forest_height = height

hood_size = 3


def get_neighbours(x, y, z):
    return [(x2, y2) for x2 in range(x - (z - 1), x + z) for y2 in range(y - (z - 1), y + z) if (-1 < x < forest_width and -1 < y < forest_height and (x != x2 or y != y2) and (0 <= x2 < forest_width) and (0 <= y2 < forest_height))]


initial_trees = 0.55
p = 0.01
f = 0.001

tree = [0, 255, 0]
burning = [255, 0, 0]
space = [0, 0, 0]


def initialise():
    forest = [[tree if random.random() <= initial_trees else space for x in range(forest_width)] for y in range(forest_height)]
    return forest


def update_forest(forest):
    new_forest = [[space for x in range(forest_width)] for y in range(forest_height)]
    for x in range(forest_width):
        for y in range(forest_height):
            if forest[x][y] == burning:
                new_forest[x][y] = space
            elif forest[x][y] == space:
                new_forest[x][y] = tree if random.random() <= p else space
            elif forest[x][y] == tree:
                neighbours = get_neighbours(x, y, hood_size)
                new_forest[x][y] = (burning if any([forest[n[0]][n[1]] == burning for n in neighbours]) or random.random() <= f else tree)
    return new_forest


def show_forest(forest):
    for x in range(width):
        for y in range(height):
            r, g, b = forest[x][y]
            rgbmatrix5x5.set_pixel(x, y, int(r), int(g), int(b))

    rgbmatrix5x5.show()


#forest = initialise()

DEVICE = 0x76 # Default device I2C address


bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                     # Rev 1 Pi uses bus 0

def getShort(data, index):
  # return two bytes from data as a signed 16-bit value
  return c_short((data[index+1] << 8) + data[index]).value

def getUShort(data, index):
  # return two bytes from data as an unsigned 16-bit value
  return (data[index+1] << 8) + data[index]

def getChar(data,index):
  # return one byte from data as a signed char
  result = data[index]
  if result > 127:
    result -= 256
  return result

def getUChar(data,index):
  # return one byte from data as an unsigned char
  result =  data[index] & 0xFF
  return result

def readBME280ID(addr=DEVICE):
  # Chip ID Register Address
  REG_ID     = 0xD0
  (chip_id, chip_version) = bus.read_i2c_block_data(addr, REG_ID, 2)
  print ("chip_id= ",chip_id)
  return (chip_id, chip_version)

def readBME280All(addr=DEVICE):
  # Register Addresses
  REG_DATA = 0xF7
  REG_CONTROL = 0xF4
  REG_CONFIG  = 0xF5

  REG_CONTROL_HUM = 0xF2
  REG_HUM_MSB = 0xFD
  REG_HUM_LSB = 0xFE

  # Oversample setting - page 27
  OVERSAMPLE_TEMP = 2
  OVERSAMPLE_PRES = 2
  MODE = 1

  # Oversample setting for humidity register - page 26
  OVERSAMPLE_HUM = 2
  bus.write_byte_data(addr, REG_CONTROL_HUM, OVERSAMPLE_HUM)

  control = OVERSAMPLE_TEMP<<5 | OVERSAMPLE_PRES<<2 | MODE
  bus.write_byte_data(addr, REG_CONTROL, control)

  # Read blocks of calibration data from EEPROM
  # See Page 22 data sheet
  cal1 = bus.read_i2c_block_data(addr, 0x88, 24)
  cal2 = bus.read_i2c_block_data(addr, 0xA1, 1)
  cal3 = bus.read_i2c_block_data(addr, 0xE1, 7)

  # Convert byte data to word values
  dig_T1 = getUShort(cal1, 0)
  dig_T2 = getShort(cal1, 2)
  dig_T3 = getShort(cal1, 4)

  dig_P1 = getUShort(cal1, 6)
  dig_P2 = getShort(cal1, 8)
  dig_P3 = getShort(cal1, 10)
  dig_P4 = getShort(cal1, 12)
  dig_P5 = getShort(cal1, 14)
  dig_P6 = getShort(cal1, 16)
  dig_P7 = getShort(cal1, 18)
  dig_P8 = getShort(cal1, 20)
  dig_P9 = getShort(cal1, 22)

  dig_H1 = getUChar(cal2, 0)
  dig_H2 = getShort(cal3, 0)
  dig_H3 = getUChar(cal3, 2)

  dig_H4 = getChar(cal3, 3)
  dig_H4 = (dig_H4 << 24) >> 20
  dig_H4 = dig_H4 | (getChar(cal3, 4) & 0x0F)

  dig_H5 = getChar(cal3, 5)
  dig_H5 = (dig_H5 << 24) >> 20
  dig_H5 = dig_H5 | (getUChar(cal3, 4) >> 4 & 0x0F)

  dig_H6 = getChar(cal3, 6)

  # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
  wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 * OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM)+0.575)
  time.sleep(wait_time/1000)  # Wait the required time  

  # Read temperature/pressure/humidity
  data = bus.read_i2c_block_data(addr, REG_DATA, 8)
  pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
  temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
  hum_raw = (data[6] << 8) | data[7]

  #Refine temperature
  var1 = ((((temp_raw>>3)-(dig_T1<<1)))*(dig_T2)) >> 11
  var2 = (((((temp_raw>>4) - (dig_T1)) * ((temp_raw>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
  t_fine = var1+var2
  temperature = float(((t_fine * 5) + 128) >> 8);

  # Refine pressure and adjust for temperature
  var1 = t_fine / 2.0 - 64000.0
  var2 = var1 * var1 * dig_P6 / 32768.0
  var2 = var2 + var1 * dig_P5 * 2.0
  var2 = var2 / 4.0 + dig_P4 * 65536.0
  var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
  var1 = (1.0 + var1 / 32768.0) * dig_P1
  if var1 == 0:
    pressure=0
  else:
    pressure = 1048576.0 - pres_raw
    pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
    var1 = dig_P9 * pressure * pressure / 2147483648.0
    var2 = pressure * dig_P8 / 32768.0
    pressure = pressure + (var1 + var2 + dig_P7) / 16.0

  # Refine humidity
  humidity = t_fine - 76800.0
  humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
  humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)
  if humidity > 100:
    humidity = 100
  elif humidity < 0:
    humidity = 0

  return temperature/100.0,pressure/100.0,humidity
host = '192.168.251.244'
port = 12365  # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
forest = initialise()

def main():
    #for i in range (0,5):
        (chip_id, chip_version) = readBME280ID()
        print ("Chip ID     :", chip_id)
        print ("Version     :", chip_version)

        temperature,pressure,humidity = readBME280All()
	
        print ("Temperature : ", temperature, "C")
        print ("Pressure : ", pressure, "hPa")
        print ("Humidity : ", humidity, "%")
  
        a=float(temperature)
          
        print('Receiving the data from server.')    
        s.send((bytes (f'{temperature}','utf-8')))
        print(s.recv(1024).decode())
        #re1=s.recv(1024).decode()
        time.sleep(2)
        
        r=True
        while r:
            re1=s.recv(1024).decode()
            print(s.recv(1024).decode())
            if re1 == "true":
            
                    #for i in range(0,5):
                
  
                print(re1)

                temperature,pressure,humidity = readBME280All()
                print(temperature)
                s.send((bytes (f'{temperature}','utf-8')))
                if a > 24:
                  for i in range(0,4):
                     show_forest(forest)
	                   forest = update_forest(forest)
	                   time.sleep(2)        
            else:
                r=False
                s.send((bytes (f'{temperature}','utf-8')))            
      
        s.close()

if __name__=="__main__":
   main()
   
   


