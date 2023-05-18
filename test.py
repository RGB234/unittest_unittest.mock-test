import unittest
from unittest.mock import Mock
import swearing_filter as filter

class test_filter(unittest.TestCase):
    # ^ㅣ, ^^ㅣ, 77ㅣ(특수문자 교체) / 시&발 시&&발(특수문자 삽입)
    test_text = "^ㅣ22발 ^^2%ㅣ발 ^^^ㅣ발 ^ㅐ77ㅣ ^^ㅐ끼 ㅅ&ㅂ ㅅ&&ㅂ"
    testResult = filter.swearing_Filter(test_text, 2.0)

    def test_makeList(self):
        self.assertEqual(['ㅅㅂ', 'ㅅㅂ', '시발', '시발', '시발', '새끼', '새끼'], 
                         self.testResult.makeList(self.testResult.text))
    
    def test_phoneme(self):
        self.assertEqual(
            #phoneme 함수는 한글을 초성, 중성, 종성에 대응하는 아스키코드로 분해, 이 아스키코드를 다시 chr()로 변환
            ['ᄋ', 'ᅵ', 'ᆫ'],
            self.testResult.phoneme("인")
        )
    def test_decompose(self):
        self.assertEqual(
            [[['ᄋ', 'ᅵ', 'ᆫ'],['ᄀ','ᅡ','ᆫ']],[['ᄉ','ᅵ','ᆯ'],['ᄀ','ᅧ','ᆨ']]]
            ,self.testResult.decompose_to_phoneme(["인간", "실격"]))
        
    def test_convert_Vec(self):
        ####################################### Using MOCK example start #######################################
        mock = Mock()
        mock.return_value = [[['ᄀ','ᅮ','ᄀ']],[['ᄀ','ᅩ','ᄀ']]]
        self.test_list_of_phoneme = mock()
        ####################################### Using Mock example end #########################################
        # self.test_list_of_phoneme = self.testResult.decompose_to_phoneme(["국", "곡"])
        self.assertEqual( [ [ [[0,3,1,0], [1,1,2], [0,3,1,0]] ], [ [[0,3,1,0], [1,1,1], [0,3,1,0]] ] ] 
                         ,self.testResult.convert_to_vector(self.test_list_of_phoneme))

    def test_distance(self):
        #형태가(초성,중성,종성, 글자수) 비슷한 단어 -> .distance True return
        self.test_list_of_phoneme_T = self.testResult.decompose_to_phoneme(["국", "곡"])
        # [ [단어1], [단어2] ] -> [ [ [글자1] [글자2] ] ]
        #[ [ [[초성],[중성],[종성]], [ [], [], [] ] ] ]
        self.test_Vec_T = self.testResult.convert_to_vector(self.test_list_of_phoneme_T)
        self.assertTrue( self.testResult.distance(self.test_Vec_T[0], self.test_Vec_T[1]))

        #다른 단어 -> .distance False return
        self.test_list_of_phoneme_F = self.testResult.decompose_to_phoneme(["숙고", "희극"])
        self.test_Vec_F = self.testResult.convert_to_vector(self.test_list_of_phoneme_F)
        self.assertFalse( self.testResult.distance(self.test_Vec_F[0], self.test_Vec_F[1]))
    
    def test_returnList(self):
        print(self.testResult.searching)

    def test_filter(self):
        self.testResult.filter()

    def test_show(self):
        #{"시발" :3, "새끼":2, "ㅅㅂ":2}
        self.testResult.showCensored()

    def test_showPercent(self):
        #showCensored()의 결과를 를 퍼센트로 나타냄
        self.testResult.showCensored_Percent()
    
if __name__ == '__main__':
    unittest.main()