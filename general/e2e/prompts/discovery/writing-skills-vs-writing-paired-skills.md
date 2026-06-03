We have two SKILL.md files for our project's logging story. One sets up
the subscriber registry once at startup. The other gets loaded at every
log call site. They reference each other in the body, but I'm not sure
the contract between them is right — the per-call-site skill keeps growing
a "before you start, make sure you have…" section that re-explains the
setup. Which `general:*` skill applies?
