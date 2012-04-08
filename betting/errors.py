
class MISSING_PARAMETER(Exception):
    code = '2'
    message = "Parameter Missing"
    
class EVENT_ID_NOT_FOUND(Exception):
    code = '3'
    message = "Event Doesn't Exist"
    
class BET_ID_NOT_FOUND(Exception):
    code = '4'
    message = "Bet doesn't exists"
    
class BET_EXPIRED(Exception):
    code = '5'
    message = "This bet has expired."
    
class BET_ODD_EXPIRED(Exception):
    code = '6'
    message = "Bet odds have changed"
    
class NOT_ENOUGH_CASH(Exception):
    code = '7'
    message = "User doesn't have sufficient cash"
    
class USER_NOT_FOUND(Exception):
    code = '8'
    message = "User not present in Database"