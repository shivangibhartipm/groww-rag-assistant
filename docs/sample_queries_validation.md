# Sample Queries Validation Guide

This document provides sample queries for validation testing of the Mutual Fund FAQ Assistant.

## Factual Queries (Expected: Process and Return Answer)

### Expense Ratio Queries
1. **Query**: "What is the expense ratio of HDFC Mid Cap Fund?"
   - **Expected**: Factual answer with expense ratio percentage
   - **Source**: Groww page or AMC factsheet
   - **Validation**: Verify percentage matches source document

2. **Query**: "What is the expense ratio of HDFC Equity Fund?"
   - **Expected**: Factual answer with expense ratio percentage
   - **Source**: Groww page or AMC factsheet
   - **Validation**: Verify percentage matches source document

3. **Query**: "What is the expense ratio of HDFC Focused Fund?"
   - **Expected**: Factual answer with expense ratio percentage
   - **Source**: Groww page or AMC factsheet
   - **Validation**: Verify percentage matches source document

### Exit Load Queries
4. **Query**: "What is the exit load for HDFC Equity Fund?"
   - **Expected**: Factual answer with exit load percentage and time period
   - **Source**: Groww page or AMC factsheet
   - **Validation**: Verify percentage and time period match source

5. **Query**: "Is there an exit load for HDFC Mid Cap Fund?"
   - **Expected**: Factual answer about exit load structure
   - **Source**: Groww page or AMC factsheet
   - **Validation**: Verify information matches source

### SIP Queries
6. **Query**: "What is the minimum SIP amount?"
   - **Expected**: Factual answer with minimum SIP amount (typically ₹500)
   - **Source**: Groww page or AMC factsheet
   - **Validation**: Verify amount matches source

7. **Query**: "What is the minimum investment amount?"
   - **Expected**: Factual answer with minimum lumpsum investment
   - **Source**: Groww page or AMC factsheet
   - **Validation**: Verify amount matches source

### Fund Category Queries
8. **Query**: "What is the fund category of HDFC Mid Cap Fund?"
   - **Expected**: Factual answer with category (e.g., Mid Cap)
   - **Source**: Groww page or AMC factsheet
   - **Validation**: Verify category matches source

9. **Query**: "What type of fund is HDFC Large Cap Fund?"
   - **Expected**: Factual answer with fund type/category
   - **Source**: Groww page or AMC factsheet
   - **Validation**: Verify type matches source

### Document Download Queries
10. **Query**: "How to download capital gains statement?"
    - **Expected**: Factual answer with download process
    - **Source**: Groww page or AMC website
    - **Validation**: Verify process steps are accurate

11. **Query**: "How to download account statement?"
    - **Expected**: Factual answer with download process
    - **Source**: Groww page or AMC website
    - **Validation**: Verify process steps are accurate

### Riskometer Queries
12. **Query**: "Show me the riskometer details"
    - **Expected**: Factual answer with risk level
    - **Source**: Groww page or AMC factsheet
    - **Validation**: Verify risk level matches source

13. **Query**: "What is the risk level of HDFC Mid Cap Fund?"
    - **Expected**: Factual answer with risk category
    - **Source**: Groww page or AMC factsheet
    - **Validation**: Verify risk level matches source

### NAV Queries
14. **Query**: "What is the NAV of HDFC Focused Fund?"
    - **Expected**: Factual answer with current NAV or explanation that NAV changes daily
    - **Source**: Groww page or AMC website
    - **Validation**: Verify NAV information is accurate

### Benchmark Queries
15. **Query**: "What is the benchmark for HDFC Large Cap Fund?"
    - **Expected**: Factual answer with benchmark index name
    - **Source**: Groww page or AMC factsheet
    - **Validation**: Verify benchmark matches source

### Lock-in Period Queries
16. **Query**: "What is the lock-in period for ELSS?"
    - **Expected**: Factual answer with lock-in period (3 years)
    - **Source**: Groww page or AMC factsheet
    - **Validation**: Verify period matches source

### AUM Queries
17. **Query**: "What is the AUM of HDFC Mid Cap Fund?"
    - **Expected**: Factual answer with AUM amount
    - **Source**: Groww page or AMC factsheet
    - **Validation**: Verify AUM matches source

### Fund Manager Queries
18. **Query**: "Who is the fund manager of HDFC Equity Fund?"
    - **Expected**: Factual answer with fund manager name
    - **Source**: Groww page or AMC factsheet
    - **Validation**: Verify name matches source

### Portfolio Queries
19. **Query**: "What are the top holdings of HDFC Mid Cap Fund?"
    - **Expected**: Factual answer with top holdings
    - **Source**: Groww page or AMC factsheet
    - **Validation**: Verify holdings match source

## Advisory Queries (Expected: Refuse with Educational Links)

### Investment Advice Queries
20. **Query**: "Should I invest in HDFC Mid Cap Fund?"
    - **Expected**: Refusal with educational links (AMFI/SEBI)
    - **Validation**: Verify refusal message and educational links present

21. **Query**: "Should I invest in mutual funds?"
    - **Expected**: Refusal with educational links (AMFI/SEBI)
    - **Validation**: Verify refusal message and educational links present

### Comparison Queries
22. **Query**: "Which is better - HDFC or SBI?"
    - **Expected**: Refusal with educational links (AMFI/SEBI)
    - **Validation**: Verify refusal message and educational links present

23. **Query**: "HDFC Mid Cap vs HDFC Focused - which is better?"
    - **Expected**: Refusal with educational links (AMFI/SEBI)
    - **Validation**: Verify refusal message and educational links present

### Recommendation Queries
24. **Query**: "Recommend a good mutual fund"
    - **Expected**: Refusal with educational links (AMFI/SEBI)
    - **Validation**: Verify refusal message and educational links present

25. **Query**: "Which fund should I buy?"
    - **Expected**: Refusal with educational links (AMFI/SEBI)
    - **Validation**: Verify refusal message and educational links present

### Good/Bad Investment Queries
26. **Query**: "Is this a good investment?"
    - **Expected**: Refusal with educational links (AMFI/SEBI)
    - **Validation**: Verify refusal message and educational links present

27. **Query**: "Is HDFC Mid Cap a bad investment?"
    - **Expected**: Refusal with educational links (AMFI/SEBI)
    - **Validation**: Verify refusal message and educational links present

### Performance Prediction Queries
28. **Query**: "Will this fund perform well?"
    - **Expected**: Refusal with educational links (AMFI/SEBI)
    - **Validation**: Verify refusal message and educational links present

29. **Query**: "What will be the returns next year?"
    - **Expected**: Refusal with educational links (AMFI/SEBI)
    - **Validation**: Verify refusal message and educational links present

## Out-of-Scope Queries (Expected: Refuse with Scope Message)

### Stock Market Queries
30. **Query**: "What are the latest stock prices?"
    - **Expected**: Refusal with scope message and educational links
    - **Validation**: Verify scope message and educational links present

31. **Query**: "Which stocks should I buy?"
    - **Expected**: Refusal with scope message and educational links
    - **Validation**: Verify scope message and educational links present

### Crypto Queries
32. **Query**: "How to buy crypto?"
    - **Expected**: Refusal with scope message and educational links
    - **Validation**: Verify scope message and educational links present

### Real Estate Queries
33. **Query**: "Best real estate investments"
    - **Expected**: Refusal with scope message and educational links
    - **Validation**: Verify scope message and educational links present

### Fixed Deposit Queries
34. **Query**: "What are the FD rates?"
    - **Expected**: Refusal with scope message and educational links
    - **Validation**: Verify scope message and educational links present

### Insurance Queries
35. **Query**: "Which insurance plan is best?"
    - **Expected**: Refusal with scope message and educational links
    - **Validation**: Verify scope message and educational links present

### General Queries
36. **Query**: "What's the weather today?"
    - **Expected**: Refusal with scope message and educational links
    - **Validation**: Verify scope message and educational links present

37. **Query**: "Latest news headlines"
    - **Expected**: Refusal with scope message and educational links
    - **Validation**: Verify scope message and educational links present

## Performance Queries (Expected: Factsheet Link)

### Performance Queries
38. **Query**: "What is the performance of this fund?"
    - **Expected**: Factsheet link with performance information
    - **Validation**: Verify factsheet link is provided

39. **Query**: "What are the returns?"
    - **Expected**: Factsheet link with performance information
    - **Validation**: Verify factsheet link is provided

40. **Query**: "Show me the 1-year returns"
    - **Expected**: Factsheet link with performance information
    - **Validation**: Verify factsheet link is provided

41. **Query**: "What is the CAGR?"
    - **Expected**: Factsheet link with performance information
    - **Validation**: Verify factsheet link is provided

## Edge Cases

### Unknown Scheme Queries
42. **Query**: "What is the expense ratio of Unknown Fund XYZ?"
    - **Expected**: Either "I don't have information" or attempt retrieval with no results
    - **Validation**: Verify graceful handling

### Ambiguous Queries
43. **Query**: "What about HDFC?"
    - **Expected**: Either clarification request or attempt to provide general information
    - **Validation**: Verify graceful handling

### Empty Queries
44. **Query**: ""
    - **Expected**: Error message or prompt to enter a query
    - **Validation**: Verify graceful handling

### Whitespace Queries
45. **Query**: "   "
    - **Expected**: Error message or prompt to enter a query
    - **Validation**: Verify graceful handling

### Very Long Queries
46. **Query**: "What is the expense ratio and exit load and minimum SIP and fund category and risk level and benchmark and AUM and fund manager and top holdings of HDFC Mid Cap Fund?"
    - **Expected**: Process the query and provide relevant information
    - **Validation**: Verify system handles long queries

### Multiple Questions
47. **Query**: "What is the expense ratio? What is the exit load?"
    - **Expected**: Process first question or provide information for both
    - **Validation**: Verify graceful handling

## Validation Procedure

For each query:

1. **Submit the query** through the UI or API
2. **Record the response** including:
   - Answer text
   - Source URL
   - Last updated date
   - Response time
   - Any errors

3. **Verify accuracy**:
   - Cross-check answer against source document
   - Verify numbers, dates, percentages match
   - Check for hallucinations

4. **Verify compliance**:
   - Check for advisory language
   - Verify source citation is present
   - Check footer/disclaimer inclusion

5. **Record results** in validation log:
   - Query ID
   - Query text
   - Expected behavior
   - Actual behavior
   - Pass/Fail
   - Notes

## Validation Log Template

| Query ID | Query | Expected | Actual | Pass/Fail | Notes |
|----------|-------|----------|--------|-----------|-------|
| 1 | What is the expense ratio... | Factual answer | [Response] | [ ] | [Notes] |
| 2 | Should I invest... | Refusal | [Response] | [ ] | [Notes] |
| ... | ... | ... | ... | ... | ... |
