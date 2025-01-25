from .extension import Component, Reference
from .parametric import route

from typing import Any


def component_from_netlist(netlist: dict[str, Any]) -> Component:
    """Create a component from a netlist description.

    Args:
        netlist: Dictionary with the component description. The only
          required key is ``'instances'``, which describes the references to
          all sub-components. See other keys in the example below.

    Examples:
        >>> coupler = parametric.dual_ring_coupler(
        ...     port_spec="Strip",
        ...     coupling_distance=0.6,
        ...     radius=4,
        ... )
        ... bus = parametric.ring_coupler(
        ...     port_spec="Strip",
        ...     coupling_distance=0.6,
        ...     radius=4,
        ...     bus_length=5,
        ... )
        >>> netlist1 = {
        ...     "name": "RING",
        ...     "instances": {"COUPLER": coupler, "BUS_0": bus, "BUS_1": bus},
        ...     "instance_models": [
        ...         ("COUPLER", DirectionalCouplerModel(0.8, -0.5j)),
        ...     ],
        ...     "connections": [
        ...         (("COUPLER", "P0"), ("BUS_0", "P1")),
        ...         (("BUS_1", "P1"), ("COUPLER", "P3")),
        ...     ],
        ...     "ports": [
        ...         ("BUS_0", "P0"),
        ...         ("BUS_0", "P2"),
        ...         ("BUS_1", "P2"),
        ...         ("BUS_1", "P0"),
        ...     ],
        ...     "models": [CircuitModel()],
        ... }
        >>> component1 = component_from_netlist(netlist1)

        >>> netlist2 = {
        ...     "instances": [
        ...         coupler,
        ...         {"component": bus, "origin": (0, -12)},
        ...         {"component": bus, "origin": (3, 7), "rotation": 180},
        ...     ],
        ...     "virtual connections": [
        ...         ((0, "P0"), (1, "P1")),
        ...         ((0, "P2"), (1, "P3")),
        ...         ((2, "P3"), (0, "P1")),
        ...     ],
        ...     "routes": [
        ...         ((1, "P2"), (2, "P0"), {"radius": 6}),
        ...         ((2, "P1"), (0, "P3"), pf.parametric.route_s_bend),
        ...     ],
        ...     "ports": [
        ...         (1, "P0", "In"),
        ...         (2, "P2", "Add"),
        ...     ],
        ...     "models": [(pf.CircuitModel(), "Circuit")],
        ... }
        >>> component2 = pf.component_from_netlist(netlist2)

    Notes:
        The value in ``"instances"`` can be a dictionary or a list, in which
        case, index numbers are used in place of the keys. Each value is can
        be a :class:`Component` or another dictionary with keyword arguments
        to create a :class:`Reference`.

        Sub-components can receive extra models from ``"instance_models"``.
        The last added model for each sub-component will be active.

        The ``"connections"`` list specifies connections between instances.
        Each item is of the form ``((key1, port1), (key2, port2))``,
        indicating that the reference ``key1`` must be transformed to have
        its ``port1`` connected to ``port2`` from the reference ``key2``.

        Items in the ``"routes"`` list contain 2 reference ports, similarly
        to ``"connections"``, plus an optional routing function and a
        dictionary of keyword arguments to the function:
        ``((key1, port1), (key2, port2), route_function, kwargs_dict)``. If
        ``route_function`` is not provided, ``parameteric.route`` is used.
    """
    component = Component(netlist.get("name", ""))

    references = {}
    instances = netlist["instances"]
    instances_items = instances.items() if isinstance(instances, dict) else enumerate(instances)
    for key, instance in instances_items:
        reference = Reference(**instance) if isinstance(instance, dict) else Reference(instance)
        component.add(reference)
        references[key] = reference

    # Order matters here
    for connection in netlist.get("connections", ()):
        key1, port1 = connection[0]
        key2, port2 = connection[1]
        references[key1].connect(port1, references[key2][port2])

    for connection in netlist.get("virtual connections", ()):
        key1, port1 = connection[0]
        key2, port2 = connection[1]
        component.add_virtual_connection(references[key1], port1, references[key2], port2)

    for connection in netlist.get("routes", ()):
        key1, port1 = connection[0]
        key2, port2 = connection[1]
        route_fn = connection[2] if len(connection) > 2 and callable(connection[2]) else route
        kwargs = connection[-1] if isinstance(connection[-1], dict) else {}
        component.add(
            route_fn(port1=references[key1][port1], port2=references[key2][port2], **kwargs)
        )

    for item in netlist.get("ports", ()):
        if len(item) == 3:
            key, port, name = item
        else:
            key, port = item
            name = None
        component.add_port(references[key][port], name)

    for item in netlist.get("models", ()):
        if isinstance(item, tuple):
            model, name = item
        else:
            model = item
            name = None
        component.add_model(model, name)

    for item in netlist.get("instance_models", ()):
        if len(item) == 3:
            key, model, name = item
        else:
            key, model = item
            name = None
        references[key].component.add_model(model, name)

    return component
