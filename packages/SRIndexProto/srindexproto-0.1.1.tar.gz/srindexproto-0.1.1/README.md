# SRIndexProto
- Prototype of calculator for Social Relationship Index 

# Use
```bash
# nuni-org <give-and-take> <celebration> <freq-call> <freq-meeting>

```

## Requirements
```bash
To calculate the Index, you need arguments below:
- give-and-take
- celebration
- freq-call
- freq-meeing

and set weight of each arguments in range: 
- 0 < weight1 < 1, = w1
- 0 < weight2 < 1, = w2
- 0 < weight3 < 1, = w3
- 0 < weight4 < 1, = w4
and summation of all weight(w1+w2+w3+w4) must be equal to 1
```

```bash
## Development environment setting guide

# install PDM
# git clone ...
# pdm venv create
$ source .venv/bin/activate
$ pdm install
# $ vi ...

# TEST
$ pdm install
$ pdm test
$ pip install .

$ git add <FILE_NAME>
$ git commit -a
$ git push
$ pdm publish --username __token__ --password $PYPI_TOKEN
```
