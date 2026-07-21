---
name: study-planning
description: "Create and manage long-term study plans (exam prep, certification, structured learning). Data-driven, phase-based, with printable deliverables and recurring check-ins."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [study, planning, exam-prep, timeline, tracking]
    related_skills: [plan, cron-content-pipeline]
---

# Study Planning

Use this skill when the user wants a structured long-term study plan (exam prep, certification, structured learning program).

## Core Workflow

### Step 1: Collect Data

Always gather these before building the plan:

- **Target exam/structure**: what subjects, score breakdown, per-subject weight
- **Today's date & target date**: verify CURRENT date via user, don't assume
- **Weekly available hours**: weekday evenings and weekend hours separately
- **Current skill level**: per subject (beginner/intermediate/advanced)
- **Materials**: textbooks, courses, practice exams the user owns
- **Target school/program**: name, score line, admission requirements
- **Registration deadlines**: check for separate sign-up steps

### Step 2: Verify Dates (CRITICAL)

This is the most error-prone step. Multiple verifications needed:

1. **Confirm today's date** with the user — don't assume from session metadata
2. **Find the exam date** via web_search using `"2027年考研 初试时间"` or equivalent
   - Pattern: 初试通常在12月倒数第二个周末（周六+周日）
   - MEM/管理类联考 **只考周六一天**（上午管综8:30-11:30，下午英语14:00-17:00）
3. **Find registration dates**: 预报名通常10/10-13, 正式报名10/16-27
4. **Verify test date with a calendar check**: confirm what day of week it falls on
5. **Recalculate total days**: from start date to exam date

**Pitfall: Don't guess dates.** Search the web to verify. The official announcement from MOE (教育部) is released ~September, but the pattern is stable across years.

### Step 3: Calculate Study Time

- Total days = end_date - start_date (inclusive of both ends)
- Total weeks = total_days / 7
- Total study hours = weekly_hours × total_weeks
- Subject hours allocation = proportional to score weight

Example: 管综200分/300分=67% → ~11h/week of 16h total

### Step 4: Design Phases

Standard four-phase structure:

| Phase | Name | Duration | Focus |
|-------|------|----------|-------|
| P1 | 基础搭建 (Foundation) | ~40% of time | First pass through materials, build framework |
| P2 | 强化提升 (Intensification) | ~25% | Subject-specific drills, start writing |
| P3 | 真题冲刺 (Practice Exams) | ~25% | Full past papers under timed conditions |
| P4 | 模考冲刺 (Final Sprint) | ~10% | Full mock exams, templates finalization, state prep |

For exam prep with ~25 weeks:
- P1: ~10 weeks (foundation, build gradually)
- P2: ~6 weeks (intensify, problem sets)
- P3: ~7 weeks (past exam papers chronologically)
- P4: ~2 weeks (final mocks, templates, rest)

### Step 5: Build Printable Deliverable

Generate an HTML file with:
- **Phase headers** with color coding (1 per page section in landscape A4)
- **Week-by-week table**: week #, date range, checkbox, per-subject tasks
- **Weekly check-in grid**: blank rows for hand-written progress tracking
- **Exam day details**: time, subjects, order
- **Print-friendly CSS**: `@page { size: A4 landscape; }`, media print rules
- **Milestone callouts**: registration deadlines highlighted in red

Upload to R2 when possible for the user to download as a link.

### Step 6: Set Up Check-in Cadence

Explain to the user:
- Weekly check-in: report progress each weekend
- The agent adjusts next week's plan based on completion rate
- If falling behind, escalate to me for a catch-up plan

## Weekly Check-in Format

When the user reports back:

1. Verify which week they're on
2. Ask: "Did you complete the planned tasks? What was hard?"
3. Adjust next week's load: lighter if struggling, maintain if on track, accelerate if ahead
4. Set up a TODO for the next week's tasks

## Per-Subject Guidance Patterns

### English (for non-native speakers)
- 六级+ level: skip intensive vocabulary, focus on reading speed + exam strategy
- Maintain daily contact: 20min reading minimum
- Earlier years' reading sections are best practice material
- Prioritize: Reading Comprehension → Translation → Writing → Cloze

### Math (for 管理类联考 初等数学)
- Covers: Arithmetic, Algebra, Geometry, Data Analysis
- Foundation phase: textbook chapter by chapter
- Intensification: drill by problem type
- Key: speed — 25 questions in 55 minutes = just over 2 min/question

### Logic
- Three types: Formal Logic, Argument Logic, Analytical Reasoning
- Zero-based learners: start with concept understanding, not speed
- Build from: concepts → reasoning types → problem set drilling

### Writing
- Two essays: 论证有效性分析 (find logical fallacies) + 论说文 (argumentative)
- P1-P2: understand structure, collect material
- P3: actually write under timed conditions
- P4: finalize 2-3 templates per essay type

## Pitfalls

- **Date errors**: always double-check exam date with multiple web sources and a calendar confirmation. Users notice and will correct you.
- **Over-ambition**: 16h/week is sustainable; don't assign more than available hours
- **Ignoring registration deadlines**: missing the registration window means the entire plan is wasted. Mark it RED in the deliverable.
- **Assuming today's date**: always confirm the current date with the user
- **Printable HTML**: design for A4 landscape, include checkboxes that work on paper, use sticky phase headers for scroll-on-screen use too

## Support Files

- `references/mem-exam.md` — MEM-specific reference: exam structure, score lines, target school data, registration timeline, textbook info

## Verification Checklist

After creating the plan:
- [ ] Exam date verified via web_search + calendar check
- [ ] Registration deadlines confirmed
- [ ] Total days/weeks recalculated correctly
- [ ] Weekly hours match user's stated availability
- [ ] Subject allocation matches score weight
- [ ] Printable deliverable uploaded to R2
- [ ] Check-in cadence explained to user
- [ ] TODO set for first week's tasks
