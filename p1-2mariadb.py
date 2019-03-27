#
# ESMR P1 uitlezer
# 11-2017 2016 - GJ - gratis te kopieren en te plakken
# 12-03-19 BG - en aan te passen ;)
# Stuurt gegevens naar tabel in Db

import serial
import sys
import time
import MySQLdb as mdb
versie = "1.2bg"

################
#Error display #
################

log = open("log.txt", "a")


def show_error():
   ft = sys.exc_info()[0]
   fv = sys.exc_info()[1]
   print("Fout type: %s" % ft)
   print("Fout waarde: %s" % fv)
   return

###########################################################
#function for storing readings into MySql                 #
###########################################################


def insertDB(T1afgenomen, T2afgenomen, T1terug, T2terug, Tarief, Afgenomenvermogen, Teruggeleverdvermogen, Totaalvermogen, Gas):

   try:
      con = mdb.connect('localhost', 'scotty', 'bhag4560', 'smeterdb')
      cursor = con.cursor()

      sql = "INSERT INTO mstanden(date, time, timestamp, T1afgenomen, T2afgenomen, T1terug, T2terug, Tarief, Afgenomenvermogen, Teruggeleverdvermogen, Totaalvermogen, Gas) \
    VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
          (time.strftime("%Y-%m-%d"), time.strftime("%H:%M"), timestamp, T1afgenomen, T2afgenomen,
           T1terug, T2terug, Tarief, Afgenomenvermogen, Teruggeleverdvermogen, Totaalvermogen, Gas)
      cursor.execute(sql)
      sql = []
      con.commit()
      con.close()
      log.write("Database import: " + time.strftime("%Y-%m-%d") +
                " " + time.strftime("%H:%M") + "\r\n")

   except mdb.Error, e:
      log.write("MariaDB error " + str(e) + time.strftime("%Y-%m-%d")
                + " " + time.strftime("%H:%M") + "\r\n")


##############################################################################
# Main program
##############################################################################
print ("DSMR 5.0 P1 uitlezer",  versie)
print ("Control-C om te stoppen")

# Set COM port config
ser = serial.Serial()
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS
ser.parity = serial.PARITY_NONE
ser.stopbits = serial.STOPBITS_ONE
ser.xonxoff = 0
ser.rtscts = 0
ser.timeout = 20
ser.port = "/dev/ttyUSB0"

# Open COM port
try:
   ser.open()
except:
   log.write("fout bij openen poort %s " % ser.name)
   sys.exit("Fout bij het openen van %s. Programma afgebroken." % ser.name)

# stack: array voor de 26 regels van het telegram.
counter = 0
stack = []

while counter < 26:
   p1_line = ''
# Read 1 line
   try:
      p1_raw = ser.readline()
   except:
      sys.exit(
          "Seriele poort %s gesloten. Programma afgebroken." % ser.name)
   p1_str = str(p1_raw)
   p1_line = p1_str.strip()
   stack.append(p1_line)
   counter = counter + 1
   # print (p1_line)

# counter: telegram heeft 26 regels.
# Daltarief, Afgenomenvermogen 1-0:1.8.1
# Piektarief, Afgenomenvermogen 1-0:1.8.2
# Daltarief, teruggeleverd vermogen 1-0:2.8.1
# Piek tarief, teruggeleverd vermogen 1-0:2.8.2
# Huidige stroomafname: 1-0:1.7.0
# Huidig teruglevering: 1-0:2.7.0
# Gasmeter: 0-1:24.2.1
# Tarief: 0-0:96.14

# Initialize
counter = 0
meter_tot = 0
T1afgenomen = 0
T1terug = 0
T2afgenomen = 0
T2terug = 0
Tarief = 0
Gas = 0
Afgenomenvermogen = 0
Teruggeleverdvermogen = 0
Totaalvermogen = 0
# f = open("teller.txt", "a")  # tijdelijke file voor testwerk, append
# genereer timestamp afgerond op min
timestamp = int(time.time() / 100) * 100

while counter < 26:
   if stack[counter][0:9] == "1-0:1.8.1":
      T1afgenomen = int(float(stack[counter][10:16]))
      log.write("daldag opgenomen: " + stack[counter][10:16] + "\r\n")
   elif stack[counter][0:9] == "1-0:1.8.2":
      T2afgenomen = int(stack[counter][10:16])
      log.write("piekdag opgenomen: " + stack[counter][10:16] + "\r\n")
   elif stack[counter][0:9] == "1-0:2.8.1":
      T1terug = int(stack[counter][10:16])
   elif stack[counter][0:9] == "1-0:2.8.2":
      T2terug = int(stack[counter][10:16])
   elif stack[counter][0:9] == "1-0:1.7.0":
      Afgenomenvermogen = int(float(stack[counter][10:16]) * 1000)
   elif stack[counter][0:9] == "1-0:2.7.0":
      Teruggeleverdvermogen = int(float(stack[counter][10:16]) * 1000)
      Totaalvermogen = Afgenomenvermogen - Teruggeleverdvermogen
   elif stack[counter][0:9] == "0-0:96.14":
      Tarief = int(stack[counter][12:16])
   elif stack[counter][0:10] == "0-1:24.2.1":
      Gas = int(float(stack[counter][26:35]) * 1000)
   else:
      pass
   counter = counter + 1

insertDB(T1afgenomen, T2afgenomen, T1terug, T2terug, Tarief,
         Afgenomenvermogen, Teruggeleverdvermogen, Totaalvermogen, Gas)


# Close port and show status
try:
   ser.close()
except:
   sys.exit("Oops %s. Programma afgebroken." % ser.name)
