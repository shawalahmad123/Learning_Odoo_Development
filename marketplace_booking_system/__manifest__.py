# -*- coding: utf-8 -*-

{
  "name"                 :  "Pandora Market Place Booking & Reservation",
  "summary"              :  """The Odoo Marketplace admin can create booking products such as movie tickets so the customers can schedule their booking and reservation directly from the marketplace website.""",
  "category"             :  "Marketing",
  "version"              :  "1.0.0",
  "author"               :  "Pandoratech L.L.C",
  "license"              :  "Other proprietary",
  "website"              :  "https://pandoratech.ae",
  "depends"              :  [
                             'odoo_marketplace',
                             'website_booking_system',
                            ],
  "data"                 :  [
                            'views/records.xml'
                            ],

  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,

}