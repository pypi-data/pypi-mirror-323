import math
from dataclasses import dataclass

import dearpygui.dearpygui as dpg
from upgen.model.uphy import DataType, Device, Signal, Slot, Parameter
from upgen.model.uphy import Root as RootModel

datatype_to_min_max = {
    DataType.INT8: (-(2**7), 2**7 - 1),
    DataType.INT16: (-(2**15), 2**15 - 1),
    DataType.INT32: (-(2**31), 2**31 - 1),
    DataType.UINT8: (0, 2**8 - 1),
    DataType.UINT16: (0, 2**16 - 1),
    DataType.UINT32: (0, 2**32 - 1),
    DataType.REAL32: (-math.inf, math.inf),
}


@dataclass
class InputGUI:
    signal: Signal
    value_id: list[str | int]

    def __init__(self, signal: Signal):
        self.signal = signal
        dpg.add_text(signal.name)
        with dpg.group():
            self.value_id = [
                dpg.add_text("N/A") for _ in range(signal.array_length or 1)
            ]

    def update(self, value: list[int | float] | None):
        if value is None:
            for ix in range(self.signal.array_length or 1):
                dpg.set_value(self.value_id[ix], "N/A")
        else:
            for ix in range(self.signal.array_length or 1):
                dpg.set_value(self.value_id[ix], value[ix])


@dataclass
class OutputGUI:
    signal: Signal
    value_id: list[str | int]
    value: list[int] | None = None

    def __init__(self, signal: Signal):
        self.signal = signal
        self.value = [0] * (signal.array_length or 1)
        dpg.add_text(signal.name)
        min, max = datatype_to_min_max[signal.datatype]
        with dpg.group():
            self.value_id = [
                dpg.add_input_int(
                    width=100,
                    callback=lambda sender, app_data, user_data: self.callback(
                        ix, app_data
                    ),
                    min_value=min,
                    max_value=max,
                )
                for ix in range(signal.array_length or 1)
            ]

    def callback(self, ix: int, value: int):
        self.value[ix] = value


class ParamGUI:
    def __init__(self, signal: Parameter):
        self.signal = signal


@dataclass
class SlotGUI:
    inputs: dict[str, InputGUI]
    outputs: dict[str, OutputGUI]
    params: dict[str, ParamGUI]


@dataclass
class DeviceGUI:
    widget: int | str
    slots: dict[str, SlotGUI]
    status_id: str | int

    def update_status(self, status: str):
        dpg.set_value(self.status_id, status)

    def close(self):
        dpg.delete_item(self.widget)


def add_device(model: RootModel, device: Device, suffix: str) -> DeviceGUI:
    width = 300
    windows = dpg.get_windows()
    for ix, window in enumerate(windows):
        dpg.set_item_pos(window, [ix * width, 0])
    ix = len(windows)

    with dpg.window(
        width=width,
        pos=[ix * width, 0],
        autosize=True,
        label=f"{device.name} - {suffix}",
    ) as window:
        with dpg.group(horizontal=True):
            dpg.add_text("Status")
            status_id = dpg.add_text()

        slot_guis = {}
        for slot in device.slots:
            with dpg.child_window(auto_resize_y=True):
                slot_gui = _add_slot(model, slot)
                slot_guis[slot.name] = slot_gui

    return DeviceGUI(window, slot_guis, status_id)


def _add_slot(model: RootModel, slot: Slot):
    module = model.get_module(slot.module)
    dpg.add_text(f"{slot.name}")

    dpg.add_separator()

    with dpg.group(indent=10), dpg.table(label=slot.name, header_row=False):
        dpg.add_table_column()
        dpg.add_table_column()

        inputs: dict[str, InputGUI] = {}
        for signal in module.inputs:
            with dpg.table_row():
                inputs[signal.id] = InputGUI(signal)

        outputs: dict[str, OutputGUI] = {}
        for signal in module.outputs:
            with dpg.table_row():
                outputs[signal.id] = OutputGUI(signal)

        params: dict[str, ParamGUI] = {}
        for signal in module.parameters:
            with dpg.table_row():
                params[signal.id] = ParamGUI(signal)

    return SlotGUI(inputs=inputs, outputs=outputs, params=params)


def setup():
    dpg.create_context()
    dpg.create_viewport(title="U-Phy Controller", width=800)
    dpg.setup_dearpygui()


def run():
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
