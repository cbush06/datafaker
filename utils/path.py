from typing import Any

def walk_path_for_value(doc_name: str, path: str, context: dict[str, Any]):
    path_segs = path.split('.')
    value_key = path_segs[len(path_segs) - 1]
    final_context = context

    # Drill down to the value the user specified (firstObj.secondObj.....)
    if(len(path_segs) > 1):
        for next_seg in path_segs[:len(path_segs) - 1]:
            final_context = final_context[next_seg]   

    if(value_key not in final_context):
        raise ValueError(f"No field named {value_key} was found in the from context of {doc_name}")

    return final_context[value_key]