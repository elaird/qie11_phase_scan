#!/usr/bin/env python2


def setting(rbx):
    # http://hcalmon.cms/cgi-bin/cvsweb.cgi/HcalCfg/RBX/ngSettings.cfg?rev=1.451
    if rbx in ["HEM05", "HEM06"]:
        return 89
    if rbx in ["HEP01", "HEP02"]:
        return 69
    return 79


def loop(tag):
    for end in "MP":
        for iRbx in range(1, 19):
            rbx = "HE%1s%02d" % (end, iRbx)
            print '  <CFGBrick>'
            print '  <Parameter name="INFOTYPE" type="string">DELAY</Parameter>'
            print '  <Parameter name="CREATIONSTAMP" type="string">2018-04-24</Parameter>'
            print '  <Parameter name="CREATIONTAG" type="string">%s</Parameter>' % tag
            print '  <Parameter name="RBX" type="string">%s</Parameter>' % rbx

            for iRm in range(1, 6):
                for iQie in range(1, 49):
                    if iRm == 5 and 13 <= iQie:
                        continue
                    print '  <Data elements="1" encoding="dec" qie="%d" rm="%d">%d</Data>' % (iQie, iRm, setting(rbx))

            print '  </CFGBrick>'


def main(tag):
    print '<?xml version="1.0" encoding="ISO-8859-1"?>\n<CFGBrickSet>'
    loop(tag)
    print '</CFGBrickSet>'


if __name__ == "__main__":
    main(tag="HE_2018_v2")
