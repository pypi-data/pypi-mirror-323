# -*- coding: UTF-8 -*-
# Copyright 2013-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lxml import etree
from lxml import isoschematron


def validate_xml(xmlfile, xsdfile):
    """

    Validate the given :attr:`xmlfile` using the given :attr:`xsdfile`.

    When :attr:`xsdfile` ends with :file:`.xsd`, the generated :attr:`xmlfile`
    file is validated using :class:`lxml.etree.XMLSchema`. When it ends with
    :file:`.sch`, the generated :attr:`xmlfile` file is validated using
    :class:`lxml.isoschematron.Schematron`.


    """
    doc = etree.parse(xmlfile)
    if xsdfile.endswith(".xsd"):
        # xsd = etree.XMLSchema(etree.parse(xsdfile))
        xsd = etree.XMLSchema(file=xsdfile)
        xsd.assertValid(doc)
    elif xsdfile.endswith(".sch"):
        # schematron = isoschematron.Schematron(etree.parse(xsdfile))
        schematron = isoschematron.Schematron(file=xsdfile)
        schematron.assertValid(doc)
