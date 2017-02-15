#!/usr/bin/env python3

import argument_parser
import template_instantiator


if __name__ == '__main__':
    parser = argument_parser.get_argument_parser()
    args = parser.parse_args()
    
    instantiator = template_instantiator.TemplateInstatiator(args)
    
    try:
        instantiator.instantiate()
    except Exception as e:
        print('error: ' + str(e))
