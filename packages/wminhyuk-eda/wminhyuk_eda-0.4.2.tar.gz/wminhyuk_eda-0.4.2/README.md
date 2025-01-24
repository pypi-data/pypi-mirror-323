# wminhyuk-eda

### USE
```
$ pip install
$ wminhyuk-eda
Usage: wminhyuk-eda [OPTIONS] KEYWORD
Try 'wminhyuk-eda --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Missing argument 'KEYWORD'.                                                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

$ wminhyuk-eda --help
 Usage: wminhyuk-eda [OPTIONS] KEYWORD

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    keyword      TEXT  [default: None] [required]                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --asc            --no-asc                     [default: no-asc]                                                      │
│ --rcnt                               INTEGER  [default: 12]                                                          │
│ --keyword-sum    --no-keyword-sum             [default: no-keyword-sum]                                              │
│ --help                                        Show this message and exit.                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

$ wminhyuk-eda 자유 --asc
president  count
      윤보선      1
      최규하     14
      박근혜    111
      노무현    230
      전두환    242
      이명박    262
      김영삼    274
      문재인    275
      김대중    305
      노태우    399
      이승만    438
      박정희    513

$ wminhyuk-eda 자유 --asc --rcnt 3 --keyword-sum
president  count  keyword_sum
      윤보선      1            6
      최규하     14           28
      박근혜    111          250
```

### DEV
```bash
$ source .venv/bin/activate
& pdm add pandas
& pdm add -dG eda jupyterlab
```

### EDA
- run jupyterlab
```
& hyoyter lab
```


### Ref
- [install jupyterlab](https://jupyter.org/install)
- https://pypi.org/project/president-speech/
