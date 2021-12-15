#!/usr/bin/env python3
from bs4 import BeautifulSoup as Soup, NavigableString
from enum import Enum
import requests
import json
import re

class ScanType(Enum):
    HEADER = 0
    OBJ_FUN = 1
    ENUM = 2


def main():
    BOT_API_DOCS_URL = 'https://core.telegram.org/bots/api#getting-updates'

    doc_page = requests.get(BOT_API_DOCS_URL)
    soup = Soup(doc_page.text, features='lxml')

    enums = []
    objs = []
    funs = []
    ret_map = {}

    for h4 in soup.find_all('h4'):
        table = find_next_table(h4)
        if table:
            entry_name = h4.get_text()
            res_type, desc, res = table

            if res_type == ScanType.OBJ_FUN:
                entry_type, entry_attr = res

                if entry_type == 'Object':
                    objs.append({'name': entry_name, 'description': desc, 'fields': entry_attr})
                else:
                    raw_ret = get_return_type(desc)

                    if raw_ret not in ret_map:
                        print(f'Return type: {raw_ret}')
                        adjust = input('> ')
                        ret_map[raw_ret] = adjust if adjust else raw_ret

                    ret = ret_map[raw_ret]
                    funs.append({'name': entry_name, 'description': desc, 'params': entry_attr, 'return': ret})

            elif res_type == ScanType.ENUM:
                enums.append({'name': entry_name, 'variants': res})

            else:
                print('<<<<<<<<<<', entry_name, table)

        else:
            print('>>>>>>>>>>>>>>', h4.get_text())

    result = {'enums': enums, 'objects': objs, 'functions': funs}
    print(f'Enums: {len(enums)}')
    print(f'Objec: {len(objs)}')
    print(f'Funct: {len(funs)}')
    with open('api2.json', 'w') as f:
        json.dump(result, f, indent=2)
    return result


def get_text(elem):
    if isinstance(elem, NavigableString):
        return str(elem)
    else:
        return elem.get_text()


def find_next(elem, tag, end='h4'):
    for sibling in elem.next_siblings:
        if sibling.name == tag:
            return sibling

        if sibling.name == end:
            return


def is_enum(text):
    needles = (
        r'the following \d+ ',
        'should be one of',
    )

    return any(re.search(n, text) for n in needles)


def get_return_type(desc):
    r = r'(?: On success, (?:the sent )?| An )([^\.]+) is returned\.|(?: On success, returns)([^\.]+)|Returns (?:the |a )?([\w ]+?)(?: on success| object)?\.'
    res = re.search(r, desc, flags=re.I)

    print(res, desc)
    if not res:
        raise Exception('Could not find return type in description')

    if sum(e == None for e in res.groups()) != 2:
        raise Exception('Exactly one return regex should match')

    ret = next(e for e in res.groups() if e).strip()
    ret = re.sub(r'^an? ', '', ret)
    ret = re.sub(r' objects?$', '', ret)
    return ret


def get_enum_varients(elem):
    ul = find_next(elem, 'ul')
    return [get_text(c) for c in ul.find_all('li')]


def extract_table_info(table):
    rows = table.find_all('tr')
    if rows[0].find_all('th')[0].get_text() == 'Parameter':
        table_type = 'Function'
    else:
        table_type = 'Object'

    raw_fields = (tuple(map(get_text, r.find_all('td'))) for r in rows[1:])
    fields = []

    if table_type == 'Function':
        REQUIRED_MAP = {
            'Yes': True,
            'Optional': False
        }

        for f,t,r,d in raw_fields:
            fields.append({
                'field': f,
                'type': t,
                'required': REQUIRED_MAP[r],
                'description': d
            })

    else:
        for f,t,d in raw_fields:
            r = True
            if d[:10] == 'Optional. ':
                r = False
                d = d[10:]

            fields.append({
                'field': f,
                'type': t,
                'required': r,
                'description': d
            })

    return table_type, fields


# Returns (code, data)
# where code is 0, 1, 2
# 0: data will be None, there are no args for this thing
# 1: data will be a found table
# 2: data will be a list of other variants of this enum
# if nothing returned, no table found
def find_next_table(h4_elem):
    desc = []
    empty_obj = False
    empty_func = False

    for sibling in h4_elem.next_siblings:
        text = get_text(sibling)

        if sibling.name == 'p':
            desc.append(text)

        if sibling.name == 'h4':
            if empty_obj:
                return (ScanType.OBJ_FUN, '\n'.join(desc), ('Object', []))

            if empty_func:
                return (ScanType.OBJ_FUN, '\n'.join(desc), ('Function', []))

            print('\n'.join(desc))
            print()
            return None

        if 'Requires no parameters' in text:
            empty_func = True

        if 'holds no information' in text:
            empty_obj = True

        if sibling.name == 'table':
            return (ScanType.OBJ_FUN, '\n'.join(desc), extract_table_info(sibling))

        if is_enum(text):
            return (ScanType.ENUM, '\n'.join(desc), get_enum_varients(sibling))

if __name__ == '__main__':
    res = main()
