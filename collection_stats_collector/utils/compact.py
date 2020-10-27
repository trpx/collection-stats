

class Compact:

    @classmethod
    def float(cls, flt: float):
        if flt >= 1000:
            s = f'{flt:.2e}'
        elif flt >= 10:
            s = f'{flt:.0f}'
        elif flt >= 1:
            s = f'{flt:.1f}'
        elif flt == 0:
            s = f'{flt:.0f}'
        elif flt >= 0.1:
            s = f'{flt:.2f}'
        elif flt >= 0.01:
            s = f'{flt:.3f}'
        else:
            s = f'{flt:.2e}'
        if s != '0':
            if '.' in s:
                s = s.rstrip('0')
                if s.endswith('.'):
                    s = s[:-1]
        return s

    @classmethod
    def share(cls, share: float):
        return f'{cls.float(share*100)}%'
