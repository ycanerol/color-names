from bs4 import BeautifulSoup
from dominate import document
from dominate.tags import *
import colorsys

def hex_to_rgb(h):
    h = h.lstrip('#')
    rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
    return rgb


files = ['a-f.html', 'g-m.html', 'n-z.html']
all_colors = []
for file in files:
    with open(file, 'r') as f:
        soup = BeautifulSoup(f, features='html.parser')

    color_tables = soup.find_all("table", class_="wikitable")
    colors = []

    for ctable in color_tables:
        rows = ctable.find_all("tr")[1:]
        for row in rows:
            # Names of colors are found in th tags
            names = row.find_all("th")
            # The rest of the information about the color in in td tags
            columns = row.find_all("td")
            if len(columns) >= 2:
                name = names[0].text.strip()
                hex_value = columns[0].text.strip()
                colors.append((name, hex_to_rgb(hex_value)))

    all_colors.extend(colors)

# Sort all colors based on their HSV values
all_colors.sort(key=lambda rgb: colorsys.rgb_to_hsv(*rgb[1]))

# Group colors based on the first letter of their name
indexed_colors = dict()
for name, rgbval in all_colors:
    name_first_letter = name.lower()[0]
    try:
        cols = indexed_colors[name_first_letter]
        indexed_colors.update({name_first_letter: cols + [(name, rgbval)]})
    except KeyError:
        indexed_colors.update({name_first_letter: [(name, rgbval)]})

# Put the dictionary of colors into alphabetic order
indexed_colors = dict(sorted(indexed_colors.items()))
avg_color_per_letter = {}

for letter, colors in indexed_colors.items():
    avg_r, avg_g, avg_b = 0, 0, 0
    for i, (name, color) in enumerate(colors):
        avg_r += color[0]
        avg_g += color[1]
        avg_b += color[2]
    i += 1
    avg_r, avg_g, avg_b = round(avg_r/i), round(avg_g/i), round(avg_b/i)
    avg_color_per_letter.update({letter:(avg_r, avg_g, avg_b)})


# Create an HTML document to display the results
doc = document(title='colors')
with doc.head:
    style("""
    /* Tooltip container */
    .tooltip {
      position: relative;
      display: inline-block;
      padding-bottom: 12px;
    }

    /* Tooltip text */
    .tooltip .tooltiptext {
      visibility: hidden;
      width: 100px;
      background-color: black;
      color: #fff;
      text-align: center;
      padding: 1px 0;
      border-radius: 6px;

      /* Position the tooltip text - see examples below! */
      position: absolute;
      z-index: 1;
    }

    /* Show the tooltip text when you mouse over the tooltip container */
    .tooltip:hover .tooltiptext {
      visibility: visible;
    }
    body {
    background-color: #666666;
    }
    """)

with doc:
    h1('Colors')
    with table():
        for letter in indexed_colors.keys():
            with tr():
                th(letter, style=f"padding-left: 40px; background-color:rgb{avg_color_per_letter[letter]};")
                for cname, rgb in indexed_colors[letter]:
                    with td(" ", cls="tooltip", style=f"padding-left: 10px; background-color:rgb{rgb};"):
                        span(cname, cls="tooltiptext")

with open('colors.html', 'w') as f:
    f.write(doc.render())
