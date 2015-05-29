#!/usr/bin/python

import requests, getopt, sys, lxml
import lxml.objectify
from pprint import pprint as pp

def usage():
    print('Usage: '+sys.argv[0]+' OPTIONS')
    print('')
    print('Where OPTIONS are:')
    print('-i, --sdsb_instance          Identifier of KaPA instance')
    print('-l, --client_member_class    Identifier of Subsystem making the request')
    print('-c, --client_member_code     Identifier of Organization making the request')
    print('-s, --client_subsystem_code  Identifier of Subsystem making the request')
    print('-t, --target_url             URL where request is sent')
    print('-g, --test_string            String which is embedded into request body.')
    print('                             If not defined, "test_string" will be used.')
    print('-m, --target_member_class    Type of Organization receiving the request (COM, GOV, PRI)')
    print('-e, --target_member_code     Identifier of Organization receiving the request')
    print('-y, --target_subsystem_code  Identifier of Subsystem receiving the request')
    print('-n, --target_namespace       Namespace of target service. If not defined, ')
    print('                             http://test.x-road.fi/producer will be used.')
    print('')


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:l:c:s:t:g:m:e:y:n:", ["help", "output="])
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
    test_string = "test_string"
    target_member_class = None
    target_member_code = None
    target_subsystem_code = None
    target_namespace = "http://test.x-road.fi/producer"

    for opt, arg in opts:
        if opt in ("-i", "--sdsb_instance"):
            sdsb_instance = arg
        elif opt in ("-l", "--client_member_class"):
	        member_class = arg
        elif opt in ("-c", "--client_member_code"):
            member_code = arg
        elif opt in ("-s", "--client_subsystem_code"):
            subsystem_code = arg
        elif opt in ("-t", "--target_url"):
            target_url = arg
        elif opt in ("-g", "--test_string"):
            test_string = arg
        elif opt in ("-m", "--target_member_class"):
            target_member_class = arg
        elif opt in ("-e", "--target_member_code"):
            target_member_code = arg
        elif opt in ("-y", "--target_subsystem_code"):
            target_subsystem_code = arg
        elif opt in ("-n", "--target_namespace"):
            target_namespace = arg
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
            <id:sdsbInstance>{0}</id:sdsbInstance>
            <id:memberClass>{5}</id:memberClass>
            <id:memberCode>{6}</id:memberCode>
            <id:subsystemCode>{7}</id:subsystemCode>
            <id:serviceCode>helloService</id:serviceCode>
            <id:serviceVersion>v1</id:serviceVersion>
        </sdsb:service>
        <sdsb:userId>EE1234567890</sdsb:userId>
        <sdsb:id>ID11234</sdsb:id>
    </SOAP-ENV:Header>
    <SOAP-ENV:Body>
        <ns1:helloService xmlns:ns1="{8}">
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
                   target_member_class,
                   target_member_code,
                   target_subsystem_code,
                   target_namespace,
                            )

    encoded_request = request.encode('utf-8')

    headers = {"Content-Type": "text/xml",
               "Content-Length": len(encoded_request)}
    response = requests.post(url = target_url,
                     headers = headers,
                     data = encoded_request,
                     verify = False)

    pp(response.text)

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
