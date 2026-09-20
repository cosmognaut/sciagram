import argparse

def raise_power(base: float, power: float) -> float:
    """Raises a given base to a given power"""
    return base**power

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # we will add conflicting options quiet and verbose here
    parser.add_argument("x", type=float, help="the base")
    parser.add_argument("y", type=float, help="the exponent")
    parser.add_argument("-v", "--verbosity", type=int, choices=[0, 1, 2], default=0, help="the verbosity level you want the program to output at")
    args = parser.parse_args()
    user_base = args.x
    user_exp = args.y
    answer = raise_power(user_base, user_exp)
    if args.verbosity == 2:
        print(f"You have set the verbosity level to {args.verbosity}")
        print(f"{user_base} raised to {user_exp} gives {answer}")
    elif args.verbosity == 1:
        print(f"You have set the verbosity level to {args.verbosity}")
        print(f"{user_base}**{user_exp} == {answer}")
    else:
        print(f"You have not set the verbosity level to anything, so it's at {args.verbosity}")
        print(answer)


