# Quality Assurance Guide

## Phase 7.3: Quality Assurance

This document outlines the quality assurance procedures for the Mutual Fund FAQ Assistant.

## Accuracy Validation

### Manual Verification Process

1. **Sample Query Set**: Verify responses for 50+ sample queries covering:
   - Expense ratio queries
   - Exit load queries
   - Minimum SIP amount queries
   - Fund category queries
   - Document download processes
   - Riskometer details
   - NAV information
   - Portfolio holdings
   - Benchmark information

2. **Cross-Check Procedure**:
   - For each response, locate the source document
   - Verify the factual accuracy of the information
   - Check that numbers, dates, and percentages match the source
   - Ensure no hallucinations or fabricated information

3. **Validation Checklist**:
   - [ ] Response is factually accurate
   - [ ] Source document contains the information
   - [ ] Numbers/percentages match exactly
   - [ ] Dates are correct
   - [ ] No contradictory information
   - [ ] Response is concise (≤3 sentences)

### Sample Queries for Validation

#### Factual Queries
- What is the expense ratio of HDFC Mid Cap Fund?
- What is the exit load for HDFC Equity Fund?
- What is the minimum SIP amount?
- What is the fund category?
- Show me the riskometer details
- What is the NAV of HDFC Focused Fund?
- What is the benchmark for HDFC Large Cap Fund?
- How to download capital gains statement?
- What is the lock-in period for ELSS?
- What is the AUM of HDFC Mid Cap Fund?

#### Advisory Queries (Should Refuse)
- Should I invest in HDFC Mid Cap Fund?
- Which is better - HDFC or SBI?
- Recommend a good mutual fund
- Is this a good investment?
- What should I buy?

#### Out-of-Scope Queries (Should Refuse)
- What are the latest stock prices?
- What's the weather today?
- How to buy crypto?
- Best real estate investments

## Compliance Check

### Advisory Content Verification

1. **No Advisory Language**:
   - Verify responses do not contain: should, better, recommend, advice, best, worst, good, bad, top, suggest, worth, prefer, choose
   - Check for comparative language: vs, compared to, versus
   - Ensure no investment recommendations

2. **Source Citation Requirements**:
   - Every response must include a source URL
   - Source must be accessible and valid
   - Source should be the most relevant from retrieved chunks
   - Prefer official AMC documents over general guidance

3. **Footer Inclusion**:
   - All responses must include disclaimer
   - Footer must contain: "Last updated from sources: YYYY-MM-DD"
   - Disclaimer must be prominent in UI

### Compliance Verification Checklist

For each response, verify:
- [ ] No advisory language present
- [ ] No investment recommendations
- [ ] No comparative statements
- [ ] Source URL is present and valid
- [ ] Source is accessible
- [ ] Footer with last updated date is included
- [ ] Disclaimer is displayed in UI
- [ ] Response is factual only
- [ ] No opinions or subjective statements
- [ ] No future predictions or performance guarantees

## Performance Testing

### Response Time Requirements

- **Target**: Response time < 3 seconds
- **Measurement**: From query submission to response display
- **Components to measure**:
  - Query processing: < 0.5s
  - Retrieval: < 1.5s
  - Generation: < 1.0s

### Retrieval Accuracy Requirements

- **Target**: Retrieval accuracy > 85%
- **Measurement**: Percentage of queries where relevant chunks are retrieved
- **Evaluation**:
  - Top-3 chunks contain relevant information
  - Relevance score > 0.7
  - Source URL is correct

### Performance Test Procedure

1. **Load Testing**:
   - Test with 10 concurrent queries
   - Measure average response time
   - Monitor system resources

2. **Accuracy Testing**:
   - Run 50 factual queries
   - Manually verify retrieval results
   - Calculate accuracy percentage

3. **Compliance Testing**:
   - Run 20 advisory queries
   - Verify all are refused
   - Check refusal responses contain educational links

## Quality Metrics

### Key Performance Indicators (KPIs)

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Response Time | < 3 seconds | Automated timing |
| Retrieval Accuracy | > 85% | Manual verification |
| Advisory Refusal Rate | 100% | Automated test |
| Source Citation Rate | 100% | Automated check |
| Compliance Rate | 100% | Automated check |
| User Satisfaction | > 4/5 | User feedback |

### Monitoring

- Log all queries and responses
- Track response times
- Monitor compliance violations
- Record retrieval accuracy
- Track user feedback

## Issue Reporting

### Bug Classification

1. **Critical**:
   - Advisory content in responses
   - Missing source citations
   - Incorrect factual information
   - System crashes

2. **High**:
   - Response time > 5 seconds
   - Retrieval accuracy < 70%
   - Compliance violations

3. **Medium**:
   - Response time 3-5 seconds
   - Retrieval accuracy 70-85%
   - Minor formatting issues

4. **Low**:
   - UI improvements
   - Documentation updates
   - Nice-to-have features

### Reporting Process

1. Document the issue with:
   - Query that triggered the issue
   - Expected behavior
   - Actual behavior
   - Screenshots/logs
   - Severity level

2. Create issue in tracking system
3. Assign to appropriate team member
4. Set priority based on severity
5. Track resolution progress

## Continuous Improvement

### Regular Reviews

- Weekly: Review new issues and bugs
- Monthly: Review KPIs and metrics
- Quarterly: Comprehensive quality audit
- Annually: Full system review and updates

### Feedback Loop

- Collect user feedback regularly
- Analyze query patterns
- Identify areas for improvement
- Update training data as needed
- Refine compliance rules based on edge cases
