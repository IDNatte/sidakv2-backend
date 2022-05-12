def parse(header):
    """
    Authorization header parser,
    returning 'Bearer' and 'token' value if any else return none
    """
    parser = header.split(' ')
    if len(parser) == 2:
        if 'Bearer' in parser:
            return parser[1]
        else:
            return None
    else:
        return None
