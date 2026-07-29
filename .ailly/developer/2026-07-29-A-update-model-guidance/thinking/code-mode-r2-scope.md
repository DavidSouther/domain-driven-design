# Thinking: code-mode-r2-scope

**Error:** `R2 code-mode.md must scope Code Mode to standalone scripts/automations, not application features`

**Context:** Step 4, verify the integrated model-guidance contract. The step is reviewing the complete documentation contract after the model-selection, maintenance, Code Mode pricing, and harness-adapter changes.

## Situation Summary

The broader Code Mode shape test fails at R2 even though this branch did not change `developer/skills/ailly/references/shapes/code-mode.md` or `developer/tests/test_code_mode_shape.py`. The current and pre-branch versions have the same mismatch: the shape calls Code Mode a `"few-off" script or automation`, while R2 recognizes only the literal phrases `standalone script` or `small script`.

## Root Cause Analysis

This is a pre-existing source/test vocabulary mismatch, not a regression caused by the model-guidance work. The shape correctly excludes application features in meaning, but the R2 implementation does not infer that meaning: after lowercasing the file, it fails unless one of two exact substrings is present. Neither `"few-off" script` nor the later phrase `standalone automation` contains either accepted substring.

The test's own module contract describes Code Mode as purpose-built for `small standalone scripts and automations`, and the coordinator's Code Mode section already uses `small standalone script or automation`. Therefore, the narrowest contract-preserving repair is to align the shape's opening sentence with that established vocabulary; weakening R2 to accept `"few-off" script` would preserve inconsistent terminology and make the asserted standalone boundary less explicit.

## Forward-Backward Map

- **Current red, forward:** R2 reads and lowercases the shape, finds neither `standalone script` nor `small script`, and returns the reported error before checking R3–R8.
- **Branch-causality check:** both relevant files are unchanged across `3274499^..HEAD`, and the parent version already contains the same incompatible phrases, so reverting or altering the Step 2 pricing change cannot affect R2.
- **Desired green, backward:** R2 needs the shape itself to contain an accepted phrase while retaining the explicit exclusion of application features.
- **Meeting point:** change the opening scope sentence to describe a `small standalone script or automation`; this makes the documentation vocabulary agree with the feature-test contract and the coordinator without changing Code Mode behavior.

## Next Steps (in order)

1. **Record R2 as an unrelated pre-existing baseline failure during Step 4 review** — expected outcome: the model-guidance diff remains attributable only to its planned files, and no attempt is made to fix R2 through `code-mode-thresholds.md` pricing or model-selection text.
2. **In the Build phase, change the shape's opening scope sentence from a `"few-off" script or automation` to a `small standalone script or automation`, preserving the immediately following application-feature exclusion** — expected outcome: the lowercased shape contains both `small script` semantics and the exact `standalone script` substring, so R2 no longer returns this error while the documented boundary becomes explicit.
3. **Run only `developer/tests/test_code_mode_shape.py` after that change** — expected outcome: execution proceeds beyond R2 and ends with `PASS: Code Mode shape reference and routing contract holds`, because the currently inspected shape already contains the R3–R8 markers.
4. **Re-run the Step 4 integrated verification unchanged** — expected outcome: the broader suite no longer stops on Code Mode R2; any remaining failure identifies a separate integrated-contract issue rather than this vocabulary mismatch.
