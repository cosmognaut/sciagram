import argparse

def raise_power(base: float, power: float) -> float:
    """Raises a given base to a given power"""
    return base**power

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # we will add conflicting options quiet and verbose here; they belong to this group.
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--verbose", action="store_true", help="if you want to enable verbose output")
    group.add_argument("-q", "--quiet", action="store_true", help="if you want to enable quiet output")

    parser.add_argument("x", type=float, help="the base")
    parser.add_argument("y", type=float, help="the exponent")

    args = parser.parse_args()
    user_base = args.x
    user_exp = args.y
    answer = raise_power(user_base, user_exp)
    if args.verbose:
        print(f"Verbose output set to {args.verbose}")
        print(f"{user_base} raised to {user_exp} gives {answer}")
    elif args.quiet:
        print(f"Quiet output set to {args.quiet}")
        print(answer)
    else:
        print(f"Verbose output is set to {args.verbose} and quiet output is set to {args.quiet}")
        print(f"{user_base}**{user_exp} == {answer}")


