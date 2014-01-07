#!/usr/bin/python2
# -*- coding: utf-8 -*-

import urllib2 as ulib
import bs4 as bs
import unidecode as undcd

URL = 'http://www.mar.mil.br/dhn/chm/tabuas/'
YEAR = '2014'
DATA_DIR = 'data'

MOON_PHASES = {
    'Nova.gif': 'N',
    'Cresc.gif': 'C',
    'Cheia.gif': 'F',
    'Ming.gif': 'W'
}

current_moon = 'N'

def parse_port_option(option):
    return {
        'id': option.attrs['value'],
        'name': option.text.strip()
    }

def parse_header(content):
    header = {}
    center = content.find_all('center')[2]
    header['name'] = undcd.unidecode(center.strong.font.text)

    all_text = center.find_all('font')[1].text.encode('utf-8')
    info_text = all_text.split('\n\n')[0]
    raw_info = [i.replace('\xc2\xa0', '') for i in info_text.split('\n')]

    header['latitude'] = dm_to_decimal(raw_info[1].split(' ')[1])
    header['longitude'] = dm_to_decimal(raw_info[2].split(' ')[1])

    return header

def dm_to_decimal(dm):
    direction = dm[-1]
    only_numbers = ''.join([c if c.isdigit() or c == ',' else ' ' for c in dm])
    splitted = only_numbers.split(' ')
    degrees = float(splitted[0])
    minutes = float(splitted[2].replace(',', '.'))

    decimal = degrees + minutes / 60
    if direction in ['S', 'W']:
        return -decimal
    else:
        return decimal

def parse_day_table(rows):
    global current_moon
    day_table = {}

    first_row = rows[0].find_all('td')
    if first_row[0].img:
        moon = first_row[0].img['src']
        current_moon = MOON_PHASES[moon]

    day_table['moon'] = current_moon
    day_table['date'] = first_row[1].text.split('    ')[1]

    tide_table = []
    extract_height = lambda cols : float(cols[3].text.strip())
    h1 = extract_height(rows[0].find_all('td'))
    h2 = extract_height(rows[1].find_all('td'))
    label = 'high' if h1 > h2 else 'low'
    for row in rows:
        columns = row.find_all('td')
        entry = {}
        entry['time'] = columns[2].text
        entry['height'] = extract_height(columns)
        entry['label'] = label
        label = 'high' if label == 'low' else 'low'
        tide_table.append(entry)

    day_table['tide'] = tide_table
    return day_table

def parse_month_table(content):
    table = content.find('table')
    trs = table.find_all('tr')[2:]
    ntrs = len(trs)
    month_table = {}
    day_table = []
    for index, tr in enumerate(trs):
        tds = tr.find_all('td')

        if len(tds) == 1:
            day = parse_day_table(day_table)
            month_table[day['date']] = day
            day_table = []
            continue

        day_table.append(tr)

        # the last day
        if index == ntrs - 1:
            day = parse_day_table(day_table)
            month_table[day['date']] = day

    return month_table

if __name__ == '__main__':
    import json
    import os

    if not os.path.exists(DATA_DIR):
        os.mkdir(DATA_DIR)

    raw_html = ulib.urlopen(URL).read()
    home = bs.BeautifulSoup(raw_html)

    ports_combo = home.find(attrs={'name': 'cboNomePorto'})
    port_options = ports_combo.find_all(name='option')
    ports = [parse_port_option(o) for o in port_options if not u'até' in o.text]

    months_combo = home.find(attrs={'name': 'cboMes'})
    month_options = months_combo.find_all(name='option')
    months = [m.text for m in month_options]

    index_info = []

    for i in xrange(len(ports)):
        port_table = {}
        for j, month in enumerate(months):
            url = URL + ports[i]['id'] + month + YEAR + ".htm"
            raw_content = ulib.urlopen(url).read()
            content = bs.BeautifulSoup(raw_content)

            if j == 0:
               header = parse_header(content)
               index_info.append(header)
               port_table = {
                   'name': header['name'],
                   'latitude': header['latitude'],
                   'longitude': header['longitude'],
                   'table': {}
               }
               print 'Starting ' + header['name'] + '...'

            month_table = parse_month_table(content)
            port_table['table'].update(month_table)

        file_name = port_table['name'].lower().replace(' ', '_') + '.json'
        file_path = os.path.join(DATA_DIR, file_name)

        fp = open(file_path, 'w+')
        json.dump(port_table, fp, sort_keys=True)
        fp.close()

        print 'Finished! Saved in: %s' % file_path

        index_info[-1]['file'] = file_name

    # generate the index file
    index_path = os.path.join(DATA_DIR, 'index.json')
    fp = open(index_path, 'w+')
    json.dump(index_info, fp, sort_keys=True, indent=4, separators=(',', ': '))
    fp.close()
