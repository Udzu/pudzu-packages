# [pudzu-charts](../pudzu/charts.py)

## Summary 
Pillow-based charting.
 
## Dependencies
*Required*: [pandas](http://pandas.pydata.org/), [pudzu-pillar](pillar.md), [pudzu-dates](dates.md).

## Documentation

Five chart types are currently supported: **bar charts**, **time charts**, **grid charts**, **map charts** and **calendar charts**. For usage information, see the docstrings or [sample scripts](https://github.com/Udzu/pudzu/).

### Legends

**generate_legend**: generate a chart category legend.

![smurf etymology legend](charts/legend.jpg)

### Bar charts

**bar_chart**: generate a bar chart; supports grouped, stacked and percentage stacked charts, as well as horizontal charts and flexible coloring and labeling.

![us elections bar chart](charts/uspopular.jpg)

![flag hues bar chart](charts/flaghues.jpg)

### Time charts

**time_chart**: generate a time chart; supports numeric and date timelines highlighting both ranges and events.

![g7 time chart example](charts/g7.jpg)

![jerusalem time chart example](charts/jerusalem.jpg)

### Grid charts

**grid_chart**: generate an image grid chart; supports grouping cells to generate Euler diagrams.

![grid chart example](charts/periodic.jpg)

![grid chart example](charts/markovtext.jpg)

### Map charts

**map_chart**: generate a map chart. Input is a map template with each region having a unique color. Regions can be named (see generate_name_csv), labelled (see generate_bbox_csv) and have overlays such as label arrows.

![map chart example](charts/femaleleaders.jpg)

![map chart example](charts/dishes.jpg)

### Calendar charts

**month_chart**: generate a calendar chart for a given month; supports non-Western calendars.

![jerusalem time chart example](charts/trump.jpg)
