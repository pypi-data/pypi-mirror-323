from xml.etree import cElementTree as ElementTree

def __xlist(list):
    result = []
    for element in list:
        if element:
            # treat like dict
            if len(element) == 1 or element[0].tag != element[1].tag:
                result.append(__xdict(element))
            # treat like list
            elif element[0].tag == element[1].tag:
                result.append(__xlist(element))
        elif element.text:
            text = element.text.strip()
            if text:
                result.append(text)
    return result

def __xdict(root):
    '''
    Example usage:

    >>> tree = ElementTree.parse('your_file.xml')
    >>> root = tree.getroot()
    >>> xmldict = XmlDictConfig(root)

    Or, if you want to use an XML string:

    >>> root = ElementTree.XML(xml_string)
    >>> xmldict = XmlDictConfig(root)

    And then use xmldict for what it is... a dict.
    '''
    result = {}
    parent_element = root
    print("running __xdict(root)")
    print(''.join(['root argument is of type ', str(type(root))]))
    print(''.join(['root argument value is:']) )
    print(str(root))
    if parent_element.items():
        result.update(dict(parent_element.items()))
    for element in parent_element:
        if element:
            d = {}
            # treat like dict - we assume that if the first two tags
            # in a series are different, then they are all different.
            if len(element) == 1 or element[0].tag != element[1].tag:
                d = __xdict(element)
            # treat like list - we assume that if the first two tags
            # in a series are the same, then the rest are the same.
            else:
                # here, we put the list in dictionary; the key is the
                # tag name the list elements all share in common, and
                # the value is the list itself 
                d = {element[0].tag: __xlist(element)}
            # if the tag has attributes, add those to the dict
            if element.items():
                d.update(dict(element.items()))
            result.update({element.tag: d})
        # this assumes that if you've got an attribute in a tag,
        # you won't be having any text. This may or may not be a 
        # good idea -- time will tell. It works for the way we are
        # currently doing XML configuration files...
        elif element.items():
            result.update({element.tag: dict(element.items())})
        # finally, if there are no child tags and no attributes, extract
        # the text
        else:
            result.update({element.tag: element.text})
    return result

def from_file(path):
    tree = ElementTree.parse(path)
    root = tree.getroot()
    return __xdict(root)

def from_string(xml_string):
    root = ElementTree.XML(xml_string)
    return __xdict(root)