import time
import os
import logging
import re
import urllib.request
import xml.etree.ElementTree as et

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

PY_DOCS_URL = 'https://docs.python.org/3/library/{module}.html'


def get_attr_docstr(html, module, attr):
    """Takes in html string and searches for the attr"""
    html = re.subn('&[a-zA-Z_0-9]{1,7};', '', html)[0]
    tree = et.fromstring(html)
    try:
        dl = tree.find(f'.//*[@id="{module}.{attr}"]/..')
        elem = dl[1].findall('./{http://www.w3.org/1999/xhtml}p')[0]
        text_list = []
        for text in elem.itertext():
            text_list.append(text)
        return ''.join(text_list)
    except Exception as e:
        return f'Docs not found for {module}.{attr}'


def get_docs_html(module):
    """Calls the pydocs website to get the raw html"""
    url = PY_DOCS_URL.format(module=module)
    html = []
    with urllib.request.urlopen(url) as f:
        line = True
        while line:
            line = f.readline().decode('utf-8')
            html.append(line)
    return ''.join(html)


def get_docs(module, attr):
    """Gets the docs for the module/attr. Returns the doc str for the module/attr formatted"""
    html = get_docs_html(module)
    doc_text = get_attr_docstr(html, module, attr)
    return doc_text


def parse_module_slot(module_slot):
    """Parses a module slot. Return the module and and attr to search for"""
    if not module_slot:
        return (None, None)
    slot_split = module_slot.split('.')
    if len(slot_split) > 2:
        module = '.'.join(slot_split[0:-1])
        attr = slot_split[-1]
    elif len(slot_split) == 2:
        module = slot_split[0]
        attr = slot_split[1]
    else:
        return (None, None)
    return module, attr


# --- Intents ---

def GetDocs(intent_request):
    """
    Handles looking up the docs for the module passed in.
    :param intent_request:  the intent sent from the lex service
    :return: lex response dict
    """
    module_slot = intent_request['currentIntent']['slots']['module']
    content = get_docs(*parse_module_slot(module_slot))
    return {
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': 'Fulfilled',
            "message": {
              'contentType': 'PlainText',
              'content': content
            }
        }
    }


def get_intent_handler(intent_name):
    """
    Gets the intent handler by using the intent_name.
    Looks in the globals and locals for a function matching the intent_name exactly
    intent_name is a str
    """
    possibles = globals().copy()
    possibles.update(locals())
    intent_handler = possibles.get(intent_name)
    if not intent_handler:
        raise NotImplementedError('Intent with name ' + intent_name + ' not supported')
    return intent_handler


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']
    intent_handler = get_intent_handler(intent_name)
    return intent_handler(intent_request)


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    os.environ['TZ'] = 'America/Los_Angeles'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)

if __name__ == '__main__':
    pass
    # message = get_docs(*parse_module_slot('sys.argv'))
    # message = get_docs(*parse_module_slot('re.compile'))
    # print(message)
    # s = re.subn('&[a-zA-Z_0-9]{1,7};', '', 'cat&mdash;')
    # s = re.subn('&.*(4);', '', 'cat&masjdfaosdjfoiasjdfdash;')
    # print(s)
