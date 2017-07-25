#!/usr/bin/env python

import optparse

def tuples(filename, default_setting, ped=False, capid=False):
    out = []
    if not filename:
        return out

    f = open(filename)
    for line in f:
        fields = line.strip().split(",")
        if not fields:
            continue
        if fields[0] == "iEta":
            continue

        if ped:
            if capid:
                # iEta,iPhi,Depth,CapID,RM,RM fiber,channel,Best DAC setting,Best mean pedestal,Error on best mean pedestal
                ieta, iphi, depth, capid, rm, fi, ch, dac, ped_mean, ped_unc = fields
                setting = (int(capid), int(dac))
            else:
                # iEta,iPhi,Depth,RM,RM fiber,channel,Best DAC setting,Best mean pedestal,Error on best mean pedestal
                ieta, iphi, depth, rm, fi, ch, dac, ped_mean, ped_unc = fields
                setting = int(dac)
        else:
            # iEta,iPhi,Depth,RM,RM fiber,channel number,Mean TDC time[ns],Uncertainty,Adjustment [ns],Adjustment [phase units]
            ieta, iphi, depth, rm, fi, ch, mean, unc, adjt, adj = fields
            setting = default_setting - int(adj)

        rm = int(rm)
        fi = int(fi)
        ch = int(ch)
        qie = 6 * (fi - 1) + ch + 1
        out.append((rm, qie, setting))
    f.close()
    return out


def extra(default_setting):
    out = []

    # zero-suppressed    
    for (rm, qie) in [(1, 35),
                      (2, 19),
                      (2, 30),
                      (2, 38),
                      (3,  8),
                      (3, 19),
                      (3, 35),
                      (4, 19),
                      ]:
        out.append((rm, qie, default_setting))

    # CU
    for qie in range(1, 13):
        out.append((5, qie, default_setting))
    return out


def main(opts):
    if opts.ped:
        lst = tuples(opts.PedestalDAC, default_setting=opts.defaultPedestalDAC, ped=True) + extra(opts.defaultPedestalDAC)
        lst.sort()

        lst2 = tuples(opts.CapIDpedestal, default_setting=opts.defaultCapIDpedestal, ped=True, capid=True)  # no extra
        lst2.sort()
    else:
        lst = tuples(opts.PhaseDelay, default_setting=opts.defaultPhaseDelay) + extra(opts.defaultPhaseDelay)
        lst.sort()

    gaps = []
    for i, (rm, qie, setting) in enumerate(lst):
        if opts.ped:
            caps = {}
            for capid in range(4):
                caps[capid] = opts.defaultCapIDpedestal
            for (rm2, qie2, (capid, setting2)) in lst2:
                if rm2 != rm:
                    continue
                if qie2 != qie:
                    continue
                caps[capid] = setting2
            print "    <Data qie='%d' rm='%d' elements='1' encoding='dec'>%d %d %d %d %d</Data>" % (qie, rm, setting, caps[0], caps[1], caps[2], caps[3])
        else:
            print "    <Data qie='%d' rm='%d' elements='1' encoding='dec'>%d</Data>" % (qie, rm, setting)
        if i:
            rm0, qie0, setting0 = lst[i - 1]
            within_rm = qie - qie0 == 1
            new_rm = qie == 1 and qie0 == 48 and (rm - rm0) == 1
            if not any([within_rm, new_rm]):
                gaps.append("prev: %d %d  ,  this: %d %d" % (rm0, qie0, rm, qie))

    if gaps:
        print "\n\nFound these gaps:"
        for gap in gaps:
            print gap


def options():
    # from QIE11_spec_2015run_30mar2016.pdf

    parser = optparse.OptionParser(usage="usage: %prog [options] ")
    parser.add_option("--ped",
                      dest="ped",
                      default=False,
                      action="store_true",
                      help="Generate pedestal settings (rather than phase delays)")
    parser.add_option("--default-PhaseDelay",
                      dest="defaultPhaseDelay",
                      default=78,
                      type="int",
                      metavar="N",
                      help="")
    parser.add_option("--PhaseDelay",
                      dest="PhaseDelay",
                      default="HEP17_TDC_timing_corrections.csv",
                      metavar="foo.csv",
                      help="")
    parser.add_option("--default-pedestalDAC",
                      dest="defaultPedestalDAC",
                      default=38,
                      type="int",
                      metavar="N",
                      help="")
    parser.add_option("--PedestalDAC",
                      dest="PedestalDAC",
                      default="Pedestal_settings_bv60pedscan_298954_ADC36_v3.csv",
                      metavar="foo.csv",
                      help="")
    parser.add_option("--default-CapIDpedestal",
                      dest="defaultCapIDpedestal",
                      default=0,
                      type="int",
                      metavar="N",
                      help="")
    parser.add_option("--CapIDpedestal",
                      dest="CapIDpedestal",
                      default="pedestal_settings_capidscan_299456_ADC9.csv",
                      metavar="foo.csv",
                      help="")
    opts, args = parser.parse_args()
    return opts


if __name__ == "__main__":
    main(options())
