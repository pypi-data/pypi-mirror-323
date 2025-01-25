import logging
import datetime
import traceback

from .interface import Formatter
from .term import TermFormatter
from ..compat import Callable

default_level_fmt_dict = {
    logging.DEBUG:    TermFormatter.default().blue(),
    logging.INFO:     TermFormatter.blue().bold(),
    logging.WARNING:  TermFormatter.yellow().bold(),
    logging.ERROR:    TermFormatter.red().bold(),
    logging.CRITICAL: TermFormatter.red().bold(),
}
default_date_fmt = TermFormatter.blue().bold()
default_level_fmt_dict_nocolor = {
    logging.DEBUG:    TermFormatter.default(),
    logging.INFO:     TermFormatter.default(),
    logging.WARNING:  TermFormatter.default(),
    logging.ERROR:    TermFormatter.default(),
    logging.CRITICAL: TermFormatter.default(),
}
default_date_fmt_nocolor = TermFormatter.default()


def _fmt_level(level_fmt_dict: dict[int,Formatter], pad_levelname: bool, level: int, levelname: str) -> str:
    pad = ""
    if pad_levelname:
        pad = " " * (8 - len(levelname))
    try:
        formatter = level_fmt_dict[level]
        return f"[{formatter.fmt(levelname)}]{pad}"
    except Exception:
        return levelname


def _fmt_date(date_fmt: Formatter, date_strftime_fmt: str, posix_time: float) -> str:
    return date_fmt.fmt(
        datetime.datetime.fromtimestamp(posix_time).strftime(
            date_strftime_fmt
        )
    )


def default_prefix_formatter(
    record: logging.LogRecord,
    level_fmt_dict: dict[int,Formatter]|None = None,
    date_fmt: Formatter|None = None,
    pad_levelname: bool = True,
    date_strftime_fmt: str = "%H:%M:%S",
    **kwargs
) -> list[str]:
    if level_fmt_dict is None:
        level_fmt_dict = default_level_fmt_dict
    if date_fmt is None:
        date_fmt = default_date_fmt

    return [
        _fmt_level(level_fmt_dict, pad_levelname, record.levelno, record.levelname),
        _fmt_date(date_fmt, date_strftime_fmt, record.created),
    ]


class LogFormatter(logging.Formatter):
    def __init__(
        self,
        separator: str = " - ",
        use_color: bool = True,
        prefix_formatter: Callable[[logging.LogRecord],list[str]]|None = None,
        prefix_formatter_kwargs: dict|None = None,
        print_traceback: bool = False,
        traceback_level: int = logging.WARNING,
        block_dashes: int = 35,
        add_name: bool = True,
        add_path: bool = False,
        before_message: str = ":"
    ):
        if prefix_formatter is None:
            prefix_formatter = default_prefix_formatter
        if prefix_formatter_kwargs is None:
            prefix_formatter_kwargs = {}
        if not use_color:
            prefix_formatter_kwargs["level_fmt_dict"] = default_level_fmt_dict_nocolor
            prefix_formatter_kwargs["date_fmt"] = default_date_fmt_nocolor

        self.separator = separator
        self.prefix_formatter = prefix_formatter
        self.prefix_formatter_kwargs = prefix_formatter_kwargs
        self.print_traceback = print_traceback
        self.traceback_level = traceback_level
        self.block_dashes = block_dashes
        self.add_name = add_name
        self.add_path = add_path
        self.before_message = before_message

    def _dashline(self, msg: str) -> str:
        dash_str = "-" * self.block_dashes
        return f"{dash_str}{msg}{dash_str}"

    def _block(self, title: str, msg: str) -> str:
        if self.block_dashes <= 0:
            return [msg]
        return "\n" + "\n".join([
            self._dashline(f" BEGIN {title} "),
            msg,
            self._dashline(f"  END {title}  "),
        ])

    def format(self, record: logging.LogRecord) -> str:
        desc = self.prefix_formatter(record, **self.prefix_formatter_kwargs)
        if self.add_name:
            desc.append(record.name)
        if self.add_path:
            desc.append(f"{record.pathname}:{record.funcName}:{record.lineno}")

        msg = ""
        try:
            msg = str(record.msg % record.args)
        except Exception:
            msg = str(record.msg)
        blurbs = [self.separator.join(desc) + self.before_message, msg]
        if all([
            self.print_traceback,
            record.levelno >= self.traceback_level
        ]):
            exc_str = traceback.format_exc()
            if not exc_str.startswith("NoneType: None"):
                blurbs.append(self._block("EXCEPTION", exc_str))

        return " ".join(blurbs)
