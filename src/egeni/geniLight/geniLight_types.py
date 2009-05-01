class UserSliceInfo:
    def __init__(self, user_name, slice_name):
        self.user_name = user_name
        self.slice_name = slice_name
        return
    def save_to_string(self):
        return self.user_name + '_' + self.slice_name

class GeniResult:
    def __init__(self, code, error_msg):
        self.code = code
        self.error_msg = error_msg
        return

class GeniRecordEntry:
    def __init__(self, type, name):
        self.type = type
        self.name = name
        return
