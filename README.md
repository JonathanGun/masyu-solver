# masyu-solver
# Introduction
A solver for [Masyu](http://www.nikoli.co.jp/en/puzzles/masyu.html) Puzzles. The goal of this project is to make masyu solver using restriction-based algorithm.

## Requirement
Python 3 (tested on python 3.7)
OpenCV for python 3

## Usage
```
python masyu.py --image <input-file> --size <board-size>
```
or
```
python masyu.py -i <input-file> -s <board-size>
```

<input-file> currently can only be txt
<board-size> please refer this when the input file is image type

## To-Do
- no need to refer size of board
- input from stdin
- finish recursive backtracking algorithm after global restriction on board

## Acknowledgment
I made this solver to fulfill IF2120 Discrete Mathematics subject.
