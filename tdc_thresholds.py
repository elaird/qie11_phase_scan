#!/usr/bin/env python


def settings(nCycles=1, debug=False):
    out = []
    for iBit in range(8):
        out.append(1 << iBit)
    if debug:
        print(out)

    return out * nCycles


def commands(setting, subdet, put=False):
    out = []

    if subdet == "HB":
        sectors = "[01-18]"
        rms = "[1-4]"
        qies = "[1-64]"
        n_per_end = 18 * 4 * 64
    elif subdet == "HE":
        sectors = "[01-18]"
        rms = "[1-4]"
        qies = "[1-48]"
        n_per_end = 18 * 4 * 48
    else:
        print("Subdetector %s is not supported." % subdet)
        return out

    for end in "MP":
        stem = "%s%s%s-%s" % (subdet, end, sectors, rms)
        if put:
            out.append("put %s-QIE%s_TimingThresholdDAC %d*%d" % (stem, qies, n_per_end, setting))
        else:
            out.append("get %s-QIE%s_TimingThresholdDAC" % (stem, qies))
    return out


def test():
    for s in settings(debug=True):
        print(commands(s, put=True))
        print(commands(s, put=False))

    
if __name__ == "__main__":
    test()
