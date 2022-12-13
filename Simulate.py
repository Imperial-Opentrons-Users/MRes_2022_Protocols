from opentrons.simulate import simulate, format_runlog

# read the file - include file path
protocol_file = open("c:/users/geoff/github/filename.py")

# simulate() the protocol, keeping the runlog
runlog, _bundle = simulate(protocol_file, "c:/users/geoff/github/filename.py")

# print the runlog
print('\n', format_runlog(runlog), '\n', sep = '')