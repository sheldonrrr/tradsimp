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

import io
import os
import json
import re

CONFIG_FILE = 'config'
DICT_FILE = 'dictionary'

CHAINED_CONVERSIONS = {
    'hk2tw': ('hk2t', 't2tw'),
    'tw2hk': ('tw2t', 't2hk'),
}

CHAINED_CONVERSION_NAMES = {
    'hk2tw': 'Traditional Chinese (Hong Kong) to Traditional Chinese (Taiwan)',
    'tw2hk': 'Traditional Chinese (Taiwan) to Traditional Chinese (Hong Kong)',
}

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
        self._dict_init_done = False
        self._dict_chain = list()
        self._dict_chain_data = list()
        self._normalization_chain_data = list()
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

        # echo the input if no conversion is wanted
        if self.conversion == "no_conversion":
            return string

        chain = CHAINED_CONVERSIONS.get(self.conversion)
        if chain is not None:
            result = string
            for mode in chain:
                result = self._get_chain_converter(mode).convert(result)
            return result

        if not self._dict_init_done:
            self._init_dict()
            self._dict_init_done = True

        if self._normalization_chain_data:
            string = self._convert(string, self._normalization_chain_data)

        result = []
        # Separate string using the list of separators in a regular expression
        split_string_list = self.split_chars_re.split(string)
        for i in range(0, len(split_string_list)):
            if i % 2 == 0:
                # Work with the text string
                # Append converted string to result
                result.append(self._convert(split_string_list[i], self._dict_chain_data))
            else:
                # Work with the separator
                # Append separator string to converted_string
                result.append(split_string_list[i])
        # Join it all together to return a result
        return "".join(result)

    def clear_replacement_counts(self):
        self.replacement_counts.clear()
        for child in self._chain_converters.values():
            child.clear_replacement_counts()

    def get_replacement_counts(self):
        merged = dict(self.replacement_counts)
        chain = CHAINED_CONVERSIONS.get(self.conversion)
        if chain is not None:
            for mode in chain:
                for key, count in self._get_chain_converter(mode).get_replacement_counts().items():
                    merged[key] = merged.get(key, 0) + count
        return merged

    def _convert(self, string, dictionary = [], is_dict_group = False, match_policy = 'short_circuit', counts = None):
        """
        Convert string using one or more dictionaries. Group policies follow OpenCC
        short_circuit (first match wins) and union (longest match across dicts).
        """
        if counts is None:
            counts = self.replacement_counts

        if is_dict_group and match_policy == 'union':
            return self._convert_union_group(string, dictionary, counts)

        tree = StringTree(string)
        for c_dict in dictionary:
            if isinstance(c_dict, tuple) and len(c_dict) == 3 and c_dict[0] == 'group':
                _, policy, chain = c_dict
                tree = StringTree(self._convert("".join(tree.inorder()), chain, True, policy, counts))
            elif isinstance(c_dict, tuple):
                tree.convert_tree(c_dict, counts)
                if not is_dict_group:
                    tree = StringTree("".join(tree.inorder()))
        return "".join(tree.inorder())

    def _convert_union_group(self, string, dictionary, counts = None):
        if counts is None:
            counts = self.replacement_counts

        tree = StringTree(string)
        dicts = []
        for item in dictionary:
            if isinstance(item, tuple) and len(item) == 3 and item[0] == 'group':
                _, policy, chain = item
                string = self._convert(string, chain, True, policy, counts)
                tree = StringTree(string)
            else:
                dicts.append(item)
        if dicts:
            tree.convert_tree_union(dicts, counts)
        return "".join(tree.inorder())

    def _get_chain_converter(self, mode):
        if mode not in self._chain_converters:
            self._chain_converters[mode] = OpenCC(self.resource_getter, mode)
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
            self._dict_init_done = True
            return

        self._dict_chain = []
##        print(self.conversion)
        config = self.conversion + '.json'
##        print(config)
        bytes = self.resource_getter(CONFIG_FILE, config)
        if bytes is not None:
            setting_json = json.loads(bytes.decode("utf-8"))
        else:
            raise IOError('unable to open opencc config file')

        self.conversion_name = setting_json.get('name')

        self._normalization_chain = []
        for step in setting_json.get('normalization', []):
            self._add_dict_chain(self._normalization_chain, step.get('dict'))

        for chain in setting_json.get('conversion_chain'):
            self._add_dict_chain(self._dict_chain, chain.get('dict'))

        self._normalization_chain_data = []
        self._add_dictionaries(self._normalization_chain, self._normalization_chain_data)
        self._dict_chain_data = []
        self._add_dictionaries(self._dict_chain, self._dict_chain_data)
        self._dict_init_done = True

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
                        entry = (max_len, map_dict)
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
            self.conversion = conversion


class StringTree:
    """
    Class to hold string during modification process.
    """
    def __init__(self, string):
        self.string = string
        self.left = None
        self.right = None
        self.string_len = len(string)
        self.matched = False

    def convert_tree(self, test_dict, counts = None):
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
                self.left.convert_tree(test_dict, counts)
            if self.right is not None:
                self.right.convert_tree(test_dict, counts)
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
                            self.left = StringTree(self.string[:i])
                            self.left.convert_tree(test_dict, counts)
                        if (i+test_len) < self.string_len:
                            # Put everything to the right of the match into the right sub-tree and further process it
                            self.right = StringTree(self.string[i+test_len:])
                            self.right.convert_tree(test_dict, counts)
                        # Save the dictionary value in this tree
                        value = test_dict[1][fragment]
                        if len(value.split(' ')) > 1:
                            # multiple mapping, use the first one for now
                            value = value.split(' ')[0]
                        if counts is not None and fragment != value:
                            pair = (fragment, value)
                            counts[pair] = counts.get(pair, 0) + 1
                        self.string = value
                        self.string_len = len(self.string)
                        self.matched = True
                        return
                test_len -= 1

    def convert_tree_union(self, test_dicts, counts = None):
        if self.matched:
            if self.left is not None:
                self.left.convert_tree_union(test_dicts, counts)
            if self.right is not None:
                self.right.convert_tree_union(test_dicts, counts)
            return

        best_len = 0
        best_index = -1
        best_value = None
        best_fragment = None
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
            if best_len:
                break
            test_len -= 1

        if best_len:
            if best_index > 0:
                self.left = StringTree(self.string[:best_index])
                self.left.convert_tree_union(test_dicts, counts)
            end = best_index + best_len
            if end < self.string_len:
                self.right = StringTree(self.string[end:])
                self.right.convert_tree_union(test_dicts, counts)
            value = best_value
            if len(value.split(' ')) > 1:
                value = value.split(' ')[0]
            if counts is not None and best_fragment != value:
                pair = (best_fragment, value)
                counts[pair] = counts.get(pair, 0) + 1
            self.string = value
            self.string_len = len(self.string)
            self.matched = True

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

