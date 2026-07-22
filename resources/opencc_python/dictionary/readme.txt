Upstream data source
    Dictionary text files in this folder are synced from:
    https://github.com/BYVoid/OpenCC (commit 81223ed (ver.1.4.1))

    Notes:
    - Upstream OpenCC runtime configs now use ocd2 dictionaries.
    - This plugin keeps txt dictionaries for compatibility with opencc_python/opencc.py.
    - Run scripts/sync_opencc.py against an OpenCC checkout to refresh dictionaries,
      generated files (TSCharactersExt, STPhrases_GeneratedFromRegionalPhrases, *Rev),
      and config JSON from upstream.

reverse.py
    Legacy helper for reversing dictionary keys and values (requires Python3).
    Upstream ships TWPhrasesRev.txt and HKPhrasesRev.txt directly; sync_opencc.py
    uses upstream data/scripts/reverse.py for HKVariantsRev, TWVariantsRev, and
    JPShinjitaiCharactersRev.
