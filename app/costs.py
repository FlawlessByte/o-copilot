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

import structlog

logger = structlog.get_logger("o-copilot.costs")

BASE_COST = Decimal("1")
CHAR_COST = Decimal("0.05")
THIRD_VOWEL_COST = Decimal("0.3")
LENGTH_PENALTY_COST = Decimal("5")
UNIQUE_WORD_BONUS = Decimal("2")
VOWELS = {"a", "e", "i", "o", "u"}

def _compute_world_length_multiplier(text):
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
    
    total_credits = BASE_COST
    
    char_count = len(text)
    
    if char_count == 0:
        logger.debug("compute_credits", char_count=0, credits=str(total_credits))
        return total_credits
    
    total_credits += Decimal(char_count) * CHAR_COST
    third_vowel_hits = 0
    word_count = 0
    
    # - **Length Penalty:** If the message length exceeds 100 characters, add a penalty of 5 credits.
    if char_count > 100:
        total_credits += LENGTH_PENALTY_COST
        logger.debug("Length penalty applied")

    
    
    tmp = ""
    normed_msg = ""
    words = []
    # tmp_word = ""
    
    for idx, ch in enumerate(text):
        # **Third VOWELS:** If any third (i.e. 3rd, 6th, 9th) character is an uppercase or lowercase vowel (a, e, i, o, u) add 0.3 credits for each occurrence.
        if (idx+1) % 3 == 0 and idx < char_count:
            if ch.lower() in VOWELS:
                total_credits += THIRD_VOWEL_COST
                third_vowel_hits += 1
        
        
        if ch == " ":
            # word ended
            total_credits += _compute_world_length_multiplier(tmp)
            words.append(tmp)
            word_count += 1
            normed_msg += tmp.lower()
            tmp = ""
            # tmp_word = ""
        elif ch.isalnum() or ch == "-" or ch == "'":
            # tmp_word += ch.lower()
            tmp += ch
        
        
    total_credits += _compute_world_length_multiplier(tmp.lower())
    normed_msg += tmp.lower()
    words.append(tmp)
    word_count += 1

    # - **Palindromes:** If the entire message is a palindrome (that is to say, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward), double the total cost after all other rules have been applied.
    if normed_msg == normed_msg[::-1]:
        total_credits += total_credits
        logger.debug("Palindrome found")
        
    # - **Unique Word Bonus: If all words in the message are unique (case-sensitive), subtract 2 credits from the total cost (remember the minimum cost should still be 1 credit).**
    if len(words) == len(set(words)):
        total_credits = max(BASE_COST, total_credits - UNIQUE_WORD_BONUS)
        logger.debug("Unique word bonus applied")
    
    logger.debug(
        "compute_credits",
        char_count=char_count,
        word_count=word_count,
        third_vowel_hits=third_vowel_hits,
        credits=str(total_credits),
    )
    return total_credits

