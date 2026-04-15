def parse_msg(msg: str):
    vars_list = []
    commands = []

    for i in msg.split("; "):
        if i.strip() == "":
            continue
        if "=" in i:
            vars_list.append(i)
        else:
            commands.append(i)

    return vars_list, commands
