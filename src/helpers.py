def get_lines(titlefile):
    try:
        with open(titlefile, "r", encoding='utf-8') as f:
            lines = f.readlines() 
        return lines
    except:
        return []