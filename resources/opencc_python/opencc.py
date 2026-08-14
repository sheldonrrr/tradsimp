# -*- coding: utf-8 -*-

##########################################################
# Author: Yichen Huang (Eugene)
# GitHub: https://github.com/yichen0831/opencc-python
# January, 2016
##########################################################

##########################################################
# Revised by: Hopkins
# December, 2022
# Apache License Version 2.0, January 2004
# - Use a tree-like structure hold the result during conversion
# - Always choose the longest matching string from left to right in dictionary
#   by trying lookups in the dictionary rather than looping
# - Split the incoming string into smaller strings before processing to improve speed
# - Only match once per dictionary
# - If a dictionary is configured as part of a group, only match once per group
#   in order of the listed dictionaries
# - Cache the results of reading a dictionary in self.dict_cache
##########################################################
##########################################################
# Revised for Chinese Conversion plugin:
# - Honor OpenCC config "segmentation" (mmseg forward max-match)
# - Optional Jieba segmentation mode for phrase-level accuracy
##########################################################

import json
import re

CONFIG_FILE = 'config'
DICT_FILE = 'dictionary'

SEGMENTATION_MMSEG = 'mmseg'
SEGMENTATION_JIEBA = 'jieba'

CHAINED_CONVERSIONS = {
    'hk2tw': ('hk2t', 't2tw'),
    'tw2hk': ('tw2t', 't2hk'),
}

CHAINED_CONVERSION_NAMES = {
    'hk2tw': 'Traditional Chinese (Hong Kong) to Traditional Chinese (Taiwan)',
    'tw2hk': 'Traditional Chinese (Taiwan) to Traditional Chinese (Hong Kong)',
}

FORCED_PIVOT_REVERSE = {
    's2t': 't2s',
    's2tw': 'tw2sp',
    's2twp': 'tw2sp',
    's2hk': 'hk2sp',
    's2hkp': 'hk2sp',
}

# Regional reverse-phrase tables. Multi-char keys are merged into mmseg
# segmentation so shorter TSPhrases hits cannot split 義大利 / 滑鼠 etc.
REGIONAL_REVERSE_PHRASE_DICTS = ('TWPhrasesRev.txt', 'HKPhrasesRev.txt')


class OpenCC:
    def __init__(self, resource_getter, conversion=None):
        """
        init OpenCC
        :param resource_getter: function that takes 2 parameters.
         The first parameter is CONFIG_FILE, or DICT_FILE
         The second parameter is a file name associated with the directory.
         It returns bytes from the selected file.
        :param conversion: the conversion of usage, options include
         'hk2s', 'hk2sp', 'hk2tw', 's2hk', 's2hkp', 's2t', 's2tw', 's2twp', 't2hk', 't2s',
         't2tw', 'tw2hk', 'tw2s', 'tw2sp', 'tw2t', 'jp2t', 't2jp'
         check the json file names in config directory
        :return: None
        """
        self.conversion_name = ''
        self.conversion = conversion
        self.replacement_counts = {}
        self.chars_processed = 0
        self.diagnostic_counts = {}
        self._diagnostic_samples = []
        self._diagnostic_sample_keys = set()
        self._diagnostic_sample_limit = 20
        self._dict_init_done = False
        self._dict_chain = list()
        self._dict_chain_data = list()
        self._normalization_chain_data = list()
        self._segmentation_chain = list()
        self._seg_max_len = 1
        self._seg_keys = set()
        self._has_segmentation = False
        self._segmentation_mode = SEGMENTATION_MMSEG
        self._force_pivot_conversion = False
        self._post_convert = None  # optional callable(str) -> str (e.g. MediaWiki zhconv)
        self._post_convert_label = None
        self._jieba_samples = []
        self._jieba_sample_keys = set()
        self._jieba_sample_limit = 8
        self.dict_cache = dict()
        self._chain_converters = {}
        self.resource_getter = resource_getter
        # List of sentence separators from OpenCC PhraseExtract.cpp. None of these separators are allowed as
        # part of a dictionary entry
        self.split_chars_re = re.compile(
            r'(\s+|-|,|\.|\?|!|\*|　|，|。|、|；|：|？|！|…|“|”|‘|’|『|』|「|」|﹁|﹂|—|－|（|）|《|》|〈|〉|～|．|／|＼|︒|︑|︔|︓|︿|﹀|︹|︺|︙|︐|［|﹇|］|﹈|︕|︖|︰|︳|︴|︽|︾|︵|︶|｛|︷|｝|︸|﹃|﹄|【|︻|】|︼|—|， |： |︲|～)')
        if self.conversion is not None:
            self._init_dict()


    def convert(self, string):
        """
        Convert string from Simplified Chinese to Traditional Chinese or vice versa
        """
        converted, _spans = self.convert_with_details(string)
        return converted

    def set_post_convert(self, callback, label=None):
        """
        Optional post-pass after OpenCC (e.g. MediaWiki zhconv).
        callback: callable(str) -> str, or None to clear.
        When the post-pass changes text, bilingual spans collapse to one safe span.
        """
        self._post_convert = callback
        self._post_convert_label = label

    def get_post_convert_label(self):
        return self._post_convert_label

    def _apply_post_convert(self, original, converted, spans):
        callback = self._post_convert
        if callback is None or converted is None:
            return converted, spans
        try:
            post = callback(converted)
        except Exception:
            return converted, spans
        if post is None or post == converted:
            return converted, spans
        # Post-pass may reshuffle phrase boundaries; keep one aligned span.
        return post, [self._make_span(0, len(original), original, post)]

    def convert_with_details(self, string):
        """
        Convert text and return source-aligned spans for bilingual rendering.

        Spans are exact for a conversion stage whose output length is stable. If a
        later regional-phrase stage changes length, the affected segmentation unit
        is deliberately returned as one span so callers never lose or misalign text.
        """
        # Count only on this instance (chain/pivot children keep their own totals).
        if string is not None:
            self.chars_processed += len(string)

        pivot_mode = self._forced_pivot_reverse_mode()
        if pivot_mode is not None:
            pivot = self._get_chain_converter(pivot_mode).convert(string)
            converted, _target_spans = self._convert_with_details_direct(pivot)
            spans = self._forced_pivot_spans(
                string, pivot, converted, pivot_mode)
            return self._apply_post_convert(string, converted, spans)
        converted, spans = self._convert_with_details_direct(string)
        return self._apply_post_convert(string, converted, spans)

    def _convert_with_details_direct(self, string):
        """Run the selected config once, without the optional pivot pre-pass."""
        # echo the input if no conversion is wanted
        if self.conversion == "no_conversion":
            return string, [self._make_span(0, len(string), string, string)]

        chain = CHAINED_CONVERSIONS.get(self.conversion)
        if chain is not None:
            result = string
            for mode in chain:
                result = self._get_chain_converter(mode).convert(result)
            return result, [self._make_span(0, len(string), string, result)]

        if not self._dict_init_done:
            self._init_dict()
            self._dict_init_done = True

        self._record_mixed_input_diagnostics(string)
        original = string
        if self._normalization_chain_data:
            string = self._convert(string, self._normalization_chain_data)

        result = []
        spans = []
        source_offset = 0
        # Separate string using the list of separators in a regular expression
        split_string_list = self.split_chars_re.split(string)
        for i in range(0, len(split_string_list)):
            if i % 2 == 0:
                converted, unit_spans = self._convert_text_unit_with_details(
                    split_string_list[i], source_offset)
                result.append(converted)
                spans.extend(unit_spans)
            else:
                separator = split_string_list[i]
                result.append(separator)
                spans.append(self._make_span(
                    source_offset, source_offset + len(separator),
                    separator, separator))
            source_offset += len(split_string_list[i])
        converted = "".join(result)
        if original != string:
            # Compatibility normalization can change source coordinates. Preserve
            # content correctness and use one safe bilingual span in that rare case.
            spans = [self._make_span(0, len(original), original, converted)]
        return converted, self._merge_adjacent_spans(spans)

    def _forced_pivot_reverse_mode(self):
        if not self._force_pivot_conversion:
            return None
        return FORCED_PIVOT_REVERSE.get(self.conversion)

    def _forced_pivot_spans(self, original, pivot, converted, pivot_mode):
        """
        Align the real source with the final target. Most OpenCC mappings are
        length-stable; use positional spans there. Fall back to one safe span
        when either conversion stage changes length.
        """
        dictionary = 'forced-pivot:{}->{}'.format(
            pivot_mode, self.conversion)
        if len(original) != len(pivot) or len(pivot) != len(converted):
            return [self._make_span(
                0, len(original), original, converted,
                kind='forced_pivot', dictionary=dictionary)]

        spans = []
        for index, (source, target) in enumerate(zip(original, converted)):
            spans.append(self._make_span(
                index, index + 1, source, target,
                kind='forced_pivot', dictionary=dictionary))
        return self._merge_adjacent_spans(spans)

    def _convert_text_unit(self, text):
        """Segment (optional) then apply the conversion chain to each piece."""
        converted, _spans = self._convert_text_unit_with_details(text, 0)
        return converted

    def _convert_text_unit_with_details(self, text, source_offset):
        """Convert one punctuation-delimited unit and retain source boundaries."""
        if not text:
            return text, []
        if self._should_segment():
            segments = self._segment(text)
            converted_parts = []
            spans = []
            offset = source_offset
            for segment in segments:
                converted, segment_spans = self._convert_segment_with_details(
                    segment, offset)
                converted_parts.append(converted)
                spans.extend(segment_spans)
                offset += len(segment)
            if self._segmentation_mode == SEGMENTATION_JIEBA:
                self._maybe_record_jieba_sample(text, segments, converted_parts)
            return "".join(converted_parts), spans
        return self._convert_segment_with_details(text, source_offset)

    def _convert_segment_with_details(self, text, source_offset):
        if not self._dict_chain_data:
            return text, [self._make_span(
                source_offset, source_offset + len(text), text, text)]

        events = []
        first_tree = self._convert_to_tree(
            text, [self._dict_chain_data[0]], events=events)
        first_output = "".join(first_tree.inorder())
        final_output = first_output
        for item in self._dict_chain_data[1:]:
            final_output = self._convert(
                final_output, [item], events=events)
        self._record_conversion_events(events)

        records = first_tree.inorder_records()
        if len(first_output) != len(final_output):
            return final_output, [self._make_span(
                source_offset, source_offset + len(text), text, final_output,
                kind='fallback')]

        spans = []
        output_offset = 0
        for record in records:
            target_len = len(record['target'])
            target = final_output[output_offset:output_offset + target_len]
            start = source_offset + record['source_start']
            end = source_offset + record['source_end']
            source = text[record['source_start']:record['source_end']]
            match = record.get('match') or {}
            spans.append(self._make_span(
                start, end, source, target,
                kind=match.get('kind', 'unmatched'),
                dictionary=match.get('dictionary'),
                ambiguous=bool(match.get('ambiguous'))))
            output_offset += target_len
        return final_output, spans

    @staticmethod
    def _make_span(start, end, source, target, kind='unmatched',
                   dictionary=None, ambiguous=False):
        return {
            'source_start': start,
            'source_end': end,
            'source': source,
            'target': target,
            'kind': kind,
            'dictionary': dictionary,
            'ambiguous': ambiguous,
        }

    @staticmethod
    def _merge_adjacent_spans(spans):
        merged = []
        for span in spans:
            if not span.get('source') and not span.get('target'):
                continue
            if merged:
                previous = merged[-1]
                same_metadata = all(
                    previous.get(key) == span.get(key)
                    for key in ('kind', 'dictionary', 'ambiguous'))
                same_change_state = (
                    (previous['source'] == previous['target'])
                    == (span['source'] == span['target']))
                if (previous['source_end'] == span['source_start']
                        and same_metadata and same_change_state):
                    previous['source_end'] = span['source_end']
                    previous['source'] += span['source']
                    previous['target'] += span['target']
                    continue
            merged.append(dict(span))
        return merged

    def _maybe_record_jieba_sample(self, text, segments, converted_parts):
        """Keep a few multi-token cuts so logs can show how Jieba split the text."""
        if len(self._jieba_samples) >= self._jieba_sample_limit:
            return
        if not text or not segments or len(segments) < 2:
            return
        # Prefer short phrase-like spans; skip huge paragraphs.
        if len(text) < 4 or len(text) > 40:
            return
        if not any(len(seg) >= 2 for seg in segments):
            return
        key = text
        if key in self._jieba_sample_keys:
            return
        self._jieba_sample_keys.add(key)
        self._jieba_samples.append({
            'text': text,
            'segments': list(segments),
            'converted_segments': list(converted_parts),
        })

    def _should_segment(self):
        if self._segmentation_mode == SEGMENTATION_JIEBA:
            return True
        return self._has_segmentation

    def _segment(self, text):
        if self._segmentation_mode == SEGMENTATION_JIEBA:
            jieba_mod = self._get_jieba()
            if jieba_mod is not None:
                return list(jieba_mod.lcut(text, cut_all=False))
        if self._has_segmentation:
            return self._mmseg(text)
        return [text]

    def _mmseg(self, text):
        """Forward maximum matching using the config segmentation dictionaries.

        Unmatched characters stay in one run, matching OpenCC C++ MaxMatchSegmentation.
        Emitting one character per miss would hide later phrase dictionaries
        (e.g. TWPhrasesRev 義大利 → 意大利).
        """
        if not text:
            return []
        if not self._seg_keys:
            return [text]
        segments = []
        i = 0
        n = len(text)
        unmatched_start = None
        while i < n:
            matched_len = None
            max_try = min(self._seg_max_len, n - i)
            for length in range(max_try, 0, -1):
                if text[i:i + length] in self._seg_keys:
                    matched_len = length
                    break
            if matched_len is None:
                if unmatched_start is None:
                    unmatched_start = i
                i += 1
                continue
            if unmatched_start is not None:
                segments.append(text[unmatched_start:i])
                unmatched_start = None
            segments.append(text[i:i + matched_len])
            i += matched_len
        if unmatched_start is not None:
            segments.append(text[unmatched_start:n])
        return segments

    def _get_jieba(self):
        try:
            from calibre_plugins.chinese_text_conversion.resources.jieba_loader import (
                get_jieba,
            )
        except Exception:
            try:
                import os
                import sys
                resources_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if resources_dir not in sys.path:
                    sys.path.insert(0, resources_dir)
                from jieba_loader import get_jieba
            except Exception as exc:
                print('Jieba segmentation unavailable (%s); falling back to mmseg.' % exc)
                return None
        try:
            return get_jieba()
        except Exception as exc:
            print('Jieba segmentation failed to initialize (%s); falling back to mmseg.' % exc)
            return None

    def clear_replacement_counts(self):
        self.replacement_counts.clear()
        self.chars_processed = 0
        self.diagnostic_counts.clear()
        self._diagnostic_samples = []
        self._diagnostic_sample_keys = set()
        self.clear_jieba_samples()
        for child in self._chain_converters.values():
            child.clear_replacement_counts()

    def get_chars_processed(self):
        """Characters passed to convert/convert_with_details on this converter."""
        return int(self.chars_processed or 0)

    def get_chars_converted(self):
        """
        Approximate converted character count: sum of source lengths for
        non-identity OpenCC replacements (including chain/pivot children).
        """
        total = 0
        for (old, new), count in self.get_replacement_counts().items():
            if old != new:
                total += len(old) * int(count or 0)
        return total

    def clear_jieba_samples(self):
        self._jieba_samples = []
        self._jieba_sample_keys = set()
        for child in self._chain_converters.values():
            child.clear_jieba_samples()

    def get_jieba_samples(self):
        samples = list(self._jieba_samples)
        seen = set(self._jieba_sample_keys)
        chain = CHAINED_CONVERSIONS.get(self.conversion)
        if chain is not None:
            for mode in chain:
                for sample in self._get_chain_converter(mode).get_jieba_samples():
                    key = sample.get('text')
                    if not key or key in seen or len(samples) >= self._jieba_sample_limit:
                        continue
                    seen.add(key)
                    samples.append(sample)
        return samples

    def get_replacement_counts(self):
        merged = dict(self.replacement_counts)
        chain = CHAINED_CONVERSIONS.get(self.conversion)
        if chain is not None:
            for mode in chain:
                for key, count in self._get_chain_converter(mode).get_replacement_counts().items():
                    merged[key] = merged.get(key, 0) + count
        pivot_mode = self._forced_pivot_reverse_mode()
        if pivot_mode is not None:
            for key, count in self._get_chain_converter(
                    pivot_mode).get_replacement_counts().items():
                merged[key] = merged.get(key, 0) + count
        return merged

    def get_conversion_diagnostics(self):
        counts = dict(self.diagnostic_counts)
        samples = list(self._diagnostic_samples)
        chain = CHAINED_CONVERSIONS.get(self.conversion)
        if chain is not None:
            for mode in chain:
                child = self._get_chain_converter(mode).get_conversion_diagnostics()
                for key, count in child.get('counts', {}).items():
                    counts[key] = counts.get(key, 0) + count
                for sample in child.get('samples', []):
                    sample_key = (
                        sample.get('kind'), sample.get('source'),
                        sample.get('target'), sample.get('context'))
                    if (sample_key not in self._diagnostic_sample_keys
                            and len(samples) < self._diagnostic_sample_limit):
                        samples.append(sample)
        pivot_mode = self._forced_pivot_reverse_mode()
        if pivot_mode is not None:
            child = self._get_chain_converter(
                pivot_mode).get_conversion_diagnostics()
            for key, count in child.get('counts', {}).items():
                counts[key] = counts.get(key, 0) + count
            for sample in child.get('samples', []):
                sample_key = (
                    sample.get('kind'), sample.get('source'),
                    sample.get('target'), sample.get('context'))
                if (sample_key not in self._diagnostic_sample_keys
                        and len(samples) < self._diagnostic_sample_limit):
                    samples.append(sample)
        return {'counts': counts, 'samples': samples}

    def _record_diagnostic(self, kind, source, target=None, context=None,
                           dictionary=None):
        key = (kind, source, target or '')
        self.diagnostic_counts[key] = self.diagnostic_counts.get(key, 0) + 1
        sample_key = (kind, source, target or '', context or '')
        if (sample_key in self._diagnostic_sample_keys
                or len(self._diagnostic_samples) >= self._diagnostic_sample_limit):
            return
        self._diagnostic_sample_keys.add(sample_key)
        self._diagnostic_samples.append({
            'kind': kind,
            'source': source,
            'target': target or '',
            'context': context or '',
            'dictionary': dictionary or '',
        })

    def _record_conversion_events(self, events):
        for event in events:
            if (not event.get('ambiguous')
                    or event.get('dictionary') != 'STCharacters.txt'):
                continue
            self._record_diagnostic(
                'ambiguous_character_fallback',
                event.get('source', ''),
                event.get('target', ''),
                dictionary=event.get('dictionary'))

    def _record_mixed_input_diagnostics(self, string):
        if not (self.conversion or '').startswith('s2'):
            return
        entry = self.dict_cache.get('STCharacters.txt')
        if not entry:
            return
        map_dict = entry[1]
        simplified_keys = set(map_dict)
        traditional_only = set()
        for value in map_dict.values():
            traditional_only.update(value.split(' '))
        traditional_only.difference_update(simplified_keys)
        for index, char in enumerate(string):
            if char not in traditional_only:
                continue
            context = string[max(0, index - 6):index + 7]
            self._record_diagnostic(
                'traditional_input_in_simplified_mode', char, context=context)

    def get_segmentation_mode(self):
        return self._segmentation_mode

    def set_segmentation_mode(self, mode):
        """
        Set segmentation backend: 'mmseg' (default, OpenCC config) or 'jieba'.
        """
        if mode not in (SEGMENTATION_MMSEG, SEGMENTATION_JIEBA):
            raise ValueError('unsupported segmentation mode: %s' % mode)
        if self._segmentation_mode == mode:
            return
        self._segmentation_mode = mode
        for child in self._chain_converters.values():
            child.set_segmentation_mode(mode)

    def set_force_pivot_conversion(self, enabled):
        """Enable lossy Traditional -> Simplified -> target conversion."""
        self._force_pivot_conversion = bool(enabled)

    def get_force_pivot_conversion(self):
        return bool(self._forced_pivot_reverse_mode())

    def _convert(self, string, dictionary = [], is_dict_group = False,
                 match_policy = 'short_circuit', counts = None, events=None):
        """
        Convert string using one or more dictionaries. Group policies follow OpenCC
        short_circuit (first match wins) and union (longest match across dicts).
        """
        tree = self._convert_to_tree(
            string, dictionary, is_dict_group, match_policy, counts, events)
        return "".join(tree.inorder())

    def _convert_to_tree(self, string, dictionary = [], is_dict_group = False,
                         match_policy = 'short_circuit', counts = None,
                         events=None):
        """
        Like _convert, but keep StringTree.matched so nested short_circuit groups
        do not re-apply later dictionaries (e.g. STCharacters) to identity phrases.
        """
        if counts is None:
            counts = self.replacement_counts

        if is_dict_group and match_policy == 'union':
            return self._convert_union_group_to_tree(
                string, dictionary, counts, events)

        tree = StringTree(string)
        for c_dict in dictionary:
            if isinstance(c_dict, tuple) and len(c_dict) == 3 and c_dict[0] == 'group':
                _, policy, chain = c_dict
                # Preserve matched spans from the nested group; do not flatten.
                tree = self._convert_to_tree(
                    "".join(tree.inorder()), chain, True, policy, counts, events)
            elif isinstance(c_dict, tuple):
                tree.convert_tree(c_dict, counts, events)
                if not is_dict_group:
                    tree = StringTree("".join(tree.inorder()))
        return tree

    def _convert_union_group_to_tree(self, string, dictionary, counts = None,
                                     events=None):
        if counts is None:
            counts = self.replacement_counts

        tree = StringTree(string)
        dicts = []
        for item in dictionary:
            if isinstance(item, tuple) and len(item) == 3 and item[0] == 'group':
                _, policy, chain = item
                tree = self._convert_to_tree(
                    "".join(tree.inorder()), chain, True, policy, counts, events)
            else:
                dicts.append(item)
        if dicts:
            tree.convert_tree_union(dicts, counts, events)
        return tree

    def _get_chain_converter(self, mode):
        if mode not in self._chain_converters:
            child = OpenCC(self.resource_getter, mode)
            child.set_segmentation_mode(self._segmentation_mode)
            self._chain_converters[mode] = child
        return self._chain_converters[mode]

    def _init_dict(self):
        """
        initialize the dict with chosen conversion
        :return: None
        """
        if self.conversion is None:
            raise ValueError('conversion is not set')

        if self.conversion in CHAINED_CONVERSIONS:
            self.conversion_name = CHAINED_CONVERSION_NAMES[self.conversion]
            self._dict_chain_data = []
            self._normalization_chain_data = []
            self._segmentation_chain = []
            self._seg_keys = set()
            self._seg_max_len = 1
            self._has_segmentation = False
            self._dict_init_done = True
            return

        self._dict_chain = []
        config = self.conversion + '.json'
        bytes = self.resource_getter(CONFIG_FILE, config)
        if bytes is not None:
            setting_json = json.loads(bytes.decode("utf-8"))
        else:
            raise IOError('unable to open opencc config file')

        self.conversion_name = setting_json.get('name')

        self._normalization_chain = []
        for step in setting_json.get('normalization', []):
            self._add_dict_chain(self._normalization_chain, step.get('dict'))

        self._segmentation_chain = []
        segmentation = setting_json.get('segmentation')
        if segmentation and segmentation.get('dict'):
            self._add_dict_chain(self._segmentation_chain, segmentation.get('dict'))

        for chain in setting_json.get('conversion_chain'):
            self._add_dict_chain(self._dict_chain, chain.get('dict'))

        self._normalization_chain_data = []
        self._add_dictionaries(self._normalization_chain, self._normalization_chain_data)
        self._dict_chain_data = []
        self._add_dictionaries(self._dict_chain, self._dict_chain_data)

        seg_dict_data = []
        self._add_dictionaries(self._segmentation_chain, seg_dict_data)
        self._seg_keys, self._seg_max_len = self._collect_segmentation_keys(seg_dict_data)
        self._merge_regional_phrase_seg_keys()
        self._has_segmentation = bool(self._seg_keys)
        self._dict_init_done = True

    def _merge_regional_phrase_seg_keys(self):
        extra_keys, extra_max = self._collect_named_phrase_keys(
            self._dict_chain_data, REGIONAL_REVERSE_PHRASE_DICTS)
        if not extra_keys:
            return
        self._seg_keys.update(extra_keys)
        self._seg_max_len = max(self._seg_max_len, extra_max)

    def _collect_named_phrase_keys(self, chain_data, names):
        names = set(names)
        keys = set()
        max_len = 1
        for item in chain_data:
            if isinstance(item, tuple) and len(item) == 3 and item[0] == 'group':
                child_keys, child_max = self._collect_named_phrase_keys(
                    item[2], names)
                keys.update(child_keys)
                max_len = max(max_len, child_max)
            elif (isinstance(item, tuple) and len(item) == 3
                    and item[0] != 'group'):
                _entry_max, map_dict, dict_name = item
                if dict_name not in names:
                    continue
                for key in map_dict:
                    if len(key) < 2:
                        continue
                    keys.add(key)
                    if len(key) > max_len:
                        max_len = len(key)
        return keys, max_len

    def _collect_segmentation_keys(self, chain_data):
        keys = set()
        max_len = 1
        for item in chain_data:
            if isinstance(item, tuple) and len(item) == 3 and item[0] == 'group':
                child_keys, child_max = self._collect_segmentation_keys(item[2])
                keys.update(child_keys)
                max_len = max(max_len, child_max)
            elif (isinstance(item, tuple) and len(item) == 3
                    and item[0] != 'group'):
                entry_max, map_dict, _dict_name = item
                keys.update(map_dict.keys())
                max_len = max(max_len, entry_max)
        return keys, max_len

    def _add_dictionaries(self, chain_list, chain_data):
        for item in chain_list:
            if isinstance(item, tuple) and len(item) == 3 and item[0] == 'group':
                _, policy, children = item
                chain = []
                self._add_dictionaries(children, chain)
                chain_data.append(('group', policy, chain))
            else:
                if item not in self.dict_cache:
                    map_dict = {}
                    max_len = 1
                    bytes = self.resource_getter(DICT_FILE, item)
                    if bytes is not None:
                        converted_data = bytes.decode("utf-8")
                        converted_data_list = converted_data.splitlines()
                        for line in converted_data_list:
                            line = line.strip()
                            if not line or line.startswith('#'):
                                continue
                            key, value = line.split('\t', 1)
                            map_dict[key] = value
                            if len(key) > max_len:
                                max_len = len(key)
                        entry = (max_len, map_dict, item)
                        chain_data.append(entry)
                        self.dict_cache[item] = entry
                    else:
                        raise IOError('unable to open opencc dictionary: ' + item)
                else:
                    chain_data.append(self.dict_cache[item])

    def _add_dict_chain(self, dict_chain, dict_dict):
        """
        add dict chain
        :param dict_chain: the dict chain to add to
        :param dict_dict: the dict to be added in
        :return: None
        """
        if dict_dict.get('type') == 'group':
            chain = []
            for dict_item in dict_dict.get('dicts'):
                self._add_dict_chain(chain, dict_item)
            match_policy = dict_dict.get('match_policy', 'short_circuit')
            dict_chain.append(('group', match_policy, chain))
        elif dict_dict.get('type') == 'txt':
            dict_chain.append(dict_dict.get('file'))

    def set_conversion(self, conversion):
        """
        set conversion
        :param conversion: the conversion of usage, options include
         'hk2s', 'hk2sp', 'hk2tw', 's2hk', 's2hkp', 's2t', 's2tw', 's2twp', 't2hk', 't2s',
         't2tw', 'tw2hk', 'tw2s', 'tw2sp', 'tw2t', 'jp2t', 't2jp'
         check the json file names in config directory
        :return: None
        """
        if self.conversion == conversion:
            return
        elif conversion == "no_conversion":
            # just loopback the input
            self.conversion = conversion
        else:
            self._dict_init_done = False
            self._chain_converters = {}
            self.replacement_counts.clear()
            self.chars_processed = 0
            self.diagnostic_counts.clear()
            self._diagnostic_samples = []
            self._diagnostic_sample_keys = set()
            self.conversion = conversion


class StringTree:
    """
    Class to hold string during modification process.
    """
    def __init__(self, string, source_start=0):
        self.string = string
        self.left = None
        self.right = None
        self.string_len = len(string)
        self.source_start = source_start
        self.source_end = source_start + len(string)
        self.match = None
        self.matched = False

    def convert_tree(self, test_dict, counts = None, events=None):
        """
        Compare smaller and smaller sub-strings going from left to
        right against test_dict. If an entry is found, place the remaining
        string portion on the left and right into sub-trees and recurively
        convert each.
        :param test_dict: a tuple of the max key length and dict currently being
                          applied against the string
        :return: None
        """
        if self.matched == True:
            if self.left is not None:
                self.left.convert_tree(test_dict, counts, events)
            if self.right is not None:
                self.right.convert_tree(test_dict, counts, events)
        else:
            test_len = min(self.string_len, test_dict[0])
            while test_len != 0:
                # Loop through trying successively smaller substrings in the dictionary
                for i in range(0, self.string_len - test_len + 1):
                    fragment = self.string[i:i+test_len]
                    if fragment in test_dict[1]:
                        # Match found.
                        if i > 0:
                            # Put everything to the left of the match into the left sub-tree and further process it
                            self.left = StringTree(
                                self.string[:i], self.source_start)
                            self.left.convert_tree(test_dict, counts, events)
                        if (i+test_len) < self.string_len:
                            # Put everything to the right of the match into the right sub-tree and further process it
                            self.right = StringTree(
                                self.string[i+test_len:],
                                self.source_start + i + test_len)
                            self.right.convert_tree(test_dict, counts, events)
                        # Save the dictionary value in this tree
                        raw_value = test_dict[1][fragment]
                        candidates = raw_value.split(' ')
                        value = raw_value
                        if len(candidates) > 1:
                            # multiple mapping, use the first one for now
                            value = candidates[0]
                        if counts is not None and fragment != value:
                            pair = (fragment, value)
                            counts[pair] = counts.get(pair, 0) + 1
                        dict_name = test_dict[2]
                        kind = (
                            'phrase'
                            if len(fragment) > 1 or 'Phrases' in dict_name
                            else 'character')
                        self.source_start += i
                        self.source_end = self.source_start + test_len
                        self.match = {
                            'source': fragment,
                            'target': value,
                            'dictionary': dict_name,
                            'kind': kind,
                            'ambiguous': len(candidates) > 1,
                            'candidates': candidates,
                        }
                        if events is not None:
                            events.append(dict(self.match))
                        self.string = value
                        self.string_len = len(self.string)
                        self.matched = True
                        return
                test_len -= 1

    def convert_tree_union(self, test_dicts, counts = None, events=None):
        if self.matched:
            if self.left is not None:
                self.left.convert_tree_union(test_dicts, counts, events)
            if self.right is not None:
                self.right.convert_tree_union(test_dicts, counts, events)
            return

        best_len = 0
        best_index = -1
        best_value = None
        best_fragment = None
        best_dict = None
        max_key_len = 0
        for test_dict in test_dicts:
            max_key_len = max(max_key_len, test_dict[0])

        test_len = min(self.string_len, max_key_len)
        while test_len > 0:
            for i in range(0, self.string_len - test_len + 1):
                fragment = self.string[i:i + test_len]
                for test_dict in test_dicts:
                    if fragment in test_dict[1]:
                        if test_len > best_len:
                            best_len = test_len
                            best_index = i
                            best_fragment = fragment
                            best_value = test_dict[1][fragment]
                            best_dict = test_dict
            if best_len:
                break
            test_len -= 1

        if best_len:
            if best_index > 0:
                self.left = StringTree(
                    self.string[:best_index], self.source_start)
                self.left.convert_tree_union(test_dicts, counts, events)
            end = best_index + best_len
            if end < self.string_len:
                self.right = StringTree(
                    self.string[end:], self.source_start + end)
                self.right.convert_tree_union(test_dicts, counts, events)
            candidates = best_value.split(' ')
            value = candidates[0]
            if counts is not None and best_fragment != value:
                pair = (best_fragment, value)
                counts[pair] = counts.get(pair, 0) + 1
            dict_name = best_dict[2]
            kind = (
                'phrase'
                if len(best_fragment) > 1 or 'Phrases' in dict_name
                else 'character')
            self.source_start += best_index
            self.source_end = self.source_start + best_len
            self.match = {
                'source': best_fragment,
                'target': value,
                'dictionary': dict_name,
                'kind': kind,
                'ambiguous': len(candidates) > 1,
                'candidates': candidates,
            }
            if events is not None:
                events.append(dict(self.match))
            self.string = value
            self.string_len = len(self.string)
            self.matched = True

    def inorder_records(self):
        records = []
        if self.left is not None:
            records.extend(self.left.inorder_records())
        records.append({
            'source_start': self.source_start,
            'source_end': self.source_end,
            'target': self.string,
            'match': self.match,
        })
        if self.right is not None:
            records.extend(self.right.inorder_records())
        return records

    def inorder(self):
        """
        Inorder traversal of this tree
        :param None
        :return: list of words from a inorder traversal of the tree
        """
        result = []

        if self.left is not None:
            result += self.left.inorder()

        result.append(self.string)

        if self.right is not None:
            result += self.right.inorder()
        return result
