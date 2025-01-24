# kang-eda
![LGTM](https://i.lgtm.fun/2vrl.png)

### DEV
```bash
$ source .venv/bin/activate
$ pdm add pandas
$ pdm add -dG eda jupyterlab
$ pdm add typer
$ pdm add <...>
$ pdm add -dG pytest

$ git add .
$ git commit -m
$ git push
$ pdm publish
```

### EDA
- run jupyterlab

```
$ jupyter lab
```

### How To Use
```bash
$ pip install kang-eda or pdm add kang-eda
$ python
>>> from kang_eda.cli import group_by_count
>>> group_by_count("TEXT FOR UR SEARCH", True or False, int for Count)

kang-eda --help

 Usage: kang-eda [OPTIONS] KEYWORD

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    keyword      TEXT  [default: None] [required]                                                                   │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --asc            --no-asc                     [default: no-asc]                                                      │
│ --row                                INTEGER  [default: 12]                                                          │
│ --keyword-sum    --no-keyword-sum             [default: no-keyword-sum]                                              │
│ --help                                        Show this message and exit.                                            │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯



###
>>> from kang_eda.cli import group_by_count
>>> group_by_count("행복" , True , 12)
   president  count
0        최규하     13
1        이승만     51
2        김영삼     84
3        노태우    143
4        박정희    154
5        김대중    156
6        노무현    184
7        문재인    191
8        전두환    191
9        박근혜    277
10       이명박    347
###
```


### Ref
- [install jupyterlab](https://jupyter.org/install)
- [President](https://pypi.org/project/president-speech/)
