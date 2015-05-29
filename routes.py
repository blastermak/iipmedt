from flask import Flask, render_template
import RPi.GPIO as GPIO
import threading
 
app = Flask(__name__)      

class myThread(threading.Thread):
	def __init__(self, threadID, name):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
	def run(self):
		while True:
			mainProg.monitorButton()
			

class hoofdKlasse:
	ledPin = 0
	buttonPin = 0
	def __init__(self):
		GPIO.cleanup()
		self.ledPin = 21
		self.buttonPin = 20
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.ledPin, GPIO.OUT)
		GPIO.setup(self.buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

	def checkButton(self):
		return GPIO.input(self.buttonPin)
	
	def writeFile(self, filePath, tekst):
		try:
			file = open(filePath, "w")
			file.write(str(tekst))
		except:
			print "fail writing"
		file.close()
	def monitorButton(self):
		
		if self.checkButton():
			GPIO.output(self.ledPin, False)
			#self.writeFile("/home/pi/knop1.txt", "Uit")
		elif not(self.checkButton()):
			GPIO.output(self.ledPin, True)
			#self.writeFile("/home/pi/knop1.txt", "Aan")

	def startThread(self):
		self.buttonThread = myThread(1, "buttonThread")
		self.buttonThread.start()

mainProg = hoofdKlasse()
mainProg.startThread()

@app.route('/')
def home():
	templateData = {
	'buttonTekst' : "harhar"
	}
	return render_template('index.html', **templateData)
	print mainProg.checkButton	


if __name__ == '__main__':
	app.run(host='0.0.0.0', port=4000, debug=True, use_reloader=True)
