from googletrans import Translator

trans = Translator()
result = trans.translate("안녕하세요. 이제 겨울이에요.", dest='en')
print("결과 : {}".format(result.text), "\n"
      "src : {}".format(result.src), "\n"
      "dest: {}".format(result.dest))