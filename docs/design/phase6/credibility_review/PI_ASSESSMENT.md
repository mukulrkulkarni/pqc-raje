# Gate assessment — not an approval override
UI/UX APPROVED; Scientific, Engineering and Security NEEDS WORK. No commit.

Scientific: preconditions are requirements, not assertions of low-level enforcement. The current page already says preconditions are not validated here, and R2/Pitfalls describes empty criteria. A short additional sentence explicitly assigning direct-call validation to the caller would resolve ambiguity without code changes. Do not assert all possible input violations are checked by ranking.

Engineering: snapshot is a review copy, not a standalone executable checkout. Tests derive ROOT from __file__, so executing relocated snapshot tests resolves dependencies under snapshot/, incorrectly. Run canonical tests/test_credibility_deep.py from repository root; manifest hashes establish it is the reviewed file. Prior 88 targeted tests passed. No new test defects are established by running relocated copies.

Security: manifest pins changed files, not a distribution package. Shared assets and routes exist at canonical paths and are unchanged from pinned HEAD. dependency_evidence.json supplies exact paths, hashes and comparison. Inspect canonical dependencies; no need to clone the entire repo into the snapshot.

Next requires approval: one batched direct-caller sentence plus regression assertion, repository-root targeted check, then Scientific/Engineering/Security completion using canonical files and dependency hashes. No automatic retry; no new prototypes/algorithms. UI/UX remains approved unless its scope changes. Provisional 6,000–10,000 tokens, USD 1–3, 5–8 minutes, PI plus three reviewers. Stop if access fails.
