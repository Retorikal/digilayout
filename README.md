
Prerequisites:
- python
- cairosvg
- wget
- xml-python

You can get all that by installing pip, python, then executing 
```pip install cairosvg wget xml-python```.

Example usage: ```python digilayout.py sampledecklist -t template/template_a3_land.svg -o testrun```

Needs internet connection and takes a while. Results are written to output folder as svg and pdf, with detected digitamas automatically given a matching card back on their corresponding card back output file.

Enjoy!