import netemu.command as cmd


def start():
    while True:
        try:
            line = input("> ").split()
        except (EOFError, KeyboardInterrupt):
            print()
            cmd.ExitCommand().run()
            break

        if len(line) == 0:
            continue

        if line[0] in ("exit",):
            cmd.ExitCommand().run()
            break
        elif line[0] in ("new", "n"):
            cmd.NewCommand(line[1:]).run()
        else:
            cmd.NodeCommand(line[0], line[1:]).run()
