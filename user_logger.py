import os
import sys
import io
import time

import psycopg2
import psycopg2.extras

import haversine
import folium
from folium.plugins import MarkerCluster

from PyQt5.QtCore import *
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QMainWindow, QApplication, QGridLayout, QWidget
from PyQt5.QtWebKitWidgets import QWebView

from pynput.keyboard import Key, Listener

default_statusText 	= "Please Tap RFID Card"
default_resultText 	= ""
default_startPoint 	= (14.30144, 120.95649)

isMobile = True

class RFIDLogger(QThread):
	updateMap 		= pyqtSignal(object)
	updateMessage 	= pyqtSignal(str, str)
	
	def __init__(self, parent=None):
		global default_statusText, default_resultText, default_startPoint

		QThread.__init__(self, parent)

		self.compute_successText 	= "Payment Successful, "
		self.compute_failureText	= "Transaction Failure, "
		self.compute_resultText 	= "Your total fare is: Php"

		self.welcome_statusText		= "Welcome, "
		self.welcome_resultText		= "Your total balance is: Php"
		
		self.current_statusText 	= default_statusText
		self.current_resultText 	= default_resultText
		
		# Fare Computation
		# First Four (4) kilometers = base fare
		# Succeeding kilometers = rate per km
		self.fare_base_regular 		= 9.00
		self.fare_base_discount 	= 6.20
		self.fare_rate_regular 		= 1.50
		self.fare_rate_discount 	= 1.20
		
		# RFID Tag Buffer
		self.inputBuffer = []
		
		# Status Variables
		self.isProcessing = False
		
	def run(self):
		global default_statusText, default_resultText
		
		listener = Listener(on_press=self.get_userid)
		listener.start()
		
		'''
		while True:
			if self.isProcessing == False:
				time.sleep(5)
				
				try:
					conn = psycopg2.connect(user = "pi",
											password = "jjc2022",
											host = "localhost",
											port = "5432",
											database ="jjc")
					cursor = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
					
					cursor.execute("SELECT * FROM gps_log ORDER BY date DESC LIMIT 1")
					route_data = cursor.fetchall()
					
					if len(route_data) > 0:
						current_lat = route_data[0]['lat']
						current_lon = route_data[0]['lon']
						
						self.updateMap.emit([(current_lat, current_lon)])
						
					cursor.close()
					conn.close()
					
				except Exception as e:
					if cursor:
						cursor.close()
					if conn:
						conn.close()
					print(str(e))
				
				self.updateMessage.emit(default_statusText, default_resultText)
		'''

	def get_userid(self, key):
		global isProcessing, inputBuffer

		if self.isProcessing == False:
			try:
				k = key.char
				if k.isnumeric():
					self.inputBuffer.append(k)
					
			except Exception as e:
				if key == Key.enter:
					self.isProcessing = True
					
					# Process RFID
					self.process_userid(self.inputBuffer)
					
					time.sleep(3)
					
					self.inputBuffer = []
					self.isProcessing = False

	# Get User Local Accounts Only
	def get_local_accounts(self, conn, cursor, userid):
		try:
			cursor.execute("SELECT balance FROM user_accounts WHERE userid='%s' LIMIT 1" % (userid))
			accounts_data = cursor.fetchall()
			if len(accounts_data) <= 0:
				print("No Account")
				raise Exception("Accounts error")
		except Exception as e:
			print(str(e))
			return (False, 0)
		
		return (True, accounts_data[0]['balance'])

	# Get User Online Accounts
	def get_online_accounts(self, conn, cursor, userid):
		pass

	def log_userid(self, conn, cursor, userid, status, lat, lon):
		try:
			cursor.execute("INSERT INTO user_log (userid, status, lat, lon, date) VALUES('%s', %s, %s, %s, NOW())" % (userid, str(status), str('%.5f' % lat) , str('%.5f' % lon)))
			conn.commit()
			
		except Exception as e:
			print(str(e))
			return False
			
		return True
	
	# Compute total distance travelled and fare based on LTFRB guidelines
	def compute_fare(self, conn, cursor, balance, user_data, loc_data):
		try:
			cursor.execute("SELECT * FROM gps_log WHERE date >= '%s' AND date <= '%s' ORDER BY date ASC" % (str(user_data['date']), str(loc_data['date'])))
			route_data = cursor.fetchall()
			current_lat = user_data['lat']
			current_lon = user_data['lon']
			points = [(current_lat, current_lon)]
			
			total_distance = 0
			for row in route_data:
				total_distance = total_distance + haversine.haversine((current_lat, current_lon), (row['lat'], row['lon']))
				current_lat = row['lat']
				current_lon = row['lon']
				points.append((current_lat, current_lon))
				
			if total_distance <= 4.0:
				fare = self.fare_base_regular
			else:
				fare = self.fare_base_regular + (total_distance - 4.0) * self.fare_rate_regular
				
			if balance >= fare:
				isValid = True
				cursor.execute("UPDATE user_accounts SET balance=%s WHERE userid='%s'" % (str('%.2f' % (balance - fare)), user_data['userid']))
				conn.commit()
				
			else:
				isValid = False
		
		except Exception as e:
			print(str(e))
			return (False, 0, 0, [], False)
			
		return (True, fare, total_distance, points, isValid)

	def process_userid(self, user_array):
		global mainwindow, global_statusText, global_resultText

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
			userid = ''
			for c in user_array:
				userid = userid + c
				
			print(userid)
			
			(isSuccess, balance) = self.get_local_accounts(conn, cursor, userid)
			if isSuccess == False:
				raise Exception("Accounts error")
			
			cursor.execute("SELECT * FROM user_log WHERE userid='%s' ORDER BY date DESC" % userid)
			user_data = cursor.fetchall()
			
			cursor.execute("SELECT * FROM gps_log ORDER BY date DESC LIMIT 1")
			loc_data = cursor.fetchall()
			
			if len(loc_data) > 0:
				if len(user_data) > 0:
					if user_data[0]['status'] == 0:
						isSuccess = self.log_userid(conn, cursor, userid, 1, loc_data[0]['lat'], loc_data[0]['lon'])
						if isSuccess == False:
							raise Exception("Logging error")
							
						(isSuccess, fare, distance, points, isValid) = self.compute_fare(conn, cursor, balance, user_data[0], loc_data[0])
						if isSuccess == False:
							raise Exception("Fare computation error")
						if isValid:
							self.current_statusText = self.compute_successText + userid
							self.current_resultText = self.compute_resultText + str('%.2f' % fare) + ' for ' + str('%.2f' % distance) + 'km'
						else:
							self.current_statusText = self.compute_failureText + userid
							self.current_resultText = self.compute_resultText + str('%.2f' % fare) + ' for ' + str('%.2f' % distance) + 'km'
						self.updateMap.emit(points)
					else:
						isSuccess = self.log_userid(conn, cursor, userid, 0, loc_data[0]['lat'], loc_data[0]['lon'])
						if isSuccess == False:
							raise Exception("Logging error")
							
						self.current_statusText = self.welcome_statusText + userid
						self.current_resultText = self.welcome_resultText + str('%.2f' % balance)
						
						self.updateMap.emit([(loc_data[0]['lat'], loc_data[0]['lon'])])
				else:
					isSuccess = self.log_userid(conn, cursor, userid, 0, loc_data[0]['lat'], loc_data[0]['lon'])
					if isSuccess == False:
						raise Exception("Logging error")
							
					self.current_statusText = self.welcome_statusText + userid
					self.current_resultText = self.welcome_resultText + str('%.2f' % balance)
					
					self.updateMap.emit([(loc_data[0]['lat'], loc_data[0]['lon'])])
					
				self.updateMessage.emit(self.current_statusText, self.current_resultText)
				
			else:
				raise Exception("Location Error")
		
		except Exception as e:
			cursor.close()
			conn.close()
			print(str(e))
			return False
			
		cursor.close()
		conn.close()
		return isSuccess

class DisplayWindow(QMainWindow):
	def __init__(self, screenwidth=320, screenheight=240, isMobile=False):
		super().__init__()
		
		self.isMobile = isMobile
		
		self.left = 0
		self.top = 0
		
		if self.isMobile:
			self.width = 320
			self.height = 240
		else:
			self.width = screenwidth
			self.height = screenheight
		
		self.setWindowTitle('Fare Tracking System')
		self.setGeometry(self.left, self.top, self.width, self.height)
		self.setStyleSheet('background-color: #FFFFFF;')
		
		self.createUI()
		self.startApp()
		
	def createUI(self):
		global default_statusText, default_resultText, default_startPoint
	
		self.mainContainer = QWidget()
		self.mainLayout = QGridLayout()
		
		if self.isMobile:
			fontsize = 24
		else:
			fontsize = 32
		
		self.statusLabel = QLabel()
		self.statusLabel.setWordWrap(True)
		self.statusLabel.setFont(QFont('Times New Roman', fontsize))
		self.statusLabel.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
		
		self.resultLabel = QLabel()
		self.resultLabel.setWordWrap(True)
		self.resultLabel.setFont(QFont('Times New Roman', fontsize))
		self.resultLabel.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
		
		self.setDisplay(default_statusText, default_resultText)

		self.webView = QWebView()
		self.webView.settings().setObjectCacheCapacities(0,0,0)
		
		path_blueIcon = os.path.abspath(os.path.join('data', 'marker', 'BlueMarker.png'))
		self.blueIcon = folium.features.CustomIcon(path_blueIcon, icon_size=(15,15))
		
		path_redIcon = os.path.abspath(os.path.join('data', 'marker', 'RedMarker.png'))
		self.redIcon = folium.features.CustomIcon(path_redIcon, icon_size=(15,15))
		
		path_greenIcon = os.path.abspath(os.path.join('data', 'marker', 'GreenMarker.png'))
		self.greenIcon = folium.features.CustomIcon(path_greenIcon, icon_size=(15,15))
		
		self.setRoute([default_startPoint])
		
		self.mainLayout.addWidget(self.statusLabel, 1, 1)
		self.mainLayout.addWidget(self.resultLabel, 2, 1)
		
		if self.isMobile:
			self.mainLayout.addWidget(self.webView, 3, 1)
		else:
			self.mainLayout.addWidget(self.webView, 1, 2, 2, 1)
		
		self.mainContainer.setLayout(self.mainLayout)
		self.setCentralWidget(self.mainContainer)
		
		#self.showMaximized()
		self.showFullScreen()
	
	def startApp(self):
		self.rfidLogger = RFIDLogger()
		self.rfidLogger.updateMap.connect(self.setRoute)
		self.rfidLogger.updateMessage.connect(self.setDisplay)
		self.rfidLogger.start()
		
	def setDisplay(self, statusText, resultText):
		self.statusLabel.setText(statusText)
		self.resultLabel.setText(resultText)
		
	def setRoute(self, coords):
		global default_startPoint
	
		if len(coords) <= 0:
			currentPoint = default_startPoint
		else:
			currentPoint = coords[0]
		
		tile_path = os.path.abspath(os.path.join('data', 'tiles', 'Google/{z}/{x}/{y}.png'))
		m = folium.Map(zoom_start=15, tiles=tile_path, attr='Google Maps', max_zoom=20, min_zoom=14, location=currentPoint)
		
		m.default_js = [
			('leaflet',
			 f'{os.path.abspath(os.path.join("offline", "leaflet.js"))}'),
			('jquery',
			 f'{os.path.abspath(os.path.join("offline", "jquery-1.12.4.min.js"))}'),
			('bootstrap',
			 f'{os.path.abspath(os.path.join("offline", "bootstrap.min.js"))}'),
			('awesome_markers',
			 f'{os.path.abspath(os.path.join("offline", "leaflet.awesome-markers.js"))}'),
			('sql',
			 f'{os.path.abspath(os.path.join("offline", "sql.js"))}'),
			('sql-wasm',
			 f'{os.path.abspath(os.path.join("offline", "sql-wasm.js"))}'),
			('sql-asm',
			 f'{os.path.abspath(os.path.join("offline", "sql-adm.js"))}'),
			('mbtiles',
			 f'{os.path.abspath(os.path.join("offline", "Leaflet.TileLayer.MBTiles.js"))}')
		]

		m.default_css = [
			('leaflet_css',
			 f'{os.path.abspath(os.path.join("offline", "leaflet.css"))}'),
			('bootstrap_css',
			 f'{os.path.abspath(os.path.join("offline", "bootstrap.min.css"))}'),
			('bootstrap_theme_css',
			 f'{os.path.abspath(os.path.join("offline", "bootstrap-theme.min.css"))}'),
			('awesome_markers_font_css',
			 f'{os.path.abspath(os.path.join("offline", "font-awesome.min.css"))}'),
			('awesome_markers_css',
			 f'{os.path.abspath(os.path.join("offline", "leaflet.awesome-markers.css"))}'),
			('awesome_rotate_css',
			 f'{os.path.abspath(os.path.join("offline", "leaflet.awesome.rotate.css"))}')
		]
		
		if len(coords) > 1:
			folium.Marker(location=coords[0], icon=self.redIcon).add_to(m)
			
			if coords[0] != coords[-1]:
				folium.Marker(location=coords[-1], icon=self.greenIcon).add_to(m)
		else:
			folium.Marker(location=coords[0], icon=self.blueIcon).add_to(m)
		
		'''
		if len(coords) > 1:
			folium.Marker(location=coords[0], icon=folium.Icon(color='red', prefix='fa', icon_color='white', icon='male', angle=0)).add_to(m)
			
			if coords[0] != coords[-1]:
				folium.Marker(location=coords[-1], icon=folium.Icon(color='green', prefix='fa', icon_color='white', icon='male', angle=0)).add_to(m)
		else:
			folium.Marker(location=coords[0], icon=folium.Icon(color='blue', prefix='fa', icon_color='white', icon='car', angle=0)).add_to(m)
		'''

		for point in coords:
			if point != currentPoint:
				loc = [currentPoint, point]
				folium.PolyLine(loc, color='green', weight=3, opacity=0.8).add_to(m)
				currentPoint = point
				
		m.fit_bounds(m.get_bounds(), padding=(30, 30))
		data = io.BytesIO()
		m.save(data, close_file=False)
		m.save('index.html')
		
		html = data.getvalue().decode()
		
		# Load external web page
		#self.webView.load(QUrl.fromLocalFile(os.path.abspath('index.html')))
		
		# Load internal file I/O
		self.webView.setHtml(html, baseUrl=QUrl.fromLocalFile(os.path.abspath('./')))
		
		data.close()

def main():
	global mainwindow, isMobile, global_statusText, global_resultText
	
	app = QApplication(sys.argv)
	screen = app.primaryScreen()
	screensize = screen.availableGeometry()
	mainwindow = DisplayWindow(screenwidth=screensize.width(), screenheight=screensize.height(), isMobile=isMobile)
	
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()