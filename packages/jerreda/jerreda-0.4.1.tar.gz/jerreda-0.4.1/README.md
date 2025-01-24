# jerreda

[![LGTM](https://lgtm.lol/p/843)](https://lgtm.lol/i/843)

## USE
```bash
$ jerreda
Usage: jerreda [OPTIONS] KEYWORD
Try 'jerreda --help' for help.
╭─ Error ────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Missing argument 'KEYWORD'.                                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯

$ jerreda --help
 
 Usage: jerreda [OPTIONS] KEYWORD

╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    keyword      TEXT  [default: None] [required]                                                     │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────╮
│ --asc     --no-asc             [default: no-asc]                                                       │
│ --rcnt                INTEGER  [default: 12]                                                           │
│ --help                         Show this message and exit.                                             │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯

$ jerreda 자유
president  count
      박정희    513
      이승만    438
      노태우    399
      김대중    305
      문재인    275
      김영삼    274
      이명박    262
      전두환    242
      노무현    230
      박근혜    111
      최규하     14
      윤보선      1

$ jerreda-cnt --help

 Usage: jerreda-cnt [OPTIONS] KEYWORD

╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    keyword      TEXT  [default: None] [required]                                                     │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────╮
│ --asc            --no-asc                     [default: no-asc]                                        │
│ --rcnt                               INTEGER  [default: 12]                                            │
│ --keyword-sum    --no-keyword-sum             [default: keyword-sum]                                   │
│ --help                                        Show this message and exit.                              │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯

$ jerreda-cnt 자유 --no-asc --rcnt 3 --keyword-sum
president  count  keyword_sum
      박정희    513         2145
      이승만    438         1902
      노태우    399         1445
```


### group_by_count(keyword: str)
```bash
$ pip install jerreda
$ python
>>> from jerreda.cli import group_by_count
>>> group_by_count(keyword: str=<KEYWORD>, asc: bool=<IS_ASC>, rcnt: int=<NUMBER>, keyword_sum: bool=<KEYWROD_SUM>)
```

### DEV
```bash
$ source .venv/bin/activate
$ pdm add pandas
$ pdm add -dG add jupyterlab
$ pdm add president-speech

$ git add .
$ git commit -a
$ git push
$ pdm publish

View at:
https://pypi.org/project/jerreda/0.4.1/
```

### EDA
- run jupyterlab
```bash
$ jupyter lab

```

### TEST
```
# $ pdm add -dG test pytest
$ pytest
$ pytest -s
$ pytest --cov
```

## REF
- [Install Jupyterlab](https://jupyter.org/install)
- [PyPI President-speech](https://pypi.org/project/president-speech/)
