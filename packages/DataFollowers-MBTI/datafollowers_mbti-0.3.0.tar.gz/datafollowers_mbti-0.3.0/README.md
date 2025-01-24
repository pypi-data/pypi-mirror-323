# MBTI

[![LGTM](https://lgtm.lol/p/394)](https://lgtm.lol/i/394)

### USE
```bash
$ mbti-check-type
Usage: mbti-check-type [OPTIONS] MBTI
Try 'mbti-check-type --help' for help.
╭─ Error ────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Missing argument 'MBTI'.                                                                               │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯

$ mbti-check-type --help

 Usage: mbti-check-type [OPTIONS] MBTI

╭─ Arguments ────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    mbti      TEXT  [default: None] [required]                                                        │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                                            │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯

$ mbti-check-type ISFP
권력형
```

#### check_type(mbti: str)
```bash
$ pip install DataFollowers-MBTI
$ python
>>> from mbti.cli import check_type
>>> check_type("ISFP")
'성인군자형'
``` 

### DEV
```bash
$ source .venv/bin/activate
$ pdm add jupyterlab
$ pdm add -dG test pytest

$ git add .
$ git commit -a
$ git push

View at:
https://pypi.org/project/DataFollowers-MBTI/
```

### EDA
- run jupyterlab
```bash
$ jupyter lab
```

### TEST
```bash
$ pytest
$ pytest -s
$ pytest --cov
```
