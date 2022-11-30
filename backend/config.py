import os
from pathlib import Path
BACKEND_DIR = str(Path(__file__).parent.absolute())

def alchemy_uri():
	return f'sqlite:///{BACKEND_DIR}/database/database.db'

def bind_uri():
	return {'db_run': alchemy_uri(),
			'db_src': f'sqlite:///{BACKEND_DIR}/database/sources.db',
			'db_day': f'sqlite:///{BACKEND_DIR}/database/daily.db',
    }
