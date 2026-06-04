Upstream data source
    Dictionary text files in this folder are synced from:
    https://github.com/BYVoid/OpenCC (commit 5d1eadd)

    Notes:
    - Upstream OpenCC runtime configs now use ocd2 dictionaries.
    - This plugin keeps txt dictionaries for compatibility with opencc_python/opencc.py.
    - Reverse dictionaries (*Rev.txt) are regenerated locally via reverse.py
      after syncing upstream txt files.

merge.py
    for merging dictionary files into a single file

    merge 'TWPhrasesIT.txt', 'TWPhrasesName.txt', and 'TWPhrasesOther.txt'
    into a single file 'TWPhrases.txt'

	In a command shell whose current working directory is the dictionary
    
	Run:
        python merge.py
		
	or Run:
        calibre-debug merge.py

reverse.py
    for reversing dictionary keys and values (requires Python3)

    reverse 'JPVariants.txt' 'TWVariants.txt', 'TWPhrases.txt', 'HKVariants.txt'
    to 'JPVariantsRev.txt' 'TWVariantsRev.txt', 'TWPhrasesRev.txt', 'HKVariantsRev.txt'

	In a command shell whose current working directory is the dictionary

    Run:
        python reverse.py
		
	or Run:
        calibre-debug reverse.py
