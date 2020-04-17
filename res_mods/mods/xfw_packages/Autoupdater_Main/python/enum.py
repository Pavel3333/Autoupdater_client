__all__ = ('Enum', )

class EnumValue:
    def __init__(self, classname, enumname, value):
        self.__classname = classname
        self.__enumname = enumname
        self.__value = value

    def __int__(self):
        return self.__value

    #def __repr__(self):
    #    return "EnumValue(%r, %r, %r)" % (self.__classname,
    #                                      self.__enumname,
    #                                      self.__value)

    def __str__(self):
        return self.__enumname #"%s.%s" % (self.__classname, self.__enumname)

    def __cmp__(self, other):
        if isinstance(other, str):
            return cmp(self.__enumname, other)
        return cmp(self.__value, int(other))

class EnumMetaClass:
    def __init__(self, name, bases, dict):
        for base in bases:
            if base.__class__ is not EnumMetaClass:
                raise TypeError, "Enumeration base class must be enumeration"
        bases = filter(lambda x: x is not Enum, bases)
        self.__name__ = name
        self.__bases__ = bases
        self.__dict = {}
        for key, value in dict.items():
            if not isinstance(key, str) or not isinstance(value, int): continue
            self.__dict[key] = EnumValue(name, key, value)

    def __hasattr__(self, name):
        if name == '__members__':
            return True
        
        if isinstance(name, str):
            if name in self.__dict:
                return True
        elif int(name) in self.__dict.values():
            return True
        
        return any(base.__hasattr__(name) for base in self.__bases__)
    
    def __getattr__(self, name):
        if name == '__members__':
            return self.__dict.keys()

        if isinstance(name, str) and name in self.__dict:
            return self.__dict[name]
        else:
            for key, value in self.__dict.iteritems():
                if value == name:
                    return value
        
        for base in self.__bases__:
            if base.__hasattr__(name):
                return base.__getattr__(name)

    #def __repr__(self):
    #    s = self.__name__
    #    if self.__bases__:
    #        s = s + '(' + ', '.join(map(lambda x: x.__name__,
    #                                      self.__bases__)) + ')'
    #    if self.__dict:
    #        s = "%s: {%s}" % (s, ', '.join("%s: %s" % (key, int(value)) for key, value in self.__dict.iteritems()))
    #    return s

Enum = EnumMetaClass("Enum", (), {})
