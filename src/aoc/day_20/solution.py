#!/usr/bin/env python

# # #
#
#

import os
import re
from typing import List, Literal

from aoc import utils
from aoc.utils import dprint

DAY = '20'
DEBUG = int(os.environ.get('DEBUG', 0))


def solve_part_1(fname: str):
    res = solve_p1(load_input(fname))
    print(res)


def solve_part_2(fname: str):
    res = solve_p2(load_input(fname))
    print(res)


def load_input(fname: str = None):
    """
    Load input from given file (or input.txt by default)
    using task specific parser/line_parser
    """
    return utils.load_input(fname, parser=parse)


class CommunicationModule:
    LOW = False
    HIGH = True

    # Looks like a bad idea: when more that one circut is in work,
    # the numbers add up. Make sure CommunicationMofule.reset() is called.
    emmitted_signal_counts = {LOW: 0, HIGH: 0}

    @classmethod
    def reset(cls):
        cls.emmitted_signal_counts = {cls.LOW: 0, cls.HIGH: 0}

    @staticmethod
    def from_spec(spec: str):
        if spec.startswith('%'):
            return FlipFlop(spec[1:])
        if spec.startswith('&'):
            return Conjunction(spec[1:])
        if spec == "broadcaster":
            return CommunicationModule(spec)
        if spec == "button":
            return Button("button")
        if spec[0].isalpha():
            # An untyped module is assumed to be a testing module.
            # ex: "output", "rx"
            return TestingModule(spec)
        raise ValueError(f"Unrecognized device spec '{spec}'")

    def __init__(self, name: str = None):
        self.name: str = name
        self._source_devices: List['CommunicationModule'] = []
        self._destination_devices: List['CommunicationModule'] = []
        # the buffer of input signals. different types of modules treat
        # use it differently
        self.input_signals: List[bool] = []
        # what this device computed and can send to destination devices
        self.signal: bool = self.LOW

    def __repr__(self):
        return "<{}: name={} signal={} num_sources={} num_destinations={}>".format(
            self.__class__.__name__,
            self.name,
            self.signal_,
            len(self._source_devices),
            len(self._destination_devices)
        )

    def add_destination_device(self, device: 'CommunicationModule'):
        if device not in self._destination_devices:
            self._destination_devices.append(device)
        if self not in device._source_devices:
            device._source_devices.append(self)

    def destination_devices(self):
        return self._destination_devices

    @property
    def signal_(self) -> str:
        """Produce human readable form of signal: low or high"""
        if self.signal is True:
            return "high"
        if self.signal is False:
            return "low"
        return "UNK"

    def receive(self, signal: bool, source: 'CommunicationModule'):
        """Write signal to the input buffer of the current device.
        This is triggered by the source device.
        Some devices need to know the source from which the signal comes.
        """
        self.input_signals.append(signal)

    def send(self):
        """Propagate signal to all downstream devices."""
        for device in self._destination_devices:
            dprint(f"{self.name} -{self.signal_}-> {device.name}")
            device.receive(self.signal, self)
            self.emmitted_signal_counts[self.signal] += 1

    def read(self) -> bool:
        """Read the input buffer"""
        return self.input_signals.pop(0)

    def actuate(self) -> bool:
        """Update self.signal, if necessary in response to the signals from
        the source devices, and send it to destination devices.

        Returns:
        True is anything happened
        False is nothing happened

        This method should typically redefined in specific subclasses to
        provide its own computation logic.
        """
        dprint("Actuating", repr(self))
        self.signal = self.read()
        self.send()
        return True


class Button(CommunicationModule):
    """The button emits LOW pulse"""

    def actuate(self) -> Literal[True]:
        self.signal = self.LOW  # just in case
        self.send()
        return True


class FlipFlop(CommunicationModule):
    """
    Flip-flop modules (prefix %) are either on or off; they are initially off.

    If a flip-flop module receives a high pulse, it is ignored and nothing
    happens. However, if a flip-flop module receives a low pulse, it flips
    between on and off.
    If it was off, it turns on and sends a high pulse. If it was on, it
    turns off and sends a low pulse.
    """

    # def __init__(self, *args):
    #     super().__init__(*args)
    #     # we dont need a dedicated variable to storing the state, because
    #     # the state correlates with the signal the device emits. We can
    #     # say the device changes its state in response to the input signal
    #     # and emits its new state.
    #     # self.state = False  # off state

    def actuate(self) -> bool:
        dprint("Actuating", repr(self))
        # dprint(f"..inputs: {self.input_signals}")
        if not self.input_signals:
            return False
        signal = self.read()
        if signal:
            dprint("..nothing happens")
            return False
        self.signal = not(self.signal)
        self.send()
        return True

    def __repr__(self):
        return "<{}: name={} signal={} state={} num_sources={} num_destinations={}>".format(
            self.__class__.__name__,
            self.name,
            self.signal_,
            self.signal,
            len(self._source_devices),
            len(self._destination_devices)
        )


class Conjunction(CommunicationModule):
    """
    Conjunction modules (prefix &) remember the type of the most recent pulse
    received from each of their connected input modules;
    they initially default to remembering a low pulse for each input.

    When a pulse is received, the conjunction module first updates its memory
    for that input.

    Then, if it remembers high pulses for all inputs, it sends a low pulse;
    otherwise, it sends a high pulse.
    """

    def receive(self, signal, source):
        """Write signal to the input buffer of the current device.
        This is normally triggered by the source device.

        ConjunctionModule keeps track the source devices from which the
        signal comes.
        """

        # initialize input buffer, it should be of the same length as the
        # number of source devices. It could not be done in __init__ because
        # the number of source devices was not know at that point. Maybe
        # a better idea would be to have something like `add_source_device()`
        # and perform (update) initialization there for any added device.
        if not self.input_signals:
            self.input_signals = [False] * len(self._source_devices)

        for idx, srcdev in enumerate(self._source_devices):
            dprint(f"Receiving {signal} from {source.name}. From {srcdev}?")
            if srcdev.name == source.name:
                self.input_signals[idx] = signal

    def read(self) -> List[bool]:
        return self.input_signals

    def actuate(self) -> Literal[True]:
        dprint("Actuating", repr(self))
        self.signal = not(all(self.read()))
        self.send()
        return True

    def __repr__(self):
        return "<{}: name={} inputs={}>".format(
            self.__class__.__name__, self.name,
            self.input_signals
        )


class TestingModule(CommunicationModule):

    def actuate(self):
        dprint("Actuating", repr(self))
        signal = self.read()

        # a failed attempt to solve part 2
        if self.name == 'rx':
            # print(repr(self), self.signal, signal)
            self.signal = signal
            #print(self.emmitted_signal_counts)
            if self.signal is False:
                raise RuntimeError("Time to stop")

        # if self._destinations:
        #     raise NotImplementedError(
        #         "TestingModule cannot send signal to downstream devices")
        # if len(self._source_devices) != 1:
        #     raise NotImplementedError(
        #         f"Input devices to TestingModule {len(self._source_devices)}")

# class RXModule(CommunicationModule):
#
#     def actuate(self):
#         signal = self.read()
#         # what is there are several inputs devices?
#         print(f"Input devices to RX: {len(self._sources)}")
#         print(self.emmitted_signal_counts)
#         raise RuntimeError("Done")


def parse(lines: List[str]) -> Button:
    """Build a directed graph of devices, Button being the root node
    of the graph.

    Returns
      Button device
    """
    devices = {}
    semi_parsed_lines = []
    for line in lines:
        fields = re.split(r'[,\s]+', line.replace('->', ''))
        dev = CommunicationModule.from_spec(fields.pop(0))
        devices[dev.name] = dev
        semi_parsed_lines.append((dev, fields))

    #print(devices)
    for src_dev, dest_devices in semi_parsed_lines:
        for dest in dest_devices:
            # if a device was never seen on LHS, e.g. `output`, `rx`
            if dest not in devices:
                dev = CommunicationModule.from_spec(dest)
                devices[dev.name] = dev
            src_dev.add_destination_device(devices[dest])

    button = CommunicationModule.from_spec("button")
    button.add_destination_device(devices["broadcaster"])

    return button


def actuate(device: CommunicationModule):
    """Propagate a signal in the network in BFS fashion"""
    queue = [device]
    while queue:
        dprint(f"\nNumber of devices in the queue: {len(queue)}")
        # This internal loop is not necessary, the external while-loop
        # alone is sufficient. However, it is kept here for readability:
        # the external loop is clock ticks, the internal loop is what
        # happens in the devices at this clock tick.
        for _ in range(len(queue)):
            device = queue.pop(0)
            if device.actuate():
                queue.extend(device.destination_devices())


def solve_p1(button: CommunicationModule) -> int:
    """Solution to the 1st part of the challenge"""
    CommunicationModule.reset()
    n = 1000
    for _ in range(n):
        actuate(button)
    signal_counts = CommunicationModule.emmitted_signal_counts
    dprint(signal_counts)
    return utils.prod(signal_counts.values())


def solve_p2(button: CommunicationModule) -> int:
    """Solution to the 2nd part of the challenge"""
    return 0


def solve_p2_v1(button: CommunicationModule) -> int:
    """Solution to the 2nd part of the challenge

    Brute force solution does not work, it does not converge.
    Either there is a bug in my implementation or the solution should
    be based on a different idea.
    """
    CommunicationModule.reset()
    cnt = 0
    while True:
        cnt += 1
        if cnt % 10000 == 0:
            print(f"Button pressed {cnt} times")
        actuate(button)
    print(f"Button pressed {cnt} times")
    return cnt


tests = [
    # part 2 not applicable to these tests because they do not contain rx
    # module
    (load_input('test.1.txt'), 8000*4000, None),
    (load_input('test.2.txt'), 4250*2750, None),
]


reals = [
    (load_input(), 19181*47932, None)
]

if __name__ == '__main__':
    utils.run_tests(DAY, tests, solve_p1, solve_p2)
    utils.run_real(DAY, reals, solve_p1, solve_p2)
