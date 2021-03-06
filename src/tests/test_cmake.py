import base64
import tempfile

import pytest


@pytest.fixture
def test_metadata_file():
    temp_png = tempfile.NamedTemporaryFile('wb', suffix='.png')
    temp_png.write(base64.b64decode(b'iVBORw0KGgoAAAANSUhEUgAAAIAAAACACAMAAAD04JH5AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyNpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuNi1jMTQ4IDc5LjE2NDAzNiwgMjAxOS8wOC8xMy0wMTowNjo1NyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIDIxLjAgKFdpbmRvd3MpIiB4bXBNTTpJbnN0YW5jZUlEPSJ4bXAuaWlkOjE5NkU4OENBNTk3NDExRUFCMTgyODFBRDFGMTZDODJGIiB4bXBNTTpEb2N1bWVudElEPSJ4bXAuZGlkOjE5NkU4OENCNTk3NDExRUFCMTgyODFBRDFGMTZDODJGIj4gPHhtcE1NOkRlcml2ZWRGcm9tIHN0UmVmOmluc3RhbmNlSUQ9InhtcC5paWQ6MTk2RTg4Qzg1OTc0MTFFQUIxODI4MUFEMUYxNkM4MkYiIHN0UmVmOmRvY3VtZW50SUQ9InhtcC5kaWQ6MTk2RTg4Qzk1OTc0MTFFQUIxODI4MUFEMUYxNkM4MkYiLz4gPC9yZGY6RGVzY3JpcHRpb24+IDwvcmRmOlJERj4gPC94OnhtcG1ldGE+IDw/eHBhY2tldCBlbmQ9InIiPz4ohDCNAAAACVBMVEUAAAD///8A/wDg4n4DAAAAmklEQVR42uzZMQqAMAxA0er9D+1Wl1ITijTi+6PQ8qYYsTVJUu/Ilj569gAAAABqAtIDM30UAAAAoDrAuwAAAODLK9nCdAQAAACoBHh/FD84AQAAALYDJEnpQTk6MPgCD98LAAAAUAiQXkXT9wIAAADUBEx/qEQBg2fhUQwAAAAAAAAAAHADFnbCKSC8EwIAAABsAkjST7sEGACd4xph9WtahAAAAABJRU5ErkJggg=='))
    temp_png.flush()

    temp_yml = tempfile.NamedTemporaryFile('w', suffix='.yml')
    temp_yml.write(f'''title: Rocks & Diamonds
description: A pulse pounding, rock rollin', diamond hunting adventure
author: gadgetoid
splash:
  file: {temp_png.name}
version: v1.0.0
''')
    temp_yml.flush()
    return temp_yml, temp_png


@pytest.fixture
def test_empty_metadata_file():
    temp_yml = tempfile.NamedTemporaryFile('w', suffix='.yml')
    temp_yml.write('''title: Rocks & Diamonds
description: A pulse pounding, rock rollin', diamond hunting adventure
author: gadgetoid
version: v1.0.0
''')
    temp_yml.flush()
    return temp_yml


@pytest.fixture
def test_asset_config_file():
    temp_yml = tempfile.NamedTemporaryFile('w', suffix='.yml')
    temp_yml.write('''assets.cpp:
  assets/buttons.png: asset_buttons
''')
    temp_yml.flush()
    return temp_yml


@pytest.fixture
def test_cmake_file():
    temp_cmake = tempfile.NamedTemporaryFile('wb', suffix='.cmake')
    return temp_cmake


def test_cmake_no_args():
    from ttblit import main

    with pytest.raises(SystemExit):
        main(['cmake'])


def test_cmake_asset(test_asset_config_file, test_cmake_file):
    from ttblit import main

    with pytest.raises(SystemExit):
        main([
            'cmake',
            '--config', test_asset_config_file.name,
            '--cmake', test_cmake_file.name
        ])


def test_cmake(test_metadata_file, test_cmake_file):
    from ttblit import main

    test_metadata_file, test_metadata_splash_png = test_metadata_file

    with pytest.raises(SystemExit):
        main([
            'cmake',
            '--config', test_metadata_file.name,
            '--cmake', test_cmake_file.name
        ])

    assert open(test_cmake_file.name).read().startswith('# Auto Generated File - DO NOT EDIT!')


def test_cmake_no_depends(test_empty_metadata_file, test_cmake_file):
    from ttblit import main

    with pytest.raises(SystemExit):
        main([
            'cmake',
            '--config', test_empty_metadata_file.name,
            '--cmake', test_cmake_file.name
        ])

    assert open(test_cmake_file.name).read().replace('    ', '') == '''# Auto Generated File - DO NOT EDIT!
set(METADATA_DEPENDS

)
set(METADATA_TITLE "Rocks & Diamonds")
set(METADATA_AUTHOR "gadgetoid")
set(METADATA_DESCRIPTION "A pulse pounding, rock rollin', diamond hunting adventure")
set(METADATA_VERSION "v1.0.0")
'''


def test_cmake_multiple_outputs(test_resources, test_cmake_file):
    from ttblit import main

    with pytest.raises(SystemExit):
        main([
            'cmake',
            '--config', str(test_resources / 'assets_multi_out.yml'),
            '--cmake', test_cmake_file.name
        ])

    assert open(test_cmake_file.name).read().startswith('# Auto Generated File - DO NOT EDIT!')
