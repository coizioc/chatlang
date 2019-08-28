# The Chatlang Language Specification

## File Format

Chatlang programs are UTF-8 text files with the file extension `.clog`.

## Comments

Comments are wrapped in parentheses:

```
[17:24] Coizioc: I'm alright. (No I'm not.)
```

## Program Format

A Chatlang program consists of multiple messages, each containing one or more statements. A **message** consists of three parts: (1) a timestamp, (2) a username, and (3) the message contents.

### Timestamps

A timestamp may either be in 12-hour or 24-hour format. You may use either (or both if you're feeling adventurous, though it is not recommended), so the following messages are equivalent:

```
[01:23 PM] Coizioc: Say hello!
[13:23] Coizioc: Say hello!
```

The timestamps may or may not be zero-padded, based on your preference. The timestamps `[1:3]`, `[01:3]`, `[1:03]`, and `[01:03]` are all equivalent and valid. However, stylistically, it would be preferable to use the latter two formats over the others.

When the program is running, all timestamps are converted to 24-hour format.

Each message's timestamp should be the same as or after the previous message's timestamp. However, this is not enforced by the interpreter and the timestamps may be whatever time you wish.

### Usernames

Naming a username follows the same rules as a variable. The username determines the scope of the message's variables. Scope will be discussed in greater detail in another section.

### Message Body

A message body contains one or more statements. The types of statements that can be made will be discussed in a later section.

## Variables

A variable identifier may contain one or more words. A variable may only begin with a letter, however afterwards, numbers, whitespace, and apostrophes may be used. No keywords may be used in a variable identifier (a full list can be found in the **Keywords** section), and a variable cannot have `'s` in it. Variables are case insensitive.

Examples of valid variables include:

```
lol
Area 51
heat death of the universe
```

And examples of invalid variables include:

```
21 guns (variable cannot begin with a number)
things that add up ("add" is a keyword)
the cat's claw ('s cannot be in a variable)
```

## Variable Types

There are no explicit types in Chatlang. However, variables can hold one of the following categories of values:

### Number

A number literal are written as decimal numbers:

```
10
24.342
```

These are stored as double precision floating-point numbers.

### String

String literals use double quotes:

```
"Hello world!"
```

### Boolean

There is no way to directly assign a Boolean value to a variable, but you can evaluate a logical expression and put that into a variable using the keyword `whether`:

```
[17:12] Coizioc: I am whether cats are greater than dogs. (Evaluates to true because cats are obviously the superior animal. In practice, this depends on the values assigned to "cats" and "dogs" before this statement.)
```

### Function

A variable can hold an alias for a function declaration, and can be called like the original function. The details of function declaration and calling can be found in the **Functions** section.

```
[10:45] Coizioc: Make my dog do with bone: Say "woof". Done.
[10:45] Coizioc: Shiba inu is my dog.
(Both of these statements will call the function "my dog":)
[10:46] Coizioc: Call my dog.
[10:46] Coizioc: Call shiba inu. 
```

## Variable Assignment

There are three ways to assign a value to a variable. By default, all variables have the value 0, and do not have to be assigned a value before they are used. In the following sections, `VAR` will be a valid identifier, and `VALUE` can be one of the following:

- An operation
- A string
- A logical expression

### X is Y Assignment

The first way to assign a variable is to use the following syntax:

```
[I am | I'm | (my) VAR [is | are | was | were]] VALUE.
```

Numbers can be assigned using decimal notation using this method. However, one may also use **poetic numbers**, which uses the length of the words contained in `VALUE` to assign an integer to the variable.

For example,

```
(initializes "cat" with 135. len(a) = 1, len(fat) = 3, len(tabby) = 5)
My cat is a fat tabby. 
(initializes "the city I live in" with 294.
	len(twenty-seven) = 12 (modulo 10 is 2), len(kilometers) = 9, len(away) = 4)
The city I live in is twenty-seven kilometers away.
```

When using this assignment method, all variables to the right of `am`, `is`, `are`, etc. must begin with a scope specifier. Otherwise, they will be assumed to be part of a poetic number:

```
Age is 14.
(assigns 3 to "number of victory royales". len(age) = 3)
My number of victory royales is age. 
(assigns 14 to "number of victory royales". The value of "age" is 14.)
My number of victory royales is my age. 
```

### Let X be Y Assignment

The second way to assign a variable is to use the following syntax:

```
Let VAR be VALUE.
```

For example,

```
Let the age of the dog be 14. (Sets "the age of the dog" to 14.)
Let game time be whether my parents are home. (Sets "game time" to the result of "parents" == "home")
Let my ego be my ego times 2. (Doubles the value of "ego".)
```

### Put X in Y Assignment

The third way to assign a variable is to use the following syntax:

```
Put VALUE in VAR.
```

For example,

```
Put my dog in the car. (Sets "the car" to the value of "dog".)
Put 3 times 4 minus 5 in my number. (Sets "number" to 3 * 4 - 5 = 7)
```

## Variable Scope

Each username is its own scope. This mean each user can have their own variable with the same identifier, and have different values for it:

```
[10:24 PM] Coizioc: My dog is grey. (Assigns 4 to @Coizioc's "dog".)
[10:24 PM] EpicGamer: My dog is purple. (Assigns 6 to @EpicGamer's "dog".)
[10:25 PM] Coizioc: Say my dog. (Prints 4.)
[10:25 PM] EpicGamer: Say my dog. (Prints 6.)
```

Each user also has their own variable `i`, which refers to themselves. A user can reference themselves by using the keywords `I`, `me`, or `myself`:

```
[10:24 PM] Coizioc: I am gay. (Assigns 3 to @Coizioc)
[10:25 PM] Coizioc: Say myself. (Prints the value of @Coizioc: 3.)
```

Other users can reference another user's `i` variable using `@USERNAME`:

```
[10:25 PM] TomatoModest: Say @Coizioc. (Prints the value of @Coizioc: 3.)
```

If the user you are trying to reference wrote the previous message, you can use the keywords `you`, `yourself` to refer to that user:

```
[10:24 PM] Coizioc: I am round. (Assigns 5 to @Coizioc)
[10:25 PM] EpicGamer: Say yourself. (Prints the value of @Coizioc: 5.)
```

You can specify which user's variable you want to access by prefixing it with `my`, `your`, or `@USERNAME's`:

```
[10:24 PM] Coizioc: My dog is a good boy. (Assigns 143 to @Coizioc's "dog")
[10:25 PM] EpicGamer: Say your dog. (Prints the value of @Coizioc's "dog": 143.)
[10:25 PM] TomatoModest: Say @Coizioc's dog. (Prints the value of @Coizioc: 143.)
```

## Operations

Operations are evaluated from left to right, ignoring the order of operations.

| Operation | Infix Syntax                          | Prefix Syntax                         |
| --------- | ------------------------------------- | ------------------------------------- |
| +         | `A plus B`, `A and B`, `A added to B` | `add A and B`                         |
| -         | `A minus B`, `A without B`            | `subtract A ` [`and ` | ` from`] ` B` |
| *         | `A times B`, `A multiplied with B`    | `multipliy A and B`                   |
| /         | `A divided by B`                      | `divide A` [`and` | `by`] `B`         |
| %         | `A remain B`, `A remains B`           |                                       |

Infix syntax can be chained together, while prefix syntax can only use two terms.

## Logical Expressions

The basic syntax for a logical expression is as follows:

```
LEFT [am | is | are | was | were] (not) (COMPARISON) RIGHT
```

Here is a table of all the possible comparisons and their syntax:

| Comparison | Syntax         |
| ---------- | -------------- |
| ==         | `equal to`     |
| <          | `less than`    |
| <=         | `at most`      |
| >          | `greater than` |
| >=         | `at least`     |

All of these operations can be negated using the `not` keyword. If there is no comparison, it is assumed that the logical expression is `LEFT == RIGHT`. If there is neither a comparison nor a `RIGHT`, the interpreter checks whether `LEFT != 0` :

```
[9:45 PM] Coizioc: I am weeb. (Assigns @Coizioc with 4)
[9:45 PM] TomatoModest: I am tomato. (Assigns @TomatoModest with 6)

(Puts @Coizioc != 0 into "size". Result is true.)
[9:46 PM] Coizioc: My size is whether myself.

(Puts @Coizioc == @TomatoModest into "size". Result is false.)
[9:46 PM] Coizioc: My size is whether I am @TomatoModest. 

(Puts @Coizioc == @TomatoModest into "size". Result is false.)
[9:47 PM] Coizioc: My size is whether I am equal to @TomatoModest. 

(Puts @Coizioc != @TomatoModest into "size". Result is true.)
[9:46 PM] Coizioc: My size is whether I am not equal to @TomatoModest. 

(Puts @Coizioc == @TomatoModest into "size". Result is true.)
[9:47 PM] Coizioc: My size is whether I am less than @TomatoModest. 

(Puts @Coizioc == @TomatoModest into "size". Result is true.)
[9:47 PM] Coizioc: My size is whether I am at most @TomatoModest. 

(Puts @Coizioc == @TomatoModest into "size". Result is false.)
[9:47 PM] Coizioc: My size is whether I am greater than @TomatoModest. 

(Puts @Coizioc == @TomatoModest into "size". Result is false.)
[9:47 PM] Coizioc: My size is whether I am at least @TomatoModest. 
```

You can also perform logical `and` and logical `or` on each logical expression. Just as in other programming languages, logical `and` has precedence over logical `or`.

## Flow Control

### Conditional Statements

The syntax for an if/else statement is as follows:

```
[if | when] CONDITION, STATEMENT (, [or else | otherwise], STATEMENT)
```

For example:

```
[08:15] Coizioc: If my score is greater than your score, say "Ha, loser", otherwise, say "oh no".
```

### Anchors and Goto Statements

An **anchor** is a point that the program knows the location of. Each first instance of a timestamp is an anchor. One can also define a custom anchor by using the syntax `#VAR`. The program can go to an anchor using a goto statement:

```
[10:45] Coizioc: Say "hello!". (This program prints "hello!" until is is halted.)
[10:45] Coizioc: Go to [10:45]. (The first timestamp with [10:45] is on line 1, so the program will go there.)
```

One can use `remember` instead of `go to` as well. When the program executes a goto statement, it will execute all the code from the message the anchor belongs to, regardless of its position in the message:

```
[10:45] Coizioc: Say "hello!". #wakeup. (This program prints "hello!" until is is halted.)
[10:45] Coizioc: Go to #wakeup. (The program will execute the Say "hello!" statement, even though the anchor appears after the statement, since it is part of the same message that contains the anchor.)
```

## Functions

To create a function, one can use the syntax:

```
make VAR do (with PARAM, PARAM, ...): STATEMENT. STATEMENT. ... Done.
```

We can return a value from a function using a return statement:

```
[return | give back] VAR.
```

For example, we can create a greeting function by doing the following:

```
[21:30] Coizioc: Make greet do with name: Return "hello " and name. Done.
```

We can call this function and put it into a variable like so:

```
[21:31] Coizioc: My greeting is call greet with "Coiz!". (Puts the returned value of greet into "greeting", which will be "hello Coiz!".)
```

## Output

To print output to the screen, one can type `say OPERATION | STRING | VAR.`. When a function call happens in its own statement (as opposed to being called in a variable assignment or another location), the returned value of the function will be printed:

```
[21:31] Coizioc: Call greet with "world!". (outputs "hello world!".)
```

