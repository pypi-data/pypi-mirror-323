# eda-ji

![LGTM](https://i.lgtm.fun/1yei.gif)
presidents ranked by mentions of ('You Want to know') in their speeches!
+ Possible to output the total count of how many times the keyword was mentioned in all speeches by each president.
### USE
```
$ pip install eda-ji
$ python
>>> from eda-ji.cli import group_by_count
>>> group_by_count(keyword, bool, n) # 오름차순/내림차순, 상위 n개 출력


eda-ji --help 참고

$ eda-ji keyword --asc(오름차순) --rnct (상위 n개) --keyword-sum(연설 속 키워드 총 합계)
or --no-ascen(내림차순)
```

### DEV
```bash
$ source .venv/bin/activate
$ pdm add pandas
$ pdm add -dG eda jupyterlab
$ pdm add president-speech
$ pdm add typer

$ vi pyproject.toml
$ pdm install

$ vi src/eda_ji/cli.py
$ eda-ji - test

$ vi tests/test_first.py
$ pytest

$ git add
$ git commit
$ git push
$ pdm publish
```

### EDA
- run jupyterlab
```
$ jupyter lab
```

### Ref
- [install jupyterlab](https://jupyter.org/install)
- [install president](https://pypi.org/project/president-speech/)
- [Typer](https://pypi.org/project/typer)

