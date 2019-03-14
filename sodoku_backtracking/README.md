
# Sudoku


Apply searching, backtracking and constraint propagation to solve easy and hard sudoku

Main Idea:
init the grid and its domain to a specift value if known already, 
otherwise, init witha  list of possible values from 1-9, excluding its peers (20 neighbour spots in row col and 3*3 grid)

solver() make a call to search(), the search() will try to guess value in the spot with the smallest domain len,
  if this guess value makes no conflict to its peers by calling consistent() to check, then we can make inference.
   infer() means aftering assigning the guess value, we might be able to make more inference of its peers,
  if the guess value failed, we need to try other possible values in its domain, and Meanwhile, we need to backtrack and remove all the assignment we made after this guess.

infer() is written in recursion, it remove the guess value from its peer's domain, and then if the domain becomes only one value, we can make the inference, but we also need to make consistent() call to check every time made an inference.



## Usage

```
  python3 sudoku.py
 
```


## Ref article:
http://norvig.com/sudoku.html
