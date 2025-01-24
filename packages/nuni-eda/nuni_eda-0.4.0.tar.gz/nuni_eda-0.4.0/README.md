# nuni-eda
 - EDA cli that prints data filtered and sorted by keyword

### Use
```bash
$ nuni-eda
Usage: nuni-eda [OPTIONS] KEYWORD
Try 'nuni-eda --help' for help.
╭─ Error ─────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Missing argument 'KEYWORD'.                                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
$ nuni-eda --help

 Usage: nuni-eda [OPTIONS] KEYWORD

╭─ Arguments ─────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    keyword      TEXT  [default: None] [required]                                                              │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --asc            --no-asc                     [default: no-asc]                                                 │
│ --rcnt                               INTEGER  [default: 12]                                                     │
│ --keyword-sum    --no-keyword-sum             [default: no-keyword-sum]                                         │
│ --help                                        Show this message and exit.                                       │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

$ nuni-eda 누리 --asc --rcnt 3 --keyword-sum
president  count  keyword_sum
      최규하      2            2
      김대중     54           55
      박근혜     44           60
```

### EDA Development environment setting
```bash
$ install pdm
$ git clone

# pdm venv create (at different delvelopment environment)
$ source .venv/bin/activate
$ pdm install pandas
$ pdm install jupyter lab
$ jupyter lab
...(coding)

$ git add <file_name>
$ git commit -a
$ git push
$ pdm publish
Username: __token__
# PR - Merge
# Tag - Release
```

### TEST
```bash
$ pdm add -dG test pytest
$ pytest
```


### Use
```bash
$ pip install nuni-eda
$ nuni-eda

```
