
import json, sys, time, urllib2

def coord_to_block(x, y):
	url = "http://data.fcc.gov/api/block/find?format=json&latitude=%s&longitude=%s" % (str(x), str(y))

	try:
		jsonStr = urllib2.urlopen(url)
	except URLError as detail:
		sys.stderr.write("Couldn't open: ", detail)
		time.sleep(2)

	jsonStr = jsonStr.read()
	jsonObj = json.loads(jsonStr)

	if jsonObj['status'] == "OK":
		return jsonObj['Block']['FIPS']
	else
		sys.stderr.write("Status NOT OK")
		sys.exit(0)



