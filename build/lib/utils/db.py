from sqlalchemy import engine

def safe_engine_call(eng: engine.Engine) -> engine.Engine:
    if(eng == None):
        raise ValueError("Attempted to make SQL call without a SQL connection. Did you provide the connection parameters?")
    return eng