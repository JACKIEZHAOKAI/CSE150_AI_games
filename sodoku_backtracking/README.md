# Sudoku


Apply backtracking and constraint propagation to solve Sudoku problem
The basic idea is simple, keep tring all the possible domain
value of a spot and keep making recursive call fo the search() funciton until find a solution.

Optimize the time cost of the algorithm by inplementing an infer() funciton to infer the possible value 
when the rest 8 values in a row/col/3*3 grid are determined. 

the Consistent() method is used to check if the current assignment of values are valid.


## Usage

```
  python3 sudoku.py
```

sudoku.py will run and solve all the easy and hard problems in easy_sudoku_problems.txt and hard_sudoku_problems.txt
it will print the time cost for solving each problems and the average time cost for easy and hard problems
need to mannually copy the easy and hard problems into sudoku.py

## Ref article:
http://norvig.com/sudoku.html

