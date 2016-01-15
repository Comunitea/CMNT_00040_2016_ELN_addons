# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2004-TODAY Pexego Sistemas Informáticos. All Rights Reserved
#    $Omar Castiñeira Saavedra$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import logging
import logging.handlers
import sys

DEBUG_LOG_FILENAME = '/var/log/openerp/openerp-edi.log'

class logger(object):
    
    def __init__(self, module):
        # set up formatting
        formatter = logging.Formatter(u'[%(asctime)s] %(levelname)s ' + module + u': %(message)s')
        self.module = module
        # set up logging to a file for all levels DEBUG and higher
        fh = logging.handlers.RotatingFileHandler(DEBUG_LOG_FILENAME, maxBytes=100000000)
        fh.setFormatter(formatter)
        self.mylogger = logging.getLogger(self.module)
        self.mylogger.addHandler(fh)
                
    # create shortcut functions
    def debug(self,message):
        self.mylogger.setLevel(logging.DEBUG)
        self.mylogger.debug(message)
        
    def info(self,message):
        self.mylogger.setLevel(logging.INFO)
        self.mylogger.info(message)    
    
    def warning(self,message):
        self.mylogger.setLevel(logging.WARNING)
        self.mylogger.warning(message)   
    
    def error(self,message):
        self.mylogger.setLevel(logging.ERROR)
        self.mylogger.error(message) 
        
    def critical(self,message):
        self.mylogger.setLevel(logging.CRITICAL)
        self.mylogger.critical(message) 
    
