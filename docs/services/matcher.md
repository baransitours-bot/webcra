# Matcher Service Documentation

The Matcher Service scores user eligibility for visas and ranks them by fit.

## Quick Start

```bash
# Interactive mode (recommended for first-time users)
python main.py match --interactive

# With profile file
python main.py match --profile user_profile.json

# Country-specific matching
python main.py match --profile user.json --country australia
```

## User Profile Format

Create `user_profile.json`:

```json
{
  "age": 28,
  "education": "bachelor",
  "work_experience": 5,
  "occupation": "software engineer",
  "language": {
    "english": {
      "ielts": 7.5
    }
  },
  "countries_of_interest": ["australia", "canada"]
}
```

### Education Levels

- `phd` - Doctoral degree
- `master` - Master's degree
- `bachelor` - Bachelor's degree
- `diploma` - Diploma/Associate degree
- `secondary` - High school

## Scoring Algorithm

### Eligibility Score (0-100%)

Weighted scoring:
- **Age**: 25% - Closer to middle of range = higher score
- **Education**: 30% - Higher qualification = higher score
- **Work Experience**: 25% - More years = higher score (up to required)
- **Language**: 20% - Higher scores = higher score

### Example Calculation

**Visa Requirements:**
- Age: 18-45
- Education: Bachelor's
- Experience: 3 years
- IELTS: 6.5

**User Profile:**
- Age: 30 (middle of range) → 100%
- Education: Master's (exceeds) → 100%
- Experience: 5 years (exceeds) → 100%
- IELTS: 7.5 (exceeds) → 100%

**Total Score**: 25% + 30% + 25% + 20% = **100%**

## Configuration

File: `services/matcher/config.yaml`

```yaml
scoring:
  weights:
    age: 0.25
    education: 0.30
    work_experience: 0.25
    language: 0.20

education_hierarchy:
  phd: 5
  master: 4
  bachelor: 3
  diploma: 2
  secondary: 1
```

## Output Format

```json
{
  "user_profile": {...},
  "total_visas_evaluated": 45,
  "matches": [
    {
      "visa_type": "Skilled Independent Visa (Subclass 189)",
      "country": "australia",
      "category": "work",
      "eligibility_score": 95.5,
      "requirements": {...},
      "gaps": [],
      "strengths": ["Education exceeds requirement", "Strong language scores"]
    }
  ]
}
```

## Features

### 1. Interactive Profile Builder

Guides users through profile creation:

```
🤔 Let's build your profile...

What is your age? 28
What is your education level? bachelor
How many years of work experience? 5
...
```

### 2. Gap Identification

Shows what's missing:

```
Gaps:
  ❌ Age: 46 (maximum is 45)
  ❌ IELTS: 6.0 (minimum is 6.5)
```

### 3. Strength Highlighting

Shows advantages:

```
Strengths:
  ✅ Education exceeds requirement
  ✅ Experience: 8 years (required: 3)
```

### 4. Country Filtering

Focus on specific countries:

```bash
python main.py match --profile user.json --country canada
```

## Troubleshooting

### No Matches Found

**Solutions:**
1. Check if structured data exists: `ls data/structured/`
2. Lower expectations (try different countries)
3. Review gaps in output

### Low Scores

**Causes:**
- Age outside range
- Missing required qualifications
- Insufficient experience

**Solutions:**
- Look for visas with lower requirements
- Consider skill upgrading
- Review alternative visa categories

## See Also

- [Classifier Service](classifier.md) - Generates structured data
- [Assistant Service](assistant.md) - Ask questions about matches
- [Configuration Guide](../guides/configuration.md)

---

**Previous**: [← Classifier Service](classifier.md) | **Next**: [Assistant Service →](assistant.md)
