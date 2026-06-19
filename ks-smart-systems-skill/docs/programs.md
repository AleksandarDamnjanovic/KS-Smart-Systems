Programs are where true power of .kst lies. At the moment, there are three types of programs. `valCondition`, `serial` and `timeLim`. `valCondition` and `serial` can be named, while `timeLim` can't. Type of variable that is used to name a program is fun.

- **valCondition(textName, conditions, result)**;
```
$example = valCondition(
    "temp on",
    $res01 < $tempLimDown
    $c1 == 0, 
    $c1 = 1
    $tempState = 1
);
```
In this case $example is name of this functions. Type of variable is fun and type of function is `valCondition`. If you don't need named function, simply don't name it; just write `valCondition(` without `$example` = part.
`valCondition` function has three arguments, or better to say three groups of arguments. First argument is function name in human readable form. Second argument is one or more conditions separated by new line; all of conditions must be true in order result to be executed. Result can also have one or more statements separated by new line.

- **serial(textName, listOfSwitches, epoh, timeStamp, lastIndex);**
        Program serial have purpose to turn on one switch from provided list of switches, when time comes. Program starts from switch with index provided in fifth argument, and keeps it on till the epoch provided in third argument in seconds ends. Then `timeStamp` provided in forth argument changes to current time and the new epoch starts from the beginning turning on next switch from the list... so on till the end of the list. When list ends, it starts from the beginning in the same fashion. Timestamp default value is 0, so always when you define `timeStamp` variable, you are going to set it with value of 0;
```
$fun01= serial("two switches", $listOfSwitches, $switchEp, $sTime, $lastIndex);
```
Function naming applies here too. Function of type serial is written in a single line with ; at the end.

- **timeLim(function, start, end);**
```
timeLim($fun01, $start, $end);
```
With function `timeLim`, you are able to define execution time of some other function. For example, if you want your serial program or conditional program to be executed only between 12:00 and 14:00, as a first argument to the `timeLim` function, you are going to provide function name of the function you want to limit by time, as second argument you are going to provide string variable that hold value of "12:00" and as third argument, string variable that holds value of "14:00".
Therefore default value of variable of type fun that hold function name of the function you want to limit by time is 1. That means that function is going to be executed by default except if it is provided to `timeLim` function. `timeLim` function keeps value of fun variable to 1 only in selected time; in other case, it keeps it to 0. If value of naming variable is 0 that means that that function is going to be ignored; if is 1 it is going to be executed.
