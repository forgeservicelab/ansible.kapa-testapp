#!/usr/bin/python

import requests, getopt, sys, lxml
#from lxml import etree
import lxml.objectify

def usage():
    print('Usage: '+sys.argv[0]+' -i sdsb_instance -l member_class -c member_code -s subsystem_code -t target_url -g test_string')

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:l:c:s:t:g:", ["help", "output="])
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)
    if (len(opts) <= 0):
        usage()
        sys.exit(2)
    sdsb_instance = None
    member_class = None
    member_code = None
    subsystem_code = None
    target_url = None
    test_string = None
    for opt, arg in opts:
        if opt in ("-i", "--sdsb_instance"):
            sdsb_instance = arg
        elif opt in ("-l", "--member_class"):
	    member_class = arg
        elif opt in ("-c", "--member_code"):
            member_code = arg
        elif opt in ("-s", "--subsystem_code"):
            subsystem_code = arg
        elif opt in ("-t", "--target_url"):
            target_url = arg
        elif opt in ("-g", "--test_string"):
            test_string = arg
        else:
            assert False, "Unknown option"

    request = u"""<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:id="http://x-road.eu/xsd/identifiers" xmlns:sdsb="http://x-road.eu/xsd/sdsb.xsd">
    <SOAP-ENV:Header>
        <sdsb:client id:objectType="SUBSYSTEM">
            <id:sdsbInstance>{0}</id:sdsbInstance>
            <id:memberClass>{1}</id:memberClass>
            <id:memberCode>{2}</id:memberCode>
            <id:subsystemCode>{3}</id:subsystemCode>
        </sdsb:client>
        <sdsb:service id:objectType="SERVICE">
            <id:sdsbInstance>FI-DEV</id:sdsbInstance>
            <id:memberClass>GOV</id:memberClass>
            <id:memberCode>0245437-2</id:memberCode>
            <id:subsystemCode>TestService</id:subsystemCode>
            <id:serviceCode>helloService</id:serviceCode>
            <id:serviceVersion>v1</id:serviceVersion>
        </sdsb:service>
        <sdsb:userId>EE1234567890</sdsb:userId>
        <sdsb:id>ID11234</sdsb:id>
    </SOAP-ENV:Header>
    <SOAP-ENV:Body>
        <ns1:helloService xmlns:ns1="http://vrk-test.x-road.fi/producer">
            <request>
                <name>{4}</name>
            </request>
        </ns1:helloService>
    </SOAP-ENV:Body>
    </SOAP-ENV:Envelope>""".format(sdsb_instance,
				   member_class,
				   member_code,
				   subsystem_code,
				   test_string,
                            )

    encoded_request = request.encode('utf-8')

    headers = {"Content-Type": "text/xml",
               "Content-Length": len(encoded_request)}
    response = requests.post(url=target_url,
                     headers = headers,
                     data = encoded_request,
                     verify=False)

    xmlobj = lxml.objectify.fromstring(response.text.encode('utf-8'))
    hsres = xmlobj.Body.getchildren()[0]
    try:
        responseLine = hsres.response.findtext('ts1:message', namespaces=hsres.nsmap)
    except AttributeError as ae:
        print "Error occurred when parsing response: " + str(ae)
        exit(1)

    print responseLine

    if responseLine.find('Hello '+test_string) >= 0:
        exit(0)
    else:
        exit(1)

if __name__ == "__main__":
    main()
