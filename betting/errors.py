class BettingAppException(Exception):
    code = None
    message = ""
    def __init__(self):
        Exception.__init__(self, self.__class__.message)
        self.code = self.__class__.code
        
class MISSING_PARAMETER(BettingAppException):
    code = '2'
    message = "Parameter Missing"
    
class EVENT_ID_NOT_FOUND(BettingAppException):
    code = '3'
    message = "Event Doesn't Exist"
    
class BET_ID_NOT_FOUND(BettingAppException):
    code = '4'
    message = "Bet doesn't exists"
    
class BET_EXPIRED(Exception):
    code = '5'
    message = "This bet has expired."
    
class BET_ODD_EXPIRED(BettingAppException):
    code = '6'
    message = "Bet odds have changed"
    
class NOT_ENOUGH_CASH(BettingAppException):
    code = '7'
    message = "User doesn't have sufficient cash"
    
class USER_NOT_FOUND(BettingAppException):
    code = '8'
    message = "User not present in Database"