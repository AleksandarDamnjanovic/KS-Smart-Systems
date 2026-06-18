The purpose of variables is to hold values that are going to be used by the system.
- **naming** Variable name always starts with $ dollar sign like `$hey`, `$iamvarname`, `$onemoreexample`. When global variable is called from another node, node index of called variable must be used; for example, if you want to refer some global variable(local name of that variable is let's say `$hey`) from another node(let's say that the variable that you want to refer is in node with index of 5) you are going to call it `$5$hey` which means variable `$hey` from node with index of 5. By the same logic, variable `$7$myint` would mean that this is variable with name of `$myint` from node with index of 7. Variable names can't hold empty spaces.
- **definition** there is a rule that says, one variable per one line like
```
    global int    $hey      = 10
           string $haha     = "haha"
           array  $nums     = [1, 2, 3]
```
- **global modifier** Variable can be local or global(if variable declaration has modifier "global", that is global variable. If variable doesn't have "global" modifier, that is local variable). Local variable can be used only in the same node, while global variable can be used from another node too. Example of global variable: `global int $op = 25`, Example of local variable: `int $op = 10`
- **types** .kst script supports multiple types of variables.
    1. int(integer, whole number) example `int $me = 50`
    2. float(number with decimal point) example `float $hey = 23.20`
    3. string(textual values), strings values must be wrapped with quotation marks like `string $bob = "bob the builder"`
    4. array can hold both, integers(`array $intarray = [0, 1, 2]`), strings(`array $stringarray = ["hi", "hey", "ho"]`) and other variable names(`array $varnames = [$c1, $c2, $d8]`). also, array can hold a range of integer values like `array $rangeexample = [0-255]`.
    5. fun, this is a special case variable. Variables of this type can't be global variables and it can store only integer type of values. This kind of variables are used solely to hold result from some function and are provided as function name arguments.
Example of entire Variables section
```
<variables>
    global int    $hey      = 10
           string $haha     = "haha"
           array  $nums     = [1, 2, 3]
           fun    $myfun    = 0
</variables>
```