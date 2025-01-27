STRING/INTAGER-NUMBER-MATH util: from JynPopMod.utils.stringnum_utils import *

### 1. **Base64 Encoding**
Encodes a string into Base64 format. Useful for encoding binary data to be transmitted in text form.

**Example Usage:**
```python
encoded = encode_base64("Hello, world!")  # Encodes the string to Base64
```

---

### 2. **Base64 Decoding**
Decodes a Base64 encoded string back to its original form.

**Example Usage:**
```python
decoded = decode_base64("SGVsbG8sIHdvcmxkIQ==")  # Decodes a Base64 string to original text
```

---

### 3. **String Reversal**
Reverses the characters of a string.

**Example Usage:**
```python
reversed_str = reverse_string("Hello")  # Returns "olleH"
```

---

### 4. **Factorial Calculation**
Calculates the factorial of a number recursively.

**Example Usage:**
```python
fact = calculate_factorial(5)  # Returns 120 (5 * 4 * 3 * 2 * 1)
```

---

### 5. **Generate Random String**
Generates a random string of a specified length, using alphanumeric characters and special symbols.

**Example Usage:**
```python
random_str = generate_random_string(10)  # Returns a random 10-character string
```

---

### 6. **Swap Values**
Swaps the values of two variables.

**Example Usage:**
```python
a, b = swap_values(5, 10)  # Swaps the values: a = 10, b = 5
```

---

### 7. **Replace String**
Replaces all occurrences of a substring with another substring within a string.

**Example Usage:**
```python
new_str = replace("Hello, world!", "world", "there")  # Replaces "world" with "there"
```

---

### 8. **Find Maximum Value**
Finds the maximum value from a list of numbers.

**Example Usage:**
```python
max_value = find_maximum([1, 2, 3, 4, 5])  # Returns 5
```

---

### 9. **Find Minimum Value**
Finds the minimum value from a list of numbers.

**Example Usage:**
```python
min_value = find_minimum([1, 2, 3, 4, 5])  # Returns 1
```

---

### 10. **Get Random Choice**
Returns a random element from a given list.

**Example Usage:**
```python
random_choice = get_random_choice([1, 2, 3, 4, 5])  # Returns a random element from the list
```

---

### 11. **Generate Unique ID**
Generates a unique identifier (UUID).

**Example Usage:**
```python
unique_id = generate_unique_id()  # Returns a unique UUID
```

---

### 12. **Concatenate Lists**
Concatenates two lists into one.

**Example Usage:**
```python
concatenated = concatenate_lists([1, 2], [3, 4])  # Returns [1, 2, 3, 4]
```

---

### 13. **Contains Swears**
Checks if a string contains any profane language.

**Example Usage:**
```python
contains = contains_swears("This is bad!")  # Returns True if profane words are found
```

---

### 14. **Filter Swears in Text**
Censors any profane language in a string.

**Example Usage:**
```python
censored_text = filter_swears_in_text("This is bad!")  # Censors bad words in the text
```

---

### 15. **Uppercase List**
Converts all strings in a list to uppercase.

**Example Usage:**
```python
uppercase_list = uppercase_list(["apple", "banana"])  # Returns ['APPLE', 'BANANA']
```

---

### 16. **Remove Duplicates**
Removes duplicate values from a list.

**Example Usage:**
```python
unique_list = remove_duplicates([1, 2, 3, 3, 4])  # Returns [1, 2, 3, 4]
```

---

### 17. **Find Index of Element**
Finds the index of an element in a list. Returns -1 if the element is not found.

**Example Usage:**
```python
index = find_index([1, 2, 3], 2)  # Returns 1
```

---

### 18. **Random Element from List**
Selects a random element from a list.

**Example Usage:**
```python
random_element = random_element([1, 2, 3, 4, 5])  # Randomly returns one element from the list
```

---

### 19. **Validate Email**
Validates an email address format using regex.

**Example Usage:**
```python
is_valid = validate_email("test@example.com")  # Returns True if valid
```

---

### 20. **Split Text into Chunks**
Splits a string into smaller chunks of a specified size.

**Example Usage:**
```python
chunks = split_into_chunks("HelloWorld", 3)  # Returns ['Hel', 'loW', 'orl', 'd']
```

---

### 21. **Generate Password (Weak, Medium, Strong)**
Generates a password of varying strength levels based on the parameter.

**Example Usage:**
```python
weak_pass = genpass("Weak")  # Generates a weak password
medium_pass = genpass("Medium")  # Generates a medium password
strong_pass = genpass("Strong")  # Generates a strong password
```

---

### 22. **Unique Elements**
Removes duplicate elements from a list and returns unique values.

**Example Usage:**
```python
unique_values = unique_elements([1, 2, 2, 3])  # Returns [1, 2, 3]
```

---

### 23. **Sum of List**
Calculates the sum of a list of numbers.

**Example Usage:**
```python
total = sum_list([1, 2, 3, 4])  # Returns 10
```

---

### 24. **Reverse List**
Reverses the order of a list.

**Example Usage:**
```python
reversed_lst = reverse_list([1, 2, 3])  # Returns [3, 2, 1]
```

---

### 25. **Check if Prime**
Checks if a number is prime.

**Example Usage:**
```python
is_prime_number = is_prime(7)  # Returns True if the number is prime
```

---

### 26. **Shorten Text**
Shortens text to a specified length, appending "..." if it exceeds the length.

**Example Usage:**
```python
short_text = shorten_text("This is a long text.", 10)  # Returns "This is a..."
```

---

### 27. **Word Count**
Counts the number of words in a string.

**Example Usage:**
```python
word_count = word_count("Hello world!")  # Returns 2
```

---

### 28. **Validate Phone Number**
Validates a phone number format using regex.

**Example Usage:**
```python
is_valid_phone = is_valid_phone_number("+1234567890")  # Returns True if valid
```

---

### 29. **Clean Null Values**
Removes null values (None, empty strings, etc.) from a list or dictionary.

**Example Usage:**
```python
cleaned_data = clean_null([None, "", "Hello", 0])  # Returns ["Hello"]
```

---

### 30. **Calculate Average**
Calculates the average of numbers in a list.

**Example Usage:**
```python
average = calculate_average([1, 2, 3, 4, 5])  # Returns 3
```

---

### 31. **Calculate Median**
Calculates the median of a list of numbers.

**Example Usage:**
```python
median = calculate_median([1, 3, 3, 6, 7, 8, 9])  # Returns 6
```

---

### 32. **Count Words**
Counts the number of words in a text.

**Example Usage:**
```python
words = count_words("This is a sentence.")  # Returns 5
```

---

### 33. **Count Sentences**
Counts the number of sentences in a text.

**Example Usage:**
```python
sentences = count_sentences("This is one sentence. This is another.")  # Returns 2
```

---

### 34. **Word Frequencies**
Counts the frequency of each word in a text.

**Example Usage:**
```python
freq = word_frequencies("apple apple banana orange apple")  # Returns {'apple': 3, 'banana': 1, 'orange': 1}
```

---

### 35. **Common Words Between Texts**
Finds common words between two texts.

**Example Usage:**
```python
common = common_words("I love programming", "I love coding")  # Returns ['I', 'love']
```

---

### 36. **Extract Keywords**
Extracts the top `n` keywords from a text using TF-IDF.

**Example Usage:**
```python
keywords = extract_keywords("This is a sample text for keyword extraction.", 5)  # Returns top 5 keywords
```

---

### 37. **Evaluate Text Length**
Calculates the average word and sentence lengths in a text.

**Example Usage:**
```python
avg_word_length, avg_sentence_length = evaluate_text_length("This is a sentence. This is another.")  # Returns (3.8, 5)
```

---

### 38. **Sentiment Analysis**
Analyzes the sentiment (positive, negative, or neutral) of a text.

**Example Usage:**
```python
sentiment = sentiment_analysis("I love this product!")  # Returns "Positive"
```

---

### 39. **Contains Specific String**
Checks if a string contains any of the characters in a specified list.

**Example Usage:**
```python
contains = containsstr("Hello world!", "aeiou")  # Returns True if vowels are found
```

---

### 40. **Remove Alphabet**
Removes all alphabetic characters from a string.

**Example Usage:**
```python
non_alpha = rem_alphabet("Hello 123!")  # Returns " 123!"
```

---

### 41. **Copy to Clipboard**
Copies text to the clipboard.

**Example Usage:**
```python
copy_to_clipboard("This text is copied!")  # Copies the text to clipboard
```

---

### 42. **Paste from Clipboard**
Pastes the text from the clipboard.

**Example

 Usage:**
```python
text = paste_from_clipboard()  # Returns the clipboard text
```

---

### 43. **String Case Count**
Counts the number of uppercase and lowercase letters in a string.

**Example Usage:**
```python
uppercase, lowercase = string_case_count("Hello World!")  # Returns (2, 8)
```