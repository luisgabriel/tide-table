#!/usr/bin/python2
# -*- coding: utf-8 -*-

import urllib2 as ulib
import bs4 as bs

URL = 'http://www.mar.mil.br/dhn/chm/tabuas/'
YEAR = '2013'

def parse_port_option(option):
    return {
        'id': option.attrs['value'],
        'name': option.text.strip()
    }

def parse_month_table_header(content):
    pass

def parse_month_table():
    pass

if __name__ == '__main__':
    raw_html = ulib.urlopen(URL).read()
    home = bs.BeautifulSoup(raw_html)

    ports_combo = home.find(attrs={'name': 'cboNomePorto'})
    port_options = ports_combo.find_all(name='option')
    ports = [parse_port_option(o) for o in port_options if not u'Até' in o.text]

    months_combo = home.find(attrs={'name': 'cboMes'})
    month_options = months_combo.find_all(name='option')
    months = [m.text for m in month_options]

    for i in xrange(len(ports)):
        for month in months:
            url = URL + ports[i]['id'] + month + YEAR + ".htm"
            #content = ulib.url
            print url

