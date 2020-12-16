import collections
import hashlib
import itertools
import os
from pathlib import Path
import random
import re
import sys


class SamplesWriter:
    def __init__(self, directory, *, max_samples=100, is_xml_like):
        self._directory = directory
        self._max_samples = max_samples
        self._is_xml_like = is_xml_like

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
            dst = Path(self._directory, *[self._fix_path_name(i) for i in path_items])
            dst = dst.with_name(dst.name+'.txt')
            os.makedirs(dst.parent, exist_ok=True)

            count = len(field_samples)

            size_samples = collections.defaultdict(list)
            sizes = collections.Counter()

            for i in field_samples:
                item_size = self._obj_size(i)
                if item_size is None:
                    continue
                try:
                    size_samples[item_size].append(i)
                    sizes[item_size] += 1
                except:
                    continue

            top_k_sizes = dict(sizes.most_common(10))
            top_k = {random.choice(size_samples[size]): None for size in top_k_sizes}

            try:
                field_samples = set(field_samples)
                unique_count = len(field_samples)
            except TypeError:
                unique_count = 'unknown'

            field_samples = [i for i in field_samples if i not in top_k]
            top_k = list(top_k.keys())

            selected_samples = random.sample(
                field_samples, min(len(field_samples), self._max_samples))

            selected_samples = top_k + selected_samples

            separator = None
            if self._is_xml_like:
                tag_example = tag if tag.startswith('@') else f"<{tag}>"
                selected_samples = [
                    f'{tag[1:]}="{i}"' if tag.startswith('@') else f"<{tag}>{i}</{tag}>"
                    for i in selected_samples
                ]
            else:
                tag_example = tag
                linebreak_chars = {'\n', '\r'}
                has_linebreaks = bool(set(str(i) for i in selected_samples
                                          if isinstance(i, str)) & linebreak_chars)
                if has_linebreaks:
                    separator = hashlib.md5(
                        str(path_items).encode('utf8')+b'0g[3%yu$78qe').hexdigest()
                    separator = '--- ' + separator[:7] + ' --- {} --- ' + separator[7:14] + ' ---'
                    for n, i in enumerate(selected_samples):
                        if set(i) & linebreak_chars:
                            selected_samples[n] = separator.format('START')+'\n'\
                                                  + str(i) + '\n'+separator.format('END')

            top_k, selected_samples = selected_samples[:len(top_k)], selected_samples[len(top_k):]

            heading = tag + "\n\n"
            heading += f"** unique: {unique_count}, total: {count} **\n\n"

            if top_k:
                sizes_prefix = ''
                if len(top_k) < len(sizes):
                    sizes_prefix = 'most frequent '
                heading += f'** {len(top_k)} {sizes_prefix}sizes {top_k_sizes} **\n\n'\
                           + '\n'.join([str(i) for i in top_k]) + '\n'

            selected_samples_count = len(selected_samples)
            if selected_samples_count:
                heading += '\n** '
                if selected_samples_count >= unique_count:
                    heading += f"all unique entries:\n"
                else:
                    heading += f"{len(selected_samples)}"
                    if top_k:
                        heading += " other "
                    heading += "random unique entries **\n\n"
            report = heading+'\n'.join([str(i) for i in selected_samples])+'\n'
            if separator:
                report = f'separator form: {separator.format("SEP")}'
                report = report.replace(
                    separator.format('START')+'\n'+separator.format('END'),
                    separator.format('SEP'),
                )
            dst.write_text(report, encoding='utf8')
            print(f"written '{dst}'", file=sys.stderr)

    @classmethod
    def _fix_path_name(cls, path_name):
        for token, replacement in [
            [':', '~'],
        ]:
            path_name = path_name.replace(token, replacement)
        path_name = re.sub(r'\s', '_', path_name)
        path_name = re.sub(r'[^\d\w_~@-]', '$', path_name, flags=re.IGNORECASE)
        return path_name

    @classmethod
    def _obj_size(cls, obj):
        if isinstance(obj, (int, float)):
            return obj
        try:
            return len(obj)
        except TypeError:
            return
