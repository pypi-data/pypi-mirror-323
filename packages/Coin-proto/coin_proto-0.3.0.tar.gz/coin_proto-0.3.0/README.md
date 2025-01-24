# Coin-proto
This prototype is a cryptocurrency trading automation system.

# Goal 
목표 : 업비트를 활용한 코인 자동매매 프로그램 프로토타입 만들기

# Plan
 1. 자료조사
 - 책, 구글링
 - 깃허브

 2. 프로그램 만들기
 - 최대한 심플하고 기본에 충실하게
 - 직접 코드를 짜는 것보다는 복붙으로

 3. 매매 알고리즘 공부하기
 - 타인의 기록들
 - 논문 검색

4.  매매기록 남기기
 - 매매기록 서식 만들고 자동화하기

### Dev
개인 컴퓨터에서 clone 후, 개발 환경 들어가서 pytest, jupyterlab 실행하는 법
```bash
$ git clone ...
$ pdm venv create
$ source .venv/bin/activate
$ pdm install
$ pdm add -dG note jupyterlab
$ pdm add -dG test pytest
$ pytes
$ jupyter lab
```

코드 수정후 커밋 및 퍼블리시 
```bash
$ git add .
$ git commit -a
$ git publish
$ git push
$ merg / release

View at:
https://pypi.org/project/Coin-proto/
```
