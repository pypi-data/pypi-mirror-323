import bidi.algorithm
import arabic_reshaper

class PersianShowInKivy:
    def persian_text(self,text):
        return  bidi.algorithm.get_display(arabic_reshaper.reshape(text))
