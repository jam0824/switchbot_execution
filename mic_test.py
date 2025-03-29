import sys
import mic

def usage():
    print("Usage: python3 mic_test.py [single|term]")

if len(sys.argv) != 2:
    usage()
    sys.exit(1)

m = mic.Mic()
arg = sys.argv[1].lower()

if arg == "single":
    m.single_trigger_loop()
elif arg == "term":
    m.term_trigger_loop()
else:
    usage()