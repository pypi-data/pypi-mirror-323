# Percents

[Official public repository](https://gitlab.dvmn.org/dvmn-open-source-dev-tools/percents)

Calculating percentages, subtracting a discount, adding a markup is a very common task.
The “Percents” library simplifies the work with percentages. To use it, all you need to do is import the `Percent` type

```python
from percents import Percent
```

Next, the idea is simple. For example, we have a sum of $1000, from which we need to subtract 38%.

```python
1000 - Percent(38)
>>> 620
```

In the same way we can add

```python
1000 + Percent(38)
>>> 1380
```

To take 38% from this amount, all you have to do is multiply the following

```python
1000 * Percent(38)
>>> 380
```

The type of data returned always matches the type of the original number

```python
result = 1000.0 + Percent(38)
>>> 1380
type(result)
>>> float
```

```python
result = Decimal(1000) + Percent(38)
>>> 1380
type(result)
>>> Decimal
```

Percent can be compared to each other

```python
percent1 = Percent(10)
percent2 = Percent(20)
assert percent2 != percent1
assert percent2 > percent1
assert percent1 < percent2

percent1 = Percent(10)
percent2 = Percent(10)
assert percent2 == percent1
assert percent2 >= percent1
assert percent1 <= percent2
```

and with other numbers. In this case, the comparison is in terms of percentage points.

```python
percent = Percent(10)
assert percent == 10
assert percent != 11
assert percent > 9
assert percent < 11
assert percent >= 10.0
assert percent <= 10.0
```

### Attributes

The `Percent` type has two attributes

- Percent.value -- value in percentage points
- Percent.multiplier -- multiplier

```python
percent = Percent(10)
percent.value
>>> 10
percent.multiplier
>>> 0.1
```
