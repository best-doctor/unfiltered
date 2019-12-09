import re

from typing import Optional


def get_user_id_from_message_text(message_text: Optional[str]) -> Optional[str]:
    if not message_text:
        return None
    wrapper_user_id_array = re.findall(r'<@[\w]*>', message_text)
    if not wrapper_user_id_array:
        return None
    return wrapper_user_id_array[0].replace('<@', '').replace('>', '')
