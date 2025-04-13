# A cheatsheet for the `re` module


The `re` module provides lets you find patterns in text using _regular expressions_.

## Raw strings

In string literals, the `\` (backslash) character has a special meaning: it lets you express
characters like "newline" or "◌̀" or "🦆" that are hard or impossible to type as is:

```py
>>> print("hello\nworld")
hello
world
>>> "A\u0300"
'À'
>>> "\N{DUCK}: \"It's quacking time\""
'🦆: "It\'s quacking time"'
```

To use the backslash characters as is, you need to use `\\`:

```py
>>> print("\n")
<BLANKLINE>
<BLANKLINE>
>>> print("\\n")
\n
>>> print("C:\\Users\\Bob\\photo.jpg")
C:\Users\Bob\photo.jpg
```

```py
>>> print("\s+")  # Don't do this! Will be an error in the future
!! SyntaxWarning: invalid escape sequence '\s'
  print("\s+")
\s+
>>> print("\\s+")  # Correct
\s+
```
<!-- ^opts skip  # Can' t catch warnings with doctest -->

However, this quickly gets tedious with regular expressions, which use `\` a lot.
If you prefix a Python string literal with an `r`, it treats backslashes as normal characters:

```py
>>> print("\\d \\\\ \\d")
\d \\ \d
>>> print(r"\d \\ \d")
\d \\ \d
>>> print(r"\\d \\\\ \\d")
\\d \\\\ \\d
>>> print(r"C:\Users\Bob\photo.jpg")
C:\Users\Bob\photo.jpg
```

These are called "raw string literals" (not "regex strings"!). A raw string literal
doesn't produce a special kind of object, it's just a different way to make a string.
```py
>>> r"\d \\ \d"
'\\d \\\\ \\d'
>>> type(r"\d \\ \d")
<class 'str'>
```

Read more on this in the reference documentation:
- [string literals](https://docs.python.org/3/reference/lexical_analysis.html#string-and-bytes-literals)
- [escape sequences](https://docs.python.org/3/reference/lexical_analysis.html#escape-sequences)


## `re` functions

### `fullmatch`

This function returns a `Match` object if the _entire string_ matches the given pattern, and `None` otherwise.

```py
>>> re.fullmatch(r"no.[0-9]+", "no.42069")
<re.Match object; span=(0, 8), match='no.42069'>
>>> re.fullmatch(r"no.[0-9]+", "no. 42069")
>>>
>>> re.fullmatch(r"no.[0-9]+", "This is no.42069!")
>>>
>>> re.fullmatch(r"no.[0-9]+", "no.42069 and others")
>>>
```
This is very useful when you want to validate external inputs:

```py
>>> re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", "bob@example.com") is not None
True
>>> re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", "not-an-em@il") is not None
False
```

Read more about `re.fullmatch`: https://docs.python.org/3/library/re.html#re.fullmatch


### `search`

This function returns the first match that it finds anywhere in the string.
If there are no matches, it returns `None`.

```py
>>> re.search(r"[0-9]+", "I have 420 birds, 69 of them ducks.")
<re.Match object; span=(7, 10), match='420'>
```

Read more about `re.search`: https://docs.python.org/3/library/re.html#re.search


### `finditer`

`finditer` returns an iterator with all the non-overlapping matches for a pattern in a string.

```py
>>> it = re.finditer(r"([0-9]+)(\.[0-9]+)?", "I have 420 birds, 69 of them ducks, most 3.5 years old.")
>>> for match in it: print(match)
<re.Match object; span=(7, 10), match='420'>
<re.Match object; span=(18, 20), match='69'>
<re.Match object; span=(41, 44), match='3.5'>
```

There are some caveats to this function. Consider this:

```py
>>> it = re.finditer(r"([0-9]+)(\.[0-9]+)?", "1.23.45.67.89.0")
>>> for match in it: print(match)
<re.Match object; span=(0, 4), match='1.23'>
<re.Match object; span=(5, 10), match='45.67'>
<re.Match object; span=(11, 15), match='89.0'>
```

- Note that some `.`s were not included in any of the matches. It's not an error to have some parts of the string not be part of any matches for `finditer`. You can detect this by comparing the `start` and `end` of consecutive matches.
- Note that the substrings `1.23`, `45.67`, `89.0` were found, even though the matches `1.2`, `3.4`, `5.6`, `7.8`, `9.0` were found, which would have covered more of the string. Because the `+` operator is "greedy", it will include as much input as possible.

`re.finditer` is similar to something like this:

```py
def finditer(pattern, string):
    pattern = re.compile(pattern)
    pos = 0
    while match := pattern.search(string, pos):
        yield match
        pos = match.end()
```
<!-- ^opts skip -->

In other words, `finditer` lives here and now. It doesn't do any global optimization, it just finds the next match on demand.

The official documentation has a more comprehensive example of `finditer`:
https://docs.python.org/3/library/re.html#writing-a-tokenizer

> Exercise for the reader: find an edge case where the above implementation of
> `finditer` is wrong.

Read more about `re.finditer`: https://docs.python.org/3/library/re.html#re.finditer


### `match`

`re.match` is a pretty niche function, despite the appealing name.
It returns a match if a _prefix_ of the string matches the given pattern.
It's like a more powerful version of `str.startswith`.

```py
>>> image = b"\x89PNG\r\n..."
>>> re.match(br"(?P<png>\x89PNG)|(?P<jpeg>\xff\xd8\xff[\xc0\xc2])", image)
<re.Match object; span=(0, 4), match=b'\x89PNG'>
```
```py
>>> log_line = "2024-05-03 12:00:01 [ERROR] I'm on fire!"
>>> re.match(r"[-0-9:. ]+\[([^\]]+)\]", log_line)
<re.Match object; span=(0, 27), match='2024-05-03 12:00:01 [ERROR]'>
```

Most of the time you don't want `re.match`: you might have undesired leftovers at the end of the string.
```py
>>> re.match(r"[^\s@]+@[^\s@]+\.\w+", "bob@example.com")  # positive test case
<re.Match object; span=(0, 15), match='bob@example.com'>
>>> re.match(r"[^\s@]+@[^\s@]+\.\w+", "obviously-wrong") is None  # negative test case
True
>>> # Ship it!
>>> re.match(r"[^\s@]+@[^\s@]+\.\w+", "impostor@example.com🦆🦆🦆")
<re.Match object; span=(0, 20), match='impostor@example.com'>
```

Read more about `re.match`: https://docs.python.org/3/library/re.html#re.match


### `findall`

Perhaps use `finditer` instead.
This function is weird because it doesn't produce `Match` objects.
But if you insist: https://docs.python.org/3/library/re.html#re.findall

