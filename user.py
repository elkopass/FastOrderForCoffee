class user:
    def __init__(self, role_id):
        self.role_id = role_id

    def get_role_string(self):
        if self.role_id == 1:
            return 'администратор'
        elif self.role_id == 2:
            return 'бариста'
        return 'пользователь'

    def get_role_id(self):
        return self.role_id