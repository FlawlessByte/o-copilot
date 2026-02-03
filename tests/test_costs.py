from decimal import Decimal

from app.costs import compute_credits


def test_hello_world_hello_clamps_to_minimum_one():
    # Base: 1
    # Char cost: 17 * 0.05 = 0.85 => 1.85
    # Words: Hello(5), world(5), hello(5) => 3 * 0.2 = 0.6 => 2.45
    # Third vowels: none
    # Unique word bonus (case-sensitive): "Hello" != "hello" so all unique => -2 => 0.45
    # Minimum cost is still 1.
    assert compute_credits("Hello world hello") == Decimal("1")


def test_hello_olleh_is_palindrome_after_normalization_and_doubles():
    # Normalized: "helloolleh" is a palindrome, so final cost doubles (after clamp).
    assert compute_credits("Hello olleH") == Decimal("1.9")


def test_generate_d_expected_value():
    assert compute_credits(
        "Generate-d a Tenant Obligations Report for the new lease terms."
    ) == Decimal("6.05")


def test_empty_string_is_base_cost_only():
    assert compute_credits("") == Decimal("1")


def test_third_vowels_counts_upper_and_lowercase():
    # Positions 3,6,9,... (1-indexed). For "aAaei":
    # index 3 is 'a' => +0.3, others none.
    # Base: 1
    # Char: 5 * 0.05 = 0.25 => 1.25
    # Word: "aAaei" length 5 => +0.2 => 1.45
    # Third vowel: +0.3 => 1.75
    # Unique word bonus: single word => -2 clamp => 1
    # Palindrome: normalized "aaaei" is not palindrome => no doubling
    assert compute_credits("aAaei") == Decimal("1")


def test_length_penalty_over_100_chars_applies():
    # 101 'a's:
    # Base 1 + char 101*0.05=5.05 + penalty 5 = 11.05
    # Word multiplier for one long word => +0.3 => 11.35
    # Third vowels: every 3rd is 'a' => floor(101/3)=33 occurrences => +9.9 => 21.25
    # Palindrome: all 'a's is palindrome => double => 42.50
    # Unique bonus: -2 => 40.50
    
    s = "a" * 101
    assert compute_credits(s) == Decimal("40.50")


def test_unique_word_bonus_not_applied_when_duplicate_case_sensitive():
    # "Hello hello" are different case? Actually both have capital H? Here we ensure duplicate exactly.
    # With duplicate word, unique bonus should not apply.
    result = compute_credits("hello hello")
    assert result > Decimal("1")


def test_non_palindrome_no_doubling():
    # "abc" normalized is "abc", not a palindrome -> no doubling.
    # Base 1 + char 0.15 = 1.15
    # Word len 3 => +0.1 => 1.25
    # Third vowels: position 3 is 'c' -> none
    # Unique bonus: -2 clamp -> 1
    assert compute_credits("abc") == Decimal("1")

