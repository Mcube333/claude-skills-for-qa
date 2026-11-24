# Coding exercises for SDET interviews (Java; Python equivalents are fine)

## Beginner (L0)
0a. Print numbers 1-50; print "Fizz" for multiples of 3, "Buzz" for 5, "FizzBuzz" for both.
0b. Find the largest number in an array.
0c. Count vowels in a string.
0d. Swap two numbers without a third variable.
0e. Check if a number is prime.

Ask the user to solve in Java, think aloud, then write 2-3 test cases (JUnit/TestNG) for their own
solution. Review for correctness, edge cases, complexity, naming and tests.

## Warm-up
1. Reverse a string without built-in reverse; then reverse each word in a sentence.
2. Check if a string is a palindrome ignoring case and non-letters.
3. Count character frequency; return the first non-repeating character.
4. Find duplicates in an array/list.
5. Remove duplicates from a list while keeping order.

## Medium
6. Two-sum: indices of two numbers adding up to a target.
7. Check if two strings are anagrams.
8. Find the second largest number in an array (handle duplicates and short arrays).
9. Validate balanced brackets `({[]})`.
10. Group words by anagram.
11. Merge two sorted arrays.
12. Find the missing number in 1..n.

## Automation-flavoured
13. Given a list of product prices as strings ("Rs. 1,499"), return them as numbers and check they are sorted ascending.
14. Parse a JSON-like map of an API response and assert required keys and types.
15. Write a retry utility: run a supplier up to n times with backoff until a condition is true (no Thread.sleep in tests themselves - discuss where waiting belongs).
16. Thread-safe counter / map used by parallel tests: show the bug with HashMap and fix it.
17. Page Object for a login page (Playwright or Selenium) with one positive and one negative test.
18. REST Assured test for GET /users/{id}: status, schema, a field value, and a 404 case.

## SQL (verbal or written)
19. Second highest salary.
20. Customers with no orders.
21. Orders whose total does not match the sum of line items.

Edge cases to look for: empty input, null, one element, duplicates, negative numbers, Unicode, very large input.

## Expert (L3-L4)
22. Design a thread-safe test data pool that hands out unique accounts to parallel tests and returns them after use.
23. Write a small retry-with-backoff wrapper for API calls that distinguishes retryable (5xx, timeouts) from non-retryable errors.
24. Parse a JUnit XML report and compute pass rate, flaky tests (passed on retry) and slowest 5 tests.
25. Implement a simple rate limiter or circuit breaker and write tests for it.
26. Review a given flaky Playwright/Selenium test and refactor it (shared state, hard waits, brittle locators).
