from flask_login import UserMixin

class Team:
    def __init__(self, team_id, team_logo, team_name):
        self.team_id = team_id
        self.team_logo = team_logo
        self.team_name = team_name
    
    def team_to_dict(self):
        return {"team_name": self.team_name, "team_id": self.team_id, "team_logo": self.team_logo}

class Player(Team):
    def __init__(self, team_id, team_logo, team_name, player_id, player_name, player_photo, player_age, player_height, player_weight, player_position, player_nationality, player_appearances, player_goals, player_pen_accuracy, player_assists, player_yellows, player_reds, player_conceded, player_saves, player_penalty_saves):
        super().__init__(team_id, team_logo, team_name)
        self.player_id = player_id
        self.player_name = player_name
        self.player_photo = player_photo
        self.player_age = player_age
        self.player_height = player_height
        self.player_weight = player_weight
        self.player_position = player_position
        self.player_nationality = player_nationality
        self.player_appearances = player_appearances
        self.player_goals = player_goals
        self.player_pen_accuracy = player_pen_accuracy
        self.player_assists = player_assists
        self.player_yellows = player_yellows
        self.player_reds = player_reds
        self.player_conceded = player_conceded
        self.player_saves = player_saves
        self.player_penalty_saves = player_penalty_saves
        
    def player_to_dict(self):
        return {"player_id": self.player_id, "team_id": self.team_id, "player_name": self.player_name, "player_photo": self.player_photo, "player_age": self.player_age, "player_height": self.player_height, "player_weight": self.player_weight, "player_position": self.player_position, "player_nationality": self.player_nationality, "player_appearances": self.player_appearances, "player_goals": self.player_goals, "player_pen_accuracy": self.player_pen_accuracy, "player_assists": self.player_assists, "player_yellows": self.player_yellows, "player_reds": self.player_reds, "player_conceded": self.player_conceded, "player_saves": self.player_saves, "player_penalty_saves": self.player_penalty_saves}

class Users(UserMixin):
    def __init__(self, username, password, location, photo, isAdmin = False):
        self.username = username
        self.password = password
        self.location = location
        self.photo = photo
        self.isAdmin = isAdmin
    
    def user_to_dict(self):
        return self.__dict__
    
    def get_id(self):
        return self.username