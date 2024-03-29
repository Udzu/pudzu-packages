# [patterns.py](pudzu/sandbox/patterns.py)

## Summary 
NFA-based grep-style pattern matcher supporting some novel operations and modifiers.
Originally developed to analyse wordplay for setting or solving cryptic crosswords.

## Dependencies
*Required*: [graphviz](https://graphviz.org/), [pyparsing](https://github.com/pyparsing/pyparsing), [pudzu-utils](https://github.com/Udzu/pudzu-packages/tree/master/pudzu-utils).

## Documentation
For supported syntax and arguments, run `patterns --help`.
For an explanation of how it's implemented, read on.

## Some background

### Regular expressions

A **regular expression** is a string that describes a search pattern.
It is built of literal characters (e.g. `a` matches the string "a"),
concatenation (e.g. `the` matches the string "the"),
alternation (e.g. `a|the` matches both "a" and "the"),
and the Kleene star (e.g. `(he)*` matches zero or more repetitions of "he").

The set of strings described by a regular expression is called a **regular language**.
Recognising whether a specific string belongs to a regular language (and hence
matches the search pattern) can be implemented efficiently using a **finite automaton**
(see below). Note that modern regular expression engines typically include
additional search pattern features, some of which let you describe languages that are no longer regular
and require additional work to recognise.

The patterns in this module are all regular and are matched using finite automata. 

### Deterministic finite automata

A **deterministic finite automaton (DFA)** is a type of abstract machine with
finitely many states (=a finite state machine, or FSM) that either accepts or rejects
a string of characters. There is a single start
state and zero or more end states. Additionally there are transitions between
states: for each character and state there may be a single transition to another
(possibly the same) state.

Figuring out whether a DFA matches a string simply involves following transitions
from the start state, consuming one character from the input at a time. If, once
the whole string has been consumed, the machine has reached an accepting state, then
the string is accepted. Otherwise it is rejected. Note that this involves looking at
each input character just once, even when the DFA corresponds to a pattern containing
alternation. For example, the following DFA matches the possessive pronouns
their, her, his and xyr:

![DFA matching their, her, his and xyr](images/nfa.png)

### Nondeterministic finite automata

A **nondeterministic finite automaton (NFA)** is the same as a DFA except that
there may be more than one transition from a given state for a given input character.
When following these transitions the automaton picks one "arbitrarily".
A string is matched if there exists a "luck run" of choices leading to an accepting state.
Additionally, NFAs are often also allowed to include **empty transitions** (marked by an ε)
which the machine may choose to follow without consuming any input character. 
For convenience, such automata are sometimes restricted to having a single start state with no
inbound transitions and a single end state with no outbound transitions.
For example,
the following NFA matches the same possessive pronouns as the DFA above:

![NFA matching their, her, his and xyr](images/dfa.png)

Figuring out whether an NFA matches a string can be implemented with backtracking:
whenever you reach a choice, try one transition and if that doesn't work backtrack and try
another. However, it can also be implemented *without* backtracking: rather than
keeping track of which single state you're in at every step, you can keep track of the *set
of all possible states* you could be in, and for each input character follow all the
possible transitions from each of those states.
You then accept the string iff the final set of states contains at least one accepting state.
The NFAs in this module are implemented this way.

This approach also provides a way of **turning any NFA into an equivalent DFA**, with the states of
the DFA corresponding to *sets of states* in the NFA. You simply start at the NFA's start state and
process every possible input character, leading to a new set of states for each one.
You then repeat the process from these sets of states, marking any set of states that contains
an accepting state as accepting. To compile a pattern into a
DFA, use the `-D` argument or `(?D:...)` expression modifier.

## NFA constructions

The bulk of this module involves constructing NFAs from an
extended regular expression language. Here is a summary
of the supported syntax and how the constructions work. Note that
these constructions are not necessarily the most efficient: that
is something that may be addressed later.

### Thompson's construction

Basic regular expressions are converted into NFAs
using a standard construction called **Thompson's construction**.

**Literal characters** are converted into a two-state NFA with a single transition:

```bash
patterns "a"
```

![literal NFA](images/literal.png)

**Concatenation** is converted by linking the end state of the first part
with the start state of the second part.

```bash
patterns "the"
```

![concatenation NFA](images/concatenation.png)
  
**Alternation** is converted by using empty transitions to link a new start state to
both starts and both ends to a new end state:

```bash
patterns "a|the"
```

![alternation NFA](images/alternation.png)

And the **Kleene star** is converted by using an empty transition back from the old
end state to the old start state to allow repetition, and an additional empty transition
to allow bypassing the old NFA altogether:

```bash
patterns "(he)*"
```

![Kleene star NFA](images/kleene.png)

### Standard syntax extensions

There are a number of standard regular expression syntax extensions that still
generate regular languages:

**Character shorthands**: the `.` wildcard and bracketed character classes
such as `[a-z]` and `[^aeiou]` can easily be converted into a two state FSM
with the appropriate transitions. Ranges aren't expressed directly in 
the FSM, though doing so would potentially be useful for large Unicode character classes.

For simplicity, I decided to introduce a
special * state transition that's used if there is no other match. This allows
implementing a negated class like `[^a]` without handling every possible matching input.
However, for efficiency it's more common to implement transitions via a lookup table of character
values, with Unicode characters compiled down to byte sequences. 
  
```bash
patterns "[ae].[^y]"
```

![character classes NFA](images/class.png)

**Repetition shortands**: the `?` (zero or one), `+` (one or more), `{m,n}` (m to n) 
and `{m,}` (m or more) operators can be converted by a combination of
repeated concatenation and Kleene star. 

```bash
patterns "o+h?"
```

![repetition NFA](images/repetition.png)

**Case-insensitive matches**. The simplest way to implement case insensitivity
is to simply expand all characters into two element character classes. To mark the whole match
case insensitive, use the `-i` parameter; to mark
a subexpression, use the `(?i:P)` syntax. Note that this does not implement
full Unicode case insensitivity, where string length may change between cases
(e.g. fußball and FUSSBALL) and where case may depend on locale (e.g. in Turkish
i uppercases to İ not I).

```bash
patterns "T(?i:he)"
```

![case-insensitive NFA](images/case.png)

### Less common extensions

There are also a number of syntax extensions that are regular but are rarely supported,
mostly since they don't play nicely with common non-regular
extensions such as backreferences.

**Conjunction** (written as `A&B`). If A and B are regular expressions, then the language that 
satisfies both expressions is also regular. One way to implement this is
define an NFA whose states are pairs of states (a,b) from A and B, and whose
transitions are (a,b) → (a',b') for input q if both a→a' and b→b' for q. The start
state is (a_start, b_start) and end state is (a_end, b_end), and some additional transitions
are necessary to handle empty transitions in A or B. This construction (like
many of the others described later on) can produce lots of superfluous states,
so it can be useful to remove redundant states from the result (see NFA trimming
section below).


```bash
patterns "(b+)&(...)" -M
```

![conjunction NFA](images/conjunction.png)

**Negation** (written a `¬A`). If A is a regular expression, then the language
that rejects everything A satisfies and accepts everything it doesn't is also regular.
It's easy to negate a DFA: just swap the
accepting and non-accepting states. Negating an NFA can therefore be done
by converting it to a DFA first. Negation also suggests a different way to implement
conjunction: `A&B` can alternatively be implemented as `¬(¬A|¬B)`.

```bash
patterns "¬(.*no.*)"
```

![negation NFA](images/negation.png)

**Reversal** (written as `(?r:A)`). If A is a regular expression, then the language
that accepts the same strings but in reverse order is also regular. This time the
construction is easier for NFAs than DFAs: you just reverse the edges and swap
the start and end states.

```bash
patterns "(?r:o+h|no)"
```

![reversal NFA](images/reversal.png)

### Novel separating operators

The main novel regular operators introduced in this module are all separating
operators: that is, they describe strings that can be separated into
two parts, each satisfying a separate regular expression. Concatenation is
the standard example of this, where the two parts are then concatenated
one after the other. Other examples include:

**Containment** (written `A<B` or `B>A`). A string satisfies `A<B` or `B>A` if
it can be separated into a string satisfying `A` inside a string satisfying `B`.
For example "loooll" satisfies `o+<l+`. To implement `A<B` we define an NFA
with three types of states: left(a) for every a in A, middle(a, b) for every
a in A and b in B, and right(a) for every a in A again. The left and right states
transition within themselves according to the transitions A, while the middle
states transition with themselves according to the transitions of B (leaving the
a state unchanged). Additionally there are empty transitions from left(a) to
middle(a, B_start), and from middle(a, B_end) to right(a) for all a. The NFA
starts at left(A_start) and ends at right(A_end).

```bash
patterns "o+<l+" -M
```

![containment NFA](images/containment.png)

**Strict containment** (written `A<<B` or `B>>A`). The containment 
operators above include the cases where the string satisfying `A` 
occurs before or after any of the string satisfying `B`, and so isn't strictly 
contained within it. We can implement strict containment by adding two more
types of state, left_first(a) and right_first(a). These transition within
themselves according to the empty transitions of A, and transition to left
and right states according to the non-empty transitions. The NFA now starts at
left_first(A_start), and middle states transition to right_first rather than right. 

```bash
patterns "o+<<l+" -M
```

![strict containment NFA](images/strict_containment.png)

**Alternating** (written `A#B` or `A##B`). A string satisfies `A##B` if the
substring made up of every other character starting with the first satisfies `A`,
while the substring starting with the second satisfies `B`. For example "UwUwU" satisfies
`U+##w+`. To implement this, we define an NFA with two type of states: left(a,b) 
and right(a,b) for a in A and b in B. The left states transition between themselves
using the empty transitions of A, and to the right states using the non-empty
transitions of A.
The right states transition similarly using the transitions of B. The start state
is left(A_start, B_start) and the end state is both right(A_end, B_end) and
left(A_end, B_end). Another version `A#B` that doesn't specify which of A or B
comes first makes right(A_start, B_start) an additional
start state.

```bash
patterns "U+##w+" -M
```

![alternating NFA](images/alternating.png)

**Interleaving** (written `A^B` or `A^^B`). A string satisfies `A^B` if it can
be split into a string satisfying `A` interleaved into one satisfying `B`.
For example, "tAAhAe" satisfies `the^A+`. To implement this, we define an
NFA with two types of states, similar to the alternating operator: left(a,b)
and right(a, b). The left states transition between themselves like A (leaving b
unchanged), and the right steps like B (leaving a unchanged). Furthermore,
there are empty transitions between left(a, b) and right(a, b) for all a and b.
The start state is left(A_start, B_start) and the end state left(A_end, B_end)
(or alternatively right, as they're equivalent).
Another version `A^^B` that insists that B is strictly inside A is implemented
similarly to strict containment above.

```bash
patterns "the^^A+" -M
```

![interleaving NFA](images/interleave.png)

### Novel subtraction operators

All the separating operators (including concatenation) have
corresponding subtraction operators. These all describe strings that
can be made to satisfy one regular expression by extending them
with another string satisfying a second regular expression.

**Left and right subtraction** (written `A-B` or `A_-B`). The simplest
form of subtraction is left and right subtraction. A string satisfies `A-B` if 
you can concatenate a string satisfying `B` to the end so that the result
satisfies `A`. For example "th" and "" both satisfy `(the|a)-.`. `A_-B` is similar,
but requires concatenation on the left. To implement `A-B`, we use the intersection
construction described for conjunction to intersect A and B. However, rather
than setting the start state to (A_start, B_start), we allow the intersection
to start at (a, B_start) for any a in A. This therefore describes all the possible
suffixes of A that satisfy B. We then go back to A and change the end states
to include all the possible start states for this suffix intersection. The
implementation of `A_-B` is similar, but uses a prefx intersection instead.

```bash
patterns "(the|a)-." -M
```

![right subtraction NFA](images/subtract.png)

**Subtraction inside and outside** (written `A->B`, `A->>B`, `A-<B` or `A-<<B`).
In the same way that left and right subtraction correspond to concatenation,
inside and outside subtraction correspond to containment. For example, "ll" satisfies
`lo+l->`. Like for containment, there are both strict and non-strict versions.
Implementing subtraction inside is similar to implementing containment itself,
except that we use partial intersections with B to wire the left and right states
directly to each other (thereby skipping over the middle). Implementing subtraction outside
is possible by looking at all the possible prefixes and suffixes that A shares with B
and seeing which ones match up in B (therefore consuming all of it). We then use 
these points that match in B to generate a selection of possible start/end points
in A. We generate an NFA for each, and combine them in an alternation.

```bash
patterns "lo+l->>." -M
```

![subtraction inside NFA](images/subtract_containment.png)

**Subtraction alternating** (written `A-#B` or `A-##B` or `A_-##B`). The subtraction
alternating operators remove every other character. For example, "mm" satisfies `(me)+#..`
since you can alternate two characterts into "mm" to get something satisfying `(me)+`.
The order-aware alternation operator `##` has two subtractions: one on the left and
on the right. To implement these, we define an NFA with states (a,b) and
transitions copied from A and extended from A&B: e.g. if a1→a2 for j in A,
a2→a3 for k in A and b1→b3 for k in B, then (a1,b1)→(a3,b2) for k.

```bash
patterns "(me)+-#.." -M
```

![subtraction alternating NFA](images/subtract_alternating.png)


**Subtraction interleaved** (written `A-^B`, `A-^^B` or `A_-^^B`). The subtraction
interleaved operators remove an interleaved substring. For example, "Mdrd" satisfies
`Madrid-^..` since you can interleave two characters inside to get madrid. The
strict interleaving operator `^^` has two subtractions: one inside and one outside.
To implement these, we define an NFA with states (a,b) and transitions
copied from A. We then add empty transitions for the transitions in A&B: i.e.
if a1→a2 for j in A and b1→b2 for j in B then (a1,a2)→(b1,b2) for ε.


```bash
patterns "Madrid-^^.." -M
```

![subtraction interleaved NFA](images/subtract_interleaved.png)

### Other wordplay syntax

In addition to the separating and subtraction operators above,
there are a number of other related operators introduced to describe wordplay.

**Slicing** (written `(?S:A)[m:n]` or `(?S:A)[m:n:s]`). This is modelled on Python's
slicing syntax and behaves similarly. E.g. `(?S:A)[1:-1]` trims the first and last
characters, `(?S:A)[::3]` matches every third character, and `(?S:A)[::-1]` matches
in reverse. This is implemented via a combination of subtraction on the left and
right (for trimming off a certain length),
intersection (for trimming *to* a certain length), alternating subtraction
(generalised to handle steps other than 2)
and reversal (for handling negative step values).

```bash
patterns "(?S:(me)+)[1::2]" -M
```

![slicing NFA](images/slicing.png)

**Replacement** (written `(?z:A)[B][C]` or `(?Z:A)[B][C]`). This behaves like subtraction
inside, except that it inserts a string matching a third expression C in place of the
removed substring. For example, "Lundon" satisfies `(?z:London)[o][u]`. The implementation
is as for subtraction, but the left and right states are wired via a copy of C.
Like for subtraction, there is a strict version `(?Z:A)[B][C]`.

```bash
patterns "(?z:London)[o][u]" -M
```

![replacement NFA](images/replacement.png)

**Rotation** (written `(?R<n>:A)` or `(?R<=<n>:A)`). This rotates a string n steps
to the right (or left, if n is negative). For example, "eth" satisfies `(R1:the)`
and "het" satisfies `(R-1:the)`. We implement this by slicing off each possible
prefix or suffix and moving it to the other end, creating an alternation of possibilities.
There is an additional form `(?R<=<n>:P)` which matches any rotation of between 1
and n characters left or right (but not 0). Note that a string is not viewed as a rotation
of itself: e.g. "the" does not satisfy `(R3:the)`.

```bash
patterns "(?R<=4:spam)" -M
```

![rotation NFA](images/rotation.png).

**Cipher shifting** (written `(?s<n>:A)` or `(?s:A)`). This applies a shift cipher
to the FSM, replacing each Latin letter by another letter n positions down the alphabet
(or up, if n is negative).
Non-Latin characters are unchanged (though an extension could allow the shift to
be locale-based or configurable). The additional form `(?s:A)` matches any shift
of between 1 and 25 characters (but not 0).

```bash
patterns "(?s13:PNG)" -M
```

![cipher shifted NFA](images/shift.png).

One bit of wordplay that sadly can't be supported is **anagrams**. This is because
an anagram operator would not be regular: e.g. the language that matches
all anagrams of `(ab)+` is not a regular language, as matching against
it would require us to keep
track of the potentially unbounded number *a*s and *b*s.

### General pattern syntax

There are also a few bits of general syntax, not connected with manipulating
individual strings.

**Pattern references** (written `(?&<ID>=A)` and `(?&<ID>)`). This syntax
allows you to define and later use a subpattern. For example "cat" and "dog" 
both match `(?&v=[aeiou])(?&c=[^aeiou])(?&c)(?&v)(?&c)` but "ewe" doesn't. A
pattern definition cannot refer to itself, though it can refer to previously 
defined patterns.

**External world list** (written `\w`). Using the `-d` parameter you can specify an external
world list and then use `\w` to match any word in the list. For efficiency, 
this is implemented as a prefix tree rather than just an alternation.

**External FSM definition** (written `\f`). Using the `-f` parameter you can specify
an explicit NFA definition and then use `\f` to refer to it inside a pattern. The
NFA definition file should consist of lines of the format "State Input State*",
each defining transitions from one state and input to zero or more other states.
Inputs should be either a single character, a character range, or the strings EMPTY or ALL.
The start and end states should be called START and END. To generate an NFA definition file
*from* a pattern, use the `-s` parameter.

## Other NFA operations

Apart from the search patterns and constructions described above, there
are a number of other operations on NFAs implemented in the module.

### Trimming NFAs

As mentioned before, some of the constructions above can produce lots of
superfluous states, so it can be useful to remove redundant states from the
resulting NFAs. Specifically, we remove states that are not reachable from the
start, as well as ones from which it isn't possible to reach an accepting state.
We also eliminate states that only have an empty transition to the end state,
since they're another common by-product.

### Minimal DFAs

For DFAs we can do better that this. Unlike for NFAs, there exists efficient
algorithms to transform any DFA into an equivalent DFA with a minimal number of states,
based on the merging of equivalent states. The simplest for our purpose
is Brzozowski's algorithm, which involves: reversing the input DFA
as described in the reversal section, then converting the result into a
DFA using the powerset construction, then reversing it again, and then converting
it again. As long as we discard any unreachable states as described above, the
resulting DFA is guaranteed to be minimal. To convert an NFA into a minimal DFA
you can use the `(?M:A)` syntax, which is just shorthand for `(?D:(?r:(?D:(?r:A))))`.

### Submatch extraction

While backreferences in patterns cannot be implemented without backtracking (or some other sort
of stack), it *is* possible to incorporate submatch extraction into an NFA-based matcher without
backtracking. The approach adopted here involves tagging NFA transitions with capture information.
Normally you'd tag empty transitions or states to indicate the start and end of a match group. However,
that isn't sufficient to identify the submatches for many of the novel operators such as `A#B`.
Instead, we tag non-empty transitions with the match group(s) that they correspond to.

```bash
patterns "(?<start>.*)(?<end>.)"
```

![tagged NFA](images/tagged.png).

When evaluating the NFA, we still transition to set of all possible states for each input
(see NFA section above). However, for each state we also keep track of capture information:
if we reach a state via a transition tagged by a capture group, then we add the current input character
to that group's capture value. If a state is reached via multiple transitions with different tags, we
simply select one of them. This corresponds to an ambiguous match, and which submatch we choose to extract
does not affect whether the match succeeds or not. We make the behaviour deterministic
by defining an implicit ordering on states, insisting for example that the first match of
an alternation or concatenation takes precedence over the second.

A few things are worth noting about this type of submatching. The absence of start/end tags means
that matches contain *every* character connected to a subexpression: repeated expressions will capture
every instance rather than just the last, and it's even possible to tag two subexpressions with
the same tag to capture both. For example `(?<tel>[0-9]+)( (?<tel>[0-9]+))*` will
capture an entire telephone number, stripping space separators. On the other hand, it's not possible
to distinguish empty submatches from failed submatches. This behaviour could be changed by also adding
start/end tags, but I've chosen to keep it.

Extending the various pattern operations to support submatch extraction is mostly straightfoward:
we just keep the transition tags when constructing new NFAs (or in the case of conjunction,
combine them). The only exception is trying to construct a DFA from the NFA: this requires
more complex transition tagging and has not been implemented. Specifically, the
DFA transitions have to keep track of multiple possible tag options, and the end states have to be
annotated with the valid ones.

```bash
patterns "(?<start>.*)(?<end>.)" -D  # (NOT IMPLEMENTED)
```

![tagged DFA](images/tagged_dfa.png).

### Generating examples and bounds

Another thing we can easily do with NFAs is generate an example matching string.
The simplest way is just to traverse the NFA graph randomly until we reach an 
accepting state. Note that using a special * state (as described in the
character shorthands section) actually helps here, as it
makes it less likely that we'll get stuck for ages in a transitions like `[^a]*`.
That said, we can also generate examples with a given minimum or maximum length
but first intersecting the NFA with `.{min,max}` or `.{min,}`. 
To generate a shortest example, we can also use Dijkstra's algorithm to find a
shortest accepting path. To generate an example for a given pattern, pass in the `-x` parameter;
to generate multiple examples and quit, pass in `-X N`.

```bash
> patterns "the^^A+" -x
[16:13:51] patterns:INFO - Example match: 'thAAe'
```

NFA traversal can also be used to generate lexicographic bounds for the possible matches,
which could be used to pre-filter a set of records before matching them against the
pattern. For example matches for the pattern `(a|the)+` will always lie between the strings "a" and 
"thethetheu" (where the last letter "u" is 'rounded up from "t" to ensure every possible match
lies below it, no matter how long). To generate bounds for a given pattern (of fixed maximum length
10), pass in the `-b` parameter.

```bash
> patterns "(a|the)+" -b
[16:13:51] patterns:INFO - Match bounds: 'a' to 'thethetheu'
```

### Generating equivalent basic regular expressions

Since all of the constructions in this module are regular and implemented
by NFAs, we can convert any of them (as well any explicitly provided FSMs)
into a regular basic regular expression. One approach
is based on **state elimination**: start with the original NFA
and then eliminate intermediate states while keeping the remaining edges labelled 
with consistent regular expressions describing those transitions. For
a full description, see for example [this Stack Exchange answer](https://cs.stackexchange.com/questions/2016/how-to-convert-finite-automata-to-regular-expressions/2389#2389).

Since the resulting expressions are typically inefficiently verbose, we apply
various heuristics to simplify them. Implemented rules include:

```
[ab]|[ac]   = [abc]
[ab]|[^ac]  = [^c]
[^ab]|[^ac] = [^a]
A|(B|C)|D   = A|B|C|D
A|B|A       = A|B
A|B|C       = B|C if A < B
AB|AC|A     = A(B|C|ε)
BA|CA|A     = (B|C|ε)A
AA*|B|C     = A*|B|C if ε < B
A(BC)D      = ABCD
AεB         = AB
A*A         = AA* (canonical form)
A*B*        = A* if A < B or B* if B < A
ε*          = ε
A**         = A*
(ε|B|C)*    = (B|C)*
(A*|B|C)*   = (A|B|C)*
(A*B*C*)*   = (A|B|C)*
(A|B|C)*    = (B|C)* if A < B*
(ABC)*      = B* if all(x < B* for x in ABC)
```

A number of the rules depend on knowing whether A < B: i.e. whether any match for A will also
match B. This is also implemented with heuristics (see below), but with the slow fallback of
generating the FSMs for A and B and checking whether `¬(¬A|B)` is empty or not.

```
    A < A
 [ab] < [abc]
 [ab] < [^cd]
[^ab] < [^a]
    ε < A*
   A* < B*    iff A < B
A|B|C < D     iff all(x < D for x in ABC)
    A < B|C|D iff any(A < x for x in BCD)
    A < B*    if  A < B  
  ABC < D*    if  all(x < D for x in ABC)

   A !< B     if  min_length(A) < min_length(B)
   A !< B     if  max_length(A) > max_length(B)
   A !< B     if  first_character(A) !< first_character(B)
   A !< B     if  last_character(A) !< last_character(B)
```


To generate an equivalent regular expression for a given pattern, pass in the `-r` parameter.
These regular expressions also make it easy to figure out the shortest and longest
possible match lengths for the pattern, as well as the possible first and last characters.

```bash
> patterns "the^^A+" -Mr
[16:13:51] patterns:INFO - Equivalent regex: '^(t(A+h|hA)A*e)$'
[16:13:51] patterns:INFO - Match lengths: 4+
```

To output just an equivalent regex then quit (e.g. to use as an argument for grep), pass in the 
`-R` parameter. This mode avoid using the slow FSM fallback described above.

### Generating NFA diagrams

Finally, the module also lets you generate FSM diagrams in SVG format using the `-c` or `-s` parameters.
These use the [graphviz](https://graphviz.org/) package to visualise the NFAs. The console diagrams generated
with `-c` are intended for use on consoles such as [kitty](https://sw.kovidgoyal.net/kitty/),
and may require a tool such as rsvg-convert to convert the SVG into a format that can be 
displayed inline. The `-s` parameter also generates a text representaton of the FSM that can be passed 
back in wtih `-f`.

## Similar projects

If you found this interesting, then you may also enjoy the much more professional [libfsm](https://github.com/katef/libfsm) project
("DFA regular expression library & friends"), as well as this series of articles ([#1](https://swtch.com/~rsc/regexp/regexp1.html)
[#2](https://swtch.com/~rsc/regexp/regexp2.html) [#3](https://swtch.com/~rsc/regexp/regexp3.html)
[#4](https://swtch.com/~rsc/regexp/regexp4.html)) about efficient regular expression matching.

