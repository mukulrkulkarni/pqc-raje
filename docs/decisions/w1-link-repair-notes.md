# W1 Ranking Tutorial Link Repair Notes

**Status:** Complete local repair evidence; browser resolution remains deferred.
**Scope:** Six broken ranking-tutorial repository-path links on static and Flask documentation surfaces.

## Ownership and strategy

| Surface | Authoritative owner | Before | After | Strategy |
|---|---|---|---|---|
| Flask `/docs/modules/ranking/tutorial` | `docs/modules/ranking_tutorial_side_by_side.html` | Six relative repository hyperlinks | One `#source-references` fragment; six repository paths as code text | Flask has no allow-listed repository-file routes. |
| Static `/modules/ranking/tutorial/index.html` | `scripts/build_website.py` generated from `docs/modules/ranking_tutorial_side_by_side.html` | Rewritten relative repository hyperlinks | Generated `#source-references` fragment | Regenerated; never hand-edited. |

The six retired served hyperlinks targeted `README.md`, CLI quickstart, debugging runbook, D4 fixture JSON, ranking core, and D4 evidence test. The source-reference note retains every repository path for local checkout users. The fragment resolves on both served surfaces.

## Commands and results

```text
python scripts\build_website.py
exit 0

python -m pytest -q tests\test_w1_ranking_tutorial_links.py tests\test_app_workflow.py tests\test_docs_routes.py tests\test_local_document_links.py
206 passed in 3.37s

python out\w1_link_audit.py
exit 0
references=260; valid=243; broken=0; planned=1; external=16; probes=52

python -m pytest -q
1069 passed

python -m compileall -q app electre3 scripts tests out\w1_link_audit.py
exit 0

git diff --check
exit 0
```

Full pytest initially exposed three D5 placement assertions that required the retired broken repository hyperlinks. W1 aligned those regression assertions with the valid served fragment strategy. The rerun passed.

## Reviews

| Review | Result | Evidence |
|---|---|---|
| Engineering | Approved | Authoritative source changed once; static derivative regenerated deterministically; link inventory has zero broken references; route, download, nested-path, fragment, asset, positive, negative, and edge coverage passed. |
| UI/UX | Approved with browser-deferred limitation | Link text identifies repository materials; fragment is focusable/resolvable; no layout or interaction code changed. Browser visual, keyboard, zoom, assistive-technology, offline, and load execution remains deferred and non-blocking. |

## Limitations

- No browser link-resolution or visual execution ran.
- External URLs remain classified but unfetched.
- Repository paths are intentionally not exposed as served URLs because Flask documentation routes do not serve arbitrary repository files.
- Static fragment resolution and Flask route behavior have local automated evidence only.
