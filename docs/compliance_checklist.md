# Compliance Verification Checklist

This document provides a comprehensive checklist for verifying compliance of the Mutual Fund FAQ Assistant responses.

## Pre-Response Compliance Check

### Query Classification
- [ ] Query is classified correctly (factual/advisory/out-of-scope)
- [ ] Advisory queries are detected with confidence > 0.5
- [ ] Out-of-scope queries are detected correctly
- [ ] Factual queries are not misclassified as advisory

### Refusal Handling
- [ ] Advisory queries trigger refusal response
- [ ] Out-of-scope queries trigger refusal response
- [ ] Refusal response contains educational links (AMFI/SEBI)
- [ ] Refusal response is polite and helpful
- [ ] Refusal response does not provide any advice

## Post-Response Compliance Check

### Advisory Language Check
- [ ] Response does NOT contain: should, better, recommend, advice, best, worst, good, bad, top, suggest, worth, prefer, choose
- [ ] Response does NOT contain comparative terms: vs, compared to, versus
- [ ] Response does NOT contain investment recommendations
- [ ] Response does NOT contain performance predictions
- [ ] Response does NOT contain future guarantees
- [ ] Response does NOT contain subjective opinions

### Content Verification
- [ ] Response is factual only
- [ ] Response contains no opinions
- [ ] Response contains no subjective statements
- [ ] Response contains no investment advice
- [ ] Response contains no buy/sell/hold recommendations
- [ ] Response contains no portfolio allocation suggestions

### Source Citation Check
- [ ] Response includes source URL
- [ ] Source URL is valid and accessible
- [ ] Source URL is from a trusted source (Groww, AMC website)
- [ ] Source URL is relevant to the query
- [ ] Source URL is the most relevant from retrieved chunks
- [ ] If multiple sources, official AMC documents are preferred

### Response Format Check
- [ ] Response is ≤ 3 sentences
- [ ] Response is concise and clear
- [ ] Response is grammatically correct
- [ ] Response is easy to understand
- [ ] Response directly answers the query

### Footer and Disclaimer Check
- [ ] Response includes "Source: <URL>"
- [ ] Response includes "Last updated from sources: YYYY-MM-DD"
- [ ] UI displays disclaimer prominently
- [ ] Disclaimer mentions SEBI-registered advisor
- [ ] Disclaimer states system provides factual information only
- [ ] Disclaimer states no investment advice provided

## Performance Query Specific Check

### Performance Query Detection
- [ ] Performance queries are detected correctly
- [ ] Response includes factsheet link
- [ ] Response does NOT provide performance numbers
- [ ] Response does NOT make performance comparisons
- [ ] Response directs user to official factsheet

## Edge Case Compliance Check

### Unknown Scheme
- [ ] Unknown scheme queries are handled gracefully
- [ ] Response indicates information not available
- [ ] No hallucinations for unknown schemes

### Ambiguous Queries
- [ ] Ambiguous queries are handled gracefully
- [ ] Response attempts clarification or provides general info
- [ ] No incorrect assumptions made

### Empty/Invalid Queries
- [ ] Empty queries trigger error message
- [ ] Whitespace-only queries trigger error message
- [ ] Error messages are helpful and polite

## System-Level Compliance Check

### Disclaimer Display
- [ ] Disclaimer is displayed on every page
- [ ] Disclaimer is prominent (yellow banner or similar)
- [ ] Disclaimer text matches regulatory requirements
- [ ] Disclaimer cannot be easily dismissed

### Educational Links
- [ ] AMFI link is correct: https://www.amfiindia.com/investor-education
- [ ] SEBI link is correct: https://investor.sebi.gov.in/
- [ ] Links are clickable and accessible
- [ ] Links open in new tab

### API Compliance
- [ ] API responses include source URL
- [ ] API responses include last updated date
- [ ] API responses do not contain advisory content
- [ ] API responses are validated before sending

## Automated Compliance Checks

### Content Filtering
- [ ] Advisory language is filtered out
- [ ] Recommendation patterns are blocked
- [ ] Excessive advisory language triggers block
- [ ] Compliance layer validates all responses

### Response Validation
- [ ] Sentence count is validated (≤ 3)
- [ ] Source presence is validated
- [ ] Compliance status is logged
- [ ] Non-compliant responses are blocked

## Manual Verification Checklist

### Sample Query Testing (50+ queries)
- [ ] 10 expense ratio queries verified
- [ ] 10 exit load queries verified
- [ ] 10 SIP/investment queries verified
- [ ] 10 fund category queries verified
- [ ] 10 document download queries verified
- [ ] 10 advisory queries verified (all refused)
- [ ] 10 out-of-scope queries verified (all refused)
- [ ] 10 performance queries verified (factsheet links)

### Cross-Check Against Sources
- [ ] Responses cross-checked against source documents
- [ ] Numbers/percentages match exactly
- [ ] Dates are correct
- [ ] No contradictory information
- [ ] No hallucinations detected

## Compliance Audit Log

| Date | Query Type | Total Checked | Passed | Failed | Issues Found | Action Taken |
|------|------------|---------------|--------|--------|--------------|--------------|
| YYYY-MM-DD | Factual | 50 | 48 | 2 | [Details] | [Action] |
| YYYY-MM-DD | Advisory | 20 | 20 | 0 | [Details] | [Action] |
| YYYY-MM-DD | Out-of-Scope | 10 | 10 | 0 | [Details] | [Action] |
| YYYY-MM-DD | Performance | 10 | 10 | 0 | [Details] | [Action] |

## Issue Severity Classification

### Critical (Immediate Action Required)
- Advisory content in responses
- Missing source citations
- Incorrect factual information
- System crashes
- Compliance violations

### High (Fix Within 24 Hours)
- Response time > 5 seconds
- Retrieval accuracy < 70%
- Missing footer/disclaimer
- Invalid source URLs

### Medium (Fix Within 1 Week)
- Response time 3-5 seconds
- Retrieval accuracy 70-85%
- Minor formatting issues
- Edge case handling improvements

### Low (Fix Within 1 Month)
- UI improvements
- Documentation updates
- Nice-to-have features
- Performance optimizations

## Compliance Sign-Off

### Pre-Deployment Checklist
- [ ] All critical issues resolved
- [ ] All high-priority issues resolved
- [ ] 50+ sample queries verified
- [ ] Cross-check against sources completed
- [ ] Compliance layer tested
- [ ] Refusal handling tested
- [ ] Educational links verified
- [ ] Disclaimer text verified
- [ ] Performance benchmarks met
- [ ] Response time < 3 seconds
- [ ] Retrieval accuracy > 85%

### Sign-Off
- **QA Engineer**: ___________________ Date: _______
- **Compliance Officer**: ___________________ Date: _______
- **Product Owner**: ___________________ Date: _______

## Continuous Compliance Monitoring

### Daily Checks
- [ ] Monitor query logs for advisory content
- [ ] Check compliance layer logs
- [ ] Verify source citation rate
- [ ] Monitor response times

### Weekly Reviews
- [ ] Review new issues and bugs
- [ ] Analyze query patterns
- [ ] Check compliance violation trends
- [ ] Update test cases as needed

### Monthly Audits
- [ ] Comprehensive quality audit
- [ ] Review KPIs and metrics
- [ ] Update compliance rules
- [ ] Retrain models if needed

### Quarterly Reviews
- [ ] Full system review
- [ ] Update documentation
- [ ] Review regulatory changes
- [ ] Plan improvements
