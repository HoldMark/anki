import requests
from bs4 import BeautifulSoup
from utils import remove_space_tabs, remove_colon


# отправили запрос

def get_content(word):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"}
    r = requests.get(f'https://dictionary.cambridge.org/dictionary/english/{word}', headers=headers)
    return BeautifulSoup(r.content, 'html.parser')


def get_dict_example(data, word):
    list_examples = data.select('.def-body.ddef_b > .examp.dexamp')

    dict_examples = {}

    if list_examples:

        for num_ex, example in enumerate(list_examples):
            if num_ex == 7:
                break

            # fast and stupid
            css_selectors_extra_info = ('.gram.dgram', '.lu.dlu')
            extra_info = ' ['
            for i in css_selectors_extra_info:
                try:
                    extra_info += example.select_one(i).text
                except Exception:
                    pass
            extra_info += ']'
            if extra_info == ' []':
                extra_info = ''
            only_example = example.select_one('.eg.deg').text
            # TODO remake that
            only_example = only_example.replace(word, f'<span>{word}</span>')

            dict_examples[f'example_{num_ex + 1}'] = only_example + extra_info

    return dict_examples


def get_definition(data, word) -> [dict]:
    list_def_data = data.select('.def-block.ddef_block')

    list_definition = []
    for def_data in list_def_data:
        wd = {}

        def_data_html = def_data.select('.def.ddef_d.db')

        if def_data_html:
            wd['def'] = remove_colon(def_data_html[0].text)
            wd = wd | get_dict_example(def_data, word)

        list_definition.append(wd)

    return list_definition


def get_sense(data, word):
    list_sense_data = data.select('.pr.dsense')

    list_sense = []

    for sense_html in list_sense_data:

        sense_html_data = sense_html.select('.dsense_h > .guideword.dsense_gw')
        list_def_with_ex = get_definition(sense_html, word)

        for def_with_ex in list_def_with_ex:
            wd = {}

            if sense_html_data:
                wd['sense'] = remove_space_tabs(sense_html_data[0].text)
            else:
                wd['sense'] = ''

            wd = wd | def_with_ex
            list_sense.append(wd)

    return list_sense


def get_pos(data, word):
    list_word_pos = data.select('.pr.entry-body__el')
    list_words = []

    for word_pos_item in list_word_pos:
        list_sense = get_sense(word_pos_item, word)

        for sense_def_ex in list_sense:
            wd = {'word': word}

            trans_uk = word_pos_item.select('.uk.dpron-i > .pron.dpron')
            trans_us = word_pos_item.select('.us.dpron-i > .pron.dpron')

            if trans_uk:
                wd['trans'] = trans_uk[0].text
                wd['trans_type'] = '(uk)'
            elif trans_us:
                wd['trans'] = trans_us[0].text
                wd['trans_type'] = '(us)'
            else:
                wd['trans'] = ''
                wd['trans_type'] = ''

            html_data_pos = word_pos_item.select('.pos.dpos')

            if html_data_pos:
                wd['pos'] = html_data_pos[0].text
            else:
                wd['pos'] = ''

            wd = wd | sense_def_ex
            list_words.append(wd)

    return list_words


def parse_word_info(word):
    soup = get_content(word)

    i = soup.select('.pr.dictionary')[0]
    w = get_pos(i, word)
    return w
