#!/usr/bin/python3

from urllib.error import HTTPError
from os.path import exists
from xml.etree import ElementTree
from datetime import datetime
import argparse
import requests
import cairosvg
import copy
import math
import wget
import xml
import sys
import re

now = datetime.now
default_template = "template/template_a3_port.svg"
en_url = "https://world.digimoncard.com/images/cardlist/card/{}.png"
jp_url = "https://en.digimoncard.com/images/cardlist/card/{}.png"
tama_url = "backings/Digi-Egg-Card-Back.png"
back_url = "backings/Digimon-Card-Back-Colorfix-shadows.png"
output_location = "output/"
images_location = "cardimg/"
img_attrib = "{http://www.w3.org/1999/xlink}href"
outname = ""


def imgpath(path):
  return "{}{}.png".format(images_location, path)


def parse_cards(path):
  decklist = open(path)
  cardlist = []

  print("Parsing cardlist and downloading images..")
  for entry in decklist.readlines():
    result = re.search(r"(/*)([0-9]) (.*?)\s*(\w+-[0-9]+)", entry)
    if result == None or result.group(1) != "":
      continue

    count = int(result.group(2))
    name = result.group(3)
    code = result.group(4)
    cardlist.extend([code for _ in range(count)])

    print("Downloading {}'s ({}) image".format(name, code))
    if not exists(output_location + imgpath(code)):
      wget.download(jp_url.format(code), "./" +
                    output_location + imgpath(code))
  print("\nImage download done.")
  print("You are about to print {} cards.".format(len(cardlist)))

  return cardlist


def get_digitama_list():
  r = requests.get(
    'https://digimoncard.io/api/search.php?limit=100&type=Digi-Egg&sort=name')
  return [card["cardnumber"] for card in r.json()]


def modify_svg(path, cardlist, outname):
  digitama_list = get_digitama_list()
  tree = ElementTree.parse(path)
  trbk = copy.deepcopy(tree)

  cardslots = tree.getroot().findall(
    "./{http://www.w3.org/2000/svg}g/{http://www.w3.org/2000/svg}g[@id='imagesgroup']/")
  backslots = trbk.getroot().findall(
    "./{http://www.w3.org/2000/svg}g/{http://www.w3.org/2000/svg}g[@id='imagesgroup']/")
  slotcount = len(cardslots)
  cardcount = len(cardlist)
  printcount = math.ceil(cardcount / slotcount)

  print("You will need to print {} times ({} cards each).".format(
    printcount, slotcount))

  last_slot_id = cardslots[-1].attrib["id"]
  dimensions = (int(last_slot_id[-2]), int(last_slot_id[-1]))

  print("Template dimensions: {} (height, width) in cards".format(dimensions))

  printed_count = 0
  # Iterate for all print slots available
  for i in range(slotcount * math.ceil(cardcount / slotcount)):
    cardslot = cardslots[i % slotcount]
    cardcode = cardlist[i] if i < len(cardlist) else ""

    # assign face card image
    cardslot.attrib[img_attrib] = imgpath(
      cardcode) if cardcode != "" else tama_url

    # assign backing card image
    index = i % slotcount
    row = index // dimensions[1]
    col = index % dimensions[1]
    position = row * dimensions[1] + (dimensions[1] - col) - 1
    backslot = backslots[position]
    backslot.attrib[img_attrib] = tama_url if cardcode in digitama_list else back_url

    if i % slotcount == slotcount - 1:
      printed_count += 1
      facename = "{}{}-{}-face.svg".format(output_location,
                                           outname, printed_count)
      backname = "{}{}-{}-back.svg".format(output_location,
                                           outname, printed_count)
      facepdfname = "{}{}-{}-face.pdf".format(
        output_location, "pdf" + outname, printed_count)
      backpdfname = "{}{}-{}-back.pdf".format(
        output_location, "pdf" + outname, printed_count)
      tree.write(facename)
      trbk.write(backname)
      cairosvg.svg2pdf(url=facename, write_to=facepdfname)
      cairosvg.svg2pdf(url=backname, write_to=backpdfname)

      print(
        "Finished crafting svg for print [{}/{}] \r".format(printed_count, printcount))


if __name__ == "__main__":
  parser = argparse.ArgumentParser(
    description="Digimon card proxy auto-layout program. The output is intended to be printed on 260gsm (back) and 150gsm (front) art paper or 310gsm doff laminated both sides.")
  parser.add_argument('filename', metavar='decklist', type=str,
                      help='Decklist file name. Supported format is exported from digimoncard.dev as text; where each entry looks like "<n> <cardname>    (<cardcode>)"')
  parser.add_argument('-t', metavar='template', type=str,
                      help="svg template to use, default format uses A3 5*5 cards. Check ./template folder for more.", default=default_template)
  parser.add_argument('-o', metavar='output', type=str,
                      help="name identifier for outputs", default=now().strftime("%m%d%Y-%H%M%S"))
  args = parser.parse_args()

  template = args.t
  outname = args.o

  cardlist = parse_cards(args.filename)
  modify_svg(template, cardlist, outname)

  print("Finished. Enjoy your proxies!")
