# eda-lucas
![LGTM](https://media4.giphy.com/media/kbVzENVNlE60MQR1HY/giphy.gif?cid=47028fa8js3o7vs2eja2vjbghebfxxf88a23c5oxy5yyh3ux&ep=v1_gifs&rid=giphy.gif&ct=g)

## DES
 - 대한민국 역대 대통령 연설문 모음
 - 대통령별 연설문에서 사용된 단어 확인 및 반복 횟수
 - 대통령별 keyword가 등장하는 연설문의 수와 연설문 속에 해당 keyword가 나오는 횟수를 합친 결과(추가 예정) 

### USE
```bash
🦊  eda-lucas
Usage: eda-lucas [OPTIONS] KEYWORD
Try 'eda-lucas --help' for help.
╭─ Error ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ Missing argument 'KEYWORD'.                                                                                                                                                              │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
🦊  eda-lucas --help

 Usage: eda-lucas [OPTIONS] KEYWORD

╭─ Arguments ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ *    keyword      TEXT  [default: None] [required]                                                                                                                                       │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --asc            --no-asc                     [default: no-asc]                                                                                                                          │
│ --rcnt                               INTEGER  [default: 12]                                                                                                                              │
│ --keyword-sum    --no-keyword-sum             [default: no-keyword-sum]                                                                                                                  │
│ --help                                        Show this message and exit.                                                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
🦊  eda-lucas 경제
president  count
      문재인    837
      이명박    787
      박정희    778
      김대중    658
      김영삼    543
      노무현    470
      노태우    449
      전두환    374
      박근혜    340
      이승만    241
      최규하     47
      윤보선      1

🦊  eda-lucas 경제  --asc --rcnt 3  --keyword-sum
president  count  keyword_sum
      윤보선      1            6
      최규하     47          287
      이승만    241          723
```

### DEV
```bah
$ source .venv/bin/activate
$ pdm add pandas
$ pdm add -dG eda jupyterlab
$ cd src/eda_lucas/cli.py 
$ vi src/eda_lucas/cli.py 
```
### pytest

```bash
$ source .venv/bin/activate
$ cd tests/test_first.py
```

### EDA
- run jupyterlab 
```
$ jupyter lab
``` 

### ReF
- [install jupyterlab](https://jupyter.org/install)
- [install president-speech](https://pypi.org/project/president-speech/)
