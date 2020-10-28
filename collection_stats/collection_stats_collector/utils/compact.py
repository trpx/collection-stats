

class Compact:

    @classmethod
    def float(cls, flt: float):
        if flt >= 10**9:
            s = f'{flt:.2e}'
        elif flt >= 10:
            s = str(round(flt, 1))
        elif flt >= 1:
            s = str(round(flt, 1))
        elif flt == 0:
            s = '0'
        elif flt >= 0.1:
            s = str(round(flt, 1))
        elif flt >= 0.01:
            s = str(round(flt, 2))
        elif flt >= 0.001:
            s = str(round(flt, 3))
        else:
            s = f'{flt:.2e}'
        if s != '0' and '.' in s:
            s = s.rstrip('0')
            if s.endswith('.'):
                s = s[:-1]
        return s
