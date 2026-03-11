import typer

COMMANDS = [
    ('close_context',      'commands.close_context',      'CLOSE_CONTEXT_HELP'),
    ('extract_transcript', 'commands.extract_transcript', 'EXTRACT_TRANSCRIPT_HELP'),
    ('get',                'commands.get',                'GET_HELP'),
    ('import_kb',          'commands.import_md',          'IMPORT_HELP'),
    ('list_add',           'commands.list_add',           'LIST_ADD_HELP'),
    ('list_kb',            'commands.list_kb',            'LIST_KB_HELP'),
    ('list_remove',        'commands.list_remove',        'LIST_REMOVE_HELP'),
    ('log',                'commands.log',                'LOG_HELP'),
    ('open_context',       'commands.open_context',       'OPEN_CONTEXT_HELP'),
    ('open_mode',          'commands.open_mode',          'OPEN_MODE_HELP'),
    ('open_select',        'commands.open_select',        'OPEN_SELECT_HELP'),
    ('query',              'commands.query',              'QUERY_HELP'),
    ('search_kb',          'commands.search',             'SEARCH_HELP'),
    ('session_details',    'commands.session_details',    'SESSION_DETAILS_HELP'),
    ('set_session',        'commands.set_session',        'SET_SESSION_HELP'),
]

app = typer.Typer(
    add_completion=False,
    help="KB — markdown-first knowledge base with session continuity for AI coding agents.",
)

for cmd_name, module_path, help_const in COMMANDS:
    module = __import__(module_path, fromlist=[cmd_name, help_const])
    app.command(name=cmd_name, help=getattr(module, help_const))(getattr(module, cmd_name))

if __name__ == "__main__":
    app()
