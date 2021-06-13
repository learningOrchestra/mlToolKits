from typing import Optional

class Utils:

    @staticmethod
    def try_get_args(args: dict, args_list: []) -> Optional[str]:
        for arg in args_list:
            observer_index = args.get(arg)
            if (observer_index is not None):
                return observer_index

        return None