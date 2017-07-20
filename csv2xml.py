#!/usr/bin/env python


def tuples(filename, ped, default_setting):
    out = []

    f = open(filename)
    for line in f:
        fields = line.strip().split(",")
        if not fields:
            continue
        if fields[0] == "iEta":
            continue

        if ped:
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


def main(filename, ped, default_setting):
    lst = tuples(filename, ped, default_setting) + extra(default_setting)
    lst.sort()

    gaps = []
    for i, (rm, qie, setting) in enumerate(lst):
        if ped:
            print "    <Data qie='%d' rm='%d' elements='1' encoding='dec'>%d 0 0 0 0</Data>" % (qie, rm, setting)
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


if __name__ == "__main__":
    # main("HEP17_TDC_timing_corrections.csv", ped=False, default_setting=78)
    main("Pedestal_settings_bv60pedscan_298954_ADC36_v3.csv", ped=True, default_setting=38)
