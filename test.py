#  [https://owpublic.blob.core.windows.net/tech-task/messages/current-period](https://owpublic.blob.core.windows.net/tech-task/messages/current-period)  
# {
#   "messages": [
#     {
#       "text": "Generate a Tenant Obligations Report for the new lease terms.",
#       "timestamp": "2024-04-29T02:08:29.375Z",
#       "report_id": 5392,
#       "id": 1000
#     },
#     {
#       "text": "Are there any restrictions on alterations or improvements?",
#       "timestamp": "2024-04-29T03:25:03.613Z",
#       "id": 1001
#     },
#   }

# [https://owpublic.blob.core.windows.net/tech-task/reports/:id](https://owpublic.blob.core.windows.net/tech-task/reports/:id)
# {
#   "id": 5392,
#   "name": "Tenant Obligations Report",
#   "credit_cost": 79
# }


# GET request to /usage that returns the usage data for the current billing period

# { 
#     usage: [
#         message_id: number
#         timestamp: string
#         report_name?: string
#         credits_used: number
#     ]
# }


# The number of credits consumed by each message is calculated as follows:

# - When a message has a `report_id` associated with it, ignore the message text, and the fixed number of credits used to generate that report can be found by querying the `reports/:id` endpoint for that `report_id`.
#     - If the `reports/:id` endpoint returns a `HTTP 404` status code for a given `report_id` you must fall back to the calculation method outlined below.
# - For messages without a valid `report_id`, the number of credits consumed is based on the message `text` and following rules apply. (**Note:** A “word” is defined as any continual sequence of letters, plus ‘ and -)
#     - **Base Cost:** Every message has a base cost of 1 credit.
#     - **Character Count:** Add 0.05 credits for each character in the message.

#     
#     
from decimal import Decimal

BASE_COST = 1
vowels = {"a", "e", "i", "o", "u"}

def compute_world_length_multiplier(text):
#         - **Word Length Multipliers:**
#         - For words of 1-3 characters: Add 0.1 credits per word.
#         - For words of 4-7 characters: Add 0.2 credits per word.
#         - For words of 8+ characters: Add 0.3 credits per word.        
    l = len(text)
    
    if l <= 3:
        return Decimal("0.1")
    elif l <= 7:
        return Decimal("0.2")
    else:
        return Decimal("0.3")
    
    
    

def compute_credits(text):
    
    total_credits = Decimal(BASE_COST)
    print(total_credits)
    
    total_chars = len(text)
    
    if total_chars == 0:
        return total_credits
    
    total_credits += Decimal(total_chars * Decimal("0.05"))
    print(total_credits)
    
    # - **Length Penalty:** If the message length exceeds 100 characters, add a penalty of 5 credits.
    if total_chars > 100:
        total_credits += Decimal(5)
    
    
    tmp = ""
    normed_question = ""
    original_words = []
    tmp_word = ""
    
    all_chars = ""
    
    print(total_credits)
    
    for idx, ch in enumerate(text):
        # G:0 e:1 n:2 e:3 r:4 a:5 t:6 e:7
        # **Third Vowels:** If any third (i.e. 3rd, 6th, 9th) character is an uppercase or lowercase vowel (a, e, i, o, u) add 0.3 credits for each occurrence.
        if (idx+1) % 3 == 0 and idx < total_chars:
            if ch.lower() in vowels:
                print(f"Adding 0.3 credits because of the vowel: {ch}")
                total_credits += Decimal("0.3")
        
        
        if ch == " ":
            # word ended
            # print(tmp)
            total_credits += compute_world_length_multiplier(tmp)
            original_words.append(tmp)
            tmp = ""
            normed_question += tmp_word
            tmp_word = ""
        elif ch.isalnum() or ch == "-" or ch == "'":
            tmp_word += ch.lower()
            tmp += ch
        
    total_credits += compute_world_length_multiplier(tmp_word)
    normed_question += tmp_word
    original_words.append(tmp)
    print(f"total credit: {total_credits}")
    
    
    print(f"Original words: {original_words}")
    print(f"Normed normed_words: {normed_question}")
    # - **Palindromes:** If the entire message is a palindrome (that is to say, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward), double the total cost after all other rules have been applied.
    if normed_question == normed_question[::-1]:
        total_credits += total_credits
        
    print(f"total credit: {total_credits}")
        
    # - **Unique Word Bonus: If all words in the message are unique (case-sensitive), subtract 2 credits from the total cost (remember the minimum cost should still be 1 credit).**
    if len(original_words) == len(set(original_words)):
        total_credits = max(1, total_credits - 2)
    
    
    
    return total_credits



print(compute_credits("Generate-d a Tenant Obligations Report for the new lease terms."))
print(compute_credits("Hello world hello"))
print(compute_credits("Hello olleH"))