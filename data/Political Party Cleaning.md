# Political Party Data Cleaning & Normalization

**File:** `data/wp_politeia_political_parties.csv`

## 1. The Issue
The current `wp_politeia_political_parties` table mixes three distinct logical concepts into a single `official_name` string:
1.  **The Political Party** (e.g., "Renovación Nacional").
2.  **The Candidate's Legal Status** (e.g., "Independiente" or "Militante").
3.  **The Electoral Coalition/Pact** (e.g., "Chile Vamos", "Contigo Chile Mejor").

### Examples of Inconsistency
-   **Redundant Entries**:
    -   `Renovación Nacional` (ID 56)
    -   `RN - Chile Vamos` (ID 12)
    -   `Independiente en cupo Renovación Nacional` (ID 62)
    -   `IND ( RN ) - Chile Vamos` (ID 31)
    
    *All four of these refer to the same core political entity (RN) but are treated as distinct "parties" in the database.*

-   **Variable Formatting**:
    -   Some use acronyms: `UDI - Chile Vamos`
    -   Some use full names: `Unión Demócrata Independiente`
    -   Some include "cupo": `Independiente en cupo...`

-   **Spelling Variations**: (Potential risk)
    -   `Renovación Nacional` vs `Renovacion Nacional` creates duplicate IDs.

## 2. Why This Matters
1.  **Analysis Difficulty**: You cannot easily answer "How many votes did RN get total?" because you'd have to sum IDs 12, 31, 56, and 62 manually.
2.  **Data Integrity**: If a party changes its coalition in the next election, we shouldn't create a new "Party" record. The party is constant; the coalition changes.

## 3. Proposed Solution: Schema Normalization

We need to treat the **Party** as a clean, unique entity and move the "Status" and "Coalition" data to the **Candidacy** or **Election** level.

### Step A: Clean `wp_politeia_political_parties`
This table should **only** contain unique, correctly spelled political parties.

| ID | official_name | short_name |
| :--- | :--- | :--- |
| 1 | Renovación Nacional | RN |
| 2 | Unión Demócrata Independiente | UDI |
| 3 | Partido Socialista | PS |
| 4 | Independiente | IND |

### Step B: Update `wp_politeia_candidacies`
Add columns to handle the specific context of that election.

-   `party_id`: Links to the clean ID (e.g., RN).
-   `is_independent`: Boolean (True if "Independiente en cupo...").
-   `parent_party_id`: (Optional) If Independent in cupo, link to the sponsoring party.
-   `coalition_name`: (String) "Chile Vamos" (The pact valid for *this specific election*).

## 4. Action Plan (How to Fix)

1.  **Audit**: List all unique `official_name` values.
2.  **Map**: Create a mapping dictionary:
    ```json
    {
      "RN - Chile Vamos": "Renovación Nacional",
      "Independiente en cupo Renovación Nacional": "Renovación Nacional",
      "IND ( RN ) - Chile Vamos": "Renovación Nacional"
    }
    ```
3.  **Consolidate**:
    -   Select the "Master ID" for each party (e.g., ID 56 for RN).
    -   Update `wp_politeia_candidacies` and `wp_politeia_party_memberships` to point to the Master ID.
    -   Delete the redundant IDs from `wp_politeia_political_parties`.
4.  **Extract Coalitions**: Move the text after " - " (e.g., "Chile Vamos") to a new field if preserving coalition data is required.
