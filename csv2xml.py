#!/usr/bin/env python2
# modeled after https://github.com/dnoonan08/hcalScripts/blob/master/makePhaseDelayTuningXML.py

import collections, datetime, optparse
from xml.etree import ElementTree


def adjustments(filename):
    out = {}
    f = open(filename)
    for line in f:
        fields = line.strip().split(",")
        if not fields:
            continue
        if fields[0] == "iEta":
            continue

        # iEta,iPhi,Depth,RM,RM fiber,channel number,Mean TDC time[ns],Uncertainty,Adjustment [ns],Adjustment [phase units]
        ieta, iphi, depth, rm, fi, ch, mean, unc, adjt, adj = fields

        rm = int(rm)
        fi = int(fi)
        ch = int(ch)
        qie = 6 * (fi - 1) + ch + 1

        rbx = "HEP17"
        out[(rbx, rm, qie)] = int(adj)
    f.close()
    return out


def adjusted(oldPhase, adjustment):
    newPhase = oldPhase - adjustment

    # FIXME: handle additional cases
    if newPhase < 64 and newPhase > 49:
        if adjustment < 0:
            newPhase += 14
        if adjustment > 0:
            newPhase -= 14
    return newPhase


def walk(tree, deltas, special, tag, bulk=None, settings=None):
    for block in tree.getroot():
        rbx = ''
        for value in block:
            if value.tag == "Parameter":
                if value.attrib["name"] == "RBX":
                    rbx = value.text
                if value.attrib["name"] == "CREATIONTAG":
                    value.text = tag

            if value.tag == "Data":
                rm = int(value.attrib["rm"])
                qie = int(value.attrib["qie"])
                special_channel = (rm, qie) in special
                oldPhase = int(value.text)

                adjustment = deltas.get((rbx, rm, qie))
                if adjustment is not None:
                    newPhase = adjusted(oldPhase, adjustment)
                    if bulk:
                        value.text = str(newPhase)
                        if not special_channel:
                            settings[rbx].append(newPhase)
                elif special_channel and (not bulk):
                    median = settings.get(rbx)
                    if median is not None:
                        value.text = str(median)


def report_medians(bulk_settings):
    header = "  RBX    n min med max"
    print header
    print "-" * len(header)

    out = {}
    for rbx, lst in sorted(bulk_settings.iteritems()):
        l2 = sorted(lst)
        n = len(l2)
        if n:
            med = l2[n / 2]
            print "%5s  %3d %3d %3d %3d" % (rbx, n, l2[0], med, l2[n - 1])
            out[rbx] = med
        else:
            print "%5s  %3d" % (rbx, n)
    return out


def make_new_file(oldXml, deltas, special, tag):
    tree = ElementTree.parse(oldXml)
    bulk_settings = collections.defaultdict(list)
    walk(tree, deltas, special, tag, bulk=True, settings=bulk_settings)
    medians = report_medians(bulk_settings)
    walk(tree, deltas, special, tag, bulk=False, settings=medians)
    tree.write("phaseDelay_%s.xml" % tag)


def main(opts):
    tag = "HE_" + datetime.date.today().strftime("%Y-%m-%d")
    deltas = adjustments(opts.phaseDelay)

    special = [(1, 35), (2, 19), (2, 30), (2, 38), (3, 8), (3, 19), (3, 35), (4, 19)]
    for iQie in range(1, 13):
        special.append((5, iQie))

    make_new_file(opts.oldXml, deltas, special, tag)


def options():
    # from QIE11_spec_2015run_30mar2016.pdf

    parser = optparse.OptionParser(usage="usage: %prog [options] ")
    parser.add_option("--old-xml",
                      dest="oldXml",
                      default="he_delay_2018_v2.xml",
                      metavar="foo.xml",
                      help="")
    parser.add_option("--phase-delay",
                      dest="phaseDelay",
                      default="HEP17_TDC_timing_corrections.csv",
                      metavar="foo.csv",
                      help="")
    opts, args = parser.parse_args()
    return opts


if __name__ == "__main__":
    main(options())
