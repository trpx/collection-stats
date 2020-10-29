import collections
import os
from pathlib import Path
import random
import sys


class SamplesWriter:
    def __init__(self, directory, max_samples=100):
        self._directory = directory
        self._max_samples = max_samples

    def write(self, struct):
        samples = self._gather_samples(struct)
        self._persist_samples(samples)

    def _gather_samples(self, struct, *, path=None, samples=None):
        path = path or ()
        samples = samples if samples is not None else collections.defaultdict(list)

        kwargs = dict(samples=samples)

        if isinstance(struct, dict):
            for k, v in struct.items():
                self._gather_samples(v, path=path+(k,), **kwargs)
        elif isinstance(struct, list):
            for i in struct:
                self._gather_samples(i, path=path, **kwargs)
        elif struct:
            samples[path].append(struct)

        return samples

    def _persist_samples(self, samples):

        for path_items, field_samples in samples.items():

            if not field_samples:
                continue

            tag = path_items[-1] if path_items else ''
            dst = Path(self._directory, *[i.replace(':', '~') for i in path_items])
            dst = dst.with_name(dst.name+'.txt')
            os.makedirs(dst.parent, exist_ok=True)

            count = len(field_samples)
            try:
                field_samples = set(field_samples)
                unique_count = len(field_samples)
            except TypeError:
                unique_count = 'unknown'

            selected_samples = random.sample(
                field_samples, min(len(field_samples), self._max_samples))

            selected_samples = [
                f'{tag[1:]}="{i}"' if tag.startswith('@') else f"<{tag}>{i}</{tag}>"
                for i in selected_samples
            ]

            heading = f"unique: {unique_count}, total: {count}"
            selected_samples_count = len(selected_samples)
            if selected_samples_count >= unique_count:
                heading += f"\nall unique entries:\n"
            else:
                heading += f"\n{len(selected_samples)} random unique entries:\n"
            dst.write_text(heading+'\n'.join(selected_samples)+'\n', encoding='utf8')
            print(f"written '{dst}'", file=sys.stderr)
