from collections import UserString


class Itemlist(UserString):
    def __init__(self, *args, **kwargs):
        conj = kwargs.get("conjunction", "and")
        oxford_comma = kwargs.get("oxford_comma", False)
        value = f"{', ' if oxford_comma else ' '}{conj} ".join(
            [x for x in [", ".join(args[0][:-1]), args[0][-1]] if x]
        )
        super().__init__(value)
