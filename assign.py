import collections
import logging
import json
import re

import time

logging.basicConfig(level=logging.DEBUG)
from spyne import Application, rpc, ServiceBase, Integer, Unicode
from spyne import Iterable
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication
import urllib



class HelloWorldService(ServiceBase):
    @rpc(float, float, float, _returns=Iterable(Unicode))
    def checkcrime(ctx, lat, lon, radius):
        url = "https://api.spotcrime.com/crimes.json?lat=%s&lon=%s&radius=%s&key=." %(lat ,lon ,radius)
        f = urllib.urlopen(url)
        c= f.read()
        dict = json.loads(c)

        # TotalCrimes
        totalcrimes = len(dict['crimes'])  # 50

        # TypesOfCrimes
        typesofcrime = []
        for i in range(totalcrimes):
            crimetype = dict['crimes'][i]
            x = crimetype['type']
            typesofcrime.append(x)
        other = 0
        arrest = 0
        vandalism = 0
        burglary = 0
        assault = 0
        theft = 0
        robbery = 0
        for i in range(len(typesofcrime)):
            if "Other" in typesofcrime[i]:
                other += 1
            elif "Theft" in typesofcrime[i]:
                theft += 1
            elif "Arrest" in typesofcrime[i]:
                arrest += 1
            elif "Assault" in typesofcrime[i]:
                assault += 1
            elif "Vandalism" in typesofcrime[i]:
                vandalism += 1
            elif "Burglary" in typesofcrime[i]:
                burglary += 1
            elif "Robbery" in typesofcrime[i]:
                robbery += 1

        y = {'Other': other, 'Theft': theft, 'Arrest': arrest, 'Assault': assault, 'Vandalism': vandalism,
             'Burglary': burglary, 'Robbery': robbery}
        #print y
        #yield y

        # MostDangerousStreets
        mylist = []
        finallist = []
        for i in range(totalcrimes):
            newd = dict['crimes'][i]
            nextd = newd['address']
            mylist.append(nextd)
        #print mylist
        for i in range(len(mylist)):
            if "BLOCK OF" in mylist[i]:
                a = re.split('BLOCK OF', mylist[i])
                z=a[1]+" "
                finallist.append(z)

            elif "BLOCK BLOCK" in mylist[i]:
                b = re.split('BLOCK BLOCK', mylist[i])
                x=b[1]+" "
                finallist.append(x)

            elif "BLOCK" in mylist[i]:
                c = re.split('BLOCK', mylist[i])
                p=c[1]+" "
                finallist.append(p)

            elif "&" in mylist[i]:
                d = re.split('&', mylist[i])
                a=d[0]
                b=" "+a
                finallist.append(b)
                q= d[1]+" "
                finallist.append(q)

            else:
                a = mylist[i]
                b=" "+a+" "
                finallist.append(b)
        #print finallist
        temp = set(finallist)
        result = {}
        for i in temp:
            result[i] = finallist.count(i)
        counter = collections.Counter(result)
        #print counter

        z = sorted(result, key=result.get, reverse=True)[:3]
        #print z




        # TimeOfCrimes
        timelist = []
        onlytime = []
        for i in range(totalcrimes):
            crimetime = dict['crimes'][i]
            timelist.append(crimetime['date'])
            timex = re.split(' ', timelist[i])
            timexx = timex[1] + " " + timex[2]
            onlytime.append(timexx)
        #print onlytime

        time123am = 0
        time36am = 0
        time69am = 0
        time912noon = 0
        time123pm = 0
        time36pm = 0
        time69pm = 0
        time912midnight = 0

        for i in range(len(onlytime)):
            a = onlytime[i]
            c = str(a)
            b = time.strptime(c, "%I:%M %p")
            min = (b.tm_hour * 60) + (b.tm_min)
            if (min >= 1 and min <= 180):
                time123am += 1
            elif (min >= 181 and min <= 360):
                time36am += 1
            elif (min >= 361 and min <= 540):
                time69am += 1
            elif (min >= 541 and min <= 720):
                time912noon += 1
            elif (min >= 721 and min <= 900):
                time123pm += 1
            elif (min >= 901 and min <= 1080):
                time36pm += 1
            elif (min >= 1081 and min <= 1260):
                time69pm += 1

            elif (min >= 1261 and min <= 1440 or min ==0):
                time912midnight += 1

        event_time_count = {
            "12:01am-3am": time123am,
            "3:01am-6am": time36am,
            "6:01am-9am": time69am,
            "9:01am-12noon": time912noon,
            "12:01pm-3pm": time123pm,
            "3:01pm-6pm": time36pm,
            "6:01pm-9pm": time69pm,
            "9:01pm-12midnight": time912midnight
        }

        finaloutput={
            "total_crime":totalcrimes,
            "the_most_dangerous_streets":z,
            "crime_type_count":y,
            "event_time_count":event_time_count
        }
        #print finaloutput
        yield finaloutput









application = Application([HelloWorldService],
                          tns='spyne.examples.hello',
                          in_protocol=HttpRpc(validator='soft'),
                          out_protocol=JsonDocument()
                          )

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    wsgi_app = WsgiApplication(application)
    server = make_server('0.0.0.0', 8000, wsgi_app)
    server.serve_forever()
