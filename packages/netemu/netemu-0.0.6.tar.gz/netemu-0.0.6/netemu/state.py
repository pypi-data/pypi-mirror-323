from netemu import core


class State:
    class Node:
        def __init__(self, nid, switch=False):
            self.proc = core.start_node()
            self.nid = nid
            self.switch = switch
            self.connected = []

    def __init__(self):
        self.nodes = {}
        self.last_node = 0
        self.last_switch = 0

    def new_node(self):
        self.last_node += 1

        n = self.Node(f"n{self.last_node}")
        self.nodes[n.nid] = n

        print(f"[{n.proc.pid}] Created node {n.nid}")

        return n.nid

    def new_switch(self):
        self.last_switch += 1

        sw = self.Node(f"sw{self.last_switch}", True)
        self.nodes[sw.nid] = sw

        core.run_in_node(
            sw.proc,
            [
                ["ip", "link", "add", "br0", "type", "bridge"],
                ["ip", "link", "set", "br0", "up"],
            ],
        )

        print(f"[{sw.proc.pid}] Created switch {sw.nid}")

        return sw.nid

    def close_nodes(self):
        for n in self.nodes.values():
            core.stop_node(n.proc)

    def execute(self, nid, cmd, disown=False):
        if nid not in self.nodes:
            print(f"Node {nid} does not exist")
            return

        n = self.nodes[nid]
        core.run_in_node(n.proc, [cmd], disown)

    def connect(self, nid1, nid2):
        if nid1 not in self.nodes:
            print(f"Node {nid1} does not exist")
            return

        if nid2 not in self.nodes:
            print(f"Node {nid2} does not exist")
            return

        n1 = self.nodes[nid1]
        n2 = self.nodes[nid2]

        if n2.nid in n1.connected or n1.nid in n2.connected:
            print("Nodes are already connected")
            return

        n1.connected.append(n2.nid)
        n2.connected.append(n1.nid)

        core.run(
            [
                [
                    "ip",
                    "link",
                    "add",
                    f"veth_{n1.nid}",
                    "type",
                    "veth",
                    "peer",
                    f"veth_{n2.nid}",
                ],
                ["ip", "link", "set", f"veth_{n1.nid}", "netns", str(n2.proc.pid)],
                ["ip", "link", "set", f"veth_{n2.nid}", "netns", str(n1.proc.pid)],
            ]
        )

        core.run_in_node(n1.proc, [["ip", "link", "set", f"veth_{n2.nid}", "up"]])

        core.run_in_node(n2.proc, [["ip", "link", "set", f"veth_{n1.nid}", "up"]])

        if n1.switch:
            core.run_in_node(
                n1.proc, [["ip", "link", "set", f"veth_{n2.nid}", "master", "br0"]]
            )
        if n2.switch:
            core.run_in_node(
                n2.proc, [["ip", "link", "set", f"veth_{n1.nid}", "master", "br0"]]
            )

        print(f"Connected {n1.nid} to {n2.nid}")
