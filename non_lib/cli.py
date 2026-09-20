import argparse

def raise_power(base: float, power: float) -> float:
    """Raises a given base to a given power"""
    return base**power

parser = argparse.ArgumentParser()
parser.add_argument("square", help="display the square of a given number", type=int)
# parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true") # store_true means assign the value True to args.verbose, not specifying this option implies False. Thus, this is an OPTIONAL argument.

parser.add_argument("-v", "--verbosity", help="increase output verbosity", type=int, choices=[0, 1, 2], default=0) # note that you cannot use store_true when you're making the option have some type such as int. store_true only means "if this flag was supplied, store the value true in args.verbose"

args = parser.parse_args()
if args.verbosity == 2:
    print(f"you set the verbosity level to {args.verbosity}")
    print(f"the square of the given number is {args.square**2}")
elif args.verbosity == 1:
    print(f"you set the verbosity level to {args.verbosity}")
    print(f"{args.square}^2 == {args.square**2}")
else:
    print(args.square**2)
