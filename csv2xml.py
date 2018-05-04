#!/usr/bin/env python2
# modeled after https://github.com/dnoonan08/hcalScripts/blob/master/makePhaseDelayTuningXML.py

import collections, datetime, optparse, sys
from xml.etree import ElementTree


def det2fe(filenames=["2018HCALLMap_ngHE_K_20180214.txt"], nExpected=26,
           iSide=0, iEta=1, iPhi=2, iDepth=4, iDet=5, iRbx=6, iRm=11, iRmFib=12, iRmFibCh=13):
    out = {}
    for filename in filenames:
        iLine = 0
        f = open(filename)
        for line in f:
            iLine += 1
            if not line:
                continue
            fields = line.split()
            if fields[0].startswith("#") or fields[0] == "side":
                continue

            if len(fields) != nExpected and nExpected is not None:
                print len(fields), fields
                continue

            if fields[iDet] != "HE":
                continue

            key = (int(fields[iSide]) * int(fields[iEta]), int(fields[iPhi]), int(fields[iDepth]))
            value = (fields[iRbx], int(fields[iRm]), int(fields[iRmFib]), int(fields[iRmFibCh]))
            if key in out:
                print "WARNING: found duplicate (line %d):" % iLine, key, value, out[key]
            else:
                out[key] = value
        f.close()
    return out


def adjustments(filename):
    conversion = det2fe()
    out = {}
    f = open(filename)
    for line in f:
        fields = line.strip().split(",")
        if not fields:
            continue
        if fields[0] == "nDigis":
            continue

        # v1: nDigis,iEta,iPhi,Depth,Mean TDC time[ns], TDC time RMS[ns], Uncertainty,Adjustment[ns],Adjustment[phase units]
        # v3: nDigis,iEta,iPhi,Depth,Mean TDC time[ns], TDC time RMS[ns], Uncertainty,Adjustment[ns],Adjustment[phase units],Net adjustment combined with first round
        n, ieta, iphi, depth, mean, rms, unc, adjt, adj = fields[:9]

        rbx, rm, fi, ch = conversion[(int(ieta), int(iphi), int(depth))]
        qie = 6 * (fi - 1) + ch + 1
        out[(rbx, rm, qie)] = int(adj)
    f.close()
    return out


def adjusted(oldPhase, adjustment, offset):
    # QIE11_spec_2015run_30mar2016.pdf

    newPhase = oldPhase - adjustment + offset

    if newPhase < 0:
        print "clipping newPhase from %d to 0" % newPhase
        newPhase = 0

    if 49 < newPhase < 64:
        if adjustment < 0:
            newPhase += 14
        if adjustment > 0:
            newPhase -= 14

    if 113 < newPhase:
        print "clipping newPhase from %d to 113" % newPhase
        newPhase = 113
    return newPhase


def walk(tree, deltas, special, date, tag, bulk=None, settings=None, offset=None):
    for block in tree.getroot():
        rbx = ''
        for value in block:
            if value.tag == "Parameter":
                if value.attrib["name"] == "RBX":
                    rbx = value.text
                if value.attrib["name"] == "CREATIONSTAMP":
                    value.text = date
                if value.attrib["name"] == "CREATIONTAG":
                    value.text = tag

            if value.tag == "Data":
                rm = int(value.attrib["rm"])
                qie = int(value.attrib["qie"])
                special_channel = (rm, qie) in special
                adjustment = deltas.get((rbx, rm, qie))

                if bulk and adjustment is not None:
                    newPhase = adjusted(int(value.text), adjustment, offset)
                    value.text = str(newPhase)
                    if not special_channel:
                        settings[rbx].append(newPhase)

                if (not bulk) and special_channel:
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



def special_channels():
    special = [(1, 35), (2, 19), (2, 30), (2, 38), (3, 8), (3, 19), (3, 35), (4, 19)]
    for iQie in range(1, 13):
        special.append((5, iQie))
    return special


def main(opts):
    deltas = adjustments(opts.phaseDelay)
    special = special_channels()
    date = datetime.date.today().strftime("%Y-%m-%d")
    tag = "%s_%s_v%d" % (opts.tag, date, opts.version)

    tree = ElementTree.parse(opts.oldXml)
    bulk_settings = collections.defaultdict(list)
    walk(tree, deltas, special, date, tag, bulk=True, settings=bulk_settings, offset=opts.offset)
    medians = report_medians(bulk_settings)
    walk(tree, deltas, special, date, tag, bulk=False, settings=medians)
    tree.write("%s.xml" % tag)


def options():
    parser = optparse.OptionParser(usage="usage: %prog [options] ")
    parser.add_option("--tag",
                      dest="tag",
                      default="phaseTuning_HE",
                      help="tag (default is phaseTuning_HE_DATE_VERSION)")
    parser.add_option("--iteration",
                      dest="iteration",
                      default=0,
                      type="int",
                      metavar="N",
                      help="iteration number")
    opts, args = parser.parse_args()
    if not opts.iteration:
        parser.print_help()
        sys.exit("\n\nPlease specify an iteration number.")
    return opts


if __name__ == "__main__":
    opts = options()

    if opts.iteration == 1:
        opts.offset = -64
        opts.oldXml = "he_delay_2018_v2.xml"
        opts.phaseDelay = "heller_HE_tuning_proposal_Apr24.csv"
        opts.version = 2
    if opts.iteration == 2:
        opts.offset = 0
        opts.oldXml = "phaseTuning_HE_2018-04-25_v2.xml"
        opts.phaseDelay = "HE_phase_adjustments_round3.csv"
        opts.version = 1

    main(opts)
