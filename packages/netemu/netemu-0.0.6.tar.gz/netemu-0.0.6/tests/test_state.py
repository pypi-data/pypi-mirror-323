from netemu.state import State
import os
import json


def test_new_node():
    state = State()
    nid = state.new_node()

    assert nid == "n1"
    assert nid in state.nodes

    assert os.path.exists(f"/proc/{state.nodes[nid].proc.pid}")

    parent_userns = os.readlink(f"/proc/{os.getpid()}/ns/user")
    parent_netns = os.readlink(f"/proc/{os.getpid()}/ns/net")
    userns = os.readlink(f"/proc/{state.nodes[nid].proc.pid}/ns/user")
    netns = os.readlink(f"/proc/{state.nodes[nid].proc.pid}/ns/net")

    assert userns == parent_userns
    assert netns != parent_netns

    state.close_nodes()

    assert not os.path.exists(f"/proc/{state.nodes[nid].proc.pid}")


def test_execute_no_node(capfd):
    state = State()

    state.execute("n1", ["sh"])

    assert capfd.readouterr().out == "Node n1 does not exist\n"


def test_execute(capfd):
    state = State()
    nid = state.new_node()

    netns = os.readlink(f"/proc/{state.nodes[nid].proc.pid}/ns/net")

    capfd.readouterr()

    state.execute(nid, ["readlink", "/proc/self/ns/net"])

    assert capfd.readouterr().out == f"{netns}\n"

    state.close_nodes()


def test_connect_no_node(capfd):
    state = State()
    state.new_node()

    capfd.readouterr()

    state.connect("n1", "n2")

    assert capfd.readouterr().out == "Node n2 does not exist\n"

    state.connect("n2", "n1")

    assert capfd.readouterr().out == "Node n2 does not exist\n"

    state.close_nodes()


def test_connect(capfd):
    state = State()
    nid1 = state.new_node()
    nid2 = state.new_node()
    state.connect(nid1, nid2)

    assert nid2 in state.nodes[nid1].connected
    assert nid1 in state.nodes[nid2].connected

    capfd.readouterr()

    state.execute(nid1, ["ip", "-json", "link", "show", "veth_n2"])

    assert json.loads(capfd.readouterr().out)[0]["operstate"] == "UP"

    state.execute(nid2, ["ip", "-json", "link", "show", "veth_n1"])

    assert json.loads(capfd.readouterr().out)[0]["operstate"] == "UP"

    state.connect(nid1, nid2)

    assert capfd.readouterr().out == "Nodes are already connected\n"

    state.close_nodes()


def test_switch(capfd):
    state = State()
    state.new_switch()
    state.new_node()
    state.new_node()

    state.connect("n1", "sw1")
    state.connect("sw1", "n2")

    state.execute("n1", ["ip", "a", "add", "10.0.0.1/24", "dev", "veth_sw1"])
    state.execute("n2", ["ip", "a", "add", "10.0.0.2/24", "dev", "veth_sw1"])

    capfd.readouterr()

    state.execute("n1", ["ping", "-c", "1", "10.0.0.2"])

    assert "1 received" in capfd.readouterr().out

    state.close_nodes()
