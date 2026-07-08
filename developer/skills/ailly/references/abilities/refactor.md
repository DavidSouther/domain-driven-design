# Refactor

> Coordinator reference loaded by `developer:ailly` after a Build-phase step is green, to improve the code before finishing.
> There is no standalone `developer:refactor` skill; you reach it from the Build phase and the cleanup phase.

## Overview

Post-green cleanup.
Runs only when tests pass and the working directory is clean.
Applies one refactoring at a time, verifying after each.
Stops when the smell vanishes, not when the code is maximally elegant.

**Guard:** check `git status` before starting.
If the working directory is not clean, stop immediately:

> "Working directory is not clean.
> Please commit or stash your changes, then restart the refactoring step."

**Constraint:** never refactor behavior and structure simultaneously.
If any check or test fails during refactoring, fix the code first, then restart the refactoring step.

## Behavior

1. Identify code smells in files touched in this loop and their logical neighbors.
   Use `git diff --name-only HEAD` to enumerate files changed since the last commit.
2. Write a refactoring plan to `.ailly/developer/YYYY-MM-DD-A-<topic>/refactor-plan.md`.
   Include one checkbox per refactoring: smell name, file and line range, intended resolution.
   Cross out each item as you complete it.
3. Apply each refactoring one at a time.
   After each: run check, run tests.
   Abort on repeated errors (see below).
4. If after refactoring the tests pass, but the smell lingers, that's OK.
   It persists until the next refactoring opportunity.
5. Record deferred smells if any remain (optional).

## Code smells to target

Code smells are patterns for applying refactoring.

### Code smells within classes

- **Three-Strikes Refactor** Duplicated code is an aroma, but has its place.
  Triplicate code is a smell.
  If you wait until you have three scenarios, each might be slightly different, and it gives you a better view for what the common feature is.
  If you refactor too early, you may find that the third scenario doesn’t quite fit with your refactored code.
- **Comments** There’s a fine line between comments that illuminate and comments that obscure.
  Are the comments necessary?
  Do they explain “why” and not “what”?
  Can you refactor the code so the comments aren’t required?
  And remember, you’re writing comments for people, not machines.
- **Conditional Complexity** Watch out for large conditional logic blocks, particularly blocks that tend to grow larger or change significantly over time.
  Consider alternative object-oriented approaches such as decorator, strategy, or type state.
- **Combinatorial Explosion** You have lots of code that does almost the same task but with tiny variations in data or behavior.
  This can be difficult to refactor, perhaps using generics or an interpreter.
- **Temporary Field** Watch out for objects that contain a lot of optional or unnecessary fields.
  If you’re passing an object as a parameter to a method, make sure that you’re using all of it and not cherry-picking single fields.
  Use the domain-objects pattern.
  See `patterns:using-patterns` and `references/patterns/domain-objects.md`.

- **Long Method** All other things being equal, a shorter method is easier to read, easier to understand, and easier to troubleshoot.
  Refactor long methods into smaller methods if you can.
- **Long Parameter List** The more parameters a method has, the more complex it is.
  Limit the number of parameters you need in a given method, or use an object to combine the parameters.
- **Large Class** Large classes, like long methods, are difficult to read, understand, and troubleshoot.
  Does the class contain too many responsibilities?
  Can you restructure the large class or break it into smaller classes?

- **Magic Constants** Avoid leaving constant, non-default primitive values in code.
  If a certain value must hold a string of a certain format, or a certain byte pattern has meaning, store it as a constant.
  Reference the constant whenever possible.
  However, format strings are not magic constants, as they have no shared meaning.
- **Type Embedded in Name** Avoid placing types in method names; it’s not only redundant, but it forces you to change the name if the type changes.
- **Uncommunicative Name** Does the name of the method succinctly describe what that method does?
  Could you read the method’s name to another developer and have them explain to you what it does?
  If not, rename it or rewrite it.
- **Inconsistent Names** Pick a set of standard terminology and stick to it throughout your methods.
  For example, if you have Open(), you should probably have Close().
  Drive the names from `domain:glossary`.

- **Dead Code** Ruthlessly delete unused code.
  That’s what source control systems are for.
  Use code coverage reports to identify unused and untested code.

### Code smells between classes

- **Alternative Classes with Different Interfaces** If two classes are similar on the inside, but different on the outside, perhaps you can modify them to share a common interface.
- **Primitive Obsession** Apply the newtype pattern instead of using primitive types at API boundaries.
  See `patterns:using-patterns` and `references/patterns/newtype.md`.
  Primitives are perfectly fine within a method or function.

- **Data Clumps** If you always see the same data hanging around together, possibly it belongs together.
  Consider rolling the related data up into a larger class.
- **Inheritance** Prefer composition to inheritance.
- **Message Chains** Watch out for long sequences of method calls or temporary variables to get routine data.
  Intermediaries are dependencies in disguise.
- **Parallel Inheritance Hierarchies** Every time you make a subclass of one class, you must also make a subclass of another.
  Consider folding the hierarchy into a single class.
- **Incomplete Library Class** A method is missing from the library, but you’re unwilling or unable to change the library to include it.
  The method ends up tacked on to some other class.
  If you can’t modify the library, consider isolating the method.

- **Inappropriate Intimacy** Watch out for classes that spend too much time together, or classes that interface in inappropriate ways.
  Classes should know as little as possible about each other.
- **Intermediary** If a class is delegating all its work, why does it exist?
  Cut out the intermediary.
  Beware classes that are merely wrappers over other classes or existing features in the framework.
- **Indecent Exposure** Beware of classes that unnecessarily expose their internals.
  Aggressively refactor classes to minimize their public surface.
  You should have a compelling reason for every item you make public.
  If you don’t, hide it.
- **Feature Envy** Methods that make extensive use of another class may belong in another class.
  Consider moving this method to the class it is so envious of.
- **Lazy Class** Classes should pull their weight.
  Every additional class increases the complexity of a project.
  If you have a class that isn’t doing enough to pay for itself, can you collapse or combine it with another class?

- **Divergent Change** If, over time, you make changes to a class that affect completely different parts of the class, it may contain too much unrelated features.
  Consider isolating the parts that changed in another class.
- **Shotgun Surgery** If a change in one class requires cascading changes in several related classes, consider refactoring so that you limit the changes to a single class.
- **Solution Sprawl** If it takes five classes to do anything useful, you might have solution sprawl.
  Consider simplifying and consolidating your design.

## Refactoring loop

```dot
digraph refactor {
    start [shape=doublecircle label="Start (working dir clean, tests green)"];
    identify [shape=box label="Identify smells in touched files + neighbors"];
    smells_found [shape=diamond label="Smells found?"];
    apply [shape=box label="Apply one refactoring"];
    run_checks [shape=box label="Run check + tests"];
    pass [shape=diamond label="Pass?"];
    fix_causes_error [shape=diamond label="Fix attempt causes same or new error?"];
    tried_thinking [shape=diamond label="Already tried thinking for this error?"];
    invoke_thinking [shape=box label="Consult references/abilities/thinking.md"];
    abort [shape=doublecircle label="ABORT"];
    fix_error [shape=box label="Fix the error"];
    more_smells [shape=diamond label="More smells?"];
    record_deferred [shape=box label="Record deferred smells (optional)"];
    done [shape=doublecircle label="Done"];

    start -> identify;
    identify -> smells_found;
    smells_found -> apply [label="yes"];
    smells_found -> done [label="no"];
    apply -> run_checks;
    run_checks -> pass;
    pass -> more_smells [label="yes"];
    pass -> fix_causes_error [label="no: fix error first"];
    fix_causes_error -> tried_thinking [label="yes"];
    fix_causes_error -> fix_error [label="no"];
    tried_thinking -> abort [label="yes"];
    tried_thinking -> invoke_thinking [label="no"];
    invoke_thinking -> fix_error [label="follow thinking plan"];
    fix_error -> run_checks;
    more_smells -> apply [label="yes"];
    more_smells -> record_deferred [label="no"];
    record_deferred -> done;
}
```

## Thinking trigger

Consult `references/abilities/thinking.md` through the active harness's isolation path when a refactoring causes a failure and a fix attempt produces the same or a new error.
Pass to the thinking runner: the exact error message, the refactoring you applied, and the smell you're addressing.

If you've already consulted `references/abilities/thinking.md` for this error and the same error reappears after following its plan, do **not** consult it again.
Instead, revert the changes and mark this refactoring as deferred.

## Deferred smells

If smells remain that are too risky to address now, record them.
Examples include changes that would require modifying multiple modules or situations where you encountered repeated failures while fixing:

Save to `.ailly/developer/YYYY-MM-DD-A-<topic>/deferred-refactoring.md`:

```markdown
# Deferred Refactoring

- `src/auth/handler.rs:42-80` **Long Method** handler is too long; extract `validate_token` and `build_session`
- `src/auth/handler.rs:55` **Magic Constant** the string `"Bearer:"` should be a constant
```
