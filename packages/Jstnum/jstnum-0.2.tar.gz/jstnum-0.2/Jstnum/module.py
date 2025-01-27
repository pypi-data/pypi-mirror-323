"""                                               PRIVATE USE AND DERIVATIVE LICENSE AGREEMENT 

        By using this software (the "Software"), you (the "User") agree to the following terms:  

1. Grant of License:  
    The Software is licensed to you for personal and non-commercial purposes, as well as for incorporation into your own projects, whether for private or public release.  

2. Permitted Use:  
    - You may use the Software as part of a larger project and publish your program, provided you include appropriate attribution to the original author (the "Licensor").  
    - You may modify the Software as needed for your project but must clearly indicate any changes made to the original work.  

3. Restrictions:  
     - You may not sell, lease, or sublicense the Software as a standalone product.  
     - If using the Software in a commercial project, prior written permission from the Licensor is required.(Credit,Cr)
     - You may not change or (copy a part of) the original form of the Software.  

4. Attribution Requirement:  
      Any published program or project that includes the Software, in whole or in part, must include the following notice:  
      *"This project includes software developed by [Jynoqtra], © 2025. Used with permission under the Private Use and Derivative License Agreement."*  

5. No Warranty:  
      The Software is provided "as is," without any express or implied warranties. The Licensor is not responsible for any damage or loss resulting from the use of the Software.  

6. Ownership:  
      All intellectual property rights, including but not limited to copyright and trademark rights, in the Software remain with the Licensor.  

7. Termination:  
     This license will terminate immediately if you breach any of the terms and conditions set forth in this agreement.  

8. Governing Law:  
      This agreement shall be governed by the laws of [the applicable jurisdiction, without regard to its conflict of law principles].  

9. Limitation of Liability:  
     In no event shall the Licensor be liable for any direct, indirect, incidental, special, consequential, or punitive damages, or any loss of profits, revenue, data, or use, incurred by you or any third party, whether in an action in contract, tort (including but not limited to negligence), or otherwise, even if the Licensor has been advised of the possibility of such damages.  

            Effective Date: [2025]  

            © 2025 [Jynoqtra]
"""

def encode_base64(data):encoded = base64.b64encode(data.encode('utf-8'));import base64;print(f"Base64: {encoded.decode('utf-8')}")
def decode_base64(encoded_data):decoded = base64.b64decode(encoded_data);import base64;print(f"UB16: {decoded.decode('utf-8')}")
def reverse_string(string):return string[::-1]
def calculate_factorial(number):
    if number == 0:return 1;return number * calculate_factorial(number - 1)
def generate_random_string(length=15):import random;return ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@/-*_', k=length))
def swap_values(a, b):return b, a
def replace(string,replacement,replacment):return string.replace(replacement,replacment)
def find_maximum(numbers):return max(numbers)
def find_minimum(numbers):return min(numbers)
def get_random_choice(choices):import random;return random.choice(choices)
def generate_unique_id():import uuid;return str(uuid.uuid4())
def concatenate_lists(list1, list2):return list1 + list2
def contains_swears(text):
    from better_profanity import profanity
    return profanity.contains_profanity(text)
def filter_swears_in_text(text):from better_profanity import profanity;return profanity.censor(text)
def uppercase_list(lst):return [item.upper() for item in lst]
def remove_duplicates(lst):return list(set(lst))
def find_index(lst, element):
    try:return lst.index(element)
    except ValueError:return -1
def random_element(lst):
    import random
    if lst:return random.choice(lst);return None
def validate_email(email):import re;pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$';return bool(re.match(pattern, email))      
def split_into_chunks(text, chunk_size):return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
def genpass(SMW):
    import time
    current_time = int(time.time());sec = current_time;strongie = generate_random_string(200);wekui = generate_random_string(20);medumi = generate_random_string(125)
    def WK():wpr1 = generate_random_string(10);wpr2 = generate_unique_id();wpr3 = generate_random_string(10);return f"{wpr1}{sec}{wekui}{wpr2}{sec+2}{wpr3}"
    def MD():mpr1 = generate_random_string(15);mpr2 = generate_unique_id();mpr3 = generate_random_string(15);return f"{mpr2}{sec+2}{mpr2}{mpr2}{medumi}{mpr3}{mpr1}{mpr2}{wekui}{sec+2}{mpr2}{mpr3}{sec+213215+sec}{mpr2}{sec+2}{mpr3}"
    def SR():spr1 = generate_random_string(20);spr2 = generate_unique_id();spr3 = generate_random_string(20);return f"{spr2}{sec+2}{spr2}{strongie}{spr2}{spr3}{spr1}{spr2}{sec+2}{wekui}{spr2}{spr3}{sec+213215+sec}{spr2}{sec+2}{spr3}"
    if SMW == "Weak":return WK()
    elif SMW == "Medium":return MD()
    elif SMW == "Strong":return SR()
    else:return None
def unique_elements(lst):return list(set(lst))
def sum_list(lst):return sum(lst)
def reverse_list(lst):return lst[::-1]
def is_prime(n):
    if n <= 1:return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:return False;return True
def shorten_text(text, length):return text[:length] + "..." if len(text) > length else text
def word_count(text):return len(text.split())
def is_valid_phone_number(phone_number):import re;pattern = r'^\+?[1-9]\d{1,14}$';return re.match(pattern, phone_number) is not None
def clean_null(data):
    if isinstance(data, list):return [item for item in data if item not in [None, "", [], {}, False]]
    elif isinstance(data, dict):return {key: value for key, value in data.items() if value not in [None, "", [], {}, False]};return data
def calculate_average(numbers):
    if not numbers:return 0;return sum(numbers) / len(numbers)
def calculate_median(numbers):
    sorted_numbers = sorted(numbers);n = len(sorted_numbers);mid = n // 2
    if n % 2 == 0:return (sorted_numbers[mid - 1] + sorted_numbers[mid]) / 2;return sorted_numbers[mid]
def count_words(text):import re;words = re.findall(r'\b\w+\b', text);return len(words)
def count_sentences(text):import re;sentences = re.split(r'[.!?]', text);return len([s for s in sentences if s.strip()])
def word_frequencies(text):import re;from collections import Counter;words = re.findall(r'\b\w+\b', text.lower());return dict(Counter(words))
def common_words(text1, text2):import re;words1 = set(re.findall(r'\b\w+\b', text1.lower()));words2 = set(re.findall(r'\b\w+\b', text2.lower()));return list(words1 & words2)
def extract_keywords(text, n=5):import re;from sklearn.feature_extraction.text import TfidfVectorizer;vectorizer = TfidfVectorizer(stop_words='english', max_features=n);tfidf_matrix = vectorizer.fit_transform([text]);keywords = vectorizer.get_feature_names_out();return keywords
def evaluate_text_length(text):import re;sentences = re.split(r'[.!?]', text);word_lengths = [len(word) for word in re.findall(r'\b\w+\b', text)];sentence_lengths = [len(sentence.split()) for sentence in sentences if sentence.strip()];avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0;avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0;return avg_word_length, avg_sentence_length
def sentiment_analysis(text):
    from textblob import TextBlob
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:return "Positive"
    elif analysis.sentiment.polarity < 0:return "Negative"
    else:return "Non Pos Non Neg"
def containsstr(string1, wic):
    import re
    def gefti(string, strip_chars=wic):matches = re.findall(f"[{re.escape(wic)}]", string);cleaned_matches = [match.strip(strip_chars) for match in matches if match];cleanret = ", ".join(cleaned_matches);return cleanret
    container1 = str(string1);container2 = gefti(container1, wic)
    if container2:return True
    else:return False
def split(string, strip_chars):cleaned_string = replace(string,strip_chars,"");return cleaned_string
def Rsls(str):return replace(str,"\\","/" )
def contamath_beta(string):
    symbols = [
        '+', '−', '±', '∓', '÷', '∗', '∙', '×', '∑', '⨊', '⅀', '∏', '∐', '∔', '∸', '≂', '⊕', '⊖', '⊗', '⊘', 
        '⊙', '⊚', '⊛', '⊝', '⊞', '⊟', '⊠', '⊡', '⋄', '⋇', '⋆', '⋋', '⋌', '~', '⩱', '⩲', '∀', '∞', '∃', '∄', '|', 
        '∤', '‱', '∇', '∘', '∻', '∽', '∾', '∿', '≀', '≁', '≬', '⊏', '⊐', '⊑', '⊒', '⋢', '⋣', '⊓', '⊔', '⊶', '⊷', 
        '⊸', '⊹', '⊺', '⋈', '⋉', '⋊', '⋮', '⋯', '⋰', '⋱', '⌈', '⌉', '⌊', '⌋', '〈', '〉', '⊲', '⊳', '⊴', '⊵', '⋪', 
        '⋫', '⋬', '⋭', '≠', '≈', '≂', '≃', '≄', '⋍', '≅', '≆', '≇', '≉', '≊', '≋', '≌', '≍', '≎', '≏', '≐', '≑', '≒', 
        '≓', '≔', '≕', '≖', '≗', '≙', '≚', '≜', '≟', '≡', '≢', '≭', '⋕', '^', '⁰', '¹', '²', '³', '⁴', '⁵', '⁶', '⁷', 
        '⁸', '⁹', '⁺', '⁻', '⁼', '⁽', '⁾', '√', '∛', '∜', '<', '>', '≤', '≥', '≦', '≧', '≨', '≩', '≪', '≫', '≮', '≯', 
        '≰', '≱', '≲', '≳', '≴', '≵', '≶', '≷', '≸', '≹', '≺', '≻', '≼', '≽', '≾', '≿', '⊀', '⊁', '⊰', '⋖', '⋗', 
        '⋘', '⋙', '⋚', '⋛', '⋞', '⋟', '⋠', '⋡', '⋦', '⋧', '⋨', '⋩', '∫', '∬', '∭', '∮', '∯', '∰', '∱', '∲', '∳', 
        '⨌', '⨍', '⨎', '⨏', '⨐', '⨑', '⨒', '⨓', '⨔', '⨕', '⨖', '⨗', '⨘', '⨙', '⨚', '⨛', '⨜', '⌀', '∠', 
        '∡', '∢', '⦛', '⦜', '⦝', '⦞', '⦟', '⦠', '⦡', '⦢', '⦣', '°', '⟂', '⏊', '⊥', '∥', '∦', '∝', '∟', '∺', 
        '≅', '⊾', '⋕', '⌒', '◠', '◡', '⊿', '△', '▷', '▽', '◁', '□', '▭', '▱', '○', '◊', '⋄', '→', '←', '↛', '↚', '↓', 
        '⇒', '⇐', '⇔', '⇋', '↯', '⇏', '∧', '∨', '⋀', '⋁', '⋂', '⋃', '¬', '≡', '∴', '∵', '∶', '∷', '∼', '⊧', '⊢', '⊣', 
        '⊤', '⊥', '⊨', '⊩', '⊪', '⊫', '⊬', '⊭', '⊮', '⊯', '⊻', '⊽', '⋎', '⋏', '∂', '𝛛', '𝜕', '𝝏', '𝞉', '𝟃', '∅', '∁', 
        '∈', '∉', '∋', '∌', '∖', '∩', '∪', '⊂', '⊃', '⊄', '⊅', '⊆', '⊇', '⊈', '⊉', '⊊', '⊋', '⊍', '⊎', '⋐', '⋑', 
        '⋒', '⋓', '⋔', '⋲', '⋳', '⋴', '⋵', '⋶', '⋷', '⋹', '⋺', '⋻', '⋼', '⋽', '⋾', '/', '*']
    for symbol in symbols:
        if symbol in string:return True
        else:return False
def Jai(q):from JynAi import JynAi;return JynAi(q)
def add_commas(input_string):return ','.join(input_string)
def remove_spaces(text):return text.replace(" ", "")
def remove_spaces_andstickT(text):import re;return re.sub(r'\s+', '', text)
def delfs(input_string, text_to_delete):return input_string.replace(text_to_delete, "")
def its(i):import sys;sys.set_int_max_str_digits(99*99*99);return i
def rem_alphabet(text):return ''.join([char for char in text if not char.isalpha()])
def copy_to_clipboard(text):import pyperclip;pyperclip.copy(text)
def paste_from_clipboard():import pyperclip;return pyperclip.paste()
def isequal(s, eq):return s.lower() == eq.lower()
def contains(s, eq):return eq.lower() in s.lower()
def exists(string):
    if rem_alphabet(string) == string:return True
    else:return False
def calculate_square_root(number):import math;return math.sqrt(number)