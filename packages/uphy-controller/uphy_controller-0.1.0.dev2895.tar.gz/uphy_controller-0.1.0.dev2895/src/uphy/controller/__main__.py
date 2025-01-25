import logging
from functools import partial
from pathlib import Path
from threading import Event, Thread
from typing import Annotated
from rich.table import Table
from rich import print

from typer import Option, Typer, BadParameter
from upgen.model.uphy import Root as RootModel

from . import Target, gui, modbus

LOG = logging.getLogger(__name__)

app = Typer(
    pretty_exceptions_enable=False,
    no_args_is_help=True,
    name="controller",
    help="Run a demo modbus controller based on a model",
)


@staticmethod
def parse_target(value: str):
    values = value.split(":")
    if len(values) != 3:
        raise BadParameter(f"Expected uuid:host:port, got {value}")

    return Target(*value.split(":"))


@app.command(name="modbus")
def modbus_tcp(
    model: Annotated[list[Path], Option()],
    target: Annotated[
        list[Target] | None,
        Option(
            parser=parse_target,
            metavar="ID:HOST:PORT",
            help="Targets to connect controller to, where ID is a device uuid or name, HOST is hostname to connect to and PORT is the port the modbus-tcp server is listening on.",
        ),
    ] = None,
):
    """Run controller against a set of fixed uphy devices."""
    models = [RootModel.parse_file(file) for file in model]

    devices_by_id = {
        str(device.id): (root, device) for root in models for device in root.devices
    }

    devices_by_name = {
        device.name: (root, device) for root in models for device in root.devices
    }

    if target is None:
        table = Table(title="Available devices")
        table.add_column("ID")
        table.add_column("Name")

        for id, (_, device) in devices_by_id.items():
            table.add_row(id, device.name)

        print(table)
        print()
        print(
            "Please add targets to connect to using the --target ID:HOST:PORT argument."
        )
        print()
        exit(-1)

    gui.setup()

    stop = Event()
    try:
        for target_obj in target:
            root, device = devices_by_id.get(target_obj.id, (None, None))
            if not device:
                root, device = devices_by_name.get(target_obj.id, (None, None))
                if not device:
                    LOG.warning("Unable to find device %s", target_obj.id)
                    continue

            device_gui = gui.add_device(
                root, device, f"{target_obj.host}:{target_obj.port}"
            )

            thread = Thread(
                target=partial(modbus.target_runner, stop, target_obj, device_gui),
                name=device.name,
            )
            thread.start()

        gui.run()
    finally:
        stop.set()


@app.command()
def mdns():
    """Run controller against devices automatically discovered via mdns."""
    from zeroconf import (
        Zeroconf,
        ServiceBrowser,
        ServiceStateChange,
        IPVersion,
        ServiceInfo,
    )
    import requests

    zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
    services = ["_modbus._tcp.local."]

    device_runners: dict[tuple, Event] = {}

    def on_device_added(device_key: tuple, info: ServiceInfo):
        addresses = info.parsed_addresses()
        properties = info.decoded_properties
        model_port = properties.get("model-port")
        model_path = properties.get("model-path")
        device_id = properties.get("device-id")
        if not model_port or not model_path or not device_id:
            LOG.error("Missing model info for %s", info.name)
            return

        device_stop = Event()
        device_runners[device_key] = device_stop

        def _run():
            for address in info.parsed_addresses(IPVersion.V4Only):
                model_url = f"http://{address}:{model_port}{model_path}"
                target_obj = Target(device_id, address, info.port)
                try:
                    model_raw = requests.get(model_url).content
                    break
                except Exception as exception:
                    LOG.debug("Failed to connect to %s:%r", model_url, exception)
                    continue
            else:
                LOG.error("Unable to get model for %s", info.name)
                return


            model = RootModel.parse_raw(model_raw)
            for device in model.devices:
                if str(device.id) == device_id:
                    break
            else:
                LOG.error("Can't find device %s in model", device_id)
                return

            LOG.info("Adding device %s", info.name)
            device_gui = gui.add_device(model, device, address)
            modbus.target_runner(device_stop, target_obj, device_gui)
            device_gui.close()

        thread = Thread(
            target=_run,
        )
        thread.start()

    def on_service_state_change(
        zeroconf: Zeroconf,
        service_type: str,
        name: str,
        state_change: ServiceStateChange,
    ) -> None:
        print(f"Service {name}: {state_change}")

        device_key = (service_type, name)

        if state_change is ServiceStateChange.Added:
            info = zeroconf.get_service_info(service_type, name)
            if info and info.port:
                on_device_added(device_key, info)

        if state_change is ServiceStateChange.Removed:
            device_stop = device_runners.pop(device_key, None)
            if device_stop:
                device_stop.set()

    gui.setup()

    ServiceBrowser(zeroconf, services, handlers=[on_service_state_change])

    gui.run()


if __name__ == "__main__":
    app()
