#!/usr/bin/python2
# -*- coding: utf-8 -*-

import urllib2 as ulib
import bs4 as bs

URL = 'http://www.mar.mil.br/dhn/chm/tabuas/'
YEAR = '2014'

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

def extract_location_name(content):
    center = content.find_all('center')[2]
    name = center.strong.font
    return name.text

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
    raw_html = ulib.urlopen(URL).read()
    home = bs.BeautifulSoup(raw_html)

    ports_combo = home.find(attrs={'name': 'cboNomePorto'})
    port_options = ports_combo.find_all(name='option')
    ports = [parse_port_option(o) for o in port_options if not u'até' in o.text]

    months_combo = home.find(attrs={'name': 'cboMes'})
    month_options = months_combo.find_all(name='option')
    months = [m.text for m in month_options]

    for i in xrange(len(ports)):
        port_table = {}
        for index, month in enumerate(months):
            url = URL + ports[i]['id'] + month + YEAR + ".htm"
            raw_content = ulib.urlopen(url).read()
            content = bs.BeautifulSoup(raw_content)

            if index == 0:
               name = extract_location_name(content)
               port_table = {
                   'name': name,
                   'table': {}
               }
               print 'Starting ' + name + '...'

            month_table = parse_month_table(content)
            port_table['table'].update(month_table)

        print port_table['name'] + ' finished!'

