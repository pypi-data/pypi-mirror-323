# -*- coding: UTF-8 -*-
# Copyright 2016-2024 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import re
from os.path import join, dirname

from django.conf import settings

from lino.api import dd, rt, _
from lino.modlib.printing.actions import WriteXmlAction
from lino_xl.lib.finan.validate import validate_pain001


class WriteElectronicInvoice(WriteXmlAction):
    # Instantiated as lino.xl.lib.finan.PaymentOrder.write_xml

    tplname = "peppol-ubl"
    # xsd_file = join(dirname(__file__), 'XSD', 'PEPPOL-EN16931-UBL.sch')
    # lxml.etree.SchematronParseError: invalid schematron schema: <string>:501:0:ERROR:RELAXNGV:RELAXNG_ERR_ELEMNAME: Expecting element pattern, got let

    def get_printable_context(self, bm, obj, ar):
        context = super().get_printable_context(bm, obj, ar)

        if not obj.must_send_einvoice():
            raise Warning(_("No e-invoice to generate for {}".format(obj)))

        sc = settings.SITE.get_config_value('site_company')
        if not sc:
            raise Warning(_("You must specify a site owner"))
        context.update(site_company=sc)

        country2scheme = dict(BE="9925", EE="9931", DE="9930", LU="9938",
        NL="9944")

        # country2scheme codes are taken from EAS code list
        # https://ec.europa.eu/digital-building-blocks/sites/display/DIGITAL/Registry+of+supporting+artefacts+to+implement+EN16931

        # schemeID:
        # 9925 : Belgium VAT number
        # 0208 : Numero d'entreprise / ondernemingsnummer / Unternehmensnummer

        def func(country):
            return country2scheme[country.isocode]
        context.update(country2scheme=func)

        # if not sc.vat_id:
        #     raise Warning(_("Site owner has no national ID"))
        # our_id = re.sub('[^0-9]', '', sc.vat_id[3:])
        # context.update(our_name=str(sc))
        # context.update(our_id=our_id)
        # raise Exception(str(context))
        return context

    # def before_build(self, bm, elem):
    #     # if not elem.execution_date:
    #     #     raise Warning(_("You must specify an execution date"))
    #     acc = elem.journal.sepa_account
    #     if not acc:
    #         raise Warning(
    #             _("Journal {} has no SEPA account").format(elem.journal))
    #     if not acc.bic:
    #         raise Warning(
    #             _("SEPA account for journal {} has no BIC").format(
    #                 elem.journal))
    #
    #     return super(WritePaymentsInitiation, self).before_build(bm, elem)

    # def validate_result_file(self, filename):
    #     try:
    #         validate_pain001(filename)
    #     except Exception as e:
    #         raise Warning(_(
    #             "Oops, the generated XML file {} is invalid: {}").format(
    #                 filename, e))
