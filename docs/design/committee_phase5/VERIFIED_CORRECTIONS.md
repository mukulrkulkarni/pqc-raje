# Verified corrections — supersede conflicting draft CONTENT_SPEC statements
PI checked source and executed verify_example.py; results saved in example_results.json.

- Concordance boundary statements c(-p)=0 assume q<p. When q=p, the OUTER diff>=-q branch wins: c=1 at equality and above, otherwise 0. The denominator guard prevents unsafe division; the nested branches do preserve step semantics. Replace the draft claim that step semantics are not preserved.
- Discordance boundary d(-p)=0 assumes p<v. When p=v, the OUTER diff<=-v branch wins: d=1 at equality and below, otherwise 0.
- Orient lower-is-better criteria before pairwise computation: electre3/ranking.py compute_ranking copies G and negates each column for which CriterionConfig.maximize is false. Direct callers of partial_concordance/compute_block must supply already-oriented data. Positive threshold distances remain in criterion units.
- Arrow a→b denotes the directional assertion being ASSESSED: 'a is at least as good as b'. It does not mean outranking was already established, nor that a strictly beats b. Both a and b are objects; their role changes when direction reverses.
- At credibility C=1, the reduction mask d>C and d<1 cannot hold for valid d in [0,1]. Full veto d>=1 is handled separately and sets S=0. Do not suggest denominator guard is normally used at C=1. Source docstring contradicts full-veto implementation: flag as later code-doc issue, do not reproduce it in tutorials or alter production here.
- Diagonal clearing uses np.fill_diagonal: self-exclusion interpretation requires row/column indices identify the same objects. It does not validate this correspondence.
- Global concordance [0,1] requires finite partial values in [0,1], nonnegative normalized weights; global_concordance itself does not validate/normalize weights.
- Example outputs 0.85 (A→B) and 0.75 (B→A) are now verified against implementation, not merely manually derived. Inputs are illustrative, not recommended defaults. The non-veto example teaches concordance; full veto cases belong to discordance deep content.

Visual proposals must use these corrections. Reviewer should incorporate them into final content specification during the single planned cross-review.
