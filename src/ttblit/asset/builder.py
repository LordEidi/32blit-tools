import importlib
import logging
import pathlib
import pkgutil
import re

from ..core.tool import Tool
from . import builders
from .formatter import AssetFormatter
from .writer import AssetWriter


class AssetBuilder(Tool):

    options = {
        'input_file': pathlib.Path,
        'input_type': str,
        'output_file': pathlib.Path,
        'output_format': AssetFormatter.parse,
        'symbol_name': str,
        'force': bool,
        'prefix': str,
        'working_path': pathlib.Path
    }

    _by_name = {}
    _by_extension = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        cls._by_name[cls.command] = cls
        for type_, extensions in cls.typemap.items():
            for ext, auto in extensions.items():
                if auto:
                    if ext in cls._by_extension:
                        raise KeyError(f'An automatic handler for {ext} has already been registered ({cls._by_extension[ext]}).')
                    cls._by_extension[ext] = f'{cls.command}/{type_}'

    def __init__(self, parser=None):
        Tool.__init__(self, parser)

        if self.parser is not None:
            self.parser.add_argument('--input_file', type=pathlib.Path, required=True, help='Input file')
            if(len(self.typemap.keys()) > 1):
                self.parser.add_argument('--input_type', type=str, default=None, choices=self.typemap.keys(), help='Input file type')
            self.parser.add_argument('--output_file', type=pathlib.Path, default=None)
            self.parser.add_argument('--output_format', type=str, default=None, choices=AssetFormatter.names(), help='Output file format')
            self.parser.add_argument('--symbol_name', type=str, default=None, help='Output symbol name')
            self.parser.add_argument('--force', action='store_true', help='Force file overwrite')

    def prepare(self, opts):
        """Imports a dictionary of options to class variables.

        Requires options to already be in their correct types.

        """
        for option, option_type in self.options.items():
            default_value = None
            if type(option_type) is tuple:
                option_type, default_value = option_type
            setattr(self, option, opts.get(option, default_value))

        if self.symbol_name is None:
            if self.working_path is None:
                name = '_'.join(self.input_file.parts)
            else:
                name = '_'.join(self.input_file.relative_to(self.working_path).parts)
            name = name.replace('.', '_')
            name = re.sub('[^0-9A-Za-z_]', '_', name)
            self.symbol_name = name.lower()

        if type(self.prefix) is str:
            self.symbol_name = self.prefix + self.symbol_name

        if self.input_type is None:
            self.input_type = self.guess_type(self.input_file)
            logging.info(f"Guessed type {self.input_type} for {self.input_file}.")
        elif self.input_type not in self.typemap.keys():
            raise ValueError(f'Invalid type {self.input_type}, choices {self.typemap.keys()}')

    def run(self, args):
        self.prepare_options(vars(args))
        aw = AssetWriter()
        aw.add_asset(*self.build())
        aw.write(self.output_format, self.output_file, self.force, report=False)

    def prepare_options(self, opts):
        """Imports a dictionary of options to class variables.

        Used for external callers which don't invoke `run` on this class.

        Converts all options into their correct types via the specified validators.

        """
        if self.options is not None and opts is not None:
            for option_name, option_value in opts.items():
                if option_name in self.options:
                    option_type = self.options[option_name]
                    default_value = None
                    if type(option_type) is tuple:
                        option_type, default_value = option_type
                    if option_value is not None:
                        opts[option_name] = option_type(option_value)
                    else:
                        opts[option_name] = default_value
                else:
                    logging.info(f'Ignoring unsupported {self.command} option {option_name}')

        self.prepare(opts)

    def build(self):
        input_data = open(self.input_file, 'rb').read()
        return self.symbol_name, self.to_binary(input_data)

    @classmethod
    def guess_type(cls, path):
        for input_type, extensions in cls.typemap.items():
            if path.suffix in extensions:
                return input_type
        raise TypeError(f"Unable to identify type of input file {path.name}.")

    @classmethod
    def guess_builder(cls, path):
        try:
            return cls._by_extension[path.suffix]
        except KeyError:
            raise TypeError(f"Unable to identify a builder for {path.name}.")


# Load all the implementations dynamically.
for loader, module_name, is_pkg in pkgutil.walk_packages(builders.__path__, builders.__name__ + '.'):
    # We don't need to import anything from the modules. We just need to load them.
    # This will cause the decorators to run, which registers the builders.
    importlib.import_module(module_name, builders.__name__)
