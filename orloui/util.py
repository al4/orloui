from __future__ import print_function

__author__ = 'alforbes'


def calculate_offset(page_number, per_page):
    """
    Calculate the offset from the page number and number per page

    :param page_number: The page we're requesting
    :param per_page: Number per page
    :return int: offset
    """
    if page_number < 1:
        return 0
    else:
        offset = (page_number - 1) * per_page
    return offset


