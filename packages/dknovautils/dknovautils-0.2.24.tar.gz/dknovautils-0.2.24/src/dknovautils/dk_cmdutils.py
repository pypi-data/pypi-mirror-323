from __future__ import annotations


from dknovautils import commons, iprint_debug, iprint_warn, AT  # type:ignore
from dknovautils.commons import *  # type: ignore

from enum import Enum, auto, unique

import sys


class CmdUtils:

    @classmethod
    def add_dt_prefix(cls, prefix: str = "dateIms") -> None:
        """
使用方法

env | python3 -m dknovautils add_prefix

	py函数 给 stdin 分行 加上前缀 40分钟 更新py库
	
		add_line_prefix
	
		-p dateI
		-p dateIs
		-p dateIns
		-p date
		
		输出分行符号 根据os来决定
        
        
        """
        cls.add_datetime_prefix_per_stdin_line(prefix=prefix)

    @classmethod
    def add_datetime_prefix_per_stdin_line(cls, prefix: str) -> None:
        """
        # _prefixs = ["date", "dateI", "dateIs", "dateIns"]

        std_input = sys.stdin.readline().rstrip('\n')  # Remove trailing newline

        """

        class Pref(Enum):
            date = 10
            dateI = 20
            dateIs = 40
            dateIms = 50
            dateIns = 60

        _prefixs = [str(name) for name, _ in Pref.__members__.items()]

        assert (
            prefix in _prefixs
        ), f"err71055 'prefix' should be one of {_prefixs}. prefix:{prefix} "

        preE = Pref[prefix]

        def fprefix() -> str:  # type: ignore
            noColon = False
            if preE == Pref.date:
                # todo
                return AT.sdf_logger_format_datetime(precise="d", noColon=noColon)
            elif preE == Pref.dateI:
                # date -I
                return AT.sdf_logger_format_datetime(precise="d", noColon=noColon)
            elif preE == Pref.dateIs:
                # date -Is
                return AT.sdf_logger_format_datetime(precise="s", noColon=noColon)
            elif preE == Pref.dateIms:
                # 
                return AT.sdf_logger_format_datetime(precise="ms", noColon=noColon)            
            elif preE == Pref.dateIns:
                # todo
                return AT.sdf_logger_format_datetime(precise="a", noColon=noColon)
            else:
                AT.never("err18903")

        BRN = "\n"
        for line in sys.stdin:
            line = line.rstrip(BRN)
            line = fprefix() + " " + line
            print(line,flush=True)


if __name__ == "__main__":

    print("input some str")

    CmdUtils.add_dt_prefix(prefix="dateIns")

    print("end all ok")

    pass
