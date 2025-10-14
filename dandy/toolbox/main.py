from bottle import route, run, static_file, TEMPLATE_PATH, template
import sys
from pathlib import Path

CWD_PATH = Path.cwd()

sys.path.append(str(CWD_PATH))


def main():
    from dandy.toolbox.utils import check_or_create_settings, load_environment_variables

    load_environment_variables(CWD_PATH)

    check_or_create_settings(CWD_PATH)

    from dandy.conf import settings

    TEMPLATE_PATH.insert(0, f'{CWD_PATH}/templates')

    @route('/')
    def index():
        return template('index.html')

    @route('/static/<filepath:path>')
    def server_static(filepath: Path | str):
        return static_file(filepath, root=f'{CWD_PATH}/static/files')

    run(
        host='localhost',
        port=8088,
        debug=settings.DEBUG,
        reloader=settings.DEBUG,
    )


if __name__ == '__main__':
    print('Starting Dandy Toolbox...')

    sys.exit(main())
