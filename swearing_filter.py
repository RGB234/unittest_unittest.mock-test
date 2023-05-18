#from sklearn.feature_extraction.text import CountVectorizer
#import scipy as sp
# 형태소 분석기
from konlpy.tag import Twitter

import re
from typing import List

import matplotlib.pyplot as plt #데이터 시각화 파이썬 모듈
# %matplotlib inline 
import platform
from matplotlib import font_manager, rc
plt.rcParams['axes.unicode_minus'] = False

if platform.system() == 'Windows':
    path='c:/Windows/Fonts/malgun.ttf'
    font_name = font_manager.FontProperties(fname=path).get_name()
    rc('font', family=font_name)
#------------------------- 데이터 시각화 준비 완료
from konlpy.tag import Twitter
import math
from typing import List
twitter = Twitter()

swearing_Kor=['시발','병신','호로','등신','새끼', '지랄', '좆', 'ㅅㅂ', 'ㅄ', 'ㅂㅅ', 'ㅈㄹ', 'ㅈㄴ']
swearing_Kor_chosung=['ㅅㅂ', 'ㅄ', 'ㅂㅅ', 'ㅈㄹ', 'ㅈㄴ']

#중복되는 자음은 순서대로 하나는 초성, 하나는 종성이다 (둘이 아스키코드 다름)
#중요: 아래의 자음, 모음을 복사하여 ord()로 아스키코드값을 찾아보면 알겠지만,
#키보드로 입력한 자모음값과 아스키코드값이 다름. 아래의 자모음(consonants, vowels)은 한글을 초,중,종성으로 분해하여 얻은 자모음값이기 때문
#phoneme 함수에서도 마찬가지로 초중종성으로 분리한 아스키 코드를 chr로 변환하여 반환
consonants = {'ᄀ':[0,3,1,0],'ᄁ':[0,3,0,0],'ᄂ':[1,1,0,0],'ᄃ':[0,1,1,0],'ᄄ':[0,1,0,0],'ᄅ':[1,1,1,0],
              'ᄆ':[1,0,0,0],'ᄇ':[0,0,1,0],'ᄈ':[0,0,0,0],'ᄉ':[0,1,1,1],'ᄊ':[0,1,0,1],'ᄋ':[1,3,0,0],
              'ᄌ':[0,2,1,2],'ᄍ':[0,2,0,2],'ᄎ':[0,2,2,2],'ᄏ':[0,3,2,0],'ᄐ':[0,1,2,0],'ᄑ':[0,0,2,0],
              'ᄒ':[0,4,1,1],'ᆪ':[0,3,1,0],'ᆲ':[1,1,1,0],'ᆳ':[1,1,1,0],'ᆹ':[0,0,1,0],'ᆰ':[0,3,1,0],
              'ᆨ':[0,3,1,0],'ᆩ':[0,3,0,0],'ᆫ':[1,1,0,0],'ᆮ':[0,1,1,0],'ᆯ':[1,1,1,0],'ᆷ':[1,0,0,0],
              'ᆸ':[0,0,1,0],'ᆺ':[0,1,1,1],'ᆻ':[0,1,0,1],'ᆼ':[1,3,0,0],'ᆽ':[0,2,1,2],'ᆾ':[0,2,2,2],
              'ᆿ':[0,3,2,0],'ᇀ':[0,1,2,0],'ᇁ':[0,0,2,0],'ᇂ':[0,4,1,1],'ᆪ':[0,3,1,0],'ᆲ':[1,1,1,0],
              'ᆳ':[1,1,1,0],'ᆹ':[0,0,1,0],'ᆰ':[0,3,1,0]}

vowels = {'ᅵ':[0,0,2],'ᅦ':[0,0,1],'ᅢ':[0,0,0],'ᅱ':[1,0,2],'ᅬ':[1,0,1],'ᅳ':[0,1,2],
          'ᅥ':[0,1,1],'ᅡ':[0,1,0],'ᅮ':[1,1,2],'ᅩ':[1,1,1],'ᅣ':[0, 2/3, 2/3],'ᅧ':[0,2/3,4/3],
          'ᅭ':[2/3,2/3,4/3],'ᅲ':[2/3,2/3,2],'ᅤ':[0,1/3,0],'ᅨ':[0,0,4/3],'ᅪ':[1/3,1,1/3],
          'ᅯ':[1/3,1,5/3],'ᅫ':[1/3,1/3,1/3],'ᅰ':[1/3,1/3,4/3],'ᅴ':[0,2/3,2]}

class swearing_Filter:
    '''
문장입력 -> makeList(검사목록생성) -> (phonemeDeassembler -> 글자 벡터화 -> 거리 계산 -> 판별) // -> 통계 및 시각화
                                                   괄호안은  크게  FIlter()  메서드 하나로
    '''   
    def __init__(self, text:str, std = 2.0):
        #twitter = Twitter()
        self.text = text
        self.fitting_standard = std  #distance 메서드 마지막에 쓰일 class변수
        
    def makeList(self, text):    #비속어인지 아닌지 판단할 목록 생성 (명사 + 예외)
        
        self.searching = [] 
        #사용한 비속어 리스트, __init__ 에서 정의x -> class를 호출할 때 그때 1번만 초기화가 되기 때문
                
        #숫자, 특수문자가 포함된 비속어 처리
        p = re.compile('(77ㅣ|77\|)')
        self.text = p.sub('끼', self.text)

        q = re.compile(r"[\^]{1,2}(\s|[0-9]|[\!\@\#\$\%\^\&\*])*[ㅣ1\|]")  #^^ㅣ , 새77ㅣ 같은 경우 
        self.text = q.sub('시', self.text)

        r = re.compile(r"[\^]{1,2}(\s|[0-9]|[\!\@\#\$\%\^\&\*])*[ㅐㅒㅔㅖ]")
        self.text = r.sub('새', self.text)

        for s in swearing_Kor:
            for i in range(0, len(s)-1):
                p = re.compile(s[i]+r'([0-9]|[\!\@\#\$\%\^\&\*])*'+s[i+1]) # 비속어 사이에 특수문자|숫자 있는 경우 (ex:시1발)
                self.text = p.sub(s[i]+s[i+1], self.text)
        
        self.new_text = self.text
        
        #초성으로 된 비속어 처리
        for chosung in swearing_Kor_chosung:
            for _ in re.finditer(chosung, self.new_text):
                self.searching.append(chosung)
                # self.searching += chosung => self.searching 리스트에 ['ㅅ','ㅂ'] 같은 형태로 저장됨
        
        self.searching += twitter.nouns(self.new_text)
        #self.searching = set(self.searching) #중복제거 - 통계에 불필요한 부분
        return self.searching
    
    def phoneme(self, target:str) -> List[str]:
        #초성(19), 중성(21) , 종성(28) 각각 initial, middle, last
        # 한글의 유니코드 = ((초성인덱스 * 21) + 중성인덱스) * 28 + 종성인덱스 + 0xAC00
        # chr(0xAC00) == 44032(10진수) -> '가'
        ord_code = ord(target) - 0xAC00
        if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', target) is not None: #한글여부 체크

            last_index = int(ord_code % 28)
            middle_index = int(((ord_code) /28) %21)
            initial_index = int(((ord_code) /28 ) /21)
            # last_index = int(ord_code % 28)
            # middle_index = int((ord_code - last_index) /28 %21)
            # initial_index = int(((ord_code - last_index) /28 - middle_index) /21)

            initial = chr(initial_index + 0x1100) #chr(0x1100) == 'ㄱ'
            middle = chr(middle_index + 0x1161) #chr(0x1161) == 'ㅏ'
            last = chr(last_index + 0x11A8 - 1) #chr(0x11A8) ==  받침'ㄱ'

        # 중요: ord('ㅣ') == 108, 
        # '긴' 에서 종성: 'ㅣ'의 ord, 유니코드값은 4469(10)로 다름
        # 따라서 이 함수의 리턴값을 print해보면 일반적인 초성 중성 종성으로
        # 분해되지 않는 것처럼 보이나, 유니코드상으로는 문제없음
        return [initial, middle, last]
    
    def decompose_to_phoneme(self, word_list:List[str]) -> List[List[List[str]]]:
        # makeList 의 결과에 phoneme 함수 적용
        self.decomposed = []
        self.word_list = word_list
        for word in self.word_list:
            tmp_L = []
            for i in range(len(word)):
                tmp_L.append(self.phoneme(word[i]))
            self.decomposed.append(tmp_L)
        return self.decomposed
    
    def convert_to_vector(self, list_of_phoneme:List[List[List[str]]]) -> List[List[List[List[float]]]]:
        #음소들을 벡터와 대응
        #결과값을 담기 위한 리스트 생성(empty list) start
        self.tmp = []
        self.list_of_phoneme = list_of_phoneme
        for v,word in enumerate(self.list_of_phoneme):
            #단어 개수만큼 self.tmp 내부에 empty list [] 생성
            self.tmp.append([])
            for _,letter in enumerate(word):
                #각 단어마다 글자 개수만큼 empty list [] 생성
                self.tmp[v].append([])
        #empty 리스트 생성 end
        #벡터와 대응
        for i,x in enumerate(self.list_of_phoneme):
            #단어
            for j,y in enumerate(x):
                #글자
                for k,z in enumerate(y):
                    #음소
                    if z in consonants.keys():
                        vec_a = consonants.get(z,[0,0,0,0]) #key가 z(음소) 인 것을 찾고 없다면 영벡터 반환
                        self.tmp[i][j].append(vec_a)
                    
                    elif z in vowels.keys():
                        vec_b = vowels.get(z,[0,0,0])
                        self.tmp[i][j].append(vec_b)
                    
                    else:
                        vec_zero = [0,0,0,0]
                        self.tmp[i][j].append(vec_zero)
                        
        word_Vec = self.tmp
        
        return word_Vec

    def distance(self, wordVec_a, wordVec_b):
        #fitting_standard = 1.0
        if len(wordVec_a) == len(wordVec_b): #글자수가 같은 두 단어의 각 단어벡터간 거리비교
                                             # word => [[글자1],[글자2],[글자3]]  letter => [[,,,],[,,],[,,,]]
            self.word_similarity = []

            for n in range(len(wordVec_a)):

                self.letter_a, self.letter_b = wordVec_a[n], wordVec_b[n]
                self.dist_letter = 0

                for i in range(len(self.letter_a)): # len(letter_a) == len(letter_b) == 3:
                    self.phoneme_a, self.phoneme_b = self.letter_a[i], self.letter_b[i]

                    if len(self.phoneme_a) == 4: #자음이면 [ , , , ]
                        # (차*가중치)를 소수점 3째자리에서 반올림 후 제곱
                        dist_comp_1 = math.pow(round(((self.phoneme_a[0] - self.phoneme_b[0]) *3),2),2)
                        dist_comp_2 = math.pow(round(((self.phoneme_a[1] - self.phoneme_b[1]) *2),2),2)
                        dist_comp_3 = math.pow(round(((self.phoneme_a[2] - self.phoneme_b[2]) *1),2),2)
                        dist_comp_4 = math.pow(round(((self.phoneme_a[3] - self.phoneme_b[3]) *2),2),2)
                        dist_phoneme = round(math.sqrt(dist_comp_1+ dist_comp_2 + dist_comp_3+ dist_comp_4),2)
                        self.dist_letter += dist_phoneme

                    elif len(self.phoneme_a) ==3: #모음이면 [ , , ]
                        dist_comp_1 = math.pow(round(((self.phoneme_a[0] - self.phoneme_b[0]) *3),2),2)
                        dist_comp_2 = math.pow(round(((self.phoneme_a[1] - self.phoneme_b[1]) *2),2),2)
                        dist_comp_3 = math.pow(round(((self.phoneme_a[2] - self.phoneme_b[2]) *1),2),2)
                        dist_phoneme = round(math.sqrt(dist_comp_1 + dist_comp_2 + dist_comp_3),2)
                        self.dist_letter += dist_phoneme

                    else:
                        print('sorry~ error')

                if self.dist_letter <= self.fitting_standard:   # ***판별기준***
                    self.word_similarity.append(True)
                else:
                    self.word_similarity.append(False)

            for D in self.word_similarity:
                if D != True:
                    return False #단 한 글자라도 유사하다고 판별되지 않는다면 단어는 유사하지 않음
                
            return True
    
    def returnList(self):      #판단 목록 반환
        return self.searching
    
#------------------------------------------------------------------------    
    def filter(self):
            
        self.makeList(self.text)
        #입력값 self.text 에서 필요한 가공을 마친 self.new_text
        before_censored = self.new_text
        
        self.swearing_Kor_Vec = self.convert_to_vector(self.decompose_to_phoneme(swearing_Kor))
        self.makeList_Vec = self.convert_to_vector(self.decompose_to_phoneme(self.returnList()))

        self.statistics = dict()
        for i in range(len(swearing_Kor)):
            for j in range(len(self.returnList())): #returnList => self.searching 반환 ( == makeList반환값)
                if self.distance(self.swearing_Kor_Vec[i], self.makeList_Vec[j]):#(True 비슷함/ False 다름)
                    # "*" 로 검열된 단어 표시
                    w = self.returnList()[j]
                    p = re.compile(w)
                    sub = '*'*len(w)
                    before_censored = p.sub(sub, before_censored)
                    
                    if swearing_Kor[i] in self.statistics:
                        self.statistics[swearing_Kor[i]] = self.statistics[swearing_Kor[i]] + 1
                    else:
                        self.statistics[swearing_Kor[i]] = 1
                        #statistics 딕셔너리 생성
                                
        after_censored = before_censored
        print(after_censored)

        return self.statistics
#-----------------------------------------------------------------------------------
    def showCensored(self):
        u = self.filter()
        x = u.keys()
        y = u.values()
        plt.figure(figsize=(12,8))
        plt.bar(x, y)
        plt.title("검열된 비속어", fontsize=20)
        plt.xlabel("사용한 비속어")
        plt.ylabel("사용 횟수")
        plt.show()
        return None
    
    def showCensored_Percent(self):
        u = self.filter()
        x = u.keys()
        sum_y = sum(u.values())
        for i in range(len(u.keys())):
            u[list(u.keys())[i]] = round((u[list(u.keys())[i]] / sum_y) * 100, 2)
        y= u.values()
        plt.figure(figsize=(12,8))
        plt.bar(x, y)
        plt.title("검열된 비속어", fontsize=20)
        plt.xlabel("사용한 비속어")
        plt.ylabel("사용 횟수(%)")
        plt.show()
        return None