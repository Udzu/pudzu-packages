# pudzu-packages

## Summary

Various Python 3.6+ packages, mostly geared towards dataviz and used to create the data visualisations in this [flickr account](https://www.flickr.com/photos/zarfo/albums) (most of which been posted to reddit at some point by [/u/Udzu](https://www.reddit.com/user/Udzu/)). The packages aren't properly tested yet but are reasonably simple, generic and docstringed.

For sample scripts that use these packages, see the [pudzu](https://github.com/Udzu/pudzu) repo.

## Installation

The packages can be installed individually using `pip install [package-name]` (for the latest release) or by directly running `python setup.py install` (which installs all of them).

## Packages

- [pudzu-utils](docs/utils.md) - various utility functions and data structures.
- [pudzu-dates](docs/dates.md) - date classes supporting flexible calendars, deltas and ranges.
- [pudzu-pillar](docs/pillar.md) - various monkey-patched Pillow utilities.
- [pudzu-charts](docs/charts.md) - Pillow-based charting tools.

## Copyright

Copyright © 2017–19 by Udzu. Licensed under the [MIT License](LICENSE).
