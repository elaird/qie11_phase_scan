#!/usr/bin/env python


def times(delta=7, tMax=-1, t0=-12, period=25):
    assert delta < period
    assert tMax < period

    out = []
    t = t0 - delta
    for iStep in range(period):
        t += delta
        if tMax < t:
            t -= period
        out.append(t)
    return out


def setting_wrt_64(time):
    if time < 0:
        assert -25 <= time
        return 50 + 2*time
    else:
        assert time <= 24.5
        return 64 + 2*time


def settings(nCycles=1, debug=False):
    if debug:
        header = "step   ns  setting"
        print(header)
        print("-" * len(header))

    out = []
    for i, t in enumerate(nCycles * times()):
        s = setting_wrt_64(t)
        out.append(s)
        if debug:
            print("  %2d  %3d   %3d" % (i, t, s))

    if debug:
        print("-" * len(header))
    return out


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
            out.append("put %s-QIE%s_PhaseDelay %d*%d" % (stem, qies, n_per_end, setting))
        else:
            out.append("get %s-QIE%s_PhaseDelay_rr" % (stem, qies))
    return out


def test():
    assert setting_wrt_64( 0) == 64
    assert setting_wrt_64( 1) == 66
    assert setting_wrt_64(-1) == 48

    t = times()
    assert sorted(t) == list(range(min(t), 1 + max(t)))

    for s in settings(debug=True):
        print(commands(s, "HB", put=True))
        print(commands(s, "HB", put=False))

    
if __name__ == "__main__":
    test()
