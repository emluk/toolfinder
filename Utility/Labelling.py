def insert_newLines(text):
    lines = []
    words = text.split(' ')
    tmp_line = ""
    for word in words:
        w = word.replace("\n", " ")
        if len(tmp_line) < 80:
            tmp_line += f"{w} "
        else:
            lines.append(tmp_line)
            tmp_line = f"{w} "
    lines.append(tmp_line)
    return '\n'.join(lines)