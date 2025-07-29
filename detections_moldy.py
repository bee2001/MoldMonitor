# detections_moldy.py

class Detections:
    def __init__(self, imn, bpr, mld):
        self.__imgname = imn
        self.__breadprmtr = bpr
        self.__molds = mld

    def set_imgname(self, imn):
        self.__imgname = imn

    def set_breadprmtr(self, bpr):
        self.__breadprmtr = bpr

    def set_molds(self, mld):
        self.__molds = mld

    def get_imgname(self):
        return self.__imgname

    def get_breadprmtr(self):
        return self.__breadprmtr

    def get_molds(self):
        return self.__molds
