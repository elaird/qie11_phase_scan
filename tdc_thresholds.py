#!/usr/bin/env python


def settings(nCycles=1, debug=False):
    out = []
    for iBit in range(8):
        out.append(1 << iBit)
    if debug:
        print(out)

    return out * nCycles


def commands(setting, rms="[1-4]", qies="[1-64]", put=False):
    out = []
    for end in "MP":
        stem = "HB%s[01-18]-%s" % (end, rms)
        if put:
            mult = 4 * 64 * 18
            out.append("put %s-QIE%s_TimingThresholdDAC %d*%d" % (stem, qies, mult, setting))
        else:
            out.append("get %s-QIE%s_TimingThresholdDAC" % (stem, qies))
    return out


def test():
    for s in settings(debug=True):
        print(commands(s, put=True))
        print(commands(s, put=False))

    
if __name__ == "__main__":
    test()
