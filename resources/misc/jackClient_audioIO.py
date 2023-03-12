#!/usr/bin/env python3

import jack
import threading
import numpy # This is needed for called library!

client = jack.Client("MyDemo")

if client.status.server_started:
    print("JACK server started")
if client.status.name_not_unique:
    print("unique name {0!r} assigned".format(client.name))

event = threading.Event()

@client.set_process_callback
def process(frames):
    assert len(client.inports) == len(client.outports)
    assert frames == client.blocksize
    for i, o in zip(client.inports, client.outports):
        dataCurrent = i.get_array()

        # TODO: Process dataCurrent

        o.get_array()[:] = dataCurrent

@client.set_shutdown_callback
def shutdown(status, reason):
    print("JACK shutdown!")
    print("status:", status)
    print("reason:", reason)
    event.set()

for number in [1]:
    client.inports.register("input_{0}".format(number))
    client.outports.register("output_{0}".format(number))

with client:
    print("Press Ctrl+C to stop")
    try:
        event.wait()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
# When the above with-statement is left (either because the end of the
# code block is reached, or because an exception was raised inside),
# client.deactivate() and client.close() are called automatically.