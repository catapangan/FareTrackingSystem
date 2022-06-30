import random
import decimal
import math
import time
import serial
import psycopg2
import psycopg2.extras

addRandomNoise = False

def toDecimalDegrees(val):
	deg = math.floor(val/100)
	val = deg + ((val - (deg * 100)) / 60)
	
	return val
	
def logLocation(lat, lon):
	try:
		conn = psycopg2.connect(user = "pi",
								password = "jjc2022",
								host = "localhost",
								port = "5432",
								database ="jjc")
		cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
		
	except Exception as e:
		if cursor:
			cursor.close()
		if conn:
			conn.close()
		print(str(e))
		return False
	
	try:
		cursor.execute("INSERT INTO gps_log (lat, lon, date) VALUES(%s, %s, NOW())" % (str('%.5f' % lat) , str('%.5f' % lon)))
		conn.commit()
		
		cursor.execute("DELETE FROM gps_log WHERE date < NOW() - INTERVAL '1 day'")
		conn.commit()
		
	except Exception as e:
		cursor.close()
		conn.close()
		print(str(e))
		return False
		
	cursor.close()
	conn.close()
	return True

def main():
	while True:
		try:		
			with serial.Serial('/dev/serial/by-id/usb-u-blox_AG_-_www.u-blox.com_u-blox_7_-_GPS_GNSS_Receiver-if00', 9600, timeout=2) as gps:
				while True:
					line = gps.readline().decode('utf-8')
					if line[-1] == '\n':
						line = line[:-1]
						data = line.split(',')
						if len(data) >= 7:
							if data[0] == '$GPGLL':
								lat = data[1]
								lon = data[3]
								isValid = data[6][0]
								
								if isValid == 'A':
									lat = toDecimalDegrees(float(lat))
									lon = toDecimalDegrees(float(lon))
									
									if addRandomNoise:
										noise = float(decimal.Decimal(random.randrange(0, 99))/100000)
										lat = lat + noise
										noise = float(decimal.Decimal(random.randrange(0, 99))/100000)
										lon = lon + noise
									
									logLocation(lat, lon)
									
									print('LAT:' + str('%.5f' % lat) + ', LON:' + str('%.5f' % lon))
									
		except Exception as e:
			print(str(e))
		
		time.sleep(1)

if __name__ == "__main__":
	main()