I built this page.

# User Profile Answers

## 1. Your Data Environment

**Data Warehouses:**
*   **Primary:** Snowflake. The rules explicitly reference Snowflake syntax and warehouse management.
*   **Secondary:** Trino is likely part of the stack, evidenced by the `mcp-trino-viz` repository in your git listing.

**BI Tools:**
*   **Primary:** Looker. You have specific rules regarding Looker instances.
*   **Secondary:** You build custom visualizations using Python (Seaborn, Sankey diagrams) and HTML/JS (D3/Canvas experiments), so you are not limited to standard BI tools.

**Languages:**
*   **Core:** Python (shared venvs), SQL, Bash.
*   **Scripting:** AppleScript (MacOS Automator workflows).
*   **Web:** HTML, JavaScript (Gemini experiments).

**Compute-Cost Considerations:**
*   **Approach:** Efficiency is required but not paralyzing. You mandate `LIMIT` clauses (10, 100, 1000) and require dry-run modes for scripts.
*   **Specifics:** You use Snowflake warehouse management tools (`snowflake-mcp-server`), implying you care about sizing and credit usage.

## 2. Your Technical Depth & Preferences

**SQL Competency:**
*   **Level:** Advanced. You reference CTEs, window functions, and optimization rules. You require strict formatting (leading commas, AND at start of lines) and are aware of specific wildcard behaviors in `WHERE` clauses.

**Explanation Preference:**
*   **Style:** "What exists and how does it work?"
*   **Depth:** You prefer mechanistic understanding over prescriptive "black box" solutions.

**Statistics & ML:**
*   **Comfort:** High. You request specific libraries like `BERTopic` for NLP.
*   **Conventions:** You enforce strict significant figure rules (2 sig figs) for averages and percentiles.
*   **Taxonomy:** You work with complex taxonomies (Machine Simulation, Stock Accuracy), requiring precise definitions.

**Preferred Frameworks:**
*   **NLP:** BERTopic.
*   **General:** Pandas, Seaborn, Scikit-learn (implied).

## 3. Your Problem-Solving Style

**Iteration:**
*   **Method:** You utilize a "Sandbox" environment extensively, suggesting an iterative "prototype to production" workflow.
*   **Safety:** You mandate `--test` or `--dry-run` flags in scripts, preferring to verify before committing to destructive actions.

**Solution Presentation:**
*   **Focus:** You prefer a landscape view ("What exists") rather than a single prescriptive path, unless the answer is obvious.
*   **Constraint:** You expect adherence to strict sprint naming and file naming conventions immediately.

## 4. Your Work Constraints

**Compliance & Security:**
*   **Strict:** You have extensive rules regarding input validation, secret management (env vars), and safe file operations (no user input in paths).
*   **Privacy:** No PII in logs.

**Tech Stack Limitations:**
*   **Product:** Autodesk Fusion (NINVFUS).
*   **Naming:** "Fusion" (never "Fusion 360" unless in URL/filename).
*   **Environment:** MacOS/Windows compatibility required for scripts.

**Timelines:**
*   **Structure:** 2-week continuous sprints.
*   **Naming:** "PDMS Data [Month] [Year] [X]/[Y]".

## 5. Your Learning / Thinking Preferences

**Format:**
*   **Visuals:** You value data visualization (Seaborn, Sankey) and likely learn well from diagrams.
*   **Code:** You require rigorous code quality (linting, security checks) and prefer seeing the implementation details.

**Interaction:**
*   **Directness:** You prefer answers without fluff.
*   **Visuals:** No emojis allowed in markdown.

## 6. Your Role Expectations

**Primary Focus:**
*   **Domain:** Product Design & Manufacturing Solutions (PDMS) Data.
*   **Activities:** You span the full stack from Data Engineering (ETL, SQL, Warehousing) to Analytics (Looker, Notebooks) and Tooling (MCP servers, Python scripts).
*   **Repositories:** You manage analytics for Fusion, Fusion Team, and GD Simulation.
*   **Level:** Senior Principal / Lead Architect. You audit codebases, set standards, and lead technical initiatives.

## 7. How You Want Me to Challenge You

**Style:**
*   **Critique:** You want aggressive error checking. If a methodology is flawed, I must point it out.
*   **Tone:** "Give me funny insults when you found I did any mistakes." You explicitly reject excessive affirmation or compliments.
*   **Correction:** Be direct. Do not sugarcoat security violations or logic gaps.

## 8. Demographic Context (Explicit)

**Work Environment:**
*   **Work Hours:** 07:00 – 18:00 PST.
*   **Lunch:** Avoid contact 12:00 – 13:00 PST.
*   **Location:** Portland, OR (US West).

**Personal:**
*   **Age:** 51
*   **Gender:** Male

## 9. Personal Preferences (Explicit)

**Food & Drink:**
*   **General:** Adventurous eater ("like all foods") but sensitive to heat/spice.
*   **Loves:** Mustard, Wasabi, Korean BBQ, Sushi.
*   **Dislikes:** Kimchi.
*   **Coffee Order:** 1 cream, 2 sugars.
*   **Favorites:** Eggs over easy with toast (Breakfast), Sushi.

**Media & Arts:**
*   **Reading:** Prefers Non-fiction.
*   **Movies:** Sci-Fi, Period pieces.
*   **Key Figures:** Carl Sagan (Writer), Christopher Nolan (Director).
*   **Music:** Eclectic, strong preference for Classical (Bach).

Agent: gemini-3-pro-preview
