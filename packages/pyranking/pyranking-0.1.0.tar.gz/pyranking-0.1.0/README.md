# PyRanking
Strategies to assign ranks

[![Coverage Status](https://img.shields.io/coveralls/quocvu/pyranking.svg?style=for-the-badge)](https://coveralls.io/github/quocvu/pyranking)
[![License](https://img.shields.io/github/license/quocvu/pyranking.svg?style=for-the-badge)](https://github.com/quocvu/pyranking/blob/master/LICENSE)

# Strategies to assign ranks

In most cases, a sorting function is a best tool to make a ranking. But how
about tie scores? You may end up with giving different ranks for tie scores.
And I'm quite sure that will make your users dissatisfied.

Solution? You are on the right page.

This module provides various ranking strategies to assign correct ranks to tie
scores. It comes with [5 most common strategies](http://en.wikipedia.org/wiki/Ranking#Strategies_for_assigning_rankings):
`competition`, `modified-competition`, `dense`, `ordinal`, and `fractional`.

## Installation

    python -m pip install pyranking

## Usage

Suppose we want to rank an array of computer languages by the year they were
introduced.

```
languages = [
  { "name": 'Javascript', "year": 1995 },
  { "name": 'Java', "year": 1995 },
  { "name": 'C#', "year": 2001 },
  { "name": 'Groovy', "year": 2003 },
  { "name": 'Scala', "year": 2003 },
  { "name": 'Go', "year": 2009 },
];
```

We need to provide a function defining the sorting criteria. The function
must accept one entry of the array and returns a value to rank on (the year
in this case). Note the returned value can be directly an attribute of the
object, or any computed value based on that object (e.g. the math test score
plus the English test score of a student).

```
score_fn = lambda x: x["year"]
```

Let's run the ranking operation on this list of languages

```
from pyranking import rank
ranked_languages = rank(languages, score_fn);
```

The `ranked_languages` is an array that looks like below. By default, it sorts
by descending order, using the `competition` strategy, and starts ranking at 1

```
[ { "rank": 1, "item": { "name": 'Go', "year": 2009 } },
  { "rank": 2, "item": { "name": 'Groovy', "year": 2003 } },
  { "rank": 2, "item": { "name": 'Scala', "year": 2003 } },
  { "rank": 4, "item": { "name": 'C#', "year": 2001 } },
  { "rank": 5, "item": { "name": 'Javascript', "year": 1995 } },
  { "rank": 5, "item": { "name": 'Java', "year": 1995 } } ]
```

To change the ranking strategy, use the optional parameter `strategy`.

```
const ranked_anguages = rank(languages, score_fn, strategy="dense");
```

To sort in ascending order

```
const ranked_languages = rank(languages, score_fn, reverse=True);
```

To start ranking at any number (e.g. 5).

```
const ranked_anguages = rank(languages, score_fn, start=5);
// Go language would have a rank of 5.
```

## License

[MIT](https://github.com/quocvu/pyranking/blob/master/LICENSE.txt)
