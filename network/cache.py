from django.core.cache import caches 

# name of the cache that we use configured in settings 
CACHE_ALIAS = 'default'

'''
format of cache:

cache key = 'resource_page_userIDrequesting_userIDrequested'

resource refers to either 'index', 'profile', 'following', 'login', or 'register' depending on which
page the user requests. 

userIDrequested is only applicable for the following page, no others.  

page is optional here. 
'''


INDEX = 'index'
PROFILE = 'profile'
FOLLOWING  = 'following'
LOGIN = 'login'
REGISTER  = 'register'


delimiter = "_"

class Cache ():
    def __init__(self,alias):
        self.cache = caches[alias]
    
    @classmethod 
    def getString(*args):
        result = ""
        for arg in args:
            if arg is not None: result += str(arg) + delimiter 
        if len(result) > 0:
            result = result[0:len(result) - 1]
        return result 

    def clear(self):
        self.cache.clear()

    def add(self, item, *args):
        ''' args should be in format 'resource_page_userIDrequesting_userIDrequested' '''
        key = self.getString(args)
        try:
            self.cache.set(key, item)
            return True 
        except:
            return False 

    def delete (self, *args ):
        ''' args should be in format 'resource_page_userIDrequesting_userIDrequested' '''
        key = self.getString(args)
        self.cache.delete(key)

    def exists(self, *args ):
        ''' args should be in format 'resource_page_userIDrequesting_userIDrequested' '''
        key = self.getString(args)
        return self.cache.get(key) is not None 

    def get (self, *args ):
        ''' args should be in format 'resource_page_userIDrequesting_userIDrequested' '''
        key = self.getString(args)
        return self.cache.get(key)