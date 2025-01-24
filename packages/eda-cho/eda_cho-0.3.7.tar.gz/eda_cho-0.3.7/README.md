# eda-cho

### DEV
```bash
$ source .venv/bin/activate
$ pdm add pandas
$ pdm add -dG eda jupyterlab
$ pdm add <...>
$ pdm add -dG test pytest

```

### EDA
- run jupyterlab
```
$ jupyter lab

```

### HOW TO USE
```bash

- 입력값 : 검색어(str) 정렬(bool) 개수(int)
- 범위에 맞지 않는 개수 입력 시 무시하고 결과 그대로 표
기
$ pip install eda-cho or pdm add eda-cho
$ python
>>> from eda_cho.cli import group_by_count
>>> group_by_count('Text_For_Search', True or False, Int For Count)

$ Cli
>>> ex: cho-test 자유 --asc --rcnt 3
>>> ex: cho-test 자유 --no-asc --rcnt 4


$ pytest
>>> pytest tests/
```


### REF
- [install jupyter](https://jupyter.org/install)
- from president_speech.db.parquet_interpreter import read_parquet, get_parquet_full_path
>>> get_parquet_full_path()
'/Users/f16/code/edu/president-speech/.venv/lib/python3.8/site-packages/president_speech/db/parquet/president_speech_ko.parquet'
>>> read_parquet().head(3)
